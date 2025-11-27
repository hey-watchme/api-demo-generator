# Demo Data Generator API

複数のペルソナ（子供、大人、高齢者など）のデモデータを動的に生成するAPI

## 概要

- **目的**: デモ・カタログ用のリアルなモックデータ生成
- **ペルソナ**: 複数の年齢層・属性のユーザーデータ
- **動的生成**: 時刻に応じた累積データ
- **データ保存先**: Supabase 2つのテーブル（2025-11-27更新）
  - `spot_results` - 録音ごとの分析結果（30分ごとに1レコード追加）
  - `daily_results` - 1日の累積分析結果（30分ごとにUPSERT更新）

## アーキテクチャ

```
EventBridge (30分cron)
  ↓
Lambda: demo-data-generator-trigger
  ↓ (HTTP Request)
API: demo-generator (FastAPI - EC2/Docker)
  ├─ ペルソナ管理
  ├─ 動的データ生成
  └─ Supabase保存
```

## ペルソナ一覧

| ID | 名前 | Device ID | 説明 | 実装状況 |
|----|------|-----------|------|---------|
| `child_5yo` | 5歳男児 | `a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d` | 幼稚園年長、マインクラフト好き | ✅ 完了 |
| `adult_30s` | 30代会社員 | `00000000-0000-0000-0001-000000000002` | IT企業、在宅ワーク | 🚧 未実装 |
| `elderly_70s` | 70代高齢者 | `00000000-0000-0000-0001-000000000003` | 退職、園芸趣味 | 🚧 未実装 |

## ディレクトリ構成

```
demo-generator/
├── api/                    # FastAPI本体
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
├── lambda/                 # Lambda Trigger
│   ├── lambda_function.py
│   ├── requirements.txt
│   ├── build.sh
│   ├── deploy.sh
│   ├── create-eventbridge-rule.sh
│   └── README.md
│
├── .env.example           # 環境変数サンプル
├── .gitignore
├── ARCHITECTURE.md        # 全体設計
└── README.md              # このファイル
```

## セットアップ

### 1. API環境構築

```bash
cd /Users/kaya.matsumoto/projects/watchme/api/demo-generator

# 環境変数設定
cp .env.example .env
# .envを編集してSupabase認証情報を設定

# APIディレクトリへ移動
cd api

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip3 install -r requirements.txt
```

### 2. APIローカル起動

```bash
cd api

# 開発サーバー起動
python3 main.py
```

API: http://localhost:8020

### 3. Lambda関数デプロイ

```bash
cd lambda

# ビルド（Docker必要）
./build.sh

# デプロイ
./deploy.sh

# EventBridge設定
./create-eventbridge-rule.sh
```

## API仕様

### エンドポイント一覧

#### `GET /`
- ルート情報

#### `GET /health`
- ヘルスチェック

#### `GET /personas`
- ペルソナ一覧取得

**レスポンス例:**
```json
[
  {
    "persona_id": "child_5yo",
    "name": "5歳男児（幼稚園年長）",
    "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "description": "白幡幼稚園の年長さん、趣味はマインクラフト",
    "profile": {
      "age": 5,
      "gender": "male",
      "occupation": "幼稚園年長",
      "hobbies": ["マインクラフト", "ブロック遊び"]
    }
  }
]
```

#### `POST /generate`
- デモデータ生成とSupabase保存

**リクエストボディ:**
```json
{
  "persona_id": "child_5yo",
  "date": "2025-10-03",      // オプション、デフォルトは今日
  "time_block": "14-30"      // オプション、デフォルトは現在時刻
}
```

**レスポンス例:**
```json
{
  "success": true,
  "persona_id": "child_5yo",
  "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "date": "2025-11-27",
  "time_block": "15-00",
  "spot_recorded_at": "2025-11-27T06:00:00+00:00",
  "spot_vibe_score": 20,
  "daily_vibe_score": 15.03,
  "daily_processed_count": 31,
  "tables_updated": ["spot_results", "daily_results"],
  "message": "Demo data generated and saved successfully to spot_results and daily_results"
}
```

### 生成されるデータ構造

#### 1. spot_resultsテーブル（録音ごとに新規レコード追加）

30分ごとに新しい録音データとして1レコード追加します。

**Primary Key**: `(device_id, recorded_at)`

