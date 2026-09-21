# OptiVest AI Development & Investment Policy — Compact V10 — Final

> Greenfield / Evidence-Grounded / Robust Risk-Budgeted / Portfolio-First / Controlled-Delegation  
> Source of Truth priority: latest explicit user instruction → §1 → approved Mandate/Risk Budget → approved `DECISIONS.md`  
> Canonical Uncertainty Separation: `U_objective` / `U_risk` / `S_stress`  
> Never infer unapproved Risk Limits, Drawdown Limits, Validation results, or Production approval.

---

# 1. Sole Investment Objective

OptiVestは**Greenfield**。既存Architecture/DB/API/Ranking/投資ロジックとの互換維持を目的としない。本Sectionが唯一の最上位Investment Objective。Prompt/UI/Score/Backtest/既存Codeは再定義不可。変更はユーザー明示指示後、本Sectionと`DECISIONS.md`を先に更新する。

## Mission

> **Point-in-Time情報のみから将来Total Return確率分布を推定し、Quality/Growth/Valuation、推定不確実性、Permanent Loss、Tail Risk、Liquidity、Cost、Tax where relevant、資産間Dependencyを統合する。許容不能な直接強制可能RiskはStructural Hard Constraintsとして先に除外し、推定Risk/Hybrid Riskは承認済みRobust chance/quantile semanticsで制約する。そのFeasible Portfolio集合内で、推定誤差・Model Risk・Regime変化にRobustな長期複利成長を最大化するPortfolio/Actionを提示する。**

Canonical economic objective（外部入出金がない場合）:
`Annualized Log-Wealth Growth(P,w) = (1/T) E_P[log(W_T(w)/W_0)]`

Canonical robust objectiveは§9に従い、plausible uncertainty set `U_objective` に対するworst-plausible long-term wealth utilityを最大化する。`T` = approved Investment Horizon。`W`のBase currency / nominal-real / pre-after-tax semanticsはapproved Mandateで固定する。外貨建AssetはLocal-asset returnとFX return/dependencyを統合し、最終`W_T`は必ずapproved Base Currency建てで評価する。Cost/TaxがMandate上Relevantならwealth pathへ**一度だけ**反映する。

外部拠出・引出しがあるMandateでは、承認済みcash flow scheduleをPortfolio選択から独立した外生条件として全代替案へ同一に適用し、cash-flow-aware terminal log-wealth utilityを比較する。この場合の`log(W_T/W_0)/T`を投資CAGRと呼ばない。Strategy performanceは原則Time-Weighted Return、投資家の実現結果は必要に応じMoney-Weighted Return/XIRR等で別表示し、入出金による資産増減と運用成績を混同しない。

**Lexicographic Objective**
1. Approved Structural Hard / Implementation Constraints違反Portfolioを除外する。
2. Model-Estimated / Hybrid Risk Constraintsを§8のapproved robust chance/quantile / stress semanticsで判定し、違反Portfolioを除外する。
3. Feasible集合内で§9の**Canonical robust long-term wealth utility**を最大化する。外部入出金なしではRobust Expected Annualized Log-Wealth Growth、ありではcash-flow-aware utilityを用いる。
4. Robust Utility差がResidual Decision Uncertainty Margin内で識別不能なら、Permanent-loss risk → Stress Drawdown/CVaR → Model uncertainty → Concentration → Liquidity → Cost/Turnover/Complexityの順で保守的なPortfolioをTie-breakする。

Rules:
- **Risk Limitは上限でありTargetではない。** Feasibility通過後は追加の「念のための安全化」でGrowth Objectiveを置換しない。
- Risk/Returnを単一Scoreへ雑に圧縮しない。
- Expected Return小差よりEstimation Error/Tail/Robustnessを重視するが、同一Uncertaintyの重複ペナルティで期待成長を不必要に破壊しない。
- Eligible Benchmarkを正式Comparatorとして常時評価する。Approved investable Passive Market Implementation / Cash / Risk-free proxyを正式な配分候補とし、`NO_TRADE`を正式な意思決定上の代替案として許容する。
- Ranking 1位でもPortfolio Objectiveを悪化させれば買わない。
- Backtest改善目的でObjective/Risk Budget/Universe/Threshold/Uncertainty treatmentを後付け変更しない。
- Capital Preservationは独立したOptimization Objectiveではなく、Structural Hard + Model-Estimated / Hybrid Risk Constraints・Evidence/Data gatesで実現する。

Top-level Objectiveとして禁止：`P(7年で10倍)`、Composite Score、Sharpe単独、Expected Return単独、Risk-Adjusted Score単独、Historical CAGR単独、Backtest最大化。補助/診断利用のみ可。

---

# 2. Mandate & Strategy Boundary

Default: **Long-only listed equities + approved investable Passive Market Implementation + Cash/Cash Equivalent + approved Risk-free proxy; no leverage.** Eligible Benchmarkは別途Comparatorとして定義する。

Default禁止：Short、Margin、Options、Futures、CFDs、Leveraged/Inverse ETF、Synthetic/Naked leverage、Illiquid private securities、未検証Intraday。

**Eligible Benchmark** = 比較対象となるindex/benchmark definition。非投資可能な指数でもよく、Portfolio Weightを直接割り当てない。

**Passive Market Implementation** = Benchmarkまたはbroad market exposureを実際に保有するためのapproved ETF/fund/replicating portfolio等。OptimizerでWeightを割り当てるのはこちらであり、fees / tracking difference / liquidity / tax / FX / look-through / tradabilityを評価する。BenchmarkとPassive Implementationを同一視しない。

CashとRisk-free proxyも同一視せず、Risk-free proxyは`currency / maturity-duration / credit assumption / reinvestment assumption`を明示する。個別株Alpha不確実性が高いことを理由に市場Risk Premiumまで0へ縮めない。

MaterialなRisk Asset追加・増額は、最良のfeasible alternativeとの差で**Portfolio-level Robust Utility**により判断する。Canonical decision ruleは§7/§9：

`ΔRobustUtility = U*(portfolio with candidate/size) - U*(best feasible alternative)`

原則 `ΔRobustUtility > Residual Decision Uncertainty Margin` のときのみMaterialな追加Riskを正当化する。Cost/Slippage/TaxがMandate上Relevantなら両側の`W_T`へ同一semanticsで組み込み、右辺へ再加算して二重控除しない。Standalone expected-return superiorityは不要で、Diversification / Tail-risk reduction等によりPortfolio-level robust utilityをMaterialに改善する候補を許容する。

`Cash / approved Risk-free proxy / approved Passive Market Implementation`を正式な配分候補として扱い、`NO_TRADE`を正式な意思決定上の代替案として扱う。Eligible BenchmarkはWeightを持たないComparatorとして常時評価する。個別銘柄の売買Actionは§11を唯一のCanonical定義とする。

Approved Mandateは最低限 `Investment horizon / Base currency / nominal vs real objective / pre-tax vs after-tax treatment / contribution-withdrawal assumption / Eligible Benchmark definition / approved Passive Market Implementation(s)` を固定する。Personalized Portfolioでは利用可能な範囲でafter-cost / after-tax / base-currency wealthを優先し、実質購買力との差を必要に応じ表示する。外部拠出・引出しがある場合は§1のcash-flow-aware semanticsを適用する。

Defaultは**Equity Sleeve**。Global Total Portfolio最適性を意味しない。

## Multi-Asset Expansion Path

Fixed Income / Inflation-linked / Commodities / Gold / Alternatives / FX hedging等へ拡張する場合、別Mandateとして以下を承認・検証する：
- Eligible Assets / Benchmark / Base currency / nominal-real / Tax
- Return & Risk Model / Stress dependency
- Liquidity / Cost / Capacity
- PIT / Corporate-action / Index-history integrity
- Locked OOS / Shadow
- Numerical Risk Budget
- Independent validation

承認前に「全資産でGlobal Optimal」と表現しない。

---

# 3. Roles, Effort & Review Gates

**Astra — Architect / Investment Advisor**  
Owns: Objective、Mandate、Risk Budget design、Forecast architecture、Ranking、Portfolio/Sizing、Trading semantics、Data/Valuation/Confidence、Backtest/Model governance、Major architecture、Terra spec、Final design approval。  
Effort: initial/major investment design=`high`; stable design=`medium`; Objective/Numerical Risk Budget/Production/Critical issue=`xhigh`; `max`は例外。

**Terra — Implementation Engineer**  
Owns: Backend/Frontend/DB/API/Batch/Data pipeline/Tests/Bugfix/Refactor/approved design implementation。  
Effort: default=`medium`; multi-module/DB/portfolio/data-integrity=`high`; critical incident=`xhigh`。Investment semantics変更不可。必要なら`DESIGN CHANGE REQUIRED`。原則Subagent追加禁止。

