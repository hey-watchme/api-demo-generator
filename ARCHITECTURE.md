# Demo Data Generator - アーキテクチャ設計

## 📊 システム構成

```
┌─────────────────────────────────────────────────────────────┐
│ EventBridge Scheduler (30分cron: 0/30 * * * ? *)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Lambda: watchme-demo-data-generator-trigger                │
│ - 複数ペルソナを順次処理                                     │
│ - API呼び出しのオーケストレーション                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP POST /generate
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI: demo-generator (EC2/Docker)                       │
│                                                             │
│ エンドポイント:                                              │
│ ├─ GET  /personas      ペルソナ一覧                        │
│ └─ POST /generate      データ生成                           │
│                                                             │
│ ペルソナ管理:                                                │
│ ├─ child_5yo     (5歳男児、幼稚園)                         │
│ ├─ adult_30s     (30代会社員、IT)                          │
│ └─ elderly_70s   (70代女性、退職)                          │
│                                                             │
│ 機能:                                                        │
│ ├─ 時刻に応じた動的データ生成                                │
│ ├─ ペルソナ別の行動パターン                                  │
│ └─ 累積vibe_scoresの計算                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │ Supabase REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Supabase: dashboard_summary テーブル                       │
│                                                             │
│ Primary Key: (device_id, date)                             │
│                                                             │
│ デバイスID:                                                  │
│ ├─ demo-child-5yo-001                                      │
│ ├─ demo-adult-30s-001                                      │
│ └─ demo-elderly-70s-001                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 設計思想

### なぜAPI化したか？

1. **複数ペルソナ管理**
   - カタログ形式で複数ユーザーのデモデータ
   - 子供、大人、高齢者など多様な属性

2. **動的データ生成**
   - 時刻に応じた累積データ
   - ペルソナ別の行動パターン
   - リアルな感情変化の再現

3. **拡張性**
   - 新しいペルソナの追加が容易
   - ロジックの複雑化に対応
   - 手動でのデータ生成も可能

4. **保守性**
   - Lambda: シンプルなトリガー役
   - API: 複雑なビジネスロジック
   - 責任の分離

## 📁 ディレクトリ構成

```
/Users/kaya.matsumoto/projects/watchme/
├── api/demo-generator/                 # FastAPI (開発・デプロイ)
│   ├── main.py                         # APIメインコード
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   └── ARCHITECTURE.md                 # このファイル
│
└── server-configs/lambda-functions/
    └── watchme-demo-data-generator/    # Lambda Trigger
        ├── lambda_function.py          # APIを呼び出すだけ
        ├── requirements.txt            # requestsのみ
        ├── build.sh
        ├── deploy.sh
        ├── create-eventbridge-rule.sh
        └── README.md
```

## 🔄 データフロー

### 1. 定期実行（30分ごと）

```
EventBridge
  ↓
Lambda Handler
  ↓
for persona in ["child_5yo", "adult_30s", "elderly_70s"]:
    ├─ POST /generate {"persona_id": persona}
    ↓
    API: 現在時刻を計算
    API: ペルソナに応じたデータ生成
    API: Supabase upsert
    ↓
    成功/失敗をログ出力
```

### 2. 手動実行（開発・テスト）

```
curl POST /generate
  ├─ persona_id: "child_5yo"
  ├─ date: "2025-10-03" (オプション)
  └─ time_block: "14-30" (オプション)
```

## 🚀 デプロイ戦略

### Phase 1: ローカル開発 (現在)

- API: ローカルで起動 (`python3 main.py`)
- Lambda: ローカルAPIを呼び出し

### Phase 2: Docker化

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020"]
```

### Phase 3: EC2デプロイ

- 既存のEC2インスタンスにDocker Composeで追加
- nginx reverse proxy設定
- `https://api.hey-watch.me/demo-generator`

### Phase 4: 本番運用

- EventBridge: 30分cron有効化
- CloudWatch監視
- エラー通知（SNS）

## ✅ 実装済み機能（2025-10-03）

### child_5yo ペルソナ
- **UUID**: `a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d`
- **vibe_scores**: 48ブロック全体（現在時刻以降はnull）
  - 睡眠時間（00:00-06:30）: -5〜+5
  - 朝食ピーク（07:00-08:00）: +25〜+35
  - 昼食ピーク（12:00）: +40
  - 夕食ピーク（19:00）: +30〜+35
- **burst_events**: 変化量15以上を自動検出
- **analysis_result**: デモデータ用の構造体
- **insights**: 1日の総括文を自動生成

### データ構造
```json
{
  "vibe_scores": [0, -2, ..., 25, null, null, ...],  // 48要素
  "burst_events": [
    {
      "time": "07:00",
      "event": "朝の起床・準備で機嫌が上昇した",
      "score_change": 15,
      "from_score": 10,
      "to_score": 25
    }
  ],
  "analysis_result": {
    "raw_response": "デモデータのため省略",
    "processing_error": null,
    "extracted_content": "デモユーザー（5歳男児）の分析結果"
  }
}
```

## 📊 今後の拡張

### ペルソナ追加

```python
PERSONAS = {
    # 実装済み
    "child_5yo": {...},  # ✅ 完了

    # 未実装
    "adult_30s": {...},
    "elderly_70s": {...},

    # 追加予定
    "teenager_15yo": {...},      # 中学生
    "young_adult_25yo": {...},   # 若手社会人
    "parent_40s": {...},         # 子育て世代
    "senior_60s": {...},         # アクティブシニア
}
```

### データ生成ロジック強化

- 曜日・季節による変動
- より詳細なペルソナ特有の行動パターン
- 感情変化のバリエーション増加
- 複数日にわたるデータ一括生成

### API拡張

- `GET /personas/{persona_id}/history` - 過去データ取得
- `POST /bulk-generate` - 複数日分一括生成
- `DELETE /personas/{persona_id}/data` - データクリア
- より詳細なprompt生成ロジック

## 🔍 モニタリング

- Lambda CloudWatch Logs: API呼び出し成功/失敗
- API CloudWatch Logs: データ生成の詳細
- Supabase: データ蓄積状況

---

**最終更新**: 2025-10-03
