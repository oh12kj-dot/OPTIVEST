# OptiVest AI 開発・投資方針 — Compact V10 — 最終版

> 完全新規開発 / 根拠重視 / ロバストなリスク制約 / ポートフォリオ優先 / 統制された委任  
> 最上位の方針文書: 本Policy。投資目的は§1、個別の承認済み設定はMandate / Risk Budget / `DECISIONS.md`に記録し、優先順位は§17に従う。  
> 不確実性の標準区分: `U_objective` / `U_risk` / `S_stress`  
> 未承認のリスク上限・ドローダウン上限・検証結果・実運用承認を推測で補ってはならない。

---

# 1. 唯一の最上位投資目的

OptiVestは**完全新規開発**とする。既存のArchitecture / DB / API / Ranking / 投資ロジックとの互換維持は目的にしない。本節を唯一の最上位投資目的とし、Prompt / UI / Score / Backtest / 既存Codeから再定義してはならない。

投資目的を変更する場合は、ユーザーの明示指示を受けた後、本節と`DECISIONS.md`を実装より先に更新する。

## 目的

> **その時点で実際に利用可能だった情報だけを使って将来のTotal Return確率分布を推定し、Quality / Growth / Valuation、推定不確実性、Permanent Loss、Tail Risk、Liquidity、Cost、必要に応じTax、資産間Dependencyを統合する。直接判定できる許容不能リスクはStructural Hard Constraintとして先に除外し、推定を伴うリスクは承認済みのロバストな確率・分位点制約で管理する。その条件を満たすポートフォリオ集合の中で、推定誤差・Model Risk・Regime変化に強い長期複利成長を最大化するポートフォリオと行動を提示する。**

標準の経済目的関数：

`Annualized Log-Wealth Growth(P,w) = (1/T) E_P[log(W_T(w)/W_0)]`

標準のロバスト目的関数は§9に従い、現実的に起こり得る不確実性集合`U_objective`に対する最悪側の年率対数資産成長率を最大化する。

- `T` = 承認済み投資期間
- `W`の基準通貨 / 名目・実質 / 税引前・税引後の扱いは承認済み運用方針で固定
- 外貨建資産は現地通貨建リターンとFXリターン、その依存関係を統合
- 最終`W_T`は必ず承認済み基準通貨で評価
- Cost / Taxを考慮する場合は資産推移へ**一度だけ**反映
- 外部拠出・引出しがある場合は、比較する全代替案で同じCash-flow scheduleを使う。`W_T/W_0`をそのまま投資CAGRとして解釈せず、投資パフォーマンスと外部資金フローによる資産増減を分離して表示する。
- Generic / Backtestでは原則Self-financing wealthを使う。個人向けでは将来拠出・引出しをState / Constraintへ反映し、同一Cash-flow条件下のPortfolio decisionを比較する。
- Log utilityの定義域を曖昧にしない。`W_T <= 0`を黙って小さな正数へ置換しない。Model上のTotal-ruin stateと数値Underflowを区別し、数値計算用`wealth_floor`が必要なら事前にVersion管理して感応度を検証する。Total-ruin / Permanent-loss riskはFloorで隠さず別途表示・制約する。

## 優先順位

1. 承認済みStructural Hard Constraint / 実装上のHard Constraintに違反するポートフォリオを除外する。
2. Model-Estimated / Hybrid Risk Constraintを§8の承認済み判定方式で評価し、違反するポートフォリオを除外する。
3. 残った実行可能集合の中で、§9のロバストな年率対数資産成長率を最大化する。
4. ロバスト効用差が`Residual Decision Uncertainty Margin`内で識別不能な場合のみ、Permanent Loss → Stress Drawdown / CVaR → Model uncertainty → Concentration → Liquidity → Cost / Turnover / Complexityの順で保守的な案を優先する。

## 原則

- **Risk Limitは上限であり、使い切る目標ではない。**
- 制約を通過した後、根拠のない「念のための安全化」で成長目的を上書きしない。
- Risk / Returnを一つのComposite Scoreへ無理に圧縮しない。
- 小さなExpected Return差より推定誤差・Tail Risk・Robustnessを重視する。
- 同じ不確実性を複数箇所で重複して罰し、必要以上にCashへ寄せない。
- Broad diversified passive benchmark / Cash / Risk-free proxy / `NO_TRADE`を正式候補とする。
- Ranking 1位でもポートフォリオ全体の目的を悪化させるなら買わない。
- Backtestを良く見せる目的でObjective / Risk Budget / Universe / Threshold / Uncertaintyの扱いを後付け変更しない。
- Capital Preservationは独立した目的関数ではなく、Structural Hard Constraint、Model-Estimated / Hybrid Risk Constraint、Evidence / Data Gateで実現する。

最上位目的として禁止：`P(7年で10倍)`、Composite Score、Sharpe単独、Expected Return単独、Risk-Adjusted Score単独、Historical CAGR単独、Backtest最大化。これらは補助指標または診断用途に限る。

---

# 2. 運用方針と戦略範囲

原則：**Long-only listed equities + 承認済みの広範なパッシブ市場ベンチマーク + Cash / Cash Equivalent + 承認済みRisk-free proxy。Leverageは使用しない。**

原則禁止：Short、Margin、Options、Futures、CFDs、Leveraged / Inverse ETF、Synthetic / Naked leverage、流動性の低いPrivate securities、未検証Intraday。

Broad diversified passive benchmark / Cash / Risk-free proxyは正式な投資候補・比較対象とする。CashとRisk-free proxyは同一視しない。Cash Equivalentも自動的に無リスクとは扱わず、Currency / Credit / Liquidity / Settlement / Redemption条件をInstrument単位で確認する。Risk-free proxyは少なくとも`currency / maturity-duration / credit assumption / reinvestment assumption`を明示する。

個別株Alphaの不確実性が高いことを理由に、市場Risk Premiumまで機械的に0へ縮小しない。

## 追加投資の標準判断

重要なRisk Asset追加・増額は、§7の**標準投資判断基準**と§9の`U*`に従い、最良の実行可能な代替案との差をポートフォリオ全体のロバスト効用で判断する。

Standalone Expected Returnが代替案より高いことは必須ではない。DiversificationやTail Risk低減によってポートフォリオ全体のロバスト効用を改善する候補も採用可能とする。Cost / Tax / Opportunity Cost / Residual uncertaintyの扱いは§7・§13を唯一のCanonical ruleとし、本節で別定義しない。

正式Actionは§11の一覧へ統一する。

## 承認済み運用方針に必須の項目

- Investment horizon
- Base currency
- Nominal / Real objective
- Pre-tax / After-tax treatment
- Contribution / Withdrawal assumption
- Portfolio / account scope
- Reference capital scale or capacity bands
- Eligible benchmark
- After-tax評価を行う場合はTax jurisdiction / Account type / Lot treatment

個人向けポートフォリオでは、利用可能な範囲でAfter-cost / After-tax / Base-currency wealthを優先し、必要に応じて実質購買力との差も表示する。

原則は**Equity Sleeve**であり、全資産を含むGlobal Total Portfolioの最適性を意味しない。

## Portfolio会計の不変条件

Long-only / No-leverage Mandateでは、原則として執行後の対象資産、Cash、Risk-free proxyのWeightを基準通貨ベースで評価し：

`w_i >= 0`  
`Σ w_i + w_cash + w_riskfree = 1`

を満たす。

- Negative Cash、Implicit borrowing、Settlement差異による隠れLeverageを許可しない。
- Lot size / Share rounding / Fee / Tax / Partial fillを反映した**実行可能ポートフォリオ**でWeight合計、Leverage、Concentration、Liquidity、Risk Constraintを再検証する。
- Rounding residualは承認済みCash / Cash-equivalentへ置き、未定義のResidual exposureを作らない。
- Capacity評価はReference capital scaleまたは複数のCapital bandを明示して行う。金額規模なしにLiquidity / Market impactを「問題なし」と判定しない。

## Multi-Assetへの拡張

Fixed Income / Inflation-linked / Commodities / Gold / Alternatives / FX hedging等を追加する場合は別の運用方針として、以下を承認・検証する。

- Eligible Assets / Benchmark / Base currency / Nominal-Real / Tax
- Return / Risk Model
- Stress dependency
- Liquidity / Cost / Capacity
- PIT / Corporate Action / Index history integrity
- Locked OOS / Shadow
- Numerical Risk Budget
- Independent validation

承認前に「全資産でGlobal Optimal」と表現しない。

## 利用範囲・法令・ライセンス境界

自己利用の研究・投資判断支援と、第三者へ提供する投資助言・運用サービスを同一視しない。

- 第三者向け提供、受託運用、自動発注、顧客資産を扱う機能へ拡張する場合は、対象Jurisdictionの投資助言・金融商品・記録保存・適合性・開示・個人情報保護等の要件を別途確認する。
- Data / API / Model Providerの利用規約、再配布権、商用利用可否を確認し、権利が不明なDataをProductionの正式情報源として当然に利用可能と扱わない。
- 法務・規制上の確認が必要なのに未確認の場合は、その範囲を`NOT PRODUCTION READY`とする。

---

# 3. 役割・推論強度・レビュー条件

## Astra — 設計責任者 / 投資アドバイザー

担当：Objective、運用方針、Risk Budget設計、Forecast architecture、Ranking、Portfolio / Sizing、売買判断、Data / Valuation / Confidence、Backtest / Model governance、主要Architecture、Terra向け仕様、最終設計承認。

