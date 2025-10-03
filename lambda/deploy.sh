#!/bin/bash

# Demo Data Generator Lambda関数のデプロイスクリプト

set -e

REGION="ap-southeast-2"
ACCOUNT_ID="754724220380"
FUNCTION_NAME="watchme-demo-data-generator"
# ロールは自動生成されるため、ここでは指定しない
# ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/service-role/${FUNCTION_NAME}-role-xxxxx"

# Supabase認証情報（環境変数から取得、または直接指定）
SUPABASE_URL="${SUPABASE_URL:-https://qvtlwotzuzbavrzqhyvt.supabase.co}"
SUPABASE_KEY="${SUPABASE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF2dGx3b3R6dXpiYXZyenFoeXZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzODAzMzAsImV4cCI6MjA2Njk1NjMzMH0.g5rqrbxHPw1dKlaGqJ8miIl9gCXyamPajinGCauEI3k}"

echo "========================================="
echo "Deploying Demo Data Generator Lambda"
echo "========================================="

# 1. ビルド
echo ""
echo "Step 1: Building Lambda function"
echo "-----------------------------------------"
chmod +x build.sh
./build.sh

# 2. Lambda関数の作成または更新
echo ""
echo "Step 2: Creating/Updating Lambda function"
echo "-----------------------------------------"

# 関数が存在するか確認
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Function exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --zip-file fileb://function.zip

    echo "Updating configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --timeout 60 \
        --memory-size 256 \
        --environment "Variables={SUPABASE_URL=${SUPABASE_URL},SUPABASE_KEY=${SUPABASE_KEY}}"
else
    echo "Function does not exist, creating..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --timeout 60 \
        --memory-size 256 \
        --region $REGION \
        --zip-file fileb://function.zip \
        --environment "Variables={SUPABASE_URL=${SUPABASE_URL},SUPABASE_KEY=${SUPABASE_KEY}}"
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Lambda Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Next Steps:"
echo "1. Create EventBridge rule (Cron: 0/30 * * * ? *)"
echo "2. Add Lambda as target"
echo "3. Test the function manually"
echo ""
echo "To create EventBridge rule, run:"
echo "  ./create-eventbridge-rule.sh"
