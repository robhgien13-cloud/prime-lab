# PRIME LAB — 統合研究システム設計書 v1.0
更新日: 2026-10-21
状態: **設計承認待ちの実装仕様**。本文の機能は、実装済みを意味しない。

## 0. 目的・成功条件
素数に関する自律的研究の公開実験。AIが課題選択、先行研究照合、仮説生成、検証計画、反例探索、証明試行、次の研究提案を行い、すべての試行を再現可能な形で記録する。新定理の発見は保証しない。

初期30日: 1日10サイクル、予定300サイクル。成功の基準は研究記録の完全性、再現性、運用の安定性、重複削減、評価の改善。新発見件数を成功条件にしない。

## 1. 研究対象と探索の配分
研究分類: A 素数分布 / B 素数間隔 / C 合同式 / D 特殊形素数 / E 素数間の関係 / F 判定アルゴリズム / G 他分野との関係 / H 自由探索。

各日の目標: 数論内部5、隣接分野3、遠隔分野2。これは**研究テーマの配分**であり、研究行為の配分と混同しない。別軸で新規仮説3、追試・反証4、証明・理論検討2、メタ研究1を目安とする。実行可能な課題を選ぶ際、テーマ軸と行為軸を組み合わせる。毎日の達成率を記録し、欠損時は繰り越さず欠損として公開。

遠隔分野候補: 音楽理論・言語学・生物学・ネットワーク科学など。比喩をそのまま定理とせず、明確な定義、測定量、帰無仮説、反証条件へ変換する。

## 2. エージェント役割と権限
- Planner: 過去の記録と優先順位から研究課題を選ぶ。
- Librarian: 既知結果・文献・OEIS等を照合。照合できないときは「未確認」。
- Hypothesizer: 数学的に定義可能な仮説と前提条件をJSONで提案。
- Skeptic: 境界条件・小さい反例・量化記号・例外を探す。
- Experiment Designer: 検証範囲、手順、独立した検証法、停止条件を決める。
- Executor: **許可された検証プログラムのみ**隔離環境で実行。AI生成コードを無制限に実行しない。
- Proof Reviewer: 証明候補の各論理段階を点検し、可能なら形式検証へ。
- Archivist: 追記型で証拠、失敗、コスト、出典、実行環境を記録。
- Meta-Researcher: 成果の測定と手法の比較を実施し、翌日の探索配分を提案。
役割は独立モデルを必須としない。単一モデルの段階別プロンプトでもよい。ただし数値検証・定理判定はモデルの自己申告を信用しない。

## 3. 1サイクルの状態機械
QUEUED → PRIOR_ART_CHECK → HYPOTHESIS_DRAFT → FORMALIZED → TEST_PLAN → EXECUTING → REVIEW → ARCHIVED。
分岐: DUPLICATE / REFUTED / NUMERICALLY_SUPPORTED / PROOF_CANDIDATE / PROVEN_WITH_VERIFICATION / INCONCLUSIVE / ERROR / SKIPPED。
各段階の入出力・失敗理由を保存。時間・トークン・計算量の上限を超えたらERRORまたはINCONCLUSIVEとして終了し、架空の成功を作らない。
仮説の修正は新しい revision ID と parent ID を付け、元の仮説を上書きしない。

## 4. 検証基準
- 仮説は対象集合、量化範囲、条件、述語、反例の形を明記する。
- 初期検証: 小さな数、端点、既知の特殊ケース。
- 大規模検証: 事前に宣言した範囲、ランダム/層化サンプル、異なる実装による照合。サンプルは乱数seedを保存。
- 確率的素数判定を使用した場合、確率的な保証を明示。必要に応じ決定的判定や証明書を使用。
- 「反証済み」は再現できる厳密な反例がある場合のみ。
- 「数値的支持」は検査した範囲だけの主張。一般命題の証明ではない。
- 「証明候補」は未査読。証明の穴・循環論法・未証明の補題を点検。
- 「証明済み」は機械検証済みの形式証明、または独立した専門的検証などの証拠と検証方法を明記する。AIの自己評価だけでは不可。
- 「新規性確認済み」は広範な先行研究調査と外部確認が必要。検索不一致を新発見と呼ばない。
- 数値的実験から推定した関係は、探索データと評価データを分離し、選択バイアスや多重検定を記録する。

## 5. 先行研究・情報源
OEIS、arXiv math.NT、LMFDB、教科書・査読論文・一次資料。引用URL、アクセス日時、文献ID、調査クエリを保存。
ネットワーク未接続時は外部照合不能として明記し、出典や文献を捏造しない。自動取得は利用規約・レート制限に従う。
論文の結論を利用するときは適用条件を確認。先行研究一致・新規性不明を別ステータスで扱う。

