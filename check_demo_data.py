#!/usr/bin/env python3
"""
デモデータがSupabaseに保存されたか確認するスクリプト
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

# 環境変数を読み込み
load_dotenv()

def check_demo_data():
    """デモデータの確認"""

    # Supabase接続
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)

    # デモデータのdevice_id
    demo_devices = {
        "child_5yo": "00000000-0000-0000-0001-000000000001",
        "adult_30s": "00000000-0000-0000-0001-000000000002",
        "elderly_70s": "00000000-0000-0000-0001-000000000003"
    }

    date = "2025-10-03"

    print("=" * 60)
    print("デモデータ確認")
    print("=" * 60)

    for persona_id, device_id in demo_devices.items():
        print(f"\n【{persona_id}】")
        print(f"Device ID: {device_id}")
        print(f"Date: {date}")
        print("-" * 40)

        # dashboard_summaryテーブルから取得
        response = supabase.table('dashboard_summary').select('*').eq(
            'device_id', device_id
        ).eq(
            'date', date
        ).execute()

        if response.data and len(response.data) > 0:
            data = response.data[0]

            print(f"✅ データ保存成功")
            print(f"   - processed_count: {data.get('processed_count', 0)}")
            print(f"   - last_time_block: {data.get('last_time_block', 'N/A')}")
            print(f"   - average_vibe: {data.get('average_vibe', 0):.2f}")
            print(f"   - vibe_scores件数: {len(data.get('vibe_scores', []))}")
            print(f"   - insights: {data.get('insights', 'N/A')[:50]}...")
        else:
            print(f"❌ データが見つかりません")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_demo_data()