**データ形式:**
```json
{
  "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "recorded_at": "2025-11-27T03:00:00+00:00",
  "vibe_score": 45,
  "profile_result": {
    "summary": "給食の時間。友達と一緒に楽しく食事。",
    "behavior": "食事, 友達と遊ぶ",
    "vibe_score": 45,
    "recorded_at": "2025-11-27T03:00:00+00:00",
    "acoustic_metrics": {
      "loudness_range": [-39.0, -14.0],
      "dominant_patterns": [...],
      "pitch_variability": "moderate",
      "rhythm_regularity": 0.64,
      "speech_time_ratio": 0.08,
      "average_loudness_db": -17.5,
      "voice_stability_score": 0.32
    },
    "key_observations": [...],
    "behavioral_analysis": {...},
    "psychological_analysis": {...}
  },
  "created_at": "2025-11-27T13:53:09.998844+09:00",
  "llm_model": "demo-generator-static-data",
  "summary": "給食の時間。友達と一緒に楽しく食事。",
  "behavior": "食事, 友達と遊ぶ",
  "local_date": "2025-11-27",
  "local_time": "2025-11-27T12:00:00+09:00",
  "daily_aggregator_status": null,
  "daily_aggregator_processed_at": null
}
```

**特徴:**
- 30分ごとに新しい`recorded_at`で1レコード追加
- 1日48レコード: 00:00から23:30まで
- 音響分析・行動分析・心理分析を含む完全なデータ

#### 2. daily_resultsテーブル（1日1レコード、累積更新）

30分ごとに同じ日付のレコードをUPSERT（上書き）します。

**Primary Key**: `(device_id, local_date)`

**データ形式:**
```json
{
  "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "local_date": "2025-11-27",
  "vibe_score": 7.125,
  "summary": "2025-11-27は朝の静かな時間帯から始まり、日中にかけて感情の変動が見られました。起床時や園での活動時間に気分が上昇し、午後の遊び時間で活発な様子が続きました。全体として安定した一日でした。",
  "behavior": "",
  "profile_result": {},
  "vibe_scores": [
    {"time": "2025-11-27T06:01:00+09:00", "score": 0},
    {"time": "2025-11-27T06:31:00+09:00", "score": -28},
    {"time": "2025-11-27T07:01:00+09:00", "score": 20},
    ...
  ],
  "burst_events": [
    {
      "time": "07:01",
      "event": "Morning wake-up and preparation led to mood elevation",
      "score_change": 48
    },
    ...
  ],
  "processed_count": 16,
  "last_time_block": "",
  "llm_model": "demo-generator-static-data",
  "created_at": "2025-11-26T21:12:12.343166+00:00",
  "updated_at": "2025-11-27T04:43:03.805365+00:00"
}
```

**特徴:**
- 累積更新: 30分ごとに`processed_count`が増え、`vibe_scores`配列が拡張される
- 日付が変わると新しいレコードが作成される
- 1日の総合分析結果を保持

## 使用例

### curl

```bash
# ペルソナ一覧取得
curl http://localhost:8020/personas

# 子供のデモデータ生成（現在時刻）
curl -X POST http://localhost:8020/generate \
  -H "Content-Type: application/json" \
  -d '{"persona_id": "child_5yo"}'

# 大人のデモデータ生成（特定時刻指定）
curl -X POST http://localhost:8020/generate \
  -H "Content-Type: application/json" \
  -d '{"persona_id": "adult_30s", "date": "2025-10-03", "time_block": "15-00"}'
```

### Python

```python
import requests

# ペルソナ一覧
response = requests.get("http://localhost:8020/personas")
personas = response.json()

# データ生成
response = requests.post("http://localhost:8020/generate", json={
    "persona_id": "child_5yo"
})
result = response.json()
```

## Lambda関数との連携

Lambda関数 (`watchme-demo-data-generator`) がこのAPIを呼び出す形に変更：

```python
import requests

def lambda_handler(event, context):
    # 全ペルソナのデータ生成
    personas = ["child_5yo", "adult_30s", "elderly_70s"]

    for persona_id in personas:
        response = requests.post(
            "https://api.hey-watch.me/demo-generator/generate",
            json={"persona_id": persona_id}
        )
        print(f"Generated {persona_id}: {response.json()}")
```

## 実装状況