## 6. メタ研究（研究の研究）
1日10サイクルのうち1サイクル相当をメタ研究に割り当てる。週次・30日次にも集計。
指標:
- 実行成功率 = 正常終了 / 予定数
- 記録完全率 = 必須フィールド充足 / 全記録
- 反証率 = 再現可能な反例が得られた仮説 / 検証した仮説
- 既知重複率 = 既知と判明 / 先行研究照合を完了した仮説
- 独立再現率 = 別実装で一致 / 独立再現を試みた件数
- 有望度 = 事前定義したルーブリック（新規性未確認を含む、証明可能性、明確性、検証費用）
- 異分野有効率 = 明確な検証可能仮説につながった異分野着想 / 評価対象の異分野着想
- 研究費用 = APIトークン・時間・CPU時間（取得可能な範囲）
指標は母数・欠測を必ず併記し、サンプルが少ない段階で優劣を断定しない。

比較実験: 同じ難易度の課題群に「過去研究参照あり/なし」「異分野着想あり/なし」等をランダム割付し、モデル・予算・時間上限を揃える。事前に評価指標を固定し、30日後に差と不確実性を報告する。メタ研究で配分変更を提案できるが、証明基準や公開方針は自動変更できない。

## 7. データモデル（追記・再現性）
source of truth: `data/runs/YYYY-MM-DD/<run_id>.json`（1サイクル1ファイル）。
必須:
schema_version, run_id, date, started_at, finished_at, theme_class, research_mode, status, stage, hypothesis{statement,domain,assumptions,quantifiers,revision,parent_id}, prior_art{queries,references,checked_at,result}, inspiration{field,mechanism,translation_to_math}, experiment{algorithm,code_ref,seed,range,limits,environment}, observations{samples,counterexamples,logs,artifacts}, proof{candidate,review,evidence}, conclusion, next_actions, cost{tokens,cpu_seconds}, errors, provenance{model,version,prompt_version,commit_sha}。
個人情報・秘密鍵・APIトークンは絶対に保存しない。
`data/research.json` はサイト向けに生成する派生集計データ。スキーマを検証し、公開時にHTMLエスケープ相当の安全なDOM操作を用いる。失敗時は古い集計を新しいものと偽らない。
追記済み記録の訂正は別 revision / correction event で保存し、Git履歴も保持。1日10件の研究IDを確保し、失敗も含めて10件の試行履歴を残す（GitHub Actions停止など実行自体が起きない日は10件を保証できない）。

## 8. 実行構成
GitHub Pages: 静的公開サイト。
GitHub Actions: 1日1回起動し、上限10サイクルを逐次処理（各サイクルに時間制限）。手動workflow_dispatchも提供。Actionsのscheduleは遅延・スキップがあり得る。
Python: 素数列挙、検証、ログ生成、集計、テスト。sympy等の依存は固定。
LLM API: 課題生成・文献解釈・証明案・メタ分析。**外部APIの認証情報をGitHub Actions Secretsへ登録**。Secretsがない場合はLLMを実行せず「未設定」と明示。無償のPythonのみの数値探索は「AI自律研究」と呼ばない。
Actions permissions: contents:writeを必要最小限。信頼できない外部入力を実行しない。依存バージョンを固定し、タイムアウト・予算上限・同時実行制御を設定。
公開はGitHub Pages、機密はSecrets、公開ログに機密を含めない。エラー時は記録可能な範囲で失敗を保存し、通知/実行履歴を確認する。

## 9. リポジトリ構成（予定）
```
index.html
data/research.json
data/runs/YYYY-MM-DD/R-*.json
docs/RESEARCH_POLICY.md
docs/SYSTEM_DESIGN.md
docs/SCHEMA.md
src/prime_lab/{planner,literature,hypotheses,experiment,verification,archive,meta,site}.py
tests/{test_math,test_schema,test_pipeline}.py
.github/workflows/{research.yml,ci.yml}
requirements.txt
README.md
```
現在は index.html, data/research.json, README.md のみ実装済み。

## 10. 開発フェーズと受入基準
P0: 研究方針・スキーマ確定。機密情報の保存禁止、ステータス語彙、ID規則をテスト。
P1: LLMなしの計算・記録エンジン。10回のテストで10件の**正直な**記録を生成。既知の正例/反例のユニットテスト。
P2: 先行研究照合と出典保存。接続失敗・未確認を正しく表現。
P3: LLM仮説生成と批判役。JSONスキーマ検証、危険コード不実行、費用上限。
P4: 自動集計・Pages反映。公開画面と記録数の一致、XSS対策。
P5: Actions日次実行。手動実行で10サイクル、障害時の状態記録、再実行の冪等性、予算停止を確認。
P6: メタ研究。評価指標と比較実験を固定し、30日後に報告。
各フェーズはテスト・コードレビュー・公開確認を通過してから次へ。初回公開時は「実験中・未査読」と表示。

## 11. 未決事項
LLMプロバイダ・モデル・API予算上限、先行研究検索方式、証明の独立検証体制、計算時間上限、公開言語（日本語のみ/日英）、通知方法。これらは未決でもP0/P1の開発は可能。
