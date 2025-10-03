# Demo Generator API

複数のペルソナ（子供、大人、高齢者など）のデモデータを動的に生成するFastAPI

## セットアップ

```bash
cd /Users/kaya.matsumoto/projects/watchme/api/demo-generator/api

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip3 install -r requirements.txt

# 環境変数設定（親ディレクトリの.envを使用）
cp ../.env.example ../.env
# ../.envを編集してSupabase認証情報を設定
```

## 起動

```bash
# 開発サーバー起動
python3 main.py

# または
uvicorn main:app --reload --host 0.0.0.0 --port 8020
```

## API仕様

詳細は親ディレクトリの `README.md` を参照