**GPT-5.6 Sol — Independent Reviewer / Validator**  
Reviews: Investment logic、Calibration、Portfolio risk、Data integrity、OOS/Backtest、Implementation、Failure modes、Optimizer stability、Limitations。  
Effort: default=`medium`; important=`high`; critical=`xhigh`。Astra設計を正しいと仮定せず、**改善案を考える前に反証を試みる（Do not optimize Astra's design before falsification）**。原則Subagent追加禁止。

`ASTRA REVIEW REQUIRED`: Objective、Mandate、Risk Budget、Forecast/Investment semantics、Portfolio/Sizing、Buy/Sell semantics、Backtest methodology、Material architecture。

`SOL INDEPENDENT REVIEW REQUIRED`: 上記のうち実運用へ重大影響、Data Integrity、Locked OOS、Major Model Validation、Material Overlay、P0/P1 regression、Critical limitation。

MaterialなObjective / Forecast architecture / Numerical Risk Budget semantics / Robust Optimizer / Ranking / Trading semantics / Backtest methodology変更は、原則として **Design → Required Pre-Implementation Review → Decision Freeze → Implementation → Tests → Post-Implementation Validation** の順とする。実装後Reviewだけで設計妥当性を初確認しない。Decision Freeze後にMaterial semantics変更が必要ならFreezeを解除し、Decision/Reviewをやり直す。

重大不合格=`MODEL VALIDATION FAILED` → Production不可。

MaterialなIndependent Reviewは可能な範囲で**Blind First-Pass**：SolはAstraの結論・Narrativeを見る前にRaw evidence / objective / inputs / formulas / numerical outputsから独立判定し、その後Astra案との差分をReviewする。重大risk/return計算は可能なら別実装で再計算する。

---

# 4. Autonomous Workflow & Delegation

`Investigate → Evidence → Compare → Decide → Pre-Implementation Review where required → Freeze Decision → Document → Implement → Test → Post-Implementation Review/Validation → Fix → Handoff → Next Priority`

根拠十分な可逆判断は自律実行。質問は他手段で解消不能な場合のみ。必須Inputが欠落し、信頼できる方法で取得・推定できない場合は推測で埋めず、該当判定を`NOT VERIFIED`として必要最小限だけ確認する。`USER_CONFIRMATION_REQUIRED`は承認が必要な操作のGateであり、必須情報欠落時の確認まで禁止するものではない。

Default topology: `One Architect → One Active Implementer → Reviewer only when justified`

Rules:
- Single active subagent / depth=1
- Recursive delegation / competitive broadcast禁止
- Repository/File/Contextの理由なき重複調査禁止
- 親の並行再実装禁止
- Review-Fix原則1往復
- Parallelは独立TaskかつContext重複小のみ

DelegationにObjective / Scope / Acceptance Criteria / Required Files / Do NOT Change / Expected Outputを明示。

`USER_CONFIRMATION_REQUIRED`:
- 実注文
- 実運用 / Personalized Portfolio用Numerical Risk Budgetの**Production有効化または変更確定**
- 本番Deployment
- 外部課金
- 本番データ破壊 / 不可逆操作 / Git history rewrite
- Secret/Credential・重大権限変更
- ユーザー明示要件と矛盾する変更

---

# 5. Universe, PIT Data, Security Master & Evidence Firewall

Universeに明示：Country、Exchange、Security type、Market cap、Liquidity、Trading history、Fundamental coverage、Corporate actions、Delisting coverage、Currency、Data availability。変更はMaterial decisionとして記録。

## Security Master

長期履歴・Corporate Action・Ticker変更をTicker文字列だけで管理しない。Material universeでは安定した`internal_security_id / issuer_id`を持ち、可能な範囲で `ticker history / exchange / share class / ADR-underlying relation / merger-spin-off history / delisting mapping / currency / corporate-action lineage`を保持する。識別不能がBacktest/ProductionへMaterialなら`DATA_LIMITATION`。

## PIT / Tradability Rule

**PIT rule:** 判断/Backtestは、その時点で実際に利用可能かつ取引判断へ利用可能だった情報のみ。Restated Dataを過去へ遡及適用しない。

重要Data metadata:
`as_of_date / available_at / retrieved_at(where relevant) / source / staleness / quality_confidence / lineage`

Decision/Backtestでは別途 `decision_timestamp / tradable_at` を保存する。原則：

`decision_timestamp >= available_at + verified ingestion/processing latency`

かつ、取引価格は`tradable_at`以降に現実に約定可能なprice/timestampを用いる。決算・filing・index change等を公開前価格または公開直前closeへ遡及適用しない。Timestamp semanticsやlatencyを検証できないMaterial sourceはPIT-safeと推測しない。

Missing≠0。`Missing / Unknown / Not Applicable / Stale / Conflicting / Unavailable Point-in-Time`を区別。

## Free-First / Authoritative-Source-First

Priority:
1. Regulator / Government / Central Bank / Treasury / Official Exchange / Issuer filing
2. Issuer IR / official disclosure
3. Reputable free market-data source / aggregator
4. Derived data computed from verified inputs

Defaults:
- US filings/fundamentals: SEC EDGAR / XBRL
- Japan filings: EDINET
- Macro/rates/inflation/credit vintages: FRED / ALFRED where applicable
- Yahoo Finance / yfinance: supporting market-data source; not sole accounting/PIT fundamental SoT

ProviderごとにLicense / Rate limit / Timestamp semantics / Coverage / Corporate-action handling / PIT suitabilityを記録。無料SourceでMaterial品質不足なら推測せず`DATA_LIMITATION`。Backtestを歪めるなら`NOT RELIABLY BACKTESTABLE`、実運用判断を歪めるなら`NOT PRODUCTION READY`。

有料Data/APIは無料代替との差を文書化し、外部課金前にユーザー明示承認。

**FACT:** Source / Available-at / Evidence / Data quality / Confidence必須。  
**INFERENCE:** Supporting FACTs / Reasoning basis / Confidence / Material alternative / Review trigger where appropriate。

> **Unsupported LLM inferenceをForecast / Ranking / Portfolio Weight / BUY-SELLへ直接反映しない。**

---

# 6. Investment Inputs

重複/相関/Double Countingを除いて必要に応じ評価：

- Quality: Revenue/EPS/FCF growth, Margins, ROIC/ROE, **Incremental ROIC**, Reinvestment rate/runway, Unit economics, Operating leverage, Earnings quality
- Moat: Network effects, Switching costs, Brand, Scale/Cost, IP, Data, Distribution, Ecosystem
- Market: TAM/SAM/SOM, Industry growth, Market share/expansion, Competition
- Management: Capital allocation, Insider ownership, Track record, M&A, Buybacks, SBC/Dilution, Guidance accuracy, Governance
- Financial Risk: Debt, Interest coverage, Liquidity, Cash burn, Refinancing/Bankruptcy, Maturity, Covenants, Off-BS obligations
- Valuation: P/E, PEG, EV/EBITDA, EV/Sales, P/FCF, FCF Yield, Reverse DCF, Historical/Peer/Scenario valuation
- Macro/Regime: Rates, Inflation, FX, Commodities, Credit, Cycle, Liquidity, Regime sensitivity

長期Compounderでは過去ROICだけでなく、追加資本が将来どれだけのReturnを生むかを重視する。`Sustainable growth ≈ Reinvestment rate × Incremental ROIC`はdiagnostic/economic consistency checkとして利用可能だが、会計定義・capital intensity・M&A・SBC等を無視した機械的予測へしない。

Return/Risk/Confidence/Quality/Valuationを単一Scoreへ無理に圧縮しない。

---

# 7. Forecasting, Uncertainty, Decision Hurdle & Calibration

単一点予測を唯一Inputにしない。最低Bear/Base/Bull、重大対象はDistribution。

Targets: Revenue CAGR、Margin、FCF/EPS、Dilution、Capital structure、Valuation multiple、Dividend/Buyback、Expected price、Total Return/CAGR。

重大Forecastでは可能な範囲で比較：
Historical base rate / Simple benchmark / Economic prior / Market-implied expectation / Fundamental scenarios / Model disagreement / Historical error / Parameter-Model-Regime uncertainty。

Expected Returnは原則**二層構造**で構築し、片方だけを唯一の真実としない。

**A. Economic Return Bridge**: `Business growth → Per-share fundamental growth → Shareholder yield → Valuation change → FX where relevant → Total Shareholder Return`。Revenue/earnings/FCF growthだけを株価成長へ直結させず、Margin / Incremental ROIC / reinvestment / capital intensity / SBC-dilution / buyback / dividend / capital structure / valuation multiple / currency translationを整合的に橋渡しする。外貨建AssetはLocal return + FX return + dependencyとしてBase-currency wealthへ統合する。

**B. Statistical / Economic Prior**: 原則 `Risk-free → Broad-market risk premium → Factor/Sector component → Company-specific alpha` と階層分解する。Shrinkageは特にCompany-specific alphaをdefensible prior / market/base-rateへ縮小し、個別Alpha不確実性を理由にBroad-market expected return全体をCashへ機械的に縮めない。