Effort：
- 初期設計・重要な投資設計=`high`
- 安定した設計=`medium`
- Objective / Numerical Risk Budget / 実運用 / Critical issue=`xhigh`
- `max`は例外

## Terra — 実装担当

担当：Backend / Frontend / DB / API / Batch / Data pipeline / Tests / Bugfix / Refactor / 承認済み設計の実装。

Effort：
- 原則=`medium`
- 複数Module / DB / Portfolio / Data Integrity=`high`
- Critical incident=`xhigh`

承認済みの投資判断の意味・数式・Risk Budget定義を変更してはならない。変更が必要なら`DESIGN CHANGE REQUIRED`。原則として追加サブエージェントは禁止。

## GPT-5.6 Sol — 独立レビュー / 検証担当

確認対象：Investment logic、Calibration、Portfolio risk、Data integrity、OOS / Backtest、Implementation、Failure mode、Optimizer stability、Limitations。

Effort：
- 原則=`medium`
- Important=`high`
- Critical=`xhigh`

Astraの設計を正しいと仮定しない。**改善案を考える前に、まず反証を試みる。** 原則として追加サブエージェントは禁止。

## 必須レビュー

`ASTRA REVIEW REQUIRED`：Objective、運用方針、Risk Budget、Forecast / 投資判断の意味、Portfolio / Sizing、Buy / Sell定義、Backtest手法、重要Architecture。

`SOL INDEPENDENT REVIEW REQUIRED`：上記のうち、実運用へ重大な影響があるもの、Data Integrity、Locked OOS、Major Model Validation、重要Overlay、P0 / P1 regression、Critical limitation。

重要なObjective / Forecast architecture / Numerical Risk Budget / Robust Optimizer / Ranking / Trading / Backtest手法を変更する場合は、原則として次の順序を守る。

`Design → Pre-Implementation Review → Decision Freeze → Implementation → Tests → Post-Implementation Validation`

実装後レビューだけで初めて設計妥当性を確認してはならない。Decision Freeze後に重要な意味変更が必要になった場合はFreezeを解除し、Decision / Reviewをやり直す。

重大な検証不合格：`MODEL VALIDATION FAILED` → 実運用不可。

重要なIndependent Reviewは可能な範囲でBlind First-Passとする。SolはAstraの結論やNarrativeを見る前にRaw evidence / objective / inputs / formulas / numerical outputsから独立判定し、その後Astra案との差分を確認する。重要なRisk / Return計算は可能なら別実装で再計算する。

---

# 4. 自律作業フローと委任

標準フロー：

`Investigate → Evidence → Compare → Decide → Pre-Implementation Review where required → Decision Freeze → Document → Implement → Test → Post-Implementation Review / Validation → Fix → Handoff → Next Priority`

根拠が十分で元に戻せる判断は自律実行する。質問するのは、重要な必須情報が他の方法では取得・確定できず、推測すると投資判断や安全性を変える場合だけにする。その場合も未確定値を推測で埋めず、研究・シミュレーションとして継続できる範囲は継続する。`USER_CONFIRMATION_REQUIRED`は承認操作のGateであり、必要最小限の情報確認とは区別する。

標準構成：`One Architect → One Active Implementer → Reviewer only when justified`

Rules：
- Active subagentは1名、depth=1
- Recursive delegation禁止
- Competitive broadcast禁止
- Repository / File / Contextの理由なき重複調査禁止
- 親による並行再実装禁止
- Review-Fixは原則1往復
- Parallel実行は独立TaskでContext重複が小さい場合だけ

委任時は必ず以下を明示する。

`Objective / Scope / Acceptance Criteria / Required Files / Do NOT Change / Expected Output`

`USER_CONFIRMATION_REQUIRED`：
- 実際の注文発注
- 個人向けポートフォリオのRisk Budgetを実運用へ反映すること、または実運用中のRisk Budget変更を確定すること
- 本番Deployment
- 外部課金
- 本番データ破壊
- 不可逆操作
- Git history rewrite
- Secret / Credentialや重大な権限変更
- 新たな外部サービスへ、個人の保有資産・税務・口座情報などの機微な金融データを送信すること
- ユーザー明示要件と矛盾する変更

---

# 5. 投資対象範囲・PITデータ・銘柄マスター・根拠管理

Universeには少なくとも以下を明示する。

Country / Exchange / Security type / Market cap / Liquidity / Trading history / Fundamental coverage / Corporate actions / Delisting coverage / Currency / Data availability

Universe変更は重要Decisionとして記録する。

## Security Master

長期履歴、Corporate Action、Ticker変更をTicker文字列だけで管理しない。重要Universeでは安定した`internal_security_id / issuer_id`を持ち、可能な範囲で次を保持する。

`ticker history / exchange / share class / ADR-underlying relation / merger-spin-off history / delisting mapping / currency / corporate-action lineage`

識別不能がBacktestまたは実運用へ重要な影響を与える場合は`DATA_LIMITATION`。

## PIT / Tradability Rule

**判断・Backtestには、その時点で実際に利用可能だった情報だけを使う。** Restated Dataを過去へ遡及適用しない。

重要Data metadata：

`as_of_date / available_at / retrieved_at(where relevant) / source / staleness / quality_confidence / lineage`

判断・Backtestでは別途：

`decision_timestamp / tradable_at`

を保存する。

原則：

`decision_timestamp >= available_at + verified ingestion/processing latency`

取引価格は`tradable_at`以降に現実に約定可能だった価格・時刻を使う。決算、Filing、Index change等を、公開前価格や公開直前Closeへ遡及適用しない。

`tradable_at`はExchange calendar / Time zone / Holiday / Halt / Auction / Session / Clock synchronizationを考慮する。市場停止中、Quote stale、Clock不整合時に通常取引可能と推測しない。

Timestampの意味やLatencyを検証できない重要SourceをPIT-safeと推測しない。

Missing≠0。

`Missing / Unknown / Not Applicable / Stale / Conflicting / Unavailable Point-in-Time`

を区別する。

## Data Source方針

優先順位：
1. Regulator / Government / Central Bank / Treasury / Official Exchange / Issuer filing
2. Issuer IR / Official disclosure
3. Reputable free market-data source / Aggregator
4. Verified inputから計算したDerived data

標準Source：
- US filings / fundamentals：SEC EDGAR / XBRL
- Japan filings：EDINET
- Macro / rates / inflation / credit vintages：FRED / ALFRED where applicable
- Yahoo Finance / yfinance：補助的なMarket Data Source。Accounting / PIT fundamentalの唯一の正式情報源にはしない

ProviderごとにLicense / Rate limit / Timestamp semantics / Coverage / Corporate-action handling / PIT suitabilityを記録する。

複数Sourceが重要な水準で矛盾する場合は、単純平均や都合のよい値の選択をしない。Definition / Unit / Period / Currency / Restatement / Available-at / Corporate action差を照合し、正式Source優先順位と用途適合性に基づいて解決する。解消できない重要Conflictは`DATA_LIMITATION`または`REVIEW_REQUIRED`。

無料Sourceで重要な品質が不足する場合は推測で埋めず`DATA_LIMITATION`。Backtest信頼性を損なうなら`NOT RELIABLY BACKTESTABLE`。実運用の判断を歪めるなら`NOT PRODUCTION READY`。

有料Data / APIを使う場合は無料代替との差を文書化し、外部課金前にユーザーの明示承認を得る。

**FACT**：Source / Available-at / Evidence / Data quality / Confidence必須。  
**INFERENCE**：Supporting FACTs / Reasoning basis / Confidence / Material alternative / Review trigger where appropriate。

> **根拠のないLLM推論をForecast / Ranking / Portfolio Weight / BUY-SELLへ直接反映しない。**

---

# 6. 投資判断に使う入力情報

重複・相関・Double Countingを避けながら必要に応じて評価する。

- Quality：Revenue / EPS / FCF growth、Margins、ROIC / ROE、Incremental ROIC、Reinvestment rate / runway、Unit economics、Operating leverage、Earnings quality
- Moat：Network effects、Switching costs、Brand、Scale / Cost、IP、Data、Distribution、Ecosystem
- Market：TAM / SAM / SOM、Industry growth、Market share / expansion、Competition
- Management：Capital allocation、Insider ownership、Track record、M&A、Buybacks、SBC / Dilution、Guidance accuracy、Governance
- Financial Risk：Debt、Interest coverage、Liquidity、Cash burn、Refinancing / Bankruptcy、Maturity、Covenants、Off-BS obligations
- Valuation：P/E、PEG、EV/EBITDA、EV/Sales、P/FCF、FCF Yield、Reverse DCF、Historical / Peer / Scenario valuation
- Macro / Regime：Rates、Inflation、FX、Commodities、Credit、Cycle、Liquidity、Regime sensitivity

長期Compounderでは過去ROICだけでなく、**追加資本が将来どれだけのReturnを生むか**を重視する。

`Sustainable growth ≈ Reinvestment rate × Incremental ROIC`

は診断・経済整合性の確認に使えるが、会計定義、Capital intensity、M&A、SBC等を無視した機械的予測には使わない。

Return / Risk / Confidence / Quality / Valuationを一つのScoreへ無理に圧縮しない。

定性的なMoat / Management / Governance / TAM等を数値Forecastへ反映する場合は、根拠となるFACT、変換Rule / Scenario、Uncertainty、Versionを記録する。LLMの文章評価をそのままWeightやExpected Returnへ直結させない。重要な定性判断は、Version管理したFeature / Scenario assumption / Review可能な変換経路を通す。

---

# 7. 予測・不確実性・投資判断基準・較正

