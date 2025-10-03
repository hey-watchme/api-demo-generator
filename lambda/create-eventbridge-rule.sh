#!/bin/bash

# EventBridge Cron Ruleの作成スクリプト

set -e

REGION="ap-southeast-2"
ACCOUNT_ID="975050024946"
FUNCTION_NAME="watchme-demo-data-generator"
RULE_NAME="watchme-demo-data-generator-schedule"

echo "========================================="
echo "Creating EventBridge Cron Rule"
echo "========================================="

# 1. EventBridgeルールの作成（30分ごと）
echo ""
echo "Step 1: Creating EventBridge rule"
echo "-----------------------------------------"
aws events put-rule \
    --name $RULE_NAME \
    --schedule-expression "cron(0/30 * * * ? *)" \
    --state ENABLED \
    --description "Trigger demo data generator every 30 minutes" \
    --region $REGION

echo "Rule created: $RULE_NAME"

# 2. Lambda関数に実行権限を付与
echo ""
echo "Step 2: Adding Lambda permission"
echo "-----------------------------------------"
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id ${RULE_NAME}-permission \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/${RULE_NAME} \
    --region $REGION || echo "Permission may already exist"

# 3. Lambda関数をターゲットに設定
echo ""
echo "Step 3: Setting Lambda as target"
echo "-----------------------------------------"
aws events put-targets \
    --rule $RULE_NAME \
    --targets "Id"="1","Arn"="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}" \
    --region $REGION

echo ""
echo "========================================="
echo "EventBridge Rule Created!"
echo "========================================="
echo ""
echo "Rule Name: $RULE_NAME"
echo "Schedule: Every 30 minutes (cron: 0/30 * * * ? *)"
echo "Target: $FUNCTION_NAME"
echo ""
echo "The demo data generator will now run automatically every 30 minutes."
echo ""
echo "To disable the schedule:"
echo "  aws events disable-rule --name $RULE_NAME --region $REGION"
echo ""
echo "To enable the schedule:"
echo "  aws events enable-rule --name $RULE_NAME --region $REGION"
echo ""
echo "To delete the rule:"
echo "  aws events remove-targets --rule $RULE_NAME --ids 1 --region $REGION"
echo "  aws events delete-rule --name $RULE_NAME --region $REGION"