最終Forecast distributionはA/Bのevidence・base rate・market-implied expectation・historical/OOS error・model disagreementを用いて統合し、両者がMaterialに不一致なら差を隠さず`MODEL DISAGREEMENT`相当のuncertainty sourceとしてLedgerへ記録する。

### Economic Dependency / Scenario Coherence

Material forecast variableを相互独立と仮定しない。少なくともMaterialな場合は `Growth↔Margin / Growth↔Reinvestment-Incremental ROIC / Rates↔Valuation / Credit↔Refinancing-Default / Macro↔Earnings / FX↔Local asset return / Volatility↔Correlation-Liquidity` のjoint dependencyまたはregime/state conditional relationを表現する。経済的に不整合なscenarioが結果をMaterialに歪めるならModelを修正し、単純なhistorical correlationだけで十分と仮定しない。

Outputs where feasible:
Expected/Median CAGR、Downside percentile、P(loss)、Permanent-loss range/probability where calibrated、Upside probability、CVaR/ES、Prediction/Credible interval。

ConfidenceをData / Evidence / Model / Forecast / Actionに分離し、Forecast distribution / `U_objective` / `U_risk` / Review requirementへ反映する。Confidence低下を同一根拠でさらに独立Sizing penaltyへ重ねない。

## Canonical Decision Hurdle

MaterialなRisk Asset追加・増額、Ranking、Trade gateはExpected Return差ではなく**Portfolio-level robust utility差**へ統一する：

`ΔRobustUtility = U*(candidate/size allowed) - U*(best feasible alternative)`

原則：
`ΔRobustUtility > Residual Decision Uncertainty Margin`

`Residual Decision Uncertainty Margin`は`ΔRobustUtility`と同じCanonical utility単位・正規化で定義し、optimizer/value-difference estimation error・finite-sample uncertainty等のうち**`U_objective` / `U_risk` / Costへ未反映の残差だけ**からCalibrationする。独立したResidual sourceがなければ便宜的な正のMarginを足さない。Cost/Slippage/TaxがRelevantなら`U*`のwealth pathへ両側同一条件で一度だけ反映する。`Opportunity Cost`はbest feasible alternativeとの差に内包されるため再加算しない。差がMargin内なら`INSUFFICIENT EDGE EVIDENCE`とし、大きなWeight差・高Conviction BUYへ変換しない。

Company-specific alphaはforecast diagnosticとして `Robust Incremental Alpha` / Alpha Estimation Errorを表示してよいが、Portfolio Actionの最終Gateを単体Alpha/Expected Returnへ置換しない。

## Uncertainty Accounting / Ledger

Material decisionでは主要Uncertainty sourceごとに、少なくとも以下の**役割を一意に記録**する：

`source → predictive distribution / shrinkage / U_objective / U_risk / S_stress / decision margin / optional sizing adjustment`

Rules:
- `U_objective`: §9のObjectiveでworst-plausible growthを評価するplausible uncertainty。
- `U_risk`: §8のrobust chance/quantile risk constraintで使用するuncertainty。`U_objective`と同じ情報を共有してよいが用途・変換・重複影響を記録する。
- `S_stress`: plausible probability setへ無理に入れないHistorical/Hypothetical/OOD stress scenario集合。Objectiveの`min P`へ自動投入しない。
- Explicit safety bufferを使用する場合、それが`U_risk`を近似する**代替表現**か独立根拠かを明示する。同じuncertaintyをrobust chance constraintとbufferで二重反映しない。
- Fractional/confidence sizingは、Log utility / shrinkage / `U_objective` / `U_risk` / decision marginと独立したCalibration根拠がある場合のみMaterialに追加する。

同じOOS error / model disagreement / regime uncertainty等を複数layerでMaterialに反映する場合は意図・依存関係・総影響を検証する。無自覚なdouble counting、または保守化を重ねたCash偏重・Growth破壊 → `UNSTABLE MODEL` / `AMBIGUITY-DOMINATED SOLUTION` / Review。

Calibration where relevant:
Calibration curve / Interval coverage / CRPS / Log-Brier Score / Rank IC / Horizon-Sector-Regime error / Tail calibration / Over-Underconfidence。

小さな合理的入力変化でForecast/Ranking/Weight/Actionが大幅変化 → `UNSTABLE MODEL`。

### Multi-Horizon Validation

長期Horizon（例: 7年）はoverlapping outcomeだけで過信しない。可能な範囲で`1Y / 3Y / 5Y / 7Y`のForecast consistency、realized outcome、sample dependenceを確認し、7年単独でCalibration良好と断定しない。Independentな長期Outcome不足を統計補間だけで`PASS`に変換しない。

---

# 8. Risk Framework & Numerical Risk Budget

Risk taxonomy:
- Market: Volatility/Beta/Factor/Drawdown/Correlation
- Tail: Downside deviation/CVaR-ES/Gap/Jump/Fat-tail/Correlation spike
- Permanent Loss: Bankruptcy/Refinancing/Dilution/Fraud/Accounting/Governance/Regulatory destruction/Structural decline
- Liquidity/Capacity: ADV/Spread/Market impact/Participation rate/Days-to-enter-exit/Forced-sale
- Concentration: Security/Sector/Industry/Country/Currency/Factor/Customer/Supplier/Technology/Funding
- Model: Data/Parameter/Model/Forecast uncertainty/Disagreement/OOD/Regime shift

### Permanent Loss / Survival Model

Permanent LossはvolatilityおよびLarge Temporary Drawdownと分離して評価する。重大対象では少なくとも `Default/Liquidation` / `Distressed Dilution or Rescue Financing` / `Fundamental Impairment` / `Terminal Real Loss > approved threshold` / `No Recovery within approved horizon` を必要に応じ分解し、Bankruptcy/Refinancing/Accounting/Governance/Fraud/Regulatory/Structural decline等のEvidenceから推定する。定義・threshold・horizonをversion管理し、Return distributionとPortfolio constraint/sizingへ統合する。

Componentは相互排他的と数学的に確認できない限り単純加算禁止。依存するeventはcompeting-risk / state-transition / joint scenario等で扱い、double countingを検査する。

**False Precision禁止:** Production sizingにMaterialなPermanent-loss componentがCalibration未確立なら、`1.7%`等の精密な単一点確率を事実のように扱わない。Probability interval / scenario range / evidence grade / conservative gateを用い、十分なoutcome definition・base rate・calibrationが成立した範囲のみ確率値をProduction semanticsへ昇格する。

各MetricにDefinition / Horizon / Confidence level / Estimation method / Data window / Limit / Warning threshold。

## Constraint Classes

**A. Structural Hard Constraints — directly enforceable / fail-closed**  
Mandate eligibility / Long-only / Leverage / deterministic single-name-sector-country caps / Trading permissions / observed participation ceiling / required Data-Evidence gating等、観測可能InputとCodeで直接判定できる制約。違反はOptimization前に除外しProductionではFail Closed。

**B. Model-Estimated Risk Constraints — probabilistic, not guaranteed**  
Modeled Drawdown / CVaR-ES / Severe-loss probability / Permanent-loss probability or calibrated range / Recovery-duration risk / estimated factor-dependency等、将来分布/model推定に依存する制約。将来損失の上限保証ではなく`MODEL-ESTIMATED RISK`として表示する。

**C. Hybrid Constraints — observed mechanics + estimated component**  
Liquidity/Capacity / market impact / days-to-liquidate / factor-cluster exposure等、観測値と推定値の双方で決まる制約。Observed hard componentはfail-closed、Estimated componentは下記robust semanticsで判定する。

**D. Stress Scenario Constraints / Diagnostics**  
Historical crisis / severe recession / multiple compression / credit-liquidity shock / correlation spike / Hypothetical OOD等の`S_stress`。Plausible uncertainty setへ自動混入させず、approved scenario definition / severity / limit / diagnostic-vs-binding semanticsをversion管理する。

## Canonical Production Risk Semantics

Distributionを持つModel-Estimated / Hybrid Riskは、可能な範囲でpoint estimate + arbitrary bufferではなく、approved `U_risk`に対する**robust chance/quantile constraint**を標準とする：

`sup_{P ∈ U_risk} P_P(RiskMetric > Limit) <= approved ε`

または

`sup_{P ∈ U_risk} Q_{1-α}^{P}(RiskMetric) <= Limit`

Drawdown / CVaR / Permanent-loss / Recovery duration等の`ε / α / horizon / U_risk version`はProduction前に定義・Calibrationし、推測固定しない。

Explicit safety buffer形式 `Estimated Risk + Buffer <= Limit` を使用する場合は、`U_risk` robust constraintの近似/代替表現としてCalibration根拠を持つか、独立uncertainty sourceであることをLedgerに示す。同一error sourceを`U_risk`とBufferで二重計上しない。推定不能/unstableならPASS扱いせず`NOT VERIFIED` / `UNSTABLE MODEL` / `REVIEW_REQUIRED`。

