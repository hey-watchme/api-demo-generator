#!/usr/bin/env python3
"""
Demo Data Generator Lambda Trigger
Demo Generator APIを呼び出して複数ペルソナのデータを生成
EventBridge (Cron)により30分ごとに実行される
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

# 環境変数
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.hey-watch.me")
DEMO_GENERATOR_ENDPOINT = f"{API_BASE_URL}/demo-generator"

# 生成対象のペルソナリスト
PERSONAS = ["child_5yo", "adult_30s", "elderly_70s"]


def get_jst_time():
    """JSTタイムゾーンで現在時刻を取得"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)


def call_demo_generator_api(persona_id: str) -> dict:
    """Demo Generator APIを呼び出してデータ生成"""
    try:
        print(f"Calling Demo Generator API for persona: {persona_id}")
        print(f"URL: {DEMO_GENERATOR_ENDPOINT}/generate")

        response = requests.post(
            f"{DEMO_GENERATOR_ENDPOINT}/generate",
            json={"persona_id": persona_id},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Success: {persona_id} - {result.get('message')}")
            return {
                "success": True,
                "persona_id": persona_id,
                "result": result
            }
        else:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            print(f"Error: {error_msg}")
            return {
                "success": False,
                "persona_id": persona_id,
                "error": error_msg
            }

    except requests.Timeout:
        error_msg = "API timeout after 30 seconds"
        print(f"Error: {error_msg}")
        return {
            "success": False,
            "persona_id": persona_id,
            "error": error_msg
        }

    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"Error: {error_msg}")
        return {
            "success": False,
            "persona_id": persona_id,
            "error": error_msg
        }


def lambda_handler(event, context):
    """
    Lambda関数のメインハンドラー
    EventBridgeから30分ごとに呼び出される
    """
    print(f"[{get_jst_time().isoformat()}] Demo data generator trigger started")
    print(f"Event: {json.dumps(event)}")

    results = []
    success_count = 0
    error_count = 0

    # 各ペルソナのデータを生成
    for persona_id in PERSONAS:
        result = call_demo_generator_api(persona_id)
        results.append(result)

        if result["success"]:
            success_count += 1
        else:
            error_count += 1

    # 結果サマリー
    print(f"\n========== Summary ==========")
    print(f"Total personas: {len(PERSONAS)}")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"=============================\n")

    # 全て成功した場合のみ200を返す
    if error_count == 0:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "All demo data generated successfully",
                "success_count": success_count,
                "total": len(PERSONAS),
                "timestamp": get_jst_time().isoformat(),
                "results": results
            }, default=str, ensure_ascii=False)
        }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Some demo data generation failed",
                "success_count": success_count,
                "error_count": error_count,
                "total": len(PERSONAS),
                "timestamp": get_jst_time().isoformat(),
                "results": results
            }, default=str, ensure_ascii=False)
        }