単一点予測を唯一のInputにしない。最低でもBear / Base / Bullを持ち、重要対象ではDistributionを使う。

主なTarget：Revenue CAGR、Margin、FCF / EPS、Dilution、Capital structure、Valuation multiple、Dividend / Buyback、Expected price、Total Return / CAGR。

重要Forecastでは可能な範囲で以下を比較する。

Historical base rate / Simple benchmark / Economic prior / Market-implied expectation / Fundamental scenarios / Model disagreement / Historical error / Parameter-Model-Regime uncertainty

## Expected Returnの二層構造

### A. Economic Return Bridge

`Business growth → Per-share fundamental growth → Shareholder yield → Valuation change → FX where relevant → Total Shareholder Return`

Revenue / Earnings / FCF growthだけを株価成長へ直結させない。Margin、Incremental ROIC、Reinvestment、Capital intensity、SBC / Dilution、Buyback、Dividend、Capital structure、Valuation multiple、Currency translationを整合的につなぐ。

外貨建AssetはLocal return + FX return + dependencyとしてBase-currency wealthへ統合する。

### B. Statistical / Economic Prior

原則：

`Risk-free → Broad-market risk premium → Factor/Sector component → Company-specific alpha`

Shrinkageは特にCompany-specific alphaへ強く適用する。個別Alphaの不確実性が高いことを理由にBroad-market Expected Return全体をCashへ機械的に縮めない。

最終Forecast distributionはA / BのEvidence、Base rate、Market-implied expectation、Historical / OOS error、Model disagreementを統合する。A / Bが重要な水準で不一致なら差を隠さず`MODEL DISAGREEMENT`としてUncertainty Ledgerへ記録する。

## Economic Dependency / Scenario Coherence

重要Forecast variableを相互独立と仮定しない。少なくとも重要な場合は次の依存関係を扱う。

- Growth ↔ Margin
- Growth ↔ Reinvestment / Incremental ROIC
- Rates ↔ Valuation
- Credit ↔ Refinancing / Default
- Macro ↔ Earnings
- FX ↔ Local asset return
- Volatility ↔ Correlation / Liquidity

経済的に不整合なScenarioが結果を大きく歪める場合はModelを修正する。単純なHistorical correlationだけで十分と仮定しない。

## 主なOutput

可能な範囲で：

Expected / Median CAGR、Downside percentile、P(loss)、Permanent-loss range / probability where calibrated、Upside probability、CVaR / ES、Prediction / Credible interval

Expected CAGR、Median CAGR、`exp(E[log return])-1`、`CAGR(E[W_T])`は同一ではない。表示する指標は計算定義を明示し、§9のRobust log-wealth objectiveと「期待CAGR」を同じものとして扱わない。

ConfidenceはData / Evidence / Model / Forecast / Actionへ分ける。Forecast distribution、`U_objective`、`U_risk`、Review requirementへ反映し、同じ根拠をさらに独立したSizing penaltyへ重複反映しない。

## 標準投資判断基準

重要なRisk Asset追加・増額、Ranking、Trade gateはExpected Return差ではなく、ポートフォリオ全体のロバスト効用差へ統一する。

`ΔRobustUtility = U*(candidate/size allowed) - U*(best feasible alternative)`

原則：

`ΔRobustUtility > Residual Decision Uncertainty Margin`

`Residual Decision Uncertainty Margin`は`ΔRobustUtility`と同じ年率対数資産成長率の単位で定義する。

対象に含めるのは、Optimizer / value-difference estimation error、finite-sample uncertainty等のうち、**`U_objective` / `U_risk` / Costへまだ反映されていない残差だけ**とする。

独立したResidual sourceがない場合は、便宜的に正のMarginを足さない。

Cost / Slippage / Taxは`U*`のWealth pathへ両側同じ条件で一度だけ反映する。Opportunity CostはBest feasible alternativeとの差にすでに含まれるため再加算しない。

差がMargin内なら`INSUFFICIENT EDGE EVIDENCE`とし、大きなWeight差や高Conviction BUYへ変換しない。

Company-specific alphaは診断指標として表示してよいが、最終Portfolio Actionを単体Alpha / Expected Returnへ置き換えない。

## Uncertainty Ledger

重要Decisionでは主要Uncertainty sourceごとに役割を記録する。

`source → predictive distribution / shrinkage / U_objective / U_risk / S_stress / decision margin / optional sizing adjustment`

- `U_objective`：§9のObjectiveでWorst-plausible growthを評価するための現実的な不確実性
- `U_risk`：§8のロバストな確率・分位点制約に使う不確実性
- `S_stress`：Historical / Hypothetical / OOD Stress Scenario集合。Objectiveの`min P`へ自動投入しない
- Explicit safety bufferを使う場合、それが`U_risk`の近似・代替なのか、独立した根拠なのかを明示する
- Fractional / Confidence sizingを追加する場合は、Log utility / Shrinkage / `U_objective` / `U_risk` / Decision Marginと独立したCalibration根拠を要求する

同じOOS error / Model disagreement / Regime uncertainty等を複数Layerへ反映する場合は、依存関係と総影響を確認する。

無自覚なDouble Counting、または保守化の重ね過ぎによるCash偏重・Growth破壊は`UNSTABLE MODEL` / `AMBIGUITY-DOMINATED SOLUTION` / Review対象。

## Calibration

必要に応じて：Calibration curve / Interval coverage / CRPS / Log-Brier Score / Rank IC / Horizon-Sector-Regime error / Tail calibration / Over-Underconfidence。

小さな合理的入力変更でForecast / Ranking / Weight / Actionが大きく変わる場合は`UNSTABLE MODEL`。

## Multi-Horizon Validation

長期Horizon、例として7年、をOverlapping outcomeだけで過信しない。可能な範囲で`1Y / 3Y / 5Y / 7Y`のForecast consistency、Realized outcome、Sample dependenceを確認する。

独立した長期Outcomeが不足する状態を統計補間だけで`PASS`へ変換しない。

---

# 8. リスク管理体系と数値リスク予算

Risk taxonomy：
- Market：Volatility / Beta / Factor / Drawdown / Correlation
- Tail：Downside deviation / CVaR-ES / Gap / Jump / Fat-tail / Correlation spike
- Permanent Loss：Bankruptcy / Refinancing / Dilution / Fraud / Accounting / Governance / Regulatory destruction / Structural decline
- Liquidity / Capacity：ADV / Spread / Market impact / Participation rate / Days-to-enter-exit / Forced-sale
- Concentration：Security / Sector / Industry / Country / Currency / Factor / Customer / Supplier / Technology / Funding
- Model：Data / Parameter / Model / Forecast uncertainty / Disagreement / OOD / Regime shift
- Operational / Execution：Stale portfolio state / Duplicate order / Partial fill / Market halt / Broker-API outage / Clock skew / Custody-Counterparty / Reconciliation failure / Permission error

## Permanent Loss / Survival Model

Permanent LossはVolatilityや大きなTemporary Drawdownと分離して評価する。

重要対象では必要に応じて次を分解する。

- Default / Liquidation
- Distressed Dilution / Rescue Financing
- Fundamental Impairment
- Terminal Real Loss > approved threshold
- No Recovery within approved horizon

Bankruptcy / Refinancing / Accounting / Governance / Fraud / Regulatory / Structural decline等のEvidenceから推定し、定義・Threshold・HorizonをVersion管理する。

Componentは相互排他的と数学的に確認できない限り単純加算しない。依存EventはCompeting-risk / State-transition / Joint scenario等で扱い、Double Countingを検査する。

### 偽の精密さを禁止

Calibrationが確立していないPermanent-loss componentを、実運用時のSizingで`1.7%`などの細かい単一点確率として事実のように扱わない。

Calibrationが十分でない場合は：

- Probability interval
- Scenario range
- Evidence grade
- Conservative gate

を使う。

十分なOutcome definition、Base rate、Calibrationが成立した範囲だけ確率値を実運用の正式判定へ使用する。

各MetricにはDefinition / Horizon / Confidence level / Estimation method / Data window / Limit / Warning thresholdを持たせる。

## Constraint Classes

### A. Structural Hard Constraints

直接判定でき、違反時は安全側で停止する制約。

例：運用方針上の適格性、Long-only、Leverage、決定論的Single-name / Sector / Country cap、Trading permission、観測済みParticipation ceiling、Required Data / Evidence gate、Stale portfolio state時の新規注文禁止、Duplicate-order protection。

違反PortfolioはOptimization前に除外する。

### B. Model-Estimated Risk Constraints

将来分布やModel推定に依存する確率的制約。

例：Modeled Drawdown、CVaR / ES、Severe-loss probability、Permanent-loss probability / calibrated range、Recovery-duration risk、Estimated factor dependency。

将来損失を保証するものではないため`MODEL-ESTIMATED RISK`と表示する。

### C. Hybrid Constraints

観測値と推定値の両方で決まる制約。

例：Liquidity / Capacity、Market impact、Days-to-liquidate、Factor-cluster exposure。

観測可能なHard componentは安全側で停止し、Estimated componentは下記のロバスト判定を使う。

### D. Stress Scenario Constraints / Diagnostics

Historical crisis、Severe recession、Multiple compression、Credit / Liquidity shock、Correlation spike、Hypothetical OOD等の`S_stress`。

これらを`U_objective`へ自動で混ぜない。Scenario definition / Severity / Limit / Binding-vs-Diagnosticの扱いをVersion管理する。

## 実運用時の標準リスク判定

Distributionを持つModel-Estimated / Hybrid Riskは、可能な範囲で単純なPoint estimate + Arbitrary bufferではなく、承認済み`U_risk`に対するロバストな確率・分位点制約を標準とする。