### ✅ 実装済み（2025-11-27更新）
- [x] **ペルソナ対応**: child_5yo（5歳男児）
- [x] **2つのテーブルへのデータ生成**
  - [x] **spot_results** - 録音ごとの分析結果（30分ごとに新規レコード追加）
  - [x] **daily_results** - 1日の累積分析（30分ごとにUPSERT更新）
- [x] **spot_results用データ生成**
  - [x] profile_result JSONB（acoustic_metrics, behavioral_analysis, psychological_analysis）
  - [x] 録音時刻（recorded_at）ベースのデータ生成
  - [x] ローカル日時（local_date, local_time）対応
- [x] **daily_results用データ生成**
  - [x] vibe_scores配列（時刻とスコアのペア）
  - [x] burst_events配列（感情変化イベント）
  - [x] 累積更新ロジック（processed_count増加）
  - [x] 平均vibe_score計算
- [x] **child_5yoの1日ルーティンデータ（48ブロック分のスタティックデータ）**
- [x] **burst_eventsの自動検出（変化量15以上）**
- [x] **時刻に応じた累積データ計算**
- [x] **EC2/Dockerデプロイ完了** (2025-10-03)
- [x] **Lambda関数デプロイ完了** (2025-10-03)
- [x] **EventBridge自動実行設定完了** (30分ごと)
- [x] **テーブル構造の更新** (2025-11-27)

### 🚧 今後の拡張
- [ ] adult_30s, elderly_70sペルソナの実装
- [ ] 曜日・季節による変動
- [ ] 複数日にわたるデータ生成
- [ ] より詳細なprompt生成ロジック

## ポート番号

- **8020**: Demo Generator API
- 他のAPIとの衝突を避けるため

## 📦 デプロイ手順

### 🚀 自動デプロイ（CI/CD）- 推奨

> **📘 詳細**: [CI/CD標準仕様書](../../server-configs/CICD_STANDARD_SPECIFICATION.md)を参照

mainブランチへのプッシュで自動的にデプロイ：

```bash
git add .
git commit -m "feat: 新機能の追加"
git push origin main
```

**CI/CDプロセス**:
1. GitHub ActionsがECRにDockerイメージをプッシュ
2. GitHub Secretsから環境変数を取得してEC2に`.env`ファイルを作成
3. Docker Composeでコンテナを再起動

### 必要なGitHub Secrets設定

```
AWS_ACCESS_KEY_ID       # AWS認証
AWS_SECRET_ACCESS_KEY   # AWS認証
EC2_HOST                # デプロイ先EC2
EC2_SSH_PRIVATE_KEY     # SSH接続用
EC2_USER                # SSHユーザー
SUPABASE_URL            # Supabase URL（重要）
SUPABASE_KEY            # Supabase APIキー（重要）
```

### 手動デプロイ（非推奨）

CI/CDを使用せずに手動でデプロイする場合のみ：

```bash
# EC2で実行
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
cd /home/ubuntu/demo-generator
./run-prod.sh
```

## 🚀 本番環境

### アクセス情報
- **外部URL**: `https://api.hey-watch.me/demo-generator/`
- **内部ポート**: `8020`
- **コンテナ名**: `demo-generator-api`
- **EC2サーバー**: `3.24.16.82`
- **ECRリポジトリ**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-demo-generator`

### API利用方法

#### 外部からのアクセス
```bash
# API情報
curl https://api.hey-watch.me/demo-generator/

# ヘルスチェック
curl https://api.hey-watch.me/demo-generator/health

# ペルソナ一覧
curl https://api.hey-watch.me/demo-generator/personas

# デモデータ生成
curl -X POST https://api.hey-watch.me/demo-generator/generate \
  -H "Content-Type: application/json" \
  -d '{"persona_id": "child_5yo"}'
```

#### 内部からのアクセス
```bash
# ローカルホスト経由
curl http://localhost:8020/health

# テストデータで処理実行
curl -X POST http://localhost:8020/generate \
  -H "Content-Type: application/json" \
  -d '{"persona_id": "child_5yo"}'
```

### 運用管理コマンド

#### SSH接続
```bash
# 本番環境へのSSH接続
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
```

#### サービス管理
```bash
# コンテナ確認
docker ps | grep demo-generator

# ログ確認
docker logs demo-generator-api --tail 100 -f

# コンテナ再起動
cd /home/ubuntu/demo-generator
docker-compose -f docker-compose.prod.yml restart

