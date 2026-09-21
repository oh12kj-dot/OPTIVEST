# UNVERIFIED_USER_DIRECTED_CAPTURE

User-directed automated retrieval from Nasdaq Trader public endpoints on 2026-09-09. These files are quarantined raw evidence and were not inserted into the trusted Phase 2 database. Provider permission, timestamp semantics, PIT suitability, security identity and completeness remain `NOT_VERIFIED`.

| Part | URL | HTTP | Request UTC | Response UTC | Bytes | Lines | SHA-256 | Source trailer |
|---|---|---:|---|---|---:|---:|---|---|
| `nasdaqlisted.txt` | `https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt` | 200 | `2026-09-09T04:47:42.4119522Z` | `2026-09-09T04:47:43.4319473Z` | 347068 | 5594 | `31a17ff730e8e42753e45051ac44732a3790ff36ed0a03adf32f0170a211a2e4` | `File Creation Time: 0908202621:31|||||||` |
| `otherlisted.txt` | `https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt` | 200 | `2026-09-09T04:47:43.4981891Z` | `2026-09-09T04:47:44.3569196Z` | 539021 | 7599 | `4f5ae4f711afd0e39a75f07393c84c8f549dd98cf58a76459f0dd26a9ed02ce6` | `File Creation Time: 0908202621:31||||||` |

Offline parser result after the real-trailer compatibility fix:

- Nasdaq: 5,592 data rows; 3,002 `ELIGIBLE_FOR_REVIEW`; 2,590 `REVIEW_REQUIRED`.
- Other exchanges: 7,597 data rows; 1,732 `ELIGIBLE_FOR_REVIEW`; 5,865 `REVIEW_REQUIRED`.
- Observed `Exchange=M` rows remain `REVIEW_REQUIRED`.
- Independent Sol parser review: PASS for this scoped compatibility repair.

This manifest does not grant or assert a provider license and does not make the data decision-eligible.