`sup_{P ∈ U_risk} P_P(RiskMetric > Limit) <= approved ε`

または

`sup_{P ∈ U_risk} Q_{1-α}^{P}(RiskMetric) <= Limit`

Drawdown / CVaR / Permanent-loss / Recovery duration等の`ε / α / horizon / U_risk version`は実運用開始前に定義・Calibrationし、推測で固定しない。

`Estimated Risk + Buffer <= Limit`形式を使う場合は、`U_risk`によるロバスト制約の近似・代替としてCalibration根拠を持つか、独立したUncertainty sourceであることをLedgerへ記録する。

同じError sourceを`U_risk`とBufferで二重計上しない。

推定不能・不安定ならPASS扱いせず`NOT VERIFIED` / `UNSTABLE MODEL` / `REVIEW_REQUIRED`。

StressをBinding constraintとして承認した場合は、例えば：

`StressMetric(w,s) <= approved stress limit_s`

を`S_stress`上で検査する。Stress結果は確率保証ではないことを明示する。

## Portfolio Joint Risk Violation Budget

複数のRisk Constraintを個別にPASSしても、ポートフォリオ全体で重大制約違反が起こる確率が十分低いとは限らない。

実運用では可能な範囲で：

`sup_{P ∈ U_risk} P_P(any approved material risk constraint violated) <= approved ε_portfolio`

または同等のJoint exceedance定義を持つ。

Drawdown / CVaR / Permanent-loss / Recovery / Liquidity等の依存関係はJoint simulation / State-regime model / Conservative boundで評価する。

Joint event setはHorizon / Scenario / Event definitionを事前にそろえる。異なるHorizonや意味のRiskを無条件に一つのUnion eventへまとめ、単一`ε_portfolio`で精密に管理できると仮定しない。

Individual `ε_i`はPortfolio Risk Budgetと整合させる。強く依存するRiskを独立として単純加算しない。

Joint distributionの信頼性が低い場合は保守的BoundとLimitationを表示し、便宜的に全制約を一律`5%`等へ設定しただけで、Portfolio joint riskを「検証済み」と表現しない。

## Risk Capacity / Risk Tolerance / Life-Cycle Adaptation

個人向けRisk Budgetは年齢だけで決めない。

少なくとも次を分離評価する。

- **Risk Capacity**：Investment horizon / Near-term liquidity need / Emergency reserve outside portfolio / Expected contributions-withdrawals / Income stability / Liabilities / Known cash needs / Loss absorption capacity
- **Risk Tolerance**：Temporary drawdown / Time-under-water / Concentration / Action churnへの心理的・行動的耐性
- **Mandate Ceiling**：承認済みStructural / Model-Estimated / Hybrid limits

個人向けRisk Budgetは、Risk Capacity / Risk Tolerance / Mandate Ceilingの**制約集合の共通部分**として決める。

`Approved Risk Envelope = Capacity Constraints ∩ Tolerance Constraints ∩ Mandate Ceiling`

同じMetric・同じHorizon・同じ定義へ変換できる上限についてだけ、概念的に最も厳しい値を採用する。異なる次元のRiskを一つのScalarへ潰して`min(...)`を計算しない。

年齢や「若いから」だけを理由にGrowth presetを自動選択しない。

長期・高Capacity / Toleranceの投資家では、Growth獲得のためTemporary Drawdown / Volatility / Recovery duration / Moderate concentrationの上限を広げることはできる。

一方、Permanent Loss、Fraud / Accounting / Governance、Data Integrity、Evidence quality、Liquidity safety、Model uncertainty、PIT、OOS、Shadow、Fail-closed基準は、Growth profileを理由に機械的に緩和しない。

Risk Limitは**使い切る目標ではなく上限**。Optimizerは追加RiskがRobust Expected Log-Wealth Growthを改善しない限り、上限までRiskを取らない。

Risk Capacity / Tolerance assessmentはVersion / as-of / inputs / limiting factor / rationaleを保存する。個人向け実運用へRisk Budgetを反映する前にユーザー明示承認を必須とする。

## 仮Risk Budget — UI編集可

初期状態では研究・シミュレーション用の**仮Risk Budget**を自動作成し、UIから編集可能とする。

状態は`PROVISIONAL / RISK BUDGET NOT APPROVED`であり、ユーザー固有の最適値を意味しない。

### Research Preset共通ルール

以下は`BALANCED_RESEARCH_V1` / `GROWTH_RESEARCH_V1`共通。

- Approved broad diversified passive benchmark：`0–100%`
- Passive benchmark 100%は標準Comparator / Exposure-semantics referenceとして評価可能に保つが、個別Risk Budgetの全制約を常に満たすことまでは要求しない
- Min liquidity：Security-specific rule必須
- Max days-to-liquidate：Normal conditionで原則`5 trading days`
- Max participation rate：原則`10% of ADV`
- Max turnover / implementation cost：Strategyに応じてCalibration。0固定禁止
- Cash：`0–100%`
- Risk-free proxy：承認済みなら`0–100%`
- Leverage：`0%`
- Data / Evidence / Model confidence、PIT / OOS / Shadow、Fraud / Accounting / Governance等のGateはGrowth presetでも緩和しない
- 未較正のCVaR / Severe-loss / Permanent-loss / Joint-risk等を実運用上限として推測固定しない

### `BALANCED_RESEARCH_V1`

- Investment Horizon：`7 years`
- Max single-name equity：`10%`
- Max sector / industry：`30%` 研究用参考値。実運用ではAbsoluteかBenchmark-relativeかを明示
- Max factor-correlated cluster：`35%`。実運用ではHybrid / robust model-estimated判定が必要
- Max modeled drawdown reference：`25%`。実運用では確率・分位点の基準をCalibration
- Max stress drawdown reference：`35%`。実運用では`S_stress`のScenario / Limit定義が必要
- Max acceptable recovery duration：`36 months`
- Portfolio CVaR：実運用開始前にCalibration
- Severe-loss probability：実運用開始前にCalibration
- Permanent-loss exposure：実運用開始前にProbability / Range定義をCalibration
- Portfolio joint material-risk violation probability：`ε_portfolio`等を実運用開始前にCalibration

### `GROWTH_RESEARCH_V1`

対象：長期投資が可能で、十分なRisk CapacityとRisk Toleranceを持つ投資家。年齢だけで選択しない。

- Investment Horizon：`7–10+ years`
- Max single-name equity：`12.5%`研究上限。`15%`は別途正当化・承認した場合のみ
- Max sector / industry：`35%`研究用参考値
- Max factor-correlated cluster：`40%`
- Max modeled drawdown reference：`30%`
- Max stress drawdown reference：`45%`
- Max acceptable recovery duration：`48 months`
- Portfolio CVaR / Severe-loss / Permanent-loss / Joint material-risk budget：実運用開始前にCalibration

`GROWTH_RESEARCH_V1`はTemporary Drawdown / Recovery / Moderate concentrationの許容幅を広げる研究Presetであり、Permanent Loss toleranceやData / Model governanceを弱めるPresetではない。

ETF / Fundは可能な範囲でLook-through exposureを使い、Direct holdingとの重複をSecurity / Sector / Country / Factor concentrationへ反映する。

Direct securityのPosition capと、Fund内部のLook-through economic exposure capは別Constraintとして定義する。Fundの内部構成銘柄へDirect single-name capを機械的にそのまま適用しない。必要ならLook-through capまたはBenchmark-relative concentration ruleを別途承認する。

Approved passive benchmarkは常にComparatorとして評価可能に保つ。個人向けRisk Budgetにより100% Benchmark allocationがDrawdown等で不適格になること自体は矛盾ではない。Benchmarkの自然構成だけを理由にFund positionを誤ってStructural Hard breach扱いする場合は`RISK BUDGET INCONSISTENT`またはConstraint semanticsを修正する。

Look-through不能が重要なら`DATA_LIMITATION`または保守的制約を適用する。

未数値項目を実装時に推測で固定しない。Calibration / Validationで候補を作成しUIへ提示する。

## Risk Budget整合性確認

Risk Budget保存・実運用反映前に、運用方針 / Horizon / 各Limit間の内部整合性とFeasible setの存在を検査する。

Passive benchmark / Cash / Single-name cap / Look-through / `U_risk` / `S_stress`の扱いを確認し、**少なくとも一つの承認済みBaseline allocation**、原則Cash / Risk-free / Passive+Cash等、がFeasibleであることを確認する。

Passive benchmarkはComparatorとして常に評価可能に保つが、100% allocationが個別Risk BudgetでFeasibleであることを必須条件にはしない。

矛盾、実質的な達成不能、Solver上Feasible setなしの場合は`RISK BUDGET INCONSISTENT`。

研究段階ではImpact / Sensitivityを提示し修正候補を作れるが、矛盾したRisk Budgetを`APPROVED`または`PRODUCTION READY`にしない。

## UI最低要件

- Current Risk Budget Profile / Version / Status
- 全Limitの表示・編集
- `STRUCTURAL HARD / MODEL-ESTIMATED RISK / HYBRID / STRESS`分類
- Chance / Quantile constraintのLimit / Horizon / ε or α / `U_risk` version
- Bufferを使う場合は、その意味と`U_risk`との重複有無
- `S_stress` version / Scenario / Binding-vs-Diagnostic
- Portfolio Joint Risk Violation Budget / Dependency treatment
- Defensive / Balanced / Growth等の研究Preset
- 個人向けではRisk Capacity / Risk Toleranceを別表示
- Limiting factor / Input根拠 / 推奨Preset
- 変更前後差分と想定Impact
- 制約強化によるRobust GrowthのOpportunity Cost
- Validation status
- `SAVE AS PROVISIONAL`
- `REQUEST / CONFIRM PRODUCTION ACTIVATION`