Stress binding ruleを承認した場合は、例として `StressMetric(w,s) <= approved stress limit_s` を`S_stress`上で検査する。Stressは確率保証ではないことを表示する。

### Portfolio Joint Risk Violation Budget

複数のrisk constraintを個別にPASSしてもPortfolio全体のMaterial breach確率が十分低いとは限らない。Productionでは可能な範囲で：

`sup_{P ∈ U_risk} P_P(any approved material risk constraint violated) <= approved ε_portfolio`

または同等のjoint exceedance semanticsを定義し、Drawdown / CVaR / Permanent-loss / Recovery / Liquidity等の依存をjoint simulation / state-regime model / conservative boundで評価する。

Individual `ε_i`は全体Risk Budgetと整合させ、強く依存するRiskを独立として単純加算しない。Joint distributionが信頼できない場合は保守的boundとlimitationを表示し、便宜的な一律`5%`等で`PORTFOLIO JOINT RISK VERIFIED`と扱わない。

Joint breach probabilityは、同じevaluation horizon / event clockへ意味的に写像できるRiskだけを同一joint eventへ含める。例として5-day liquidity、1-year CVaR、7-year drawdown/recovery等を定義なしに一つの`ε_portfolio`へ混ぜない。Horizonが異なる場合はhorizon別joint budgetまたは明示的なhierarchical aggregationを定義し、変換不能なRiskは別Constraintとして保持する。

## Risk Capacity / Risk Tolerance / Life-Cycle Adaptation

Personalized Risk Budgetは年齢だけで決めない。AgeはInvestment horizonや人的資本・将来拠出余力の補助情報に留め、少なくとも以下を分離評価する：

- **Risk Capacity**: Investment horizon / near-term liquidity need / emergency reserve outside portfolio / expected contributions-withdrawals / income stability / liabilities or known cash needs / loss absorption capacity
- **Risk Tolerance**: Temporary drawdown / time-under-water / concentration / action-churnへの心理的・行動的耐性
- **Mandate Ceiling**: 承認済みStructural / Model-Estimated / Hybrid limits

Personalized Risk BudgetはRisk Capacity / Risk Tolerance / Mandate Ceilingを**単一Scoreへ圧縮しない**。同じ単位・同じ意味を持つRisk metric `k`についてのみ、原則 `Limit_k <= min(Capacity-derived ceiling_k, Tolerance-derived ceiling_k, Mandate ceiling_k)` とし、異なる次元を数値の`min()`で比較しない。定量化不能な要素は独立Gate・warning・review conditionとして保持する。年齢・「若いから」だけを根拠にGrowth presetを自動選択・Production有効化しない。

長期・高Capacity/Toleranceの投資家では、Growthを得るため**Temporary Drawdown / volatility / recovery-duration / moderate concentration**のBudgetを広げ得る。一方、**Permanent Loss / Fraud-Accounting-Governance / Data Integrity / Evidence quality / Liquidity safety / Model uncertainty / PIT / OOS / Shadow / Fail-Closed**基準は、Growth profileを理由に機械的に緩和しない。

Risk Limitは**使い切るTargetではなく上限**。Optimizerは追加RiskがRobust Expected Log-Wealth Growthを改善しない限り上限までRiskを取らない。

Risk Capacity / Tolerance assessmentはVersion / as-of / inputs / limiting factor / rationaleを保存し、Personalized ProductionではRisk Budget activation前にユーザー明示承認を必須とする。

## Provisional Risk Budget — UI Editable

初期状態ではResearch/Simulation用の**仮Budget**を自動作成し、UIから編集可能とする。値は`PROVISIONAL / NOT APPROVED`であり、ユーザー固有最適値を意味しない。

Suggested default research profile: `BALANCED_RESEARCH_V1`

- Investment Horizon: `7 years`
- Max single-name equity: `10%`
- Approved Passive Market Implementation: `0–100%` eligible allocation; Eligible BenchmarkはWeightなしComparator
- Max sector/industry: `30%` Research reference; Production semantics must state absolute vs benchmark-relative。Passive Market Implementationがabsolute cap違反ならFeasibleとは扱わない
- Max factor-correlated cluster: `35%` Hybrid / robust model-estimated semantics required for Production
- Max modeled drawdown reference limit: `25%`; Production robust exceedance-probability/quantile threshold to be calibrated
- Max stress drawdown reference limit: `35%`; Production `S_stress` scenario/limit semantics required
- Max acceptable recovery duration: `36 months`; Production robust exceedance-probability threshold to be calibrated
- Portfolio CVaR: model-defined limit to be calibrated before Production
- Severe-loss probability: model-defined threshold to be calibrated before Production
- Permanent-loss exposure: model-defined calibrated probability/range semantics required before Production
- Portfolio joint material-risk violation probability: model-defined `ε_portfolio` / joint semantics to be calibrated before Production
- Min liquidity: security-specific rule required
- Max days-to-liquidate: `5 trading days` under normal assumed participation; stress estimate separately evaluated
- Max participation rate: `10% of ADV` unless validated otherwise
- Max turnover / implementation cost: strategy-calibrated; not assumed zero
- Cash: `0–100%`
- Risk-free proxy: `0–100%` if approved; distinct from Cash
- Leverage: `0%`
- Min Data/Evidence integrity confidence: calibrated before Production; Model/Forecast confidenceは原則`U_objective`/`U_risk`へ反映し、別Gate化は独立根拠がある場合のみ

Optional research profile for long-horizon/high-capacity users: `GROWTH_RESEARCH_V1`

- Intended use: long-horizon investor with sufficient Risk Capacity and Risk Tolerance; **not selected from age alone**
- Investment Horizon: `7–10+ years`
- Max single-name equity: `12.5%` Research cap; `15%` absolute research ceiling only when separately justified/approved
- Approved Passive Market Implementation: `0–100%`
- Max sector/industry: `35%` Research reference; same benchmark-relative consistency rule
- Max factor-correlated cluster: `40%` Hybrid / robust model-estimated semantics required for Production
- Max modeled drawdown reference limit: `30%`; Production robust chance/quantile threshold required
- Max stress drawdown reference limit: `45%`; Production `S_stress` semantics required
- Max acceptable recovery duration: `48 months`; Production robust exceedance-probability threshold required
- Portfolio CVaR / Severe-loss / Permanent-loss / Joint material-risk violation budget: calibrated before Production; **Growthを理由に自動緩和しない**
- Min liquidity / Data-Evidence-Model confidence / PIT-OOS-Shadow / Fraud-Accounting-Governance gates: **Balancedと同等以上の厳格さを維持**
- Max days-to-liquidate: `5 trading days` normal reference unless separately validated
- Max participation rate: `10% of ADV` unless validated otherwise
- Cash: `0–100%`
- Risk-free proxy: `0–100%` if approved
- Leverage: `0%`

`GROWTH_RESEARCH_V1`はTemporary Drawdown / Recovery / moderate concentrationの許容幅を広げるResearch presetであり、Permanent Loss toleranceやData/Model governanceを弱めるpresetではない。

ETF/fund等のinvestable implementationは可能な範囲で**look-through exposure**を用い、direct holdingとの重複をSecurity/Sector/Country/Factor concentrationへ反映する。Eligible BenchmarkはComparatorとして常時評価するが、非投資可能なindexへWeightを割り当てない。Approved Passive Market Implementationがabsolute cap等を満たさない場合は、そのImplementationをinfeasibleと扱う。Mandateが特定Implementationのfeasibilityを明示要求している場合に限り、その不成立を`RISK BUDGET INCONSISTENT`とする。Look-through不能でMaterialなら`DATA_LIMITATION`または保守的制約を適用する。

上記の未数値項目は実装時に適当な固定値を推測しない。Calibration/validationで候補を作成しUIに提示する。

### Risk Budget Consistency / Feasibility Gate

Risk Budget保存・Production activation前に、Mandate/Horizon/各Limit間の内部整合性と**少なくとも1つの実行可能Portfolioが存在すること**を検査する。Eligible BenchmarkはComparatorとして評価可能であることを確認し、その非投資可能性をPortfolio infeasibilityと混同しない。Approved Passive Market Implementationは通常Assetと同様に全Constraintを満たす場合のみFeasible。Mandateが特定Implementationのfeasibilityを要求しない限り、それ単体のinfeasibilityだけでBudget全体を`RISK BUDGET INCONSISTENT`にしない。相互に矛盾・実質的に達成不能・solver上feasible setなしの場合は`RISK BUDGET INCONSISTENT`。ResearchではImpact/Sensitivityを提示して修正候補を作れるが、矛盾したBudgetを`APPROVED`または`PRODUCTION READY`にしない。

### UI Rules

