# 無料枠を使ったAI試験運転（Gemini）

PRIME LABのAI候補生成はGoogle Gemini APIの無料枠で試せる構成です。課金を避けるため、無料枠の利用状況をGoogle AI Studioで確認し、課金を有効にしない運用を推奨します。APIの無料枠・モデルの提供状況は変わります。

## 初回設定（スマホから可能）
1. https://aistudio.google.com/apikey でAPIキーを作成する。APIキーはチャットや公開GitHubに貼らない。
2. https://github.com/robhgien13-cloud/prime-lab/settings/secrets/actions を開く。
3. **New repository secret** を選び、Nameを `GEMINI_API_KEY`、Secretに取得したキーを設定して保存する。
4. https://github.com/robhgien13-cloud/prime-lab/actions/workflows/ai-free.yml を開き、**Run workflow → main → Run workflow** を押す。

## 動作
- Gemini APIへのリクエストは原則1回のみ。エラー時に有料APIへ自動切替・再試行はしない。
- JSONの入力形式と範囲を検査し、有限範囲の反例探索を行う。
- 研究記録は「AIによる提案、未査読、証明なし、先行研究未照合」と明示する。
- 成功した場合だけ公開用JSONをGitHubにコミットし、HPの記録に反映する。
- 日次の定期実行は設定していない。手動試験のみ。
- 同日二度目のAI記録は上書き防止のため失敗する。

## 注意
無料枠の利用には提供地域やアカウントごとの制限がある。無料枠では送信内容がサービス改善に使われる場合がある。機密情報は送らない。モデルが使えない場合はGitHub ActionsのGEMINI_MODEL設定を無料枠で利用可能なモデルに変更する必要がある。

数学的検証結果は新発見の証明ではない。現在の検証器は素数の余り・素数間隔の余りに限られる。