研究・シミュレーションではUI変更を即時反映してよい。

**個人向け実運用へ変更したRisk Budgetを反映する直前に、ユーザーの明示確認を必須とする。**

重要変更では主要Limit変更時のRobust / Expected CAGR、Stress Drawdown、CVaR、Permanent-loss、Joint breach probability、Cash、Concentrationへの影響を表示する。可能ならBinding constraintとShadow priceも表示する。

過度な保守化によるUnder-investmentも診断し、`DEFENSIVE OPPORTUNITY COST`として現Risk Budgetと合理的な隣接BudgetのRobust Growth差、追加Risk、Binding constraintを表示する。

これはRisk Limitを使い切る指示ではない。

承認時は`DECISIONS.md`へ次を保存する。

`risk_budget_version / effective_as_of / investment_horizon / risk_capacity_assessment / risk_tolerance_assessment / limiting_factor / limits+warnings / U_risk+chance-quantile semantics / S_stress version+semantics / rationale / approved_by / validation_status`

未承認=`RISK BUDGET NOT APPROVED`。研究・シミュレーションは可能だが`Personalized Optimal / PRODUCTION READY`と表現しない。

## Path-wise Drawdown

可能な範囲でPath-wise wealth simulation / Scenario pathにより：

- Drawdown distribution
- `U_risk`下のRobust `P(Drawdown > Limit)` / Drawdown quantile
- `S_stress`下のStress Drawdown
- Time-under-water / Recovery duration
- Robust `P(Recovery duration > Limit)`

を評価する。

Path model自体の不確実性・Regime dependenceを明示し、実運用時のConstraintは承認済み`U_risk`判定と`S_stress` ruleへ整合させる。

---

# 9. ロバスト・ポートフォリオ構築

Required inputs：

Return distribution / Dependency model / Concentration / CVaR / Permanent loss / Liquidity-Capacity / Cost / Turnover / Tax where relevant / Confidence / Estimation uncertainty / Approved passive benchmark / Cash / Risk-free proxy / Approved `U_objective` / Approved `U_risk` / Approved `S_stress`

Objective：**§8のRisk / Implementation feasibilityを満たす集合の中でRobust Expected Annualized Log-Wealth Growthを最大化する。**

## 標準ロバスト最適化

実運用での標準形：

`w* = argmax_{w ∈ F} min_{P ∈ U_objective} (1/T) E_P[log(W_T(w)/W_0)]`

- `F`：Structural Hard Constraintおよび§8のRisk Constraint、必要な`S_stress` Binding ruleを満たすFeasible set
- `U_objective`：現実的に起こり得る不確実性集合。原則としてPredictive / Forecast residual uncertainty、Parameter / Model disagreement、Plausible regime mixture、Covariance / Dependency uncertaintyを含む
- Historical / Hypothetical extreme / OOD Stressを`U_objective`へ無条件に入れない
- `S_stress`：Historical crisis / Severe hypothetical / OOD等のStress set。Objectiveの`min P`から分離し、Risk constraint / Sensitivity / Diagnosticsへ使う
- Mandate / Data / Evidence / Survivalのうち直接拒否可能な重大Failureは`U_objective`へ曖昧に押し込まずHard gateへ置く
- `U_objective`のRadius / WeightsはForecast OOS error distribution / Coverage / Calibration / Disagreement / Regime-dependency evidenceから決める
- Portfolio Backtest CAGR / Sharpe / Utilityを良く見せるために`U_objective`を調整しない
- `U_objective` / `U_risk` / `S_stress` / Shrinkage / Decision Margin / Sizing間のUncertainty重複は§7 Ledgerで確認
- Cost / Slippage / Taxは必要に応じて`W_T(w)`へ一度だけ反映
- `U_objective`構成、Scenario weight、Solver tolerance、Failure behaviorはVersion管理し、実装者判断で勝手に変更しない
- 数値不安定、Solver failure、Constraint tolerance超過時は安全側で停止し、`UNSTABLE PORTFOLIO`または`NOT VERIFIED`

Robust solutionでは可能な範囲で以下を分解保存する。

- Posterior / Base expected growth
- Robust worst-plausible growth
- Ambiguity / Model effect
- Risk-constraint effect
- Implementation-cost effect
- Resulting Cash / Passive weight

Cash / Passive偏重が主として広い`U_objective`、Model disagreement、Dependency uncertaintyにより生じる場合は`AMBIGUITY-DOMINATED SOLUTION`を表示する。

「AssetのRisk / Returnが悪い」と「Modelが十分に識別できない」を区別する。

これはCashを禁止するStatusではなく、Uncertainty calibration / Double Counting / Sensitivity reviewのTriggerである。

上式はLong-horizon Objectiveの標準的な静的表現とする。

Daily refresh / Rebalance / Material eventでは、承認済みTrading rule、Cost、Hysteresisの下でSequential / Receding-horizon re-optimizationとして運用する。

Taxが重要な個人向けPortfolioでは、Current tax lots / Realized gains-losses / Account stateをOptimization stateへ含める。静的な一律Tax haircutだけでPath-dependent tax costを処理したことにしない。

検証済みDynamic Policyを別途承認しない限り、短期Signal最大化へObjectiveを置換しない。

## 標準実装方法

1. Expected-return shrinkage toward defensible prior / base rate
2. Posterior / Predictive return distribution
3. `U_objective`向けPlausible regime mixture
4. Dependency / Covariance shrinkage + State / Regime dependency
5. Parameter perturbation / Resampling sensitivity
6. `U_risk`を使った§8 Risk constraints
7. 分離した`S_stress` tests / constraints
8. Position / Concentration / Capacity caps
9. 独立した根拠がある場合のみFractional sizing

Fractional sizingを「念のため」の追加保守化として無条件適用しない。

Log utility / Shrinkage / `U_objective` / `U_risk` / Decision Marginですでに反映済みのUncertaintyをさらにSizingで縮小する場合は、独立根拠・依存・総影響を§7 Ledgerへ記録する。

Raw return point estimateから極端なWeightを作らない。

原則禁止：Unconstrained MVO / Full Kelly / Unbounded leverage。

銘柄採用は可能な範囲でMarginal robust utility / Incremental CVaR / Permanent-loss / Diversification / Cost / Factor concentration / Liquidity burden / Capacityで評価する。

## 標準価値関数とランキング

`U*(A)` = Candidate / Asset set `A`を許容した状態で、**同一のCurrent portfolio state / External cash-flow assumption / Mandate / Risk Budget / Cost / Tax / Data timestamp / Uncertainty定義**の下、§9 Optimizerが得る最適Robust Utility value。

Primary Rankingは単体Expected ReturnやComposite Scoreではなく、候補の存在がポートフォリオ全体の最適Robust Utilityをどれだけ改善するかで評価する。

`OpportunityValue_i = U*(candidate i allowed) - U*(candidate i excluded)`

同一条件で`allowed`が`excluded`のStrict supersetなら、理論上`OpportunityValue_i >= 0`。重要な負値はSolver / Constraint / State mismatch / Numerical errorを疑い`NOT VERIFIED`とする。

この`OpportunityValue_i`を§2 / §7の追加Risk判断と共通の標準概念とする。

計算量上必要な場合のみApproved increment / Marginal utility / Shadow price / Leave-one-in / outを近似として使い、Increment依存性をSensitivity確認する。

Modes：
- **Generic Discovery Mode**：Approved Reference Portfolio、原則Passive Market + Cash / Risk-free、を基準とし`DISCOVERY RANK`
- **Personalized Portfolio Mode**：Actual current holdings / Tax-cost contextを基準とし`PERSONALIZED PORTFOLIO OPPORTUNITY RANK`

Personalized Modeで既存保有銘柄を`excluded`にすると強制売却Tax / Costが混ざるため、「新規追加機会」と「既存保有の保持価値」を混同しない。
- 未保有候補：原則`candidate allowed vs excluded`
- 既存保有：`trade allowed vs current position frozen`等、売却強制を避けた別のIncremental decision comparisonを使い、必要なら`RETENTION VALUE`として別表示する

両Modeを混同しない。

Structural Hard Constraintまたは§8 Risk Constraint違反候補は採用対象外。

UIでは`Expected Return Rank` / `Fundamental Conviction Rank`等を補助表示してよいが、Primary Investment Rankと混同しない。

Ranking上位でもAction / WeightはTrading ruleとMinimum Trade Thresholdで別判定する。

## Risk Contribution Output

重要Portfolioでは最低限：

- Position weight
- Marginal Contribution to Risk
- Marginal Contribution to CVaR
- Marginal Contribution to Modeled / Stress drawdown where feasible
- Factor / Cluster contribution including look-through where applicable
- Liquidity / Capacity consumption

を表示・保存する。

Perturbation / ScenarioでWeightが不安定なら`UNSTABLE PORTFOLIO`。

まず原因がData / Model / `U` / Constraint / Tolerance / Double Countingのどこにあるか診断し、必要な場合だけSimpler allocation / Conservative sizing / Reviewを行う。

Cash増加を自動的な唯一の解としない。

---

# 10. 効用感応度と判断安定性

Primary Objectiveは§9のRobust log-wealth utilityを維持する。

重要Sizing / Portfolio decisionではUtility Sensitivity Testを行う。