UIは最低限以下を提供：
- Current Budget Profile / Version / Status
- 全Limitの表示・編集 + `STRUCTURAL HARD` / `MODEL-ESTIMATED RISK` / `HYBRID` / `STRESS`分類
- Chance/quantile constraintのLimit / Horizon / ε or α / `U_risk` version、または明示的なequivalent buffer semantics（重複不可）
- `S_stress` version / scenario / binding-vs-diagnostic semantics
- Portfolio joint material-risk violation budget / dependency treatment
- Defensive / Balanced / Growthなどの**Research preset**
- Personalized時はRisk Capacity / Risk Toleranceを別表示し、limiting factor・入力根拠・推奨presetを提示。Age aloneでpresetを決めない
- 変更前後差分と想定Impact + 制約強化によるRobust Growthの推定Opportunity Cost
- Validation status
- `SAVE AS PROVISIONAL`
- `REQUEST / CONFIRM PRODUCTION ACTIVATION`

Research/SimulationではUI変更を即時反映してよい。  
**実運用 / Personalized Portfolioでは、変更BudgetをProductionへ有効化する直前にユーザー明示確認が必須。**

Material変更ではRisk Budget Sensitivityを表示：主要Limit変更時のRobust utility / Expected portfolio return（外部入出金なしではCAGR、ありではTWRを原則使用） / Stress Drawdown / CVaR / Permanent-loss / Joint breach probability / Cash / Concentrationへの影響。利用可能ならbinding constraintとshadow priceも表示。

過度な保守化によるunder-investmentも診断対象とし、`DEFENSIVE OPPORTUNITY COST`として、現Budgetと合理的な隣接BudgetのRobust Growth差・追加Risk・binding constraintを表示する。これはRisk Limitを使い切る指示ではない。

承認時は`DECISIONS.md`へ：
`risk_budget_version / effective_as_of / investment_horizon / risk_capacity_assessment / risk_tolerance_assessment / limiting_factor / limits+warnings / U_risk+chance-quantile semantics / S_stress version+semantics / rationale / approved_by / validation_status`
を保存。

未承認=`RISK BUDGET NOT APPROVED`。Research/Simulationは可だが`Personalized Optimal / PRODUCTION READY`と表現不可。

## Path-wise Drawdown

可能な範囲でPath-wise wealth simulation / scenario pathにより：
- Drawdown distribution
- Robust `P(Drawdown > Limit)` / drawdown quantile under `U_risk`
- Stress Drawdown under `S_stress`
- Time-under-water / Recovery duration
- Robust `P(Recovery duration > Limit)`

を評価。Path model自体の不確実性・Regime dependenceを明示し、Production constraintはapproved `U_risk` chance/quantile semanticsおよび`S_stress` ruleと整合させる。

---

# 9. Robust Portfolio Construction

Required inputs:
Return distribution / dependency model / Concentration / CVaR / Permanent loss / Liquidity-Capacity / Cost / Turnover / Tax where relevant / Confidence / Estimation uncertainty / Eligible Benchmark / approved Passive Market Implementation / Cash / Risk-free proxy / approved `U_objective` / approved `U_risk` / approved `S_stress`。

Objective: **§8のRisk/Implementation feasibilityを満たす集合内で、§1のCanonical robust long-term wealth utilityを最大化する。**

### Canonical Robust Optimizer

外部入出金がないProductionの標準形：

`w* = argmax_{w ∈ F} min_{P ∈ U_objective} (1/T) E_P[log(W_T(w)/W_0)]`

外部入出金がある場合は、承認済みcash flow scheduleを全代替案へ同一に適用した`W_T(w; cash_flows)`のrobust terminal log-wealth utilityを最大化する。上式の`W_T/W_0`をそのまま投資CAGRまたはStrategy growthとして解釈しない。

- `F` = approved Structural Hard Constraintsを満たし、Model-Estimated / Hybrid Risk Limitsを§8のapproved robust chance/quantile semantics、必要な`S_stress` binding rule込みで満たすfeasible set
- `U_objective` = **plausible** uncertainty set。Canonical componentsは原則 `predictive/forecast residual uncertainty + parameter/model disagreement + plausible regime mixture + covariance/dependency uncertainty`。Historical/Hypothetical extreme/OOD stressを無条件に投入しない
- `S_stress` = Historical crisis / severe hypothetical / OOD等のstress set。Objectiveの`min P`とは分離し、§8 risk constraint / sensitivity / diagnosticsへ使用
- CatastrophicなMandate/Data/Evidence/Survival failureで直接拒否可能なものは`U_objective`へ曖昧に押し込まずStructural/Evidence fail-closed gateへ置く
- `U_objective`のradius/weightsはForecast OOS error distribution / coverage / calibration / disagreement / regime-dependency evidenceから設定し、Portfolio Backtest CAGR/Sharpe/utilityを最大化するよう調整してはならない
- `U_objective` / `U_risk` / `S_stress` / shrinkage / decision margin / sizing間のUncertainty重複は§7 Ledgerで検査する
- Cost/Slippage/TaxがRelevantなら`W_T(w)`のwealth transitionへ**一度だけ**組み込み、Objective外のpenaltyとして重ねない
- `U_objective`の構成、scenario weight、solver tolerance、failure behaviorはversion管理し、実装者判断で変更しない
- 数値不安定・solver failure・constraint tolerance超過時は**Fail Closed**し、`UNSTABLE PORTFOLIO`または`NOT VERIFIED`

### Wealth / Portfolio Accounting Invariants

- Long-only MandateではOptimizer対象範囲の最終Weightは原則 `Σw = 1`（approved numerical tolerance内）、各Risk Asset weight `>= 0`、Cash/Risk-freeを含む対象内資金残高は許容された借入を除き負にしない。
- Share/lot roundingや部分約定後のactual holdingsでWeight/Risk/Constraintを再計算し、丸め前TargetがPASSでも丸め後が違反なら実運用ではFail Closedする。
- Strict log utilityでは`W_T <= 0`を黙ってsmall positive valueへclipしない。数値計算上wealth floorが必要ならapproved numerical approximationとしてversion管理し、floor sensitivityとruin probabilityを別途検証する。

Robust solutionでは可能な範囲で `posterior/base expected growth / robust worst-plausible growth / ambiguity-model effect / risk-constraint effect / implementation-cost effect / resulting Cash-Passive weight` を分解保存する。Cash/Passive偏重が主として広い`U_objective`・model disagreement・dependency uncertaintyにより生じる場合は`AMBIGUITY-DOMINATED SOLUTION`を表示し、「AssetのRisk/Returnが悪い」ことと「Modelが識別できない」ことを区別する。これはCashを禁止するstatusではなく、uncertainty calibration / double counting / sensitivity review triggerである。

上式はlong-horizon ObjectiveのCanonical static representation。Daily refresh / rebalance / material eventでは、承認済みTrading semantics・Cost・Hysteresisの下で**sequential / receding-horizon re-optimization approximation**として運用する。検証済みDynamic Policyを別途承認しない限り、短期signal最大化へObjectiveを置換しない。

## Default Robust Optimization Method

Default implementation:
1. Expected-return shrinkage toward defensible prior/base rate
2. Posterior/Predictive return distribution
3. Plausible regime mixture for `U_objective`
4. Dependency/covariance shrinkage + state/regime dependency
5. Parameter perturbation / resampling sensitivity
6. §8 robust risk constraints using `U_risk`
7. Separate `S_stress` tests/constraints
8. Position/concentration/capacity caps + justified fractional sizing only when independently warranted

Fractional sizingをrobust optimizer外部の「念のための追加保守化」として無条件適用しない。Log utility / shrinkage / `U_objective` / `U_risk` / decision marginですでに反映した同一uncertaintyを再度Materialに縮小する場合、§7 Ledgerで独立根拠・依存・総影響を明示する。追加fractionがOOS calibration error / utility sensitivity / model misspecification等から別途正当化できないならDefaultでは用いない。

別方式はEconomic rationaleとValidationを記録。

Raw return point estimateから極端Weightを作らない。Default禁止: Unconstrained MVO / Full Kelly / Unbounded leverage。

銘柄採用は可能な限り：
Marginal robust utility / Incremental CVaR / Permanent-loss / Diversification / Cost / Factor concentration / Liquidity burden / Capacity
で評価。

## Canonical Value Function & Ranking

`U*(A)` = candidate/asset set `A`を許容した状態で、同一Mandate / Risk Budget / Cost / Tax / uncertainty semanticsの下、§9 Optimizerにより得られる最適Robust Utility value。

Primary Rankingは単体Expected ReturnやComposite Scoreではなく、候補の存在が**feasible Portfolio全体の最適Robust Utilityをどれだけ改善するか**で評価する`Portfolio Opportunity Rank`：

新規候補：
`OpportunityValue_i = U*(candidate i allowed) - U*(candidate i excluded)`

この`OpportunityValue_i`は§2/§7のMaterial add-risk decisionと同一Canonical concept。計算量上必要な場合のみ、approved increment / marginal utility / shadow price / leave-one-in/outを近似として使い、increment依存性をSensitivity確認する。

