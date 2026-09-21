# Phase 2 license evidence — independent Sol review

Date: 2026-09-09 (Asia/Tokyo)  
Reviewer role: GPT-5.6 Sol, falsification-first independent review  
Verdict: `REVISE`  
Operational disposition: `BLOCKED_POLICY`; no bounded live capture is currently authorized.

This is an engineering-governance review, not legal advice. It evaluates the
draft against the selected Policy, frozen ADR-0015, and current official
publisher pages. It does not change a database permission, approve Production,
accept terms, contact a provider, or establish PIT/provider quality.

## Authority and scope

- Selected Policy: `OPTIVEST_AI_POLICY_V10.md`, verified SHA-256
  `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.
- Frozen source contract: ADR-0015 and
  `docs/PHASE2_PROVIDER_EVIDENCE_DESIGN.md`.
- Draft reviewed: `docs/PHASE2_LICENSE_EVIDENCE_REVIEW.md`.
- Exact data scope: SEC submissions/API metadata and the atomic Nasdaq pair
  `nasdaqlisted.txt` plus `otherlisted.txt`.

## Current official publisher evidence

SEC:

- [EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
  documents unauthenticated REST APIs for submissions and XBRL, plus bulk
  archives, and requires automated access to follow SEC policy.
- [Developer Resources](https://www.sec.gov/about/developer-resources)
  permits comprehensive HTTPS/scripted access, requires efficient retrieval,
  limits aggregate traffic to no more than 10 requests per second, and rejects
  undeclared bots.
- [Webmaster FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions)
  says Government-created SEC content and public EDGAR filing content are free
  to access and reuse; it also supplies the declared User-Agent pattern.
- [Privacy and Security Policy](https://www.sec.gov/about/privacy-information)
  permits copying and further distribution of information presented on
  sec.gov, requests appropriate source citation, prohibits seal/logo misuse,
  and restricts trademark use or implied SEC affiliation.

Nasdaq:

- [Symbol Lookup](https://www.nasdaqtrader.com/Trader.aspx?id=symbollookup)
  says specified Nasdaq Events Data, including “Nasdaq Listed,” is available
  without restriction or further licensing notwithstanding Nasdaq terms. It
  does not name “Other-Exchange Listed” or `otherlisted.txt` in that exception.
- [Directory definitions](https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs)
  identify `nasdaqlisted.txt` under Nasdaq-Listed Securities and separately
  identify `otherlisted.txt` under Other Exchange-Listed Securities.
- [Nasdaq Legal Information](https://www.nasdaq.com/legal), last updated
  2026-05-11, applies to any Nasdaq page/service and otherwise prohibits
  automated or manual capture, copying, subsequent storage, derivative works,
  redistribution, and use in data-analysis software without express permission.

## Per-use evidence disposition

These are review conclusions for the proposed evidence mapping. They do not
alter the effective database state, which remains `NOT_VERIFIED` for every row
until immutable evidence is recorded and Astra freezes an exact permission and
duty contract.

| Dataset/use | Network capture | Local raw storage | Retention | Derived storage | Internal display | Redistribution | Commercial/Production |
|---|---|---|---|---|---|---|---|
| SEC submissions/API metadata | `ALLOWED` for bounded research | `ALLOWED` | `ALLOWED` | `ALLOWED` | `ALLOWED` | `ALLOWED` | `NOT_VERIFIED` |
| `nasdaqlisted.txt` considered alone | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |
| `otherlisted.txt` considered alone | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |
| Atomic paired Nasdaq dataset | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` | `NOT_VERIFIED` |

### SEC rationale and duties

The SEC pages affirm scripted API access and reuse broadly enough to support
the first six research operations for SEC submissions/API metadata. Required
capture duties are: a declared descriptive User-Agent with operator contact;
aggregate SEC traffic no higher than the publisher's 10 requests/second limit;
the stricter frozen 5 requests/second application cap; efficient retrieval of
only needed data; no access-control evasion; and no persistence of the contact.