可能な範囲で比較：
- Log utility
- CRRA `γ = 2`
- CRRA `γ = 3`
- CRRA `γ = 5`
- Justified approved alternative

目的はObjectiveを都合よく変更することではなく、Risk-aversion仮定に対するWeight / Action安定性を確認すること。

合理的なUtility仮定変更でWeight / Actionが大きく変わる場合：`UTILITY SENSITIVE`。

まず既存`U_objective` / `U_risk` / Decision Marginへ当該Uncertaintyがすでに反映されているか確認する。

同じ根拠でMargin拡大、Cash増加、Fractional sizingを自動で重ねない。

必要に応じてSimpler allocation / Independently justified conservative sizing / `REVIEW_REQUIRED`。

実運用でPrimary Utilityを変更する場合は重要なObjective変更として扱う。

---

# 11. 売買判断の定義

正式Actions：

`BUY / ACCUMULATE / HOLD / TRIM / SELL / AVOID / PASSIVE_MARKET / HOLD_CASH / INCREASE_CASH / REDUCE_RISK / NO_TRADE / REVIEW_REQUIRED`

- `BUY / ACCUMULATE / HOLD / TRIM / SELL / AVOID`：主に個別Security / Fund position
- `PASSIVE_MARKET`：承認済みBroad passive benchmarkへの配分・増額
- `HOLD_CASH / INCREASE_CASH / REDUCE_RISK`：Portfolio-level defensive allocation
- `NO_TRADE`：現在状態から重要な取引価値なし
- `REVIEW_REQUIRED`：判定に必要な検証・Data・承認が不足

判断基準は`Forward Return Distribution + Incremental Portfolio Robust Utility`。過去価格だけを根拠にしない。

## BUY / ACCUMULATE条件

1. Required / Fresh / PIT / Tradability / Integrity Dataが揃い、Evidence Firewallを通過
2. 個別株ではBusiness / Moat / Growth / Accounting / Governance / Survival thesisが成立。Fund / Passive / Risk-free proxyではIndex methodology / Tracking / Fees / Liquidity / Counterparty-Credit / Duration等、Asset typeに適用可能なDue diligenceを実施
3. 適用可能なValuation / Yield / Duration / Tracking cost等がForecast / Wealth distributionへ十分反映されている
4. Separate Margin-of-Safety hard gateを使う場合は明示承認し、同じValuation uncertaintyを二重控除しない
5. §7の標準投資判断基準を通過
6. §8の全Applicable ConstraintとRequired confidence / Evidence gateを通過
7. §13のCost / Liquidity / Capacity / Execution feasibilityを満たす
8. 実運用向け表示の場合は該当する§18 Production gateを満たす

Standalone Expected Return superiorityは必須ではない。

DiversificationやTail Risk低減によりPortfolio-level Robust Utilityを重要に改善する候補もBUY対象になり得る。

Daily batch / Scheduled rebalance / Material eventで再評価する。

`Daily Refresh ≠ Daily Trading`

Entry / ExitにはHysteresis + Minimum Trade Thresholdを持たせる。ThresholdはCost / Uncertaintyを二重控除しないよう§7 / §13と整合させる。

`Minimum Trade Threshold`はChurn抑制・Discrete execution・残差推定誤差等のうち、After-cost wealthや`Residual Decision Uncertainty Margin`へ未反映の独立要因だけを表す。同じCommission / Slippage / TaxをThresholdへ再加算しない。独立根拠がない追加Thresholdは0とする。

Approved Structural / Binding Risk Constraint違反を解消するためのRisk reductionは、通常のNo-trade Hysteresisを理由に先送りしない。Cost / Taxは執行方法の最適化へ反映するが、承認済みConstraint違反を正当化する理由にはしない。

HOLD / TRIM / SELLはThesis、Forward Return、Portfolio marginal utility、Risk Budget、Cost / Tax、Confidenceで決定する。

株価下落、含み損、株価上昇、一定利益、目標価格到達だけを理由に機械的SELLしない。

## Recommendation最低項目

Security / Internal ID / Ticker where applicable / Action / Mode(Generic-Personalized) / Timing / Current+Target Weight / As-of + Decision / Tradable timestamp / Expected+Median CAGR or applicable yield metric / Robust utility impact / Economic Return Bridge summary where applicable / Downside-CVaR-Permanent-loss / Stress+Joint Risk impact / Confidence dimensions / Edge Evidence status / Ambiguity status where material / Reason / Entry+Exit Trigger / Max acceptable entry price where reliable / Next Review / Expected Cost / Portfolio & Risk-Budget impact

Asset typeに適用しない項目は`Not Applicable`と明示し、Missingと混同しない。

---

# 12. Astra補正の統制

出力を分離する。

`BASE MODEL OUTPUT → ASTRA OVERLAY → FINAL OUTPUT`

重要Overrideでは以下を記録する。

Original output / Adjustment / Reason / Evidence / Position-Action / Size / Expected-Risk impact / Confidence / Expiry-Review trigger

原則`SOL INDEPENDENT REVIEW REQUIRED`。

禁止：
- 根拠のないNarrative Override
- Backtest改善目的のOverride
- Base Model outputの隠蔽
- 履歴を残さないOverride

OverlayはIncremental return-risk / Calibration / Drawdown impact / Hit rateで検証し、継続Valueがない場合は縮小・廃止する。

OverlayはStructural Hard / `U_risk` / Approved binding `S_stress` / PIT / Tradability / Evidence / Production gateを迂回してはならない。Overlay適用後にFeasibility、Cost / Tax、Constraintを再計算する。投資判断の意味や数式を重要な水準で変えるOverrideは`DESIGN CHANGE REQUIRED`としてDecision Freezeをやり直す。

Overlayの採用・閾値・係数をLocked Final OOSの結果に合わせて調整しない。Overlayも§14のValidation isolationとResearch Trial provenanceに従う。

---

# 13. リバランス・コスト・流動性・執行容量・税金

Trade候補：

- 重要なAction change
- Rebalance-band breach
- `ΔRobustUtility`がApproved Minimum Trade Thresholdを超える
- Risk breach
- Critical thesis event

Implementation Cost：

Commission / Fees / Spread / Slippage / Market impact / Delay / FX

## 標準コスト処理

Cost / Slippage / Taxを考慮する場合はPortfolio wealth transition `W_t → W_{t+1}`へ**一度だけ**反映する。

§2 / §7 Decision Hurdle、§9 Ranking、§11 Actionで同じCostを追加Penaltyとして再度差し引かない。

`Net Expected Return = Gross Expected Return - Expected Implementation Cost`

は診断表示に使ってよいが、正式なPortfolio decisionはAfter-cost wealthに基づく`ΔRobustUtility`を使う。

## Capacity

Sizingと執行可能性を整合させる。

- ADV
- Proposed participation rate
- Days-to-enter / exit
- Spread / Market impact
- Stress liquidity
- Portfolio size sensitivity

Capacity超過でBacktest Alphaが実運用不能なら`CAPACITY LIMITED`または`NOT PRODUCTION READY`。

Generic RankingはPre-taxでもよい。

個人向けポートフォリオでは利用可能ならAccount type / Realized gains-losses / Tax cost-lot / After-tax wealthを考慮する。

## Execution Safety

実際の注文発注は§4の`USER_CONFIRMATION_REQUIRED`を必ず満たす。

注文機能を実装する場合は最低限：
- Order preview：Security ID / Side / Quantity / Order type / Price limit / Estimated cost / Resulting weight / Risk impact
- Idempotency key等によるDuplicate order防止
- Broker position / Cash / Open orders / Partial fillのReconciliation
- Stale portfolio state / Stale quote / Market halt / Clock skew / API uncertainty時のFail Closed
- Partial fill / Reject / Cancel後にPortfolio stateを更新し、残注文を再最適化または再確認
- Lot / Rounding後のStructural / Risk / Capacity再検証
- Kill switch / Trading permission separation / 最小権限
- 実際のExecution resultをModel recommendationと分離して監査可能に保存

Modelが推奨したTarget Weightと、実際に約定したPositionを同一視しない。

---

# 14. バックテスト・OOS・ストレス・模擬運用

## Integrity audit

Look-ahead / Survivorship / Selection bias / Data leakage / PIT / Tradability timestamp / Security-master lineage / Delisted / Restated / Corporate actions / Overfitting / Parameter mining / Multiple testing / Researcher degrees of freedom / Double counting / Outliers / Calibration uncertainty / Turnover / Cost / Liquidity / Market impact / Capacity

Stages：

`Development → Validation → Locked Strict Final OOS → Forward / Shadow-Paper`

## Validation isolation

Feature / Model choice、Shrinkage、`U_objective` Radius / Weights、`U_risk`定義、Buffer代替表現、Risk threshold、Decision Margin、Solver / Hyperparameter等のCalibrationはLocked Final OOSを見る前に固定する。

Final OOSを見てModel / Feature / Parameter / Threshold / Objective / Universe / Risk rule / Uncertainty treatmentを変更した場合、その期間はFinal OOSではない。

Time-seriesはRolling / Walk-forward。

多数比較では必要に応じNested Walk-Forward / CSCV-PBO / Deflated Sharpe / Multiple-testing correction。

## Stress `S_stress`

Historical crisis / Recession / Rates-Inflation-Credit-Liquidity shock / Multiple compression / Growth disappointment / Sector shock / Correlation spike / FX / Hypothetical OOD。

`S_stress`を`U_objective`へ無条件に混ぜず、Approved Binding / Diagnostic定義で評価する。

## Benchmarks