# コンテナ停止・削除・再起動
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 重要な設定情報
- **ECRリポジトリ**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-api-demo-generator`
- **リージョン**: `ap-southeast-2`
- **ポート**: 8020
- **コンテナ名**: `demo-generator-api`
- **設定ファイル**: `/home/ubuntu/demo-generator/.env`
- **docker-compose**: `/home/ubuntu/demo-generator/docker-compose.prod.yml`
- **メモリ制限**: 512MB（docker-compose.prod.ymlで設定済み）
- **Nginx設定**: `/demo-generator/` → `localhost:8020`に転送

### 環境変数
```bash
# /home/ubuntu/demo-generator/.env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## 🎉 デプロイ完了状況（2025-10-03）

### システム全体が稼働中

すべてのコンポーネントが正常にデプロイされ、30分ごとに自動実行されています。

#### ✅ 1. Demo Generator API
- **URL**: `https://api.hey-watch.me/demo-generator/`
- **ステータス**: 稼働中
- **デプロイ日**: 2025-10-03
- **systemdサービス**: `demo-generator-api.service`
- **動作確認**:
  ```bash
  curl https://api.hey-watch.me/demo-generator/health
  # {"status":"healthy","timestamp":"2025-10-03T..."}
  ```

#### ✅ 2. Lambda関数
- **関数名**: `watchme-demo-data-generator`
- **ステータス**: デプロイ済み・稼働中
- **リージョン**: ap-southeast-2
- **実行時間**: 約1.3秒
- **メモリ使用**: 57MB / 256MB
- **動作確認**:
  ```bash
  aws lambda invoke --function-name watchme-demo-data-generator \
    --region ap-southeast-2 response.json
  # 3つのペルソナすべて成功
  ```

#### ✅ 3. EventBridge自動実行
- **スケジュール名**: `watchme-demo-data-generator-schedule`
- **ステータス**: 有効
- **Cron式**: `0/30 * * * ? *`（30分ごと）
- **タイムゾーン**: Asia/Tokyo
- **次回実行**: 毎時00分・30分

### 自動生成されるデータ

30分ごとに以下のペルソナのデータが自動生成されます：

| ペルソナID | デバイスID | 説明 |
|-----------|-----------|------|
| `child_5yo` | `a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d` | 5歳男児（幼稚園年長） |
| `adult_30s` | `00000000-0000-0000-0001-000000000002` | 30代会社員（エンジニア） |
| `elderly_70s` | `00000000-0000-0000-0001-000000000003` | 70代高齢者（退職） |

### 監視とメンテナンス

#### Lambda実行ログの確認
```bash
# CloudWatch Logsで確認
aws logs tail /aws/lambda/watchme-demo-data-generator --follow --region ap-southeast-2
```

#### APIログの確認
```bash
# EC2サーバーでコンテナログを確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
docker logs demo-generator-api --tail 100 -f
```

#### サービスステータス確認
```bash
# systemdサービス確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
sudo systemctl status demo-generator-api.service
```

### トラブルシューティング

#### APIが応答しない場合
```bash
# サービス再起動
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
sudo systemctl restart demo-generator-api.service
```

#### Lambda関数のエラー
```bash
# 最新の実行ログを確認
aws lambda invoke --function-name watchme-demo-data-generator \
  --region ap-southeast-2 --log-type Tail response.json
cat response.json | jq
```

#### データが生成されない場合
1. EventBridgeルールが有効化されているか確認
2. Lambda関数の実行ログを確認
3. APIのヘルスチェックを確認
4. Supabaseの`spot_results`と`daily_results`テーブルを確認

---

## 📝 変更履歴

### 2025-11-27: テーブル構造の変更
- **削除**: dashboard_summary, behavior_summary, emotion_opensmile_summary, dashboard テーブル
- **追加**: spot_results, daily_results テーブル
- **理由**: 新しい分析アーキテクチャ（Spot分析 + Daily分析）への対応
- **データ形式変更**:
  - spot_results: 録音ごとの詳細分析（profile_result JSONB）
  - daily_results: 累積分析（vibe_scores配列、burst_events配列）

### 2025-10-08
- dashboard テーブルへのデータ生成機能追加
- 30分ごとのリアルタイムデータ生成

### 2025-10-03
- 初回デプロイ完了
- Lambda関数・EventBridge設定完了
