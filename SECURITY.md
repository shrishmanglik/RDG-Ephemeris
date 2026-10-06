# Security Policy

## Supported versions

ephemeris-oss is pre-1.0. Security fixes target the latest 0.x release only.

| Version          | Supported |
| ---------------- | --------- |
| 0.x (latest)     | Yes       |
| 0.x (older)      | No        |

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub private
vulnerability reporting, from the repository's Security tab ("Report a
vulnerability"). Do not open a public issue or pull request with exploit
details.

Include:

- the affected version or commit;
- the affected function, module or command;
- clear reproduction steps;
- the expected impact.

## Scope

In scope:

- kernel integrity: ephemeris kernel files are verified by SHA-256 before use,
  and any way to load a kernel that bypasses or defeats that check is in scope;
- path handling in the kernel download and cache code;
- unsafe deserialisation or code execution reachable from package inputs;
- package contents that accidentally include private or temporary files.

Out of scope:

- vulnerabilities in third-party dependencies, which should be reported to
  those projects;
- numerical accuracy disagreements, which should be filed as ordinary issues.
