# Phase 2 license evidence review — SEC and Nasdaq forward capture

Status: `REVISED AFTER SOL REVIEW / NO PERMISSION FREEZE`. Date reviewed: 2026-09-09. Scope: engineering permission evidence for the bounded Phase 2 research capture only. This is not legal advice, provider/PIT validation, Production approval, paid-license acceptance or permission to trade. Effective database permissions remain `NOT_VERIFIED`.

## Sources reviewed

### SEC

- SEC EDGAR APIs: <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>
- SEC Developer Resources / Fair Access: <https://www.sec.gov/about/developer-resources>
- SEC Privacy and Security Policy, Website Dissemination: <https://www.sec.gov/about/privacy-information>
- SEC Webmaster Frequently Asked Questions: <https://www.sec.gov/about/webmaster-frequently-asked-questions>
- Accessing EDGAR Data: <https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data>

The SEC expressly documents programmatic API and archive access, asks automated clients to follow fair-access rules, and limits aggregate traffic to no more than 10 requests/second. The selected adapter remains capped at 5 requests/second and uses a descriptive User-Agent. SEC also states that information presented on sec.gov is public information that users may copy or further distribute without SEC permission, and its Webmaster FAQ states that Government-created SEC content and public EDGAR filing content are free to access and reuse. Appropriate source citation is requested, not stated as a condition of permission; OptiVest proposes it as an application duty. This review is limited to SEC-hosted submissions/API metadata and does not independently adjudicate embedded third-party intellectual property or material reached only through off-site links.

### Nasdaq

- Nasdaq Trader Symbol Lookup / Downloadable Files: <https://www.nasdaqtrader.com/Trader.aspx?id=symbollookup>
- Nasdaq Trader directory definitions: <https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs>
- Nasdaq general website terms: <https://www.nasdaq.com/legal>

The Symbol Lookup page labels the directory as current-day data and links to public downloadable files. It states that specified Nasdaq Events Data, including Nasdaq Listed, is available without restriction or further licensing notwithstanding the general website terms. Directory definitions separately identify `nasdaqlisted.txt` and `otherlisted.txt`; the exception does not unambiguously name the latter or map the atomic pair to automated capture, storage and derivation. The general Nasdaq terms otherwise prohibit automated/manual capture, storage, derivative use and AI/data-analysis use without permission. Therefore the exception cannot safely be extended by inference to either operation-specific permissions or the required pair.

## Proposed per-use disposition

This is a pre-review proposal. No database permission changes are authorized until independent review and a frozen decision.

| Dataset | Network capture | Local raw storage | Retention | Derived storage | Internal display | Redistribution | Commercial/Production |
|---|---|---|---|---|---|---|---|
| SEC submissions/API metadata | `ALLOWED` (proposed research mapping) | `ALLOWED` (proposed) | `ALLOWED` (proposed) | `ALLOWED` (proposed) | `ALLOWED` (proposed) | `ALLOWED` (proposed) | `NOT_VERIFIED` |
| `nasdaqlisted.txt` alone | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |
| `otherlisted.txt` alone | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |
| Atomic paired Nasdaq dataset | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |

Proposed SEC duties: identify the automated client; keep total SEC traffic at or below the stricter configured 5 requests/second cap; retrieve only necessary data; attribute SEC as an OptiVest application safeguard; do not use SEC seals/logos or imply SEC affiliation. No publisher retention/deletion deadline was found; any nonblank retention duty used by the application must be labeled as an application safeguard, not a publisher term.

Nasdaq blocker: obtain written clarification or a publisher page that explicitly covers both `nasdaqlisted.txt` and `otherlisted.txt`, automated retrieval, exact-byte local retention, derived normalized storage and internal research display. A paid agreement, order form, external billing or acceptance of new commercial terms requires `USER_CONFIRMATION_REQUIRED` before action.

## Decision and implementation boundary

1. Do not change any current `NOT_VERIFIED` permission row before Sol reviews this evidence and Astra freezes an exact permission version/duty contract.
2. Even if SEC research uses are approved, the frozen paired live acceptance cannot run partially: Nasdaq remains blocked, so design section 7 item 11 and full Phase 2 acceptance remain `NOT VERIFIED`.
3. No reviewed term establishes timestamp semantics, PIT suitability, historical completeness, tradability or provider quality. Those validation states remain `NOT_VERIFIED`.
4. Do not use general Nasdaq terms as permission for automated capture. Do not treat public reachability as a license.
5. Preserve reviewed source URL, retrieval/review instant, content hash or immutable artifact reference, reviewer identity, reason and every use-specific status/duty in an append-only license-evidence version before any future permission elevation.

## Independent review result

Sol reviewed this mapping in `docs/reviews/phase2_license_evidence_independent_review.md` and returned `REVISE`; the corrections above incorporate that review. No permission freeze follows because exact reviewed source bytes or immutable artifact references, hashes, retrieval timestamps and the final append-only evidence version have not been created. Nasdaq ambiguity remains `NOT_VERIFIED`; no favorable inference is permitted. No bounded live capture is authorized.