既存保有銘柄では`excluded`が強制売却を意味し、Tax/Costにより新規投資魅力度とは異なるため分離する：
- `RetentionValue_i = U*(current holding may remain/optimize) - U*(forced exit to zero, including applicable Tax/Cost)`
- 既存銘柄への追加投資は `AddValue_i(Δw) = U*(increase allowed) - U*(no increase beyond current/approved band)`。
`RetentionValue`をFresh BUY edgeとして表示せず、New Opportunity / Add Value / Retention Valueを分離する。

Modes:
- **Generic Discovery Mode**: approved Reference Portfolio（原則approved Passive Market Implementation + Cash/Risk-free）を基準とし`DISCOVERY RANK`として表示。Eligible Benchmarkは別途Comparatorとして表示
- **Personalized Portfolio Mode**: actual current holdings / tax-cost contextを基準とし`PERSONALIZED PORTFOLIO OPPORTUNITY RANK`として表示

両Modeを混同しない。Structural Hardまたは§8 Risk Constraints違反候補は採用対象外。UIでは`Expected Return Rank` / `Fundamental Conviction Rank`等を補助表示可だがPrimary Investment Rankと混同しない。Ranking高位でもAction/WeightはTrading SemanticsとMinimum Trade Thresholdで別判定する。

## Risk Contribution Output

Material Portfolioでは最低限：
- Position weight
- Marginal Contribution to Risk
- Marginal Contribution to CVaR
- Marginal Contribution to modeled/stress drawdown where feasible
- Factor/cluster contribution including look-through where applicable
- Liquidity/capacity consumption

を表示・保存する。

Perturbation/ScenarioでWeight不安定 → `UNSTABLE PORTFOLIO` / `REVIEW_REQUIRED`。まず原因を診断し、不安定性だけを理由にCanonical解へ任意のCash増加・fractional sizing・Simpler allocationを後付けしない。MaterialなProduction変更が必要ならapproved input / `U_objective` / `U_risk` / Constraint / numerical methodの正式変更としてReviewし、§9 Optimizerを再実行する。

---

# 10. Utility Sensitivity & Decision Stability

Primary Objectiveは§9のRobust log-wealth utilityを維持するが、Material sizing/portfolio decisionでは**Utility Sensitivity Test**を行う。

Where feasible compare:
- Log utility
- CRRA `γ = 2`
- CRRA `γ = 3`
- CRRA `γ = 5`
- Approved alternative only when justified

目的はObjectiveを都合よく変更することではなく、Risk-aversion仮定に対するWeight/Action安定性を確認すること。

Weight/Actionが合理的なUtility仮定変更でMaterialに変化する場合：
`UTILITY SENSITIVE` → root-cause/sensitivity review。**Utility Sensitivity Test自体は診断であり、Primary log-wealth ObjectiveのProduction Weight/Actionを直接上書きしない。** Materialな懸念がModel misspecification等を示すなら`REVIEW_REQUIRED`とし、approved input / `U_objective` / `U_risk` / Constraint等を正式に変更して§9を再実行する。同一根拠でmargin拡大・cash増加・fractional sizingを自動重複適用しない。

ProductionでPrimary Utilityを変更する場合はMaterial Objective decisionとして扱う。

---

# 11. Trading Semantics

Actions:
`BUY / ACCUMULATE / HOLD / TRIM / SELL / AVOID / NO_TRADE / REVIEW_REQUIRED`

Action semantics:
- `BUY`: 非保有銘柄へ新規Positionを設定する。
- `ACCUMULATE`: 既存Positionを増額する。
- `HOLD`: 現在Positionを維持し、通常は追加売買しない。
- `TRIM`: Positionを一部縮小する。
- `SELL`: PositionをTarget Weight 0まで解消する。
- `AVOID`: 非保有銘柄について現時点で新規Positionを取らない。既存保有のSELL指示には使わない。
- `NO_TRADE`: 現在のPortfolio/候補について今は取引を実行しない。銘柄の恒久的否定を意味しない。
- `REVIEW_REQUIRED`: 必要Data・Model・Risk等が未検証/不安定で通常Actionを確定しない。

基準=`Forward Return Distribution + Incremental Portfolio Robust Utility`。過去価格だけを根拠にしない。

**BUY/ACCUMULATE requires**
1. Required/fresh/PIT/tradability/integrity Data + Evidence Firewall pass
2. Business/Moat/Growth/Accounting/Governance/Survival thesis
3. Valuationがforecast/wealth distributionへ整合的に反映済み。Separate Margin-of-Safety hard gateは明示承認され、同一Valuation uncertaintyを二重控除しない場合のみ
4. CVaR/Permanent/Severe/Liquidity/Capacity等がapproved §8 Risk Budget semantics内
5. Required Data/Evidence integrity gates pass。Model/Forecast confidenceは原則`U_objective`/`U_risk`で扱い、別Gateは独立根拠がある場合のみ
6. Cost/Slippage/Market Impact/Taxを一度だけ反映したうえで§7 Canonical Decision Hurdle pass
7. §13のHysteresis / Minimum Trade Threshold pass

Standalone expected-return superiorityは必須ではない。候補がDiversification / Tail-risk reduction等によりPortfolio-level robust utilityをMaterialに改善する場合はBUY候補になり得る。

Re-evaluate on daily batch / scheduled rebalance / material events。

`Daily Refresh ≠ Daily Trading`。Entry/ExitにHysteresis + Minimum Trade Threshold。Thresholdは同じCost/uncertaintyを二重控除しないよう§7/§13と一貫させる。

HOLD/TRIM/SELLはThesis、Forward Return、Portfolio marginal utility、Risk Budget、Cost/Tax、Confidenceで決定。株価下落/含み損/上昇/一定利益/目標価格到達だけで機械的SELLしない。

Recommendation minimum:
Security/internal ID/Ticker / Action / Mode(Generic-Personalized) / Timing / Current+Target Weight / As-of+decision/tradable timestamp / Expected+Median CAGR / Robust utility impact / Economic Return Bridge summary / Downside-CVaR-Permanent-loss / Stress+Joint Risk impact / Confidence dimensions / Edge Evidence status / Ambiguity status where material / Reason / Entry+Exit Trigger / Max acceptable entry price where reliable / Next Review / Expected Cost / Portfolio & Risk-Budget impact。

---

# 12. Astra Overlay Governance

Canonical flow：
`BASE MODEL OUTPUT → ASTRA EVIDENCE/REVIEW OVERLAY → CANONICAL RE-RUN IF MATERIAL → FINAL OUTPUT`

OverlayはEvidence、Data-quality flag、Model disagreement、review finding、approved scenario/input変更案を明示するReview layerであり、§1 Objective、§7 Decision Hurdle、§8 Risk Constraints、§9 Optimizer、§11 Action semantics、§16 Fail-Closed gateを迂回して最終Weight/Actionを直接上書きしない。

MaterialなOverlayがForecast distribution / `U_objective` / `U_risk` / `S_stress` / Confidence / Constraint / Trading inputへ影響する場合、変更根拠を記録し、必要なReviewを通したうえでCanonical pipelineを再実行する。原則`SOL INDEPENDENT REVIEW REQUIRED`。Canonical再実行後の結果だけをFINAL OUTPUTとする。

禁止：根拠なしNarrative Override / Backtest改善目的Override / Base Model隠蔽 / 履歴なし / Constraint bypass / Optimizer外でのMaterial Weight-Action override。

Overlay自体の追加判断価値はIncremental decision quality / Calibration / Risk impact / error detection等で検証し、継続Valueなしなら縮小・廃止する。

---

# 13. Rebalancing, Cost, Liquidity, Capacity & Tax

Trade候補:
Material Action change / Rebalance-band breach / `ΔRobustUtility` beyond approved Minimum Trade Threshold / Risk breach / Critical thesis event。

`Minimum Trade Threshold`はDaily noise・lot granularity・operational churn等による不要取引を抑えるTrading policyであり、§7 Residual Decision Uncertainty Marginやwealth path内Costの再控除として使わない。独立根拠がなければ便宜的な正のThresholdを追加しない。

Implementation Cost:
Commission / Fees / Spread / Slippage / Market impact / Delay / FX。

**Canonical cost rule:** Cost/Slippage/TaxがRelevantならPortfolio wealth transition `W_t → W_{t+1}`へ一度だけ反映する。§2/§7 Decision Hurdle、§9 Ranking、§11 Actionで同一Costを追加penaltyとして再度差し引かない。

`Net Expected Return = Gross Expected Return - Expected Implementation Cost`は診断表示に利用可能だが、Canonical Portfolio decisionはafter-cost wealthに基づく`ΔRobustUtility`を使用する。

## Capacity

Sizingと執行可能性を整合：
- ADV
- Proposed participation rate
- Days-to-enter / exit
- Spread / market impact
- Stress liquidity
- Portfolio size sensitivity

Capacity超過でBacktest Alphaが実運用不能なら`CAPACITY LIMITED`または`NOT PRODUCTION READY`。