For display or redistribution, cite SEC as source, do not use SEC seals/logos,
and do not imply affiliation or approval. The SEC describes citation as a
request, not as a condition of permission; OptiVest may nevertheless impose it
as an application duty. No publisher retention/deletion deadline was found in
the reviewed pages. The nonblank retention duty required by frozen code must
therefore distinguish an application safeguard from a publisher-imposed term.

The SEC Webmaster FAQ expressly includes public EDGAR filing content in its
reuse statement. The draft should not imply that SEC policy excludes all
exhibits. It should instead say that this review is limited to submissions/API
metadata, does not independently adjudicate embedded third-party intellectual
property, and does not cover material reached only through off-site links.

`COMMERCIAL_PRODUCTION` remains `NOT_VERIFIED`: the reviewed pages contain no
operation-specific commercial/Production grant, the combined field conflates a
source-use question with OptiVest's separate Production-readiness gates, and no
license conclusion can satisfy Policy section 18.

### Nasdaq rationale

The “without restriction” exception is strong favorable evidence for data
called “Nasdaq Listed,” but the strict use-by-use gate cannot extend it by
inference. The page does not expressly tie the exception to both physical files
or enumerate automated capture, exact-byte storage, retention, derivation, or
internal analysis. Most importantly, `otherlisted.txt` is separately defined as
Other Exchange-Listed Securities and is not named in the exception.

The current general terms expressly prohibit the operations required by the
frozen collector absent permission. A duty or attribution label cannot cure an
unverified permission. Because ADR-0015 requires the two files as one logical,
atomic capture, one unresolved part blocks every required operation for the
pair.

## Required corrections to the draft

1. Add the SEC Webmaster FAQ and its explicit EDGAR reuse statement.
2. Replace `ALLOWED_RESEARCH_PROPOSED` and
   `ALLOWED_WITH_ATTRIBUTION_PROPOSED` with the frozen canonical states
   `ALLOWED`, `BLOCKED`, or `NOT_VERIFIED`; separately label the table as a
   review proposal and keep effective database rows unchanged until freeze.
3. Describe SEC citation accurately as publisher-requested, while recording it
   as an OptiVest application duty if desired.
4. Narrow the SEC third-party caveat as stated above; do not contradict the
   SEC's express statement about public EDGAR filing content.
5. Split `nasdaqlisted.txt`, `otherlisted.txt`, and the effective atomic pair in
   the evidence analysis. Do not use the Nasdaq-listed exception for the other
   exchange file.
6. State that the broad Nasdaq phrase does not satisfy the frozen
   operation-specific permission standard while conflicting general terms
   remain current.
7. Separate source commercial-use analysis from OptiVest Production readiness,
   or retain the combined row as `NOT_VERIFIED` with that limitation explicit.
8. Before any permission elevation, preserve reviewed source bytes or an
   immutable artifact reference, SHA-256, canonical URL, retrieval instant,
   publisher last-updated value when available, reviewer, reasoning, and every
   use-specific duty in a new append-only evidence version.

## Capture and acceptance consequence

- Current database permissions remain `NOT_VERIFIED`; therefore no SEC or
  Nasdaq live request is authorized now.
- After the corrections, immutable evidence record, and Astra freeze, a
  separately scoped SEC-only bounded research capture could be authorized by
  its six allowed research uses. This review does not itself grant that state.
- Frozen design section 7 item 11 requires both an SEC capture and the paired
  Nasdaq capture. It cannot run while any required Nasdaq use is
  `NOT_VERIFIED`; partial SEC success cannot satisfy the item.
- Provider validation, timestamp semantics, PIT suitability, historical
  completeness, model/OOS/shadow evidence, Risk Budget, and Production remain
  unchanged: `NOT_VERIFIED`, `RISK BUDGET NOT APPROVED`,
  `SHADOW VALIDATION NOT PASSED`, and `NOT PRODUCTION READY` as applicable.

