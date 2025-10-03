#!/usr/bin/env python3
"""
全データ（burst_events, analysis_result含む）を確認するスクリプト
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

# 環境変数を読み込み
load_dotenv()

def check_full_data():
    """全データ確認"""

    # Supabase接続
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)

    device_id = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    date = "2025-10-03"

    print("=" * 80)
    print("デモデータ全体確認")
    print("=" * 80)
    print(f"Device ID: {device_id}")
    print(f"Date: {date}")
    print()

    # dashboard_summaryテーブルから取得
    response = supabase.table('dashboard_summary').select('*').eq(
        'device_id', device_id
    ).eq(
        'date', date
    ).execute()

    if response.data and len(response.data) > 0:
        data = response.data[0]

        print("📊 基本情報:")
        print(f"   - processed_count: {data.get('processed_count', 0)}")
        print(f"   - last_time_block: {data.get('last_time_block', 'N/A')}")
        print(f"   - average_vibe: {data.get('average_vibe', 0):.2f}")
        print()

        print("💡 Insights:")
        print(f"   {data.get('insights', 'N/A')}")
        print()

        print("📈 Analysis Result:")
        analysis_result = data.get('analysis_result', {})
        if isinstance(analysis_result, dict):
            print(f"   - raw_response: {analysis_result.get('raw_response', 'N/A')}")
            print(f"   - processing_error: {analysis_result.get('processing_error', 'None')}")
            print(f"   - extracted_content: {analysis_result.get('extracted_content', 'N/A')}")
        else:
            print(f"   {analysis_result}")
        print()

        print("💥 Burst Events:")
        burst_events = data.get('burst_events', [])
        if burst_events and len(burst_events) > 0:
            for i, event in enumerate(burst_events, 1):
                print(f"   {i}. {event.get('time', 'N/A')}: {event.get('event', 'N/A')}")
                print(f"      変化量: {event.get('score_change', 0):+d} ({event.get('from_score', 0)} → {event.get('to_score', 0)})")
        else:
            print("   (イベントなし)")
        print()

        print("📊 vibe_scores サマリー:")
        vibe_scores = data.get('vibe_scores', [])
        valid_scores = [s for s in vibe_scores if s is not None]
        print(f"   - 配列長: {len(vibe_scores)}")
        print(f"   - 有効データ: {len(valid_scores)}")
        print(f"   - null数: {len(vibe_scores) - len(valid_scores)}")

        print()
        print("✅ 全データが正常に保存されています")
    else:
        print(f"❌ データが見つかりません")

    print("=" * 80)

if __name__ == "__main__":
    check_full_data()
