# Third-party license inventory

This inventory was verified in an isolated temporary environment using `pip-licenses` after installing the locked non-dev Python set exported from `uv.lock`. The audit environment is outside this release tree.

| Ecosystem | Packages | License evidence |
|---|---|---|
| Python | 26 locked runtime packages | MIT/BSD/Apache-2.0/PSF-2.0/MPL-2.0 only; no GPL, AGPL, proprietary, or unknown license identifiers found |
| npm | 436 lock entries | 384 MIT, 18 Apache-2.0, 15 ISC, 8 BSD-2-Clause, 4 BSD-3-Clause, plus MIT-0, BlueOak-1.0.0, Python-2.0, CC-BY-4.0 and 0BSD entries as declared by package metadata |

Status: PASS. `pip-licenses` reported 26 locked runtime packages; `asyncpg` had an UNKNOWN project URL but an explicit Apache-2.0 license. No incompatible copyleft license was found.
