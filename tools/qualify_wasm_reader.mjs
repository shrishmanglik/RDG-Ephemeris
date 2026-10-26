#!/usr/bin/env node
// SPDX-License-Identifier: Apache-2.0

import { createHash } from "node:crypto";
import { open, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const POSITION_TOLERANCE_KM = 2e-6;
const VELOCITY_TOLERANCE_KM_S = 1e-10;
const HASH_BUFFER_BYTES = 1024 * 1024;

async function sha256File(path) {
  const handle = await open(path, "r");
  const hash = createHash("sha256");
  const buffer = Buffer.allocUnsafe(HASH_BUFFER_BYTES);
  let position = 0;
  try {
    const before = await handle.stat({ bigint: true });
    for (;;) {
      const { bytesRead } = await handle.read(buffer, 0, buffer.byteLength, position);
      if (bytesRead === 0) break;
      hash.update(buffer.subarray(0, bytesRead));
      position += bytesRead;
    }
    const after = await handle.stat({ bigint: true });
    if (after.size !== before.size || after.mtimeNs !== before.mtimeNs) {
      throw new Error(`Source changed while hashing: ${path}`);
    }
    return { sha256: hash.digest("hex"), bytes: Number(before.size) };
  } finally {
    await handle.close();
  }
}

function validateInput(input) {
  if (!input || !Array.isArray(input.kernels) || input.kernels.length === 0) {
    throw new Error("Input must contain a nonempty kernels array");
  }
  for (const [kernelIndex, kernel] of input.kernels.entries()) {
    if (
      !kernel ||
      typeof kernel.path !== "string" || kernel.path.length === 0 ||
      typeof kernel.identifier !== "string" || kernel.identifier.length === 0 ||
      !/^[0-9a-f]{64}$/i.test(kernel.sha256) ||
      !Number.isSafeInteger(kernel.bytes) ||
      kernel.bytes <= 0 ||
      !Array.isArray(kernel.samples) ||
      kernel.samples.length === 0
    ) {
      throw new Error(`Invalid kernel declaration at index ${kernelIndex}`);
    }
    for (const [sampleIndex, sample] of kernel.samples.entries()) {
      if (
        !sample ||
        !Number.isInteger(sample.target) ||
        sample.target < -2147483648 ||
        sample.target > 2147483647 ||
        !Number.isInteger(sample.center) ||
        sample.center < -2147483648 ||
        sample.center > 2147483647 ||
        !Number.isFinite(sample.tdb_seconds) ||
        !Array.isArray(sample.expected) ||
        sample.expected.length !== 6 ||
        !sample.expected.every(Number.isFinite)
      ) {
        throw new Error(`Invalid sample ${sampleIndex} for kernel ${kernel.identifier}`);
      }
    }
  }
}

function compareState(actual, expected) {
  if (!Array.isArray(actual) || actual.length !== 6 || !actual.every(Number.isFinite)) {
    return { pass: false, positionErrorKm: Infinity, velocityErrorKmS: Infinity };
  }
  let positionErrorKm = 0;
  let velocityErrorKmS = 0;
  for (let index = 0; index < 3; index += 1) {
    positionErrorKm = Math.max(positionErrorKm, Math.abs(actual[index] - expected[index]));
    velocityErrorKmS = Math.max(
      velocityErrorKmS,
      Math.abs(actual[index + 3] - expected[index + 3])
    );
  }
  return {
    pass:
      positionErrorKm <= POSITION_TOLERANCE_KM &&
      velocityErrorKmS <= VELOCITY_TOLERANCE_KM_S,
    positionErrorKm,
    velocityErrorKmS
  };
}

async function qualifyKernel(kernel, readSpkStateSeekable) {
  const receipt = {
    identifier: kernel.identifier,
    sha256: kernel.sha256.toLowerCase(),
    bytes: kernel.bytes,
    actualSampleCount: kernel.samples.length,
    repeatedSampleCount: 0,
    requestCount: 0,
    maxRequestedBytes: 0,
    totalReadBytes: 0,
    maxPositionErrorKm: 0,
    maxVelocityErrorKmS: 0,
    failingIndices: [],
    repeatFailures: [],
    pass: false
  };
  const handle = await open(kernel.path, "r");
  let before;
  try {
    before = await handle.stat({ bigint: true });
    if (before.size !== BigInt(kernel.bytes)) {
      throw new Error(`Declared byte size does not match ${kernel.identifier}`);
    }

    const hash = createHash("sha256");
    const hashBuffer = Buffer.allocUnsafe(HASH_BUFFER_BYTES);
    let hashPosition = 0n;
    for (;;) {
      const { bytesRead } = await handle.read(
        hashBuffer,
        0,
        hashBuffer.byteLength,
        Number(hashPosition)
      );
      if (bytesRead === 0) break;
      hash.update(hashBuffer.subarray(0, bytesRead));
      hashPosition += BigInt(bytesRead);
    }
    if (hash.digest("hex") !== kernel.sha256.toLowerCase()) {
      throw new Error(`SHA-256 mismatch for ${kernel.identifier}`);
    }

    const source = {
      size: kernel.bytes,
      async read(offset, length) {
        receipt.requestCount += 1;
        receipt.maxRequestedBytes = Math.max(receipt.maxRequestedBytes, length);
        const bytes = Buffer.allocUnsafe(length);
        let filled = 0;
        while (filled < length) {
          const result = await handle.read(bytes, filled, length - filled, offset + filled);
          if (result.bytesRead === 0) break;
          filled += result.bytesRead;
          receipt.totalReadBytes += result.bytesRead;
        }
        return new Uint8Array(bytes.buffer, bytes.byteOffset, filled);
      }
    };

    const baseline = new Map();
    for (const [sampleIndex, sample] of kernel.samples.entries()) {
      try {
        const actual = await readSpkStateSeekable(
          source,
          sample.target,
          sample.center,
          sample.tdb_seconds
        );
        baseline.set(sampleIndex, actual);
        const comparison = compareState(actual, sample.expected);
        receipt.maxPositionErrorKm = Math.max(
          receipt.maxPositionErrorKm,
          comparison.positionErrorKm
        );
        receipt.maxVelocityErrorKmS = Math.max(
          receipt.maxVelocityErrorKmS,
          comparison.velocityErrorKmS
        );
        if (!comparison.pass) receipt.failingIndices.push(sampleIndex);
      } catch (error) {
        receipt.failingIndices.push(sampleIndex);
        receipt.sampleErrors ??= [];
        receipt.sampleErrors.push({ index: sampleIndex, message: error.message });
      }
    }

    const repeatIndices = [0, kernel.samples.length - 1];
    for (const [repeatIndex, sampleIndex] of repeatIndices.entries()) {
      receipt.repeatedSampleCount += 1;
      const sample = kernel.samples[sampleIndex];
      try {
        const actual = await readSpkStateSeekable(
          source,
          sample.target,
          sample.center,
          sample.tdb_seconds
        );
        const comparison = compareState(actual, sample.expected);
        receipt.maxPositionErrorKm = Math.max(
          receipt.maxPositionErrorKm,
          comparison.positionErrorKm
        );
        receipt.maxVelocityErrorKmS = Math.max(
          receipt.maxVelocityErrorKmS,
          comparison.velocityErrorKmS
        );
        const original = baseline.get(sampleIndex);
        const identical = original && actual.every((value, index) => value === original[index]);
        if (!comparison.pass || !identical) {
          receipt.repeatFailures.push({ repeatIndex, sampleIndex, identical: Boolean(identical) });
        }
      } catch (error) {
        receipt.repeatFailures.push({ repeatIndex, sampleIndex, message: error.message });
      }
    }

    receipt.failingIndices = [...new Set(receipt.failingIndices)].sort((a, b) => a - b);
    const after = await handle.stat({ bigint: true });
    if (after.size !== before.size || after.mtimeNs !== before.mtimeNs) {
      throw new Error(`Kernel changed during qualification: ${kernel.identifier}`);
    }
    receipt.fileStable = true;
    receipt.pass = receipt.failingIndices.length === 0 && receipt.repeatFailures.length === 0;
    return receipt;
  } catch (error) {
    receipt.error = { name: error.name, message: error.message };
    if (before) {
      const after = await handle.stat({ bigint: true }).catch(() => null);
      receipt.fileStable = Boolean(
        after && after.size === before.size && after.mtimeNs === before.mtimeNs
      );
    }
    return receipt;
  } finally {
    await handle.close();
  }
}

async function main() {
  const [inputPath, wasmPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !wasmPath || !outputPath) {
    console.error("FAIL qualify_wasm_reader: expected INPUT_JSON WASM_PATH OUTPUT_JSON");
    process.exitCode = 2;
    return;
  }

  const sdkPath = fileURLToPath(new URL("../web/ephemeris-browser.js", import.meta.url));
  const catalogPath = fileURLToPath(new URL("../web/ayanamsa-catalog.js", import.meta.url));
  const receipt = {
    schema: "ephemeris-oss-wasm-reader-qualification-v1",
    scope: "Same-kernel geometric J2000 SPK reader agreement only; not physical or apparent-position accuracy.",
    pass: false,
    input: { path: inputPath },
    inputJsonSha256: null,
    sources: {},
    tolerances: {
      positionKm: POSITION_TOLERANCE_KM,
      velocityKmS: VELOCITY_TOLERANCE_KM_S
    },
    kernels: []
  };

  try {
    const inputBytes = await readFile(inputPath);
    receipt.inputJsonSha256 = createHash("sha256").update(inputBytes).digest("hex");
    const input = JSON.parse(inputBytes.toString("utf8"));
    validateInput(input);

    const [wasmSource, sdkSource, catalogSource] = await Promise.all([
      sha256File(wasmPath),
      sha256File(sdkPath),
      sha256File(catalogPath)
    ]);
    receipt.sources = {
      wasm: { path: wasmPath, ...wasmSource },
      sdkJavaScript: { path: sdkPath, ...sdkSource },
      generatedCatalogJavaScript: {
        path: catalogPath,
        ...catalogSource
      }
    };

    const sdk = await import(new URL("../web/ephemeris-browser.js", import.meta.url));
    await sdk.initEphemerisWasm(await readFile(wasmPath));
    for (const kernel of input.kernels) {
      receipt.kernels.push(await qualifyKernel(kernel, sdk.readSpkStateSeekable));
    }
    receipt.pass = receipt.kernels.every(kernel => kernel.pass);
  } catch (error) {
    receipt.error = { name: error.name, message: error.message };
  }

  try {
    await writeFile(outputPath, `${JSON.stringify(receipt, null, 2)}\n`, "utf8");
  } catch (error) {
    console.error(`FAIL qualify_wasm_reader: could not write receipt (${error.message})`);
    process.exitCode = 1;
    return;
  }
  const samples = receipt.kernels.reduce((total, kernel) => total + kernel.actualSampleCount, 0);
  console.log(`${receipt.pass ? "PASS" : "FAIL"} qualify_wasm_reader: ${receipt.kernels.length} kernels, ${samples} samples`);
  if (!receipt.pass) process.exitCode = 1;
}

await main();