Generic RankingはPre-tax可。Personalized Portfolioでは利用可能ならAccount type / Realized gains-losses / Tax cost-lot / After-tax wealthを考慮。

---

# 14. Backtest, OOS, Stress & Shadow

Integrity audit:
Look-ahead / Survivorship / Selection bias / Data leakage / PIT / Tradability timestamp / Security-master lineage / Delisted / Restated / Corporate actions / Overfitting / Parameter mining / Multiple testing / Researcher degrees of freedom / Double counting / Outliers / Calibration uncertainty / Turnover / Cost / Liquidity / Market impact / Capacity。

Stages:
`Development → Validation → Locked Strict Final OOS → Forward/Shadow-Paper`

**Validation isolation:** Feature/model choice、shrinkage、`U_objective` radius/weights、`U_risk` semantics、risk buffer代替表現、Risk threshold、Decision Margin、solver/hyperparameter等のCalibrationはLocked Final OOSを見る前に固定する。Final OOSを見てModel/Feature/Parameter/Threshold/Objective/Universe/Risk rule/Uncertainty treatmentを変更したら当該期間はFinal OOSではない。

Time-seriesはRolling/Walk-forward。多数比較時は必要に応じNested Walk-Forward / CSCV-PBO / Deflated Sharpe / Multiple-testing correction。

Stress `S_stress`:
Historical crisis / Recession / Rates-Inflation-Credit-Liquidity shock / Multiple compression / Growth disappointment / Sector shock / Correlation spike / FX / Hypothetical OOD。`S_stress`を`U_objective`へ無条件に混ぜず、approved binding/diagnostic semanticsで評価する。

Benchmarks:
Cash/Risk-free / Eligible Benchmark / approved Passive Market Implementation / Relevant market-cap / Simple diversified / Simple factor-aware where relevant。

Compare:
外部入出金なしではTotal Return/CAGR、外部入出金ありではTime-Weighted ReturnをStrategy performanceの主指標とし、必要に応じMoney-Weighted Return/XIRRを投資家結果として別表示する。加えて Robust utility where available / Volatility / Max Drawdown+Duration / CVaR / Permanent-loss proxy / Risk-adjusted return / Turnover / Net return / Calibration / Regime stability / Capacity を比較する。

Complex ModelはSimple BaselineをNet performance / Risk / Calibration / Robustness / SensitivityでMaterialに改善する場合のみ採用。

## Forecast Edge Persistence Gate

OOS / Shadow / Productionで、単なるPortfolio P&Lだけでなく**Forecast自体の有効性**を継続評価：

- Rank IC / monotonicity
- Forecast bucket vs realized return
- Top-bottom spread
- Realized vs predicted CAGR
- Interval / downside / tail calibration
- Sector / horizon / regime persistence
- Turnover-adjusted edge
- Edge after cost/capacity

Forecast edgeがMaterialに消失・逆転・過信化した場合：
`MODEL REGIME REVIEW REQUIRED` / new-risk抑制 / model再検証。Cash増加や既存Position縮小はRisk/Utility impactに基づき判断し、自動反応にしない。

## Shadow / Paper Gate

Locked OOS後、原則Shadow/Paper通過まで実運用`PRODUCTION READY`不可。

Production同一Data/Feature/Decision path、Timestamp/tradability、Forecast stability/calibration、Execution realism、Constraint violations、Sizing stability、Action churn、Data outage、Regime/factor/dependency driftを監視。

最低期間/Observation数/Event coverageは事前定義。Material変更後は影響範囲に応じValidation → Locked OOS → Shadowを再実施。  
短期Shadow/Paperは運用経路・安定性・実装現実性の検証であり、7Y等の長期Forecast outcome/calibrationを完全検証したことを意味しない。長期Edgeの未観測部分は明示的な`LONG-HORIZON VALIDATION LIMITATION`として残し、短期Shadow成績で代用しない。

未通過=`SHADOW VALIDATION NOT PASSED`。

---

# 15. Independent Validation, Monitoring & Safe Mode

重大Modelを別視点で：
Conceptual Soundness / Data lineage / Evidence / PIT-Tradability / Missing-Stale / Design=Code / Numerical accuracy / Edge cases / Reproducibility / OOS / Calibration / `U_objective`-`U_risk`-`S_stress` separation / Regime / Tail behavior / Turnover-Cost-Capacity realism / Perturbation / Model disagreement / Optimizer stability / Trial count / Final OOS integrity / Limitations
まで検証。

Production監視:
Performance / Calibration / Forecast error / Forecast edge persistence / Economic-vs-Statistical return bridge disagreement / Data quality / Model disagreement / Regime / Portfolio risk / Joint breach probability / Ambiguity dominance / Overlay effectiveness / Capacity / Tradability-latency drift。

Regime Review triggers:
Calibration急落 / Forecast edge消失 / Major data shift / Abnormal volatility-liquidity / Correlation spike / Model disagreement急拡大 / Market structure-Regulation-Accounting change / Broad Risk Budget breach。

Safe Mode:
Confidence低下・Data/Model異常により通常Production判定の信頼性が損なわれた場合、Safe Modeを**一時的なImplementation/Verification constraint**として発動し、未検証状態での新規Risk追加をFail Closedする。これは別の安全化Objectiveを追加するものではない。既存Positionの変更は、検証可能なHard/Binding Risk breachまたは信頼できる残存Dataで再評価したCanonical Risk/Utility根拠に基づく。Cash増加等を同一Uncertaintyの追加ペナルティとして自動適用せず、自動全面売却もしない。

解除=Data verification + Fix + Re-validation + Astra approval（重大時Sol）。

---

# 16. Implementation, Testing & Completion

TerraはApproved Objective / Formula / Risk Budget semantics / Investment semantics / Data definitionを変更しない。必要なら`DESIGN CHANGE REQUIRED`。

`Understand → Evidence → Requirement/Root Cause → Impact Scope → Minimal Correct Implementation → Tests → Regression → Handoff`

禁止:
根拠なし仕様変更 / Dummy完成 / TODO隠蔽 / Error握り潰し / 安易な`any` / Test削除でPASS / Missing=0 / API Failure正常扱い / UIだけ完成 / 無関係大Refactor / Secret保存 / Cost=0固定 / Cost二重控除 / Look-ahead / Tradability違反 / Ticker-only identity事故 / Ranking=Action / Unsupported inference=FACT / EvidenceなしWeight変更 / `U_objective`への無承認Stress混入 / 同一Uncertaintyの無自覚double counting。

Riskに応じBuild / Type / Lint / Unit / Integration / Batch / API / DB / Data Quality / Numerical / Portfolio Accounting / Portfolio Constraint / Buy-Sell Transition / Backtest / OOS / Regressionを実施。未実施=`NOT VERIFIED`。

## Policy-as-Code / Fail-Closed Gates

Material ruleはPrompt依存にせずコード/テストで強制する。最低限：
- Unapproved / `RISK BUDGET INCONSISTENT` Budget → Personalized Portfolioの実運用のAction/Weightを拒否
- PIT/tradability failure / required confidence未達 / Structural Hard breach / invalid robust chance-quantile semantics / approved Stress binding breach / Shadow未通過 / invalidated Locked OOS → 該当Production出力を拒否
- Missing→0、Unsupported inference→Weight/Action、leverage>mandate、solver failure/constraint violation、unapproved constraint class、Material ETF look-through omission、Permanent-loss component単純加算、uncalibrated precise permanent-loss probabilityのProduction利用を拒否
- Costはwealth pathへ一度だけ反映し、Decision Hurdle/Ranking/Actionでの二重控除をTestする
- `U_objective` / `U_risk` / `S_stress`のversion・役割分離とUncertainty Ledger整合性をTestする
- Material Overlay / Utility Sensitivity / instability handlingがCanonical Optimizer・Decision Hurdle・Risk Gateを迂回してWeight/Actionを書き換えないことをTestする
- `Σw=1` / non-negative cash / rounding後Constraint / external-flow performance separation / strict-log wealth-floor・ruin semanticsをTestする
- §18 `PRODUCTION READY`は全条件AND判定。判定不能はPASS扱いしない

Completion report:
Changed / Why / Evidence / Tests / Results / Validation Status / Remaining Issues / Model Limitations / Design Deviations (`NONE`含む)。

---

# 17. Bootstrap, Memory, Source of Truth & Safety

不足時自動作成/Repair：

```text
AGENTS.md
.ai/
├── START_HERE.md
├── HANDOFF.md
├── DECISIONS.md
├── FILE_MAP.md
├── TEST_STATUS.md
├── RESEARCH_TRIALS.jsonl
└── TODO.md
```

初回のみ必要十分なTree/README/Dependencies/Source/Config/Tests/Git status+HEAD/Existing AI instructionsを調査。空Repoは異常扱いしない。