Cash / Risk-free / Approved broad diversified passive market benchmark / Relevant market-cap / Simple diversified / Simple factor-aware where relevant

主要Benchmarkと評価方法はFinal OOSを見る前に定義する。結果を見た後に都合のよいBenchmarkへ差し替える場合は重要Research decisionとして記録し、比較の独立性を失った期間をFinal OOS扱いしない。

## 比較指標

Total Return / CAGR / Robust utility where available / Volatility / Max Drawdown + Duration / CVaR / Permanent-loss proxy / Risk-adjusted return / Turnover / Net return / Calibration / Regime stability / Capacity

Complex ModelはSimple BaselineをNet performance / Risk / Calibration / Robustness / Sensitivityで重要に改善する場合だけ採用する。採用基準はLocked Final OOSを見る前に定義する。Final OOSはPass / Fail判定に使えるが、結果を見てModel選択・Feature・Thresholdを変更した場合は新しいLocked OOSが必要。

## Forecast Edge Persistence Gate

OOS / Shadow / 実運用では、単なるPortfolio P&LだけでなくForecast自体の有効性を継続評価する。

- Rank IC / Monotonicity
- Forecast bucket vs Realized return
- Top-bottom spread
- Realized vs Predicted CAGR
- Interval / Downside / Tail calibration
- Sector / Horizon / Regime persistence
- Turnover-adjusted edge
- Edge after cost / capacity

Forecast edgeはFinal OOS前に定義したAcceptance criteriaで評価する。重要な水準で消失・逆転・過信化した場合：

`MODEL REGIME REVIEW REQUIRED`

新規Riskを抑制しModel再検証を行う。Cash増加や既存Position縮小はRisk / Utility impactに基づいて判断し、自動反応にしない。

## Shadow / Paper Gate

Locked OOS後、原則としてShadow / Paperを通過するまで`PRODUCTION READY`としてはならない。

実運用と同じData / Feature / Decision path、Timestamp / Tradability、Forecast stability / Calibration、Execution realism、Constraint violations、Sizing stability、Action churn、Data outage、Regime / Factor / Dependency driftを監視する。

最低期間 / Observation数 / Event coverageは事前定義する。

重要変更後は影響範囲に応じValidation → Locked OOS → Shadowを再実施する。

短期Shadow / Paperは運用経路・安定性・実装現実性の検証であり、7Y等の長期Forecast outcome / Calibrationを完全検証したことを意味しない。

長期Edgeの未観測部分は`LONG-HORIZON VALIDATION LIMITATION`として残し、短期Shadow成績で代用しない。

未通過=`SHADOW VALIDATION NOT PASSED`。

---

# 15. 独立検証・監視・セーフモード

重要Modelを別視点から次まで検証する。

Conceptual Soundness / Data lineage / Evidence / PIT-Tradability / Missing-Stale / Design=Code / Numerical accuracy / Edge cases / Reproducibility / OOS / Calibration / `U_objective`-`U_risk`-`S_stress` separation / Regime / Tail behavior / Turnover-Cost-Capacity realism / Perturbation / Model disagreement / Optimizer stability / Trial count / Final OOS integrity / Limitations

## 実運用中の監視

Performance / Calibration / Forecast error / Forecast edge persistence / Economic-vs-Statistical return bridge disagreement / Data quality / Model disagreement / Regime / Portfolio risk / Joint breach probability / Ambiguity dominance / Overlay effectiveness / Capacity / Tradability-latency drift

## Model更新・昇格

実運用中のModel / Feature / Threshold / `U_objective` / `U_risk` / Overlayを自動学習・再学習で無審査に置き換えない。

- 更新候補はVersionを分離し、ChallengerとしてValidation / 必要なLocked OOS / Shadowを実施する。
- 事前承認したOnline-update policyがない限り、Production modelへ自動昇格しない。
- 自動更新方針自体が投資判断を重要な水準で変える場合はMaterial designとしてReview / Decision Freeze対象。
- Model promotion / rollback履歴をDecision / Model auditへ残す。

## Regime Review trigger

Calibration急落 / Forecast edge消失 / Major data shift / Abnormal volatility-liquidity / Correlation spike / Model disagreement急拡大 / Market structure-Regulation-Accounting change / Broad Risk Budget breach

## Safe Mode

Confidence低下・Data / Model / Broker / Reconciliation異常時は新規Riskを抑制し、不要Turnoverを避け、必要なRisk reductionを優先する。Portfolio state自体を信頼できない場合は新規注文をFail Closedする。

Position cap縮小 / Conservative forecast / Cash増加等は、既存Uncertaintyの二重Penaltyにならないか確認し、Utility / Risk impactに基づいて選択する。

自動全面売却は禁止。

解除条件：Data verification + Fix + Re-validation + Astra approval。重大時はSol reviewも必要。

---

# 16. 実装・テスト・完了条件

Terraは承認済みObjective / Formula / Risk Budget / 投資判断 / Data definitionを変更しない。

変更が必要なら`DESIGN CHANGE REQUIRED`。

標準実装フロー：

`Understand → Evidence → Requirement/Root Cause → Impact Scope → Minimal Correct Implementation → Tests → Regression → Handoff`

禁止：
- 根拠のない仕様変更
- Dummyで完成扱い
- TODO隠蔽
- Error握り潰し
- 安易な`any`
- Test削除でPASS
- Missing=0
- API Failureを正常扱い
- UIだけ完成
- 無関係な大Refactor
- Secret保存
- Cost=0固定
- Cost二重控除
- Look-ahead
- Tradability違反
- Ticker-only identity事故
- Ranking=Action
- Unsupported inference=FACT
- EvidenceなしWeight変更
- `U_objective`への無承認Stress混入
- 同一Uncertaintyの無自覚なDouble Counting

Riskに応じてBuild / Type / Lint / Unit / Integration / Batch / API / DB / Data Quality / Numerical / Portfolio Constraint / Buy-Sell Transition / Backtest / OOS / Regressionを実施する。

重要な実運用経路では、Dependency / Environment / Model / Solver versionを固定・記録し、再現可能なBuild / Runを確保する。Clock / Time zone / Random seed / Numerical tolerance等、結果へ影響する実行条件もVersion管理する。

個人の保有資産・税務・口座情報・取引履歴は機微情報として扱い、Repo / Prompt / Logへ必要以上に保存しない。保存が必要な場合はAccess control / Encryption / Redaction / Retention policyを適用し、Credentialを平文保存しない。

未実施=`NOT VERIFIED`。

## Policy-as-Code / Fail-Closed Gate

重要RuleはPrompt依存にせずCode / Testsで強制する。

最低限：
- Unapproved / `RISK BUDGET INCONSISTENT` Risk Budget → 個人向け実運用のAction / Weight出力を拒否
- PIT / Tradability failure、Required confidence未達、Structural Hard breach、Invalid robust chance-quantile定義、Approved Stress binding breach、Shadow未通過、Invalidated Locked OOS → 該当する実運用向け出力を拒否
- Missing→0、Unsupported inference→Weight / Action、Leverage>Mandate、Solver failure / Constraint violation、Unapproved constraint class、重要ETF look-through omission、Permanent-loss component単純加算、Uncalibrated precise permanent-loss probabilityの実運用利用を拒否
- CostはWealth pathへ一度だけ反映し、Decision Hurdle / Ranking / Actionで二重控除されていないことをTest
- `U_objective` / `U_risk` / `S_stress`のVersion・役割分離とUncertainty Ledger整合性をTest
- Weight sum / Non-negative weight / No hidden leverage / Rounding後Constraint / Execution reconciliation / Duplicate-order protectionをTest
- Sensitive financial data / Secretが無承認で外部送信・Repo保存されないGateをTest
- §18 `PRODUCTION READY`は全条件AND判定。判定不能はPASS扱いしない

Completion report：

Changed / Why / Evidence / Tests / Results / Validation Status / Remaining Issues / Model Limitations / Design Deviations (`NONE`含む)

## 実運用Decision Audit

実運用向けの重要Recommendation / Portfolio Actionは、Repo内の研究メモとは別に監査可能なDecision recordを残す。

最低限：
`decision_id / timestamp / portfolio_state_id / data_snapshot+hash / policy_hash / decision_version / risk_budget_version / model+solver version / input assumptions / output action+target / constraints+statuses / expected cost / user approval where required / execution result reference`

- Append-onlyまたは改ざん検知可能な方式を優先する。
- 個人の機微情報そのものをGitへ保存しない。必要ならRuntime DB等のAccess-controlled storeへ保存し、Repo側には非機微なID / Hashだけを残す。
- RecommendationとExecution resultを区別する。

---

# 17. 初期化・引き継ぎ・正式な情報源・安全管理

不足時は自動作成・修復する。

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

初回のみ、必要十分なTree / README / Dependencies / Source / Config / Tests / Git status+HEAD / Existing AI instructionsを調査する。

空Repoは異常扱いしない。

## 必須内容

- `AGENTS.md`：Mission / Objectives / Mandate / Roles / Delegation / SoT / Architecture / Startup / Coding / Investment-Trading / Testing / Git / Handoff / Prohibitions
- `START_HERE`：Current task / Model effort / Delegation / Branch / Commit / Updated / Next file / Policy filename+hash / Decision version / Risk-budget status
- `HANDOFF`：Task-Why / Completed / In Progress / Next exact step / Required+Changed files / Do NOT Change / Known issues / Tests / Commands / Git / Open questions / Next model-effort / Review / Resume
- `DECISIONS`：Objective / Horizon / Mandate / Risk Budget / Portfolio method / `U_objective` / `U_risk` / `S_stress` / Trading ruleを特定可能なADR
- `FILE_MAP`：Purpose / Symbols / Dependencies
- `TEST_STATUS`：Build / Type / Lint / Unit / Integration / Batch / Data / Model / Portfolio / Backtest / OOS / Known failures
- `RESEARCH_TRIALS.jsonl`：trial id / hypothesis / dataset snapshot+hash / commit / feature+parameter set / risk budget / OOS period / model_name / model_version / prompt_hash where applicable / policy_hash / random_seed / optimizer_version / result / accepted-rejected
- `TODO`：P0 Capital / Data / Critical、P1 Core / Model correctness、P2 Important、P3 Nice-to-have

