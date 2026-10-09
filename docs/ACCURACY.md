# Accuracy against NASA JPL, 1800 through 2100

Measured author-side results, pending independent reproduction. Errors are sampled numerical residuals in arcseconds, not a claim of perfect physical prediction.

3,612 monthly TT instants per physical graha on DE440, plus 300 range-spanning TT instants per graha from independent JPL Horizons quantity 45 (2,100 rows). Horizons reports DE441. Both reductions use solar-only deflection with an opaque solar photosphere; light-time and aberration remain enabled.

| Graha / target | DE440 median | DE440 worst | Horizons median | Horizons P95 | Horizons worst | Worst Horizons sample |
|---|---:|---:|---:|---:|---:|---|
| Sun centre | 1.93862718e-05 | 0.000108337531 | 1.5601669e-06 | 2.99024095e-06 | 3.80815838e-06 | 1976-02 |
| Moon centre | 9.85119698e-05 | 0.000716859608 | 0.00243318773 | 0.0172649702 | 0.0253509189 | 1801-01 |
| Mercury centre | 1.93394101e-05 | 0.000107906669 | 1.73181857e-06 | 3.58725987e-06 | 5.19406063e-06 | 2059-08 |
| Venus centre | 1.9265741e-05 | 0.00010745473 | 1.61171841e-06 | 3.01558294e-06 | 5.10202485e-06 | 1911-09 |
| Mars system barycentre | 1.94618337e-05 | 0.000108352879 | 1.40373266e-06 | 2.52963415e-06 | 3.22078937e-06 | 1912-09 |
| Jupiter system barycentre | 1.936898e-05 | 0.000108498989 | 1.38976159e-06 | 2.14319505e-06 | 2.55158769e-06 | 1976-02 |
| Saturn system barycentre | 1.95472182e-05 | 0.000108927907 | 1.39243358e-06 | 2.16523355e-06 | 2.71751497e-06 | 1922-10 |

R1 limits: P95 at most 0.02 arcseconds and sampled maximum at most 0.1 arcseconds. All seven rows pass these limits. Mars/Jupiter/Saturn are the compact-DE440 system barycentres (NAIF 4/5/6); this table does not assert physical-centre accuracy for those three.

| Node definition | Typical residual | Worst residual | Reference |
|---|---:|---:|---|
| True Rahu | 1.38436462e-06 | 5.9393642e-06 | Independent Skyfield DE440 orbit plane, mean ecliptic of date |
| Mean Rahu | 4.09272616e-10 | 3.68345354e-09 | Independent Decimal Meeus eq. 47.7 |
| True Ketu | Same orbit-axis residual as True Rahu | 2.04636308e-10 antipode residual | Exact opposite axis |
| Mean Ketu | Same definition residual as Mean Rahu | 2.04636308e-10 antipode residual | Exact opposite axis |

Nodes are derived definitions. JPL does not publish a Vedic Rahu/Ketu longitude. True-node limit is 0.1 arcsecond; mean-node definition limit is 0.001 arcsecond. Both pass.

The original independent check failed at occulted Mercury in November 2094 (0.676583 arcseconds). The original failed table remains in the private Astro review packet; this package carries the corrected public numerical rows and JPL receipts. Seven neighbouring samples isolate the difference to solar occultation; the engine now follows the observed Horizons convention there. This is a stated model change, not a lowered error ceiling.

This table proves the sampled Tier-A positions and node definitions only. It does not prove civil-time/Delta-T accuracy, every instant in the interval, superiority to Swiss, or all BAR-v1 release rows. R3 through R10 still require one-source qualification. R10 has not passed, so production cutover is withheld.

[Horizons manual and quantity 45](https://ssd.jpl.nasa.gov/horizons/manual.html) Â· [Skyfield apparent-coordinate API](https://rhodesmill.org/skyfield/api-position.html)

Public numerical reference data: ../bench/studies/E2-accuracy/raw-t1.json, raw-t2.json, manifest.json and horizons/receipts.json. Engine-function equivalence is recorded in ../evidence/E2-oss-ready/engine-function-equivalence.json. Raw studies are excluded from the wheel.