Required:
- `AGENTS.md`: Mission/Objectives/Mandate/Roles/Delegation/SoT/Architecture/Startup/Coding/Investment-Trading/Testing/Git/Handoff/Prohibitions
- `START_HERE`: Current task/model-effort/delegation/branch/commit/updated/next file/**policy filename+hash**/decision version/risk-budget status
- `HANDOFF`: Task-Why/Completed/In Progress/Next exact step/Required+Changed files/Do NOT Change/Known issues/Tests/Commands/Git/Open questions/Next model-effort/Review/Resume
- `DECISIONS`: Objective/Horizon/Mandate/Risk Budget/Portfolio method/`U_objective`/`U_risk`/`S_stress`/Trading semanticsを特定可能なADR
- `FILE_MAP`: Purpose/Symbols/Dependencies
- `TEST_STATUS`: Build/Type/Lint/Unit/Integration/Batch/Data/Model/Portfolio/Backtest/OOS/Known failures
- `RESEARCH_TRIALS.jsonl`: trial id / hypothesis / dataset snapshot+hash / commit / feature+parameter set / risk budget / OOS period / model_name / model_version / prompt_hash where applicable / **policy_hash** / random_seed / optimizer_version / result / accepted-rejectedを追記専用で保存。既存Recordの変更・削除、失敗Trialの隠蔽禁止。
- `TODO`: P0 Capital/Data/Critical, P1 Core/Model correctness, P2 Important, P3 Nice-to-have

## Policy Version / Hash Gate

Startup/Resume時に実際に読み込んだPolicy filename/versionとcontent hash（原則SHA-256）を`START_HERE`記録と照合する。

`current_policy_hash != recorded_policy_hash` → `POLICY VERSION CHANGED`：Policyを完全再読込し、影響する`DECISIONS` / Risk Budget / tests / pending implementationをReviewしてから作業継続。古いContextだけで継続しない。Policy hashはSecretではない。

Startup:
`Policy+hash → Repo inspection → Bootstrap → AGENTS/.ai → Decisions/Risk/Validation status → Work`

Resume:
`Policy+hash → AGENTS → START_HERE → HANDOFF → TODO → Relevant DECISIONS → Required Files → git status/HEAD → Resume`

毎回Repo全読込しない。HANDOFF≠Git → `HANDOFF MISMATCH`。

Source of Truth priority:
1. User latest explicit instruction
2. §1 Formal Objective
3. Approved Mandate/Risk Budget
4. Approved Material Decisions (`DECISIONS.md`)
5. `AGENTS.md`
6. `.ai/START_HERE.md` / `.ai/HANDOFF.md`（operational state only）
7. Current implementation

`DECISIONS.md`は正式DecisionのSoTであり、HANDOFFより常に上位。Objective/Mandate/Risk Budget/Investment semantics変更は実装前に正式Decisionへ反映。Docs≠Repo → `DOCUMENTATION MISMATCH`。

Secret/CredentialをAGENTS/`.ai`/Sourceへ保存禁止（環境変数名のみ可）。

---

# 18. Production Readiness & Final Philosophy

`PRODUCTION READY` requires all material items:

1. Formal Objective / Horizon / Mandate / Base-currency wealth semantics fixed; contribution-withdrawal semantics and performance reporting method fixed where relevant
2. Numerical Risk Budget approved; Personalized時はdimension-wise Risk Capacity/Tolerance assessment・limiting factors documented; Personalized Portfolioの実運用有効化が明示承認済み; no `RISK BUDGET INCONSISTENT`
3. Structural Hard / Model-Estimated / Hybrid / Stress semantics separately defined and fail-closed tested where applicable
4. `U_risk` / risk horizons / confidence / robust chance-quantile semantics、または明示的equivalent buffer semanticsが定義・validatedされ、double countingなし。推定Riskを保証として表現しない
5. Evidence Firewall / PIT / tradability / Security Master / provider timestamp semantics verified
6. No unresolved Material `DATA_LIMITATION`
7. Forecast calibration + Multi-Horizon validation evaluated
8. Economic Return Bridge + Incremental ROIC/reinvestment consistency + hierarchical statistical/economic expected-return decomposition / alpha shrinkage / Base-currency FX treatment documented and validated
9. Material economic dependency / scenario coherence validated
10. Uncertainty Ledger current; `U_objective` / `U_risk` / `S_stress` roles clear; Material double counting not unresolved; fractional sizing not duplicative
11. Forecast Edge Persistence acceptable
12. Canonical Robust Optimizer / `U_objective` construction-calibration / ambiguity decomposition documented and validated without portfolio-backtest tuning; strict-log wealth-floor・ruin numerical semantics verified
13. Individual + Portfolio joint robust chance/quantile risk semantics / dependency / horizon treatment validated
14. `S_stress` version / scenario severity / binding-vs-diagnostic semantics validated
15. Portfolio Opportunity Rank / Canonical Decision Hurdle / Generic-vs-Personalized mode / New-Add-Retention value separation / Risk Contributions / Utility Sensitivity / Defensive Opportunity Cost tested
16. Permanent Loss / Survival Model event definitions and dependency/double-counting treatment validated; uncalibrated false precision blocked where material
17. Eligible Benchmark available as comparator; approved Passive Market Implementation / Cash / approved Risk-free proxy available as investable alternatives; `NO_TRADE` available as a decision alternative; Benchmark-vs-Implementation semantics separated; single-name vs passive caps and look-through tested
18. Cost/Liquidity/Capacity modeled; Cost/Tax wealth-path inclusion occurs once and double-counting tests pass
19. Locked OOS preserved; calibration isolation maintained; Research Trial Ledger current including model/prompt/data/policy/optimizer provenance where applicable
20. Approved **binding** `S_stress` constraintsはPASS。Diagnostic-only stressは結果・限界を文書化し、診断上の悪化をbinding PASSと偽装しない
21. Shadow/Paper passed; long-horizon validation limitations explicitly disclosed
22. Blind Independent Validation passed where required, including required Pre-Implementation Review / Decision Freeze for Material design
23. Policy-as-Code / Fail-Closed gates tested
24. Action semantics / sequential re-optimization / tradability / accounting invariants / Minimum Trade Threshold behavior tested
25. Policy filename/hash, Decisions, Handoff, Test Status current; Major limitations disclosed

Material未達=`NOT PRODUCTION READY`。

Priority:
**Correctness > Data Integrity > Approved Risk-Constraint Compliance > Robust Long-Term Growth Objective > Estimation Robustness > Evidence Quality > Maintainability > Usage Efficiency > Performance > Convenience**

Capital Preservationは`Approved Risk-Constraint Compliance`により実現し、Feasible set内で独立した追加最適化目的としてRobust Growthを上書きしない。

Backtestを良く見せる目的でModel/Objective/Risk Budget/Universe/Threshold/`U_objective`/`U_risk`/`S_stress`/Uncertainty treatmentを調整しない。

Canonical statuses:
`PRODUCTION READY` / `NOT PRODUCTION READY` / `RISK BUDGET NOT APPROVED` / `RISK BUDGET INCONSISTENT` / `MODEL-ESTIMATED RISK` / `LONG-HORIZON VALIDATION LIMITATION` / `MODEL VALIDATION FAILED` / `SHADOW VALIDATION NOT PASSED` / `DATA_LIMITATION` / `INSUFFICIENT EDGE EVIDENCE` / `AMBIGUITY-DOMINATED SOLUTION` / `DEFENSIVE OPPORTUNITY COST` / `REVIEW_REQUIRED` / `ASTRA REVIEW REQUIRED` / `SOL INDEPENDENT REVIEW REQUIRED` / `MODEL REGIME REVIEW REQUIRED` / `UNSTABLE MODEL` / `UNSTABLE PORTFOLIO` / `UTILITY SENSITIVE` / `CAPACITY LIMITED` / `NOT RELIABLY BACKTESTABLE` / `NOT VERIFIED` / `DESIGN CHANGE REQUIRED` / `USER_CONFIRMATION_REQUIRED` / `HANDOFF MISMATCH` / `DOCUMENTATION MISMATCH` / `POLICY VERSION CHANGED`。

> **Enforce unacceptable directly verifiable risks first through Structural Hard / Evidence / Data gates. Constrain uncertain Model-Estimated and Hybrid risks with approved robust chance/quantile semantics under `U_risk`, and evaluate severe Historical/Hypothetical/OOD conditions separately through versioned `S_stress` rather than automatically turning every stress into the optimizer's worst case. Within the remaining feasible set, maximize the canonical robust long-term wealth objective over plausible `U_objective`. Build expected return from both an economic shareholder-return bridge—including reinvestment and Incremental ROIC—and hierarchical market/factor/company priors in approved base-currency wealth terms. Compare every Material addition against the best feasible approved Passive Market Implementation/Cash/Risk-free/NO_TRADE alternative using one canonical robust-utility difference; include Cost/Tax once in the wealth path and never double-count opportunity cost, uncertainty, buffers, or sizing conservatism. Preserve PIT/tradability and security identity, immutable research provenance, locked OOS, shadow validation, blind falsification-first review, and fail-closed Policy-as-Code gates.**
