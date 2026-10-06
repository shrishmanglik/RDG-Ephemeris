# Contributing to ephemeris-oss

## Development setup

```bash
pip install -e .[test]
pytest -q
```

Keep runtime dependencies minimal. A new dependency needs a stated reason and a
licence compatible with Apache-2.0.

## Developer Certificate of Origin

Every commit must be signed off under the Developer Certificate of Origin 1.1
(https://developercertificate.org/). Sign off with:

```bash
git commit -s
```

This adds a `Signed-off-by:` line with your name and email. By signing off you
certify that you wrote the change, or otherwise have the right to submit it
under the project licence, as set out in the DCO text at that link. Pull
requests with unsigned commits are not merged.

## Clean-room rule

This package is a clean-room implementation.

- Do not consult, port, translate or paraphrase code from GPL or AGPL ephemeris
  libraries, or from any other copyleft astronomy library, while working on
  this project.
- Work from primary publications: IAU resolutions, IERS Conventions, JPL and
  NAIF documentation, and peer-reviewed papers.
- If you have previously studied the source of such a library in detail, say
  so in your pull request so the maintainers can decide how to review it.

## Numeric constants

Every numeric constant in `src/` must do one of the following:

- cite a primary publication (author, title, year, and the table, equation or
  section the value comes from), or
- carry the label `Swiss-compatible realisation` or `Swiss-compatible
  convention`, together with the reason the value is chosen for compatibility
  rather than derived from a primary source.

A constant with neither is rejected by the provenance check.

## Claims

No number may appear in documentation, docstrings, the README or release notes
unless it has an entry in `claims.yaml` that states how it is reproduced. This
covers accuracy figures, speed figures, date ranges and comparisons with other
libraries. Do not make security, production or endorsement claims.

## Tests

Tests are required for every change in behaviour. Write the test first and show
that it fails on the code before your change, then make it pass. A test that
passes before the fix proves nothing.

## Pull request checklist

All of the following must exit 0:

```bash
pytest -q
python tools/check_provenance.py src --allow tools/provenance-allow.txt
python tools/check_internal_ids.py src tests docs
```

Also confirm:

- no secrets, credentials, private data or downloaded kernel files are
  committed;
- every new constant is cited or labelled as above;
- every new number in prose has a `claims.yaml` entry.
