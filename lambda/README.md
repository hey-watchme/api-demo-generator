# WatchMe Demo Data Generator Lambda

モックユーザーの`dashboard_summary`データを30分ごとに自動生成するLambda関数

## 概要

- **目的**: デモ・開発用のリアルタイムデータ生成
- **実行間隔**: 30分ごと（EventBridge Cron）
- **データ保存先**: Supabase `dashboard_summary` テーブル
- **タイムゾーン**: JST（日本標準時）

## モックアカウント情報

- **Device ID**: `a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d`
- **データ内容**: 5歳男児（幼稚園年長）の1日の活動記録（静的テンプレート）

## アーキテクチャ

```
EventBridge (Cron: 0/30 * * * ? *)
  ↓
Lambda: watchme-demo-data-generator
  ↓
Supabase: dashboard_summary (upsert)
```

## デプロイ手順

### 前提条件

- AWS CLI設定済み
- IAMロール `lambda-execution-role` 作成済み
- Supabase認証情報

### 1. Lambda関数のデプロイ

```bash
cd /Users/kaya.matsumoto/projects/watchme/server-configs/lambda-functions/watchme-demo-data-generator

# デプロイ実行
./deploy.sh
```

### 2. EventBridgeルールの作成

```bash
# Cronスケジュールを設定（30分ごと）
./create-eventbridge-rule.sh
```

## 手動デプロイ（AWSコンソール使用）

### Lambda関数の作成

1. **AWS Console → Lambda → 関数の作成**
2. **基本的な情報**:
   - **関数名**: `watchme-demo-data-generator`
   - **ランタイム**: Python 3.11
   - **アーキテクチャ**: x86_64

3. **実行ロール**:
   - **新しいロールを作成（推奨）**: 「AWS ポリシーテンプレートから新しいロールを作成」を選択
   - **ロール名**: `watchme-demo-data-generator-role`
   - **ポリシーテンプレート**: なし（デフォルトでOK - CloudWatch Logsへの書き込み権限のみ）

   ※ Supabaseは外部APIなので追加のAWS権限は不要です

4. **関数を作成**をクリック

5. **設定の調整**（作成後に「設定」タブ）:
   - **一般設定 → 編集**:
     - タイムアウト: **60秒**
     - メモリ: **256 MB**

6. **環境変数**（「設定」→「環境変数」→「編集」）:
   ```
   SUPABASE_URL=https://qvtlwotzuzbavrzqhyvt.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF2dGx3b3R6dXpiYXZyenFoeXZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzODAzMzAsImV4cCI6MjA2Njk1NjMzMH0.g5rqrbxHPw1dKlaGqJ8miIl9gCXyamPajinGCauEI3k
   ```

7. **コードアップロード**（「コード」タブ）:
   ```bash
   ./build.sh
   aws lambda update-function-code \
     --function-name watchme-demo-data-generator \
     --zip-file fileb://function.zip \
     --region ap-southeast-2
   ```

### EventBridge Cronルールの作成

1. **AWS Console → EventBridge → Rules → Create rule**
2. 設定:
   - **Name**: `watchme-demo-data-generator-schedule`
   - **Rule type**: Schedule
   - **Schedule pattern**: Cron expression
   - **Cron expression**: `0/30 * * * ? *` (30分ごと)

3. **ターゲット**:
   - **Target type**: AWS service
   - **Select a target**: Lambda function
   - **Function**: `watchme-demo-data-generator`

## テスト手順

### 手動実行

```bash
# Lambda関数を手動実行
aws lambda invoke \
  --function-name watchme-demo-data-generator \
  --region ap-southeast-2 \
  output.json

# 結果確認
cat output.json
```

### CloudWatchログ確認

```bash
# ログストリーム確認
aws logs tail /aws/lambda/watchme-demo-data-generator \
  --region ap-southeast-2 \
  --follow
```

### Supabaseでデータ確認

```sql
-- デモデータの確認
SELECT * FROM dashboard_summary
WHERE device_id = 'a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d'
ORDER BY date DESC
LIMIT 10;
```

## 運用管理

### スケジュールの一時停止

```bash
aws events disable-rule \
  --name watchme-demo-data-generator-schedule \
  --region ap-southeast-2
```

### スケジュールの再開

```bash
aws events enable-rule \
  --name watchme-demo-data-generator-schedule \
  --region ap-southeast-2
```

### ルールの削除

```bash
# ターゲットを削除
aws events remove-targets \
  --rule watchme-demo-data-generator-schedule \
  --ids 1 \
  --region ap-southeast-2

# ルールを削除
aws events delete-rule \
  --name watchme-demo-data-generator-schedule \
  --region ap-southeast-2
```

## トラブルシューティング

### Lambda関数がタイムアウトする

- タイムアウト設定を増やす（現在: 60秒）
- CloudWatchログでエラー内容を確認

### Supabase接続エラー

- 環境変数 `SUPABASE_URL` と `SUPABASE_KEY` が正しく設定されているか確認
- Lambda関数がインターネットアクセス可能か確認（VPC設定）

### データが挿入されない

- CloudWatchログでエラーを確認
- Supabaseテーブルスキーマが正しいか確認
- テストイベントで手動実行して動作確認

## データ構造

生成されるデータ例:

```json
{
  "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "date": "2025-10-03",
  "prompt": "## 1日全体の総合分析依頼...",
  "processed_count": 48,
  "last_time_block": "23-30",
  "average_vibe": 8.85417,
  "insights": "朝から昼にかけて...",
  "analysis_result": {...},
  "vibe_scores": [0, 0, 0, ...],
  "burst_events": [...]
}
```

## コスト見積もり

- **Lambda実行**: 48回/日 × 1秒 × $0.0000166667/GB-秒 ≈ $0.01/月
- **EventBridge**: 48回/日 × $0（無料枠）= $0/月
- **合計**: 約 $0.01/月（ほぼ無料）

## 更新履歴

- **2025-10-03**: 初版作成