`RESEARCH_TRIALS.jsonl`は追記専用。既存Recordの変更・削除、失敗Trialの隠蔽禁止。

## Policy Version / Hash Gate

Startup / Resume時に、実際に読み込んだPolicy filename / versionとContent hash、原則SHA-256、を`START_HERE`記録と照合する。

`current_policy_hash != recorded_policy_hash`

なら`POLICY VERSION CHANGED`。

Policyを全文読み直し、影響する`DECISIONS` / Risk Budget / Tests / Pending implementationをReviewしてから作業継続する。

古いContextだけで継続しない。

Policy hashはSecretではない。

Startup：

`Policy+hash → Repo inspection → Bootstrap → AGENTS/.ai → Decisions/Risk/Validation status → Work`

Resume：

`Policy+hash → AGENTS → START_HERE → HANDOFF → TODO → Relevant DECISIONS → Required Files → git status/HEAD → Resume`

毎回Repo全体を読み直さない。

HANDOFF≠Git → `HANDOFF MISMATCH`。

## 正式な情報源の優先順位

本Policy内で矛盾がある場合は、まず本節と§1の最上位Objectiveに照らして解消し、推測で下位実装を優先しない。

1. User latest explicit instruction
2. 本Policy §1 Formal Objective
3. 本Policyの該当Canonical rule
4. Approved Mandate / Risk Budget
5. Approved Material Decisions (`DECISIONS.md`)
6. `AGENTS.md`
7. `.ai/START_HERE.md` / `.ai/HANDOFF.md` — Operational state only
8. Current implementation

`DECISIONS.md`は正式Decisionの情報源であり、HANDOFFより常に上位。

Objective / Mandate / Risk Budget / 投資判断定義の変更は実装前に正式Decisionへ反映する。

Docs≠Repo → `DOCUMENTATION MISMATCH`。

Secret / CredentialをAGENTS / `.ai` / Sourceへ保存禁止。環境変数名のみ可。個人の保有資産・税務・口座情報も原則としてAGENTS / `.ai` / Gitへ保存せず、必要な場合は非機微ID / Hashへ置換する。

---

# 18. 実運用移行条件と最終原則

`PRODUCTION READY`には以下の重要項目をすべて満たすことが必要。

1. Formal Objective / Horizon / Mandate / Base-currency wealth semanticsが確定
2. Numerical Risk Budgetが承認済み。個人向けではRisk Capacity / Tolerance assessmentとLimiting factorを記録し、実運用への反映をユーザーが明示承認。`RISK BUDGET INCONSISTENT`なし
3. Structural Hard / Model-Estimated / Hybrid / Stressの定義が分離され、必要箇所でFail-closed test済み
4. `U_risk` / Risk horizon / Confidence / Robust chance-quantile定義、または明示的なEquivalent buffer定義が確立・検証済み。Double Countingなし。推定Riskを保証として表現しない
5. Evidence Firewall / PIT / Tradability / Security Master / Provider timestamp semanticsが検証済み
6. 未解決の重要`DATA_LIMITATION`なし
7. Forecast calibration + Multi-Horizon validationを事前定義したAcceptance criteriaで評価済み。MaterialなValidation failureなし。長期Outcome不足は`LONG-HORIZON VALIDATION LIMITATION`として明示
8. Economic Return Bridge + Incremental ROIC / Reinvestment整合性 + Hierarchical statistical/economic expected-return decomposition / Alpha shrinkage / Base-currency FX treatmentを文書化・検証済み
9. 重要なEconomic dependency / Scenario coherenceを検証済み
10. Uncertainty Ledgerが最新。`U_objective` / `U_risk` / `S_stress`の役割が明確。重要なDouble Counting未解決なし。Fractional sizing重複なし
11. Forecast Edge Persistenceが事前定義したAcceptance criteria内で、Materialな消失・逆転・過信化なし
12. Canonical Robust Optimizer / `U_objective` construction-calibration / Ambiguity decomposition / Log-wealth domain・ruin handlingを文書化・検証済み。Portfolio Backtest tuningで調整していない
13. Individual + Portfolio joint robust chance-quantile risk定義 / Dependency treatmentを検証済み
14. `S_stress` version / Scenario severity / Binding-vs-Diagnostic定義を検証済み
15. Portfolio Opportunity Rank / Canonical Decision Hurdle / Generic-vs-Personalized mode / Risk Contributions / Utility Sensitivity / Defensive Opportunity CostをTest済み
16. Permanent Loss / Survival ModelのEvent definition、Dependency、Double Counting処理を検証済み。未Calibrationの偽精密確率を重要箇所で遮断
17. Passive benchmark + Cash + Approved Risk-free proxy / `NO_TRADE`が利用可能。Direct cap / Look-through cap / Benchmark-relative semanticsをTest済み
18. Portfolio accounting invariant、Weight sum=100%、No hidden leverage、Rounding / Lot / Partial fill後のConstraint再検証をTest済み
19. Cost / Liquidity / CapacityをModel化。Reference capital scaleを定義。Cost / TaxがWealth pathへ一度だけ反映され、Double Counting test PASS
20. Locked OOSを維持。Calibration isolationを維持。Research Trial Ledgerが最新でModel / Prompt / Data / Policy / Optimizer provenanceを記録
21. 承認済みBinding `S_stress` ruleは全てPASS。Diagnostic stressの弱点はLimitationとして明示
22. Shadow / Paper PASS。Long-horizon validation limitationを明示
23. 必要なBlind Independent Validation PASS。重要DesignではPre-Implementation Review / Decision Freezeを実施
24. Policy-as-Code / Fail-Closed gate Test PASS
25. Action semantics / Sequential re-optimization / Tradability / Execution reconciliation / Duplicate-order behaviorをTest済み
26. 個人向けDataのPrivacy / Access control / External transmission / Secret handlingが検証済み
27. 第三者提供・自動発注等で法務・規制・Data license確認が必要な場合、その確認を完了
28. Model自動更新を使う場合はApproved update / promotion / rollback policyを検証済み。未承認の自動Production昇格なし
29. Policy filename / hash、Decisions、Handoff、Test Status、Decision auditが最新。Major limitationsを開示

重要項目が一つでも未達なら`NOT PRODUCTION READY`。

## 優先順位

**Correctness > Data Integrity > Approved Risk-Constraint Compliance > Robust Long-Term Growth Objective > Estimation Robustness > Evidence Quality > Maintainability > Usage Efficiency > Performance > Convenience**

Capital Preservationは`Approved Risk-Constraint Compliance`で実現し、Feasible set内で独立した追加目的としてRobust Growthを上書きしない。

Backtestを良く見せる目的でModel / Objective / Risk Budget / Universe / Threshold / `U_objective` / `U_risk` / `S_stress` / Uncertainty treatmentを調整しない。

## 正式ステータス

`PRODUCTION READY` / `NOT PRODUCTION READY` / `RISK BUDGET NOT APPROVED` / `RISK BUDGET INCONSISTENT` / `MODEL-ESTIMATED RISK` / `MODEL DISAGREEMENT` / `LONG-HORIZON VALIDATION LIMITATION` / `MODEL VALIDATION FAILED` / `SHADOW VALIDATION NOT PASSED` / `DATA_LIMITATION` / `INSUFFICIENT EDGE EVIDENCE` / `AMBIGUITY-DOMINATED SOLUTION` / `DEFENSIVE OPPORTUNITY COST` / `REVIEW_REQUIRED` / `ASTRA REVIEW REQUIRED` / `SOL INDEPENDENT REVIEW REQUIRED` / `MODEL REGIME REVIEW REQUIRED` / `UNSTABLE MODEL` / `UNSTABLE PORTFOLIO` / `UTILITY SENSITIVE` / `CAPACITY LIMITED` / `NOT RELIABLY BACKTESTABLE` / `NOT VERIFIED` / `DESIGN CHANGE REQUIRED` / `USER_CONFIRMATION_REQUIRED` / `HANDOFF MISMATCH` / `DOCUMENTATION MISMATCH` / `POLICY VERSION CHANGED`

> **直接確認できる許容不能リスクは最初に制約する。推定を伴うリスクは`U_risk`に基づく承認済みのロバストな確率・分位点制約で管理し、Historical / Hypothetical / OOD Stressは`S_stress`として別に検証する。残ったFeasible setの中では、`U_objective`に対するロバストな長期複利成長を最大化する。期待リターンは、ReinvestmentとIncremental ROICを含むEconomic Return Bridgeと、Market / Factor / Company-specific priorの両方からBase Currencyで構築する。重要な追加投資は常にBest feasible Passive / Cash / Risk-free / `NO_TRADE`と比較し、Cost / TaxはWealth pathへ一度だけ反映する。Opportunity Cost、Uncertainty、Buffer、Sizing conservatismを二重計上しない。PIT、Tradability、Security identity、Research provenance、Locked OOS、Shadow validation、Blind independent review、Policy-as-Codeを維持する。**
