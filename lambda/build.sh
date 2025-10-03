#!/bin/bash

# Lambda関数のビルドスクリプト（Docker使用）
# x86_64 Linux環境で依存関係をビルド

set -e

echo "Building watchme-demo-data-generator Lambda function for x86_64 Linux..."

# 既存のビルドファイルを削除
rm -rf package
rm -f function.zip

# Dockerを使ってx86_64 Linux環境でビルド
echo "Building dependencies using Docker (Amazon Linux 2)..."
docker run --rm \
    --platform linux/amd64 \
    -v "$PWD":/var/task \
    --entrypoint /bin/bash \
    public.ecr.aws/lambda/python:3.11 \
    -c "pip install -r requirements.txt -t /var/task/package/ --upgrade && echo 'Dependencies installed'"

# Lambda関数のコードをコピー
echo "Copying lambda function..."
cp lambda_function.py package/

# ZIPファイルを作成
echo "Creating deployment package..."
cd package
zip -r ../function.zip . -q
cd ..

# クリーンアップ
rm -rf package

echo "✅ Build complete: function.zip (x86_64 Linux compatible)"
ls -lh function.zip
