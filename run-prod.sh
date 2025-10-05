#!/bin/bash

# Demo Generator API - 本番環境デプロイスクリプト
# 標準仕様: /watchme/server-configs/CICD_STANDARD_SPECIFICATION.md 準拠

set -e  # エラー時に即座に終了

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Demo Generator API デプロイ開始${NC}"
echo -e "${GREEN}========================================${NC}"

# ECR設定
ECR_REGISTRY="754724220380.dkr.ecr.ap-southeast-2.amazonaws.com"
ECR_REPOSITORY="watchme-api-demo-generator"
CONTAINER_NAME="demo-generator-api"

# 1. ECRログイン
echo -e "${YELLOW}[1/6] ECRにログイン中...${NC}"
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY}
echo -e "${GREEN}✅ ECRログイン成功${NC}"

# 2. 最新イメージを取得
echo -e "${YELLOW}[2/6] 最新イメージを取得中...${NC}"
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
echo -e "${GREEN}✅ イメージ取得完了${NC}"

# 3. 既存コンテナの完全削除（3層アプローチ）
echo -e "${YELLOW}[3/6] 既存コンテナを削除中...${NC}"

# 3-1. 実行中コンテナの停止と削除
RUNNING_CONTAINERS=$(docker ps -q --filter "name=${CONTAINER_NAME}")
if [ ! -z "$RUNNING_CONTAINERS" ]; then
    echo "  - 実行中のコンテナを停止中..."
    docker stop $RUNNING_CONTAINERS
    docker rm -f $RUNNING_CONTAINERS
fi

# 3-2. 停止済みコンテナの削除
ALL_CONTAINERS=$(docker ps -aq --filter "name=${CONTAINER_NAME}")
if [ ! -z "$ALL_CONTAINERS" ]; then
    echo "  - 停止済みコンテナを削除中..."
    docker rm -f $ALL_CONTAINERS
fi

# 3-3. docker-compose管理コンテナの削除
echo "  - docker-compose管理コンテナを削除中..."
docker-compose -f docker-compose.prod.yml down || true

echo -e "${GREEN}✅ 既存コンテナ削除完了${NC}"

# 4. Docker未使用リソースのクリーンアップ
echo -e "${YELLOW}[4/6] 未使用Dockerリソースをクリーンアップ中...${NC}"
docker system prune -f
echo -e "${GREEN}✅ クリーンアップ完了${NC}"

# 5. 新規コンテナの起動
echo -e "${YELLOW}[5/6] 新規コンテナを起動中...${NC}"
docker-compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✅ コンテナ起動完了${NC}"

# 6. 起動確認
echo -e "${YELLOW}[6/6] 起動確認中...${NC}"
sleep 5

# コンテナステータス確認
if docker ps | grep -q ${CONTAINER_NAME}; then
    echo -e "${GREEN}✅ コンテナが正常に起動しています${NC}"
    docker ps | grep ${CONTAINER_NAME}
else
    echo -e "${RED}❌ コンテナが起動していません${NC}"
    echo -e "${RED}ログを確認してください: docker logs ${CONTAINER_NAME}${NC}"
    exit 1
fi

# ヘルスチェック
echo -e "${YELLOW}ヘルスチェック実行中...${NC}"
if curl -f http://localhost:8020/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ヘルスチェック成功${NC}"
else
    echo -e "${RED}⚠️ ヘルスチェック失敗（起動中の可能性があります）${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 デプロイ完了！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 コンテナステータス:"
docker ps | grep ${CONTAINER_NAME} || echo "コンテナが見つかりません"
echo ""
echo "📋 ログ確認: docker logs ${CONTAINER_NAME}"
echo "🌐 URL: https://api.hey-watch.me/demo-generator/"
