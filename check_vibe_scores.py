#!/usr/bin/env python3
"""
vibe_scoresの内容を詳細確認するスクリプト
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def check_vibe_scores():
    """vibe_scoresの詳細確認"""

    # Supabase接続
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)

    device_id = "00000000-0000-0000-0001-000000000001"
    date = "2025-10-03"

    print("=" * 60)
    print("子供（5歳）のvibe_scores確認")
    print("=" * 60)
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
        vibe_scores = data.get('vibe_scores', [])

        print(f"📊 vibe_scores詳細:")
        print(f"   - 件数: {len(vibe_scores)}")
        print(f"   - average_vibe: {data.get('average_vibe', 0):.2f}")
        print()

        # 時刻ブロックごとに表示
        print("時刻 | ブロック | スコア | 説明")
        print("-" * 60)

        time_descriptions = {
            0: "00:00 - 睡眠中",
            13: "07:00 - 起床・朝食",
            17: "09:00 - 午前活動（幼稚園）",
            23: "12:00 - 昼食",
            27: "14:00 - 午後活動（遊び）",
            33: "17:00 - 夕方（疲れ）",
            37: "19:00 - 夕食・家族時間",
            41: "21:00 - 就寝準備"
        }

        for i, score in enumerate(vibe_scores):
            hour = i // 2
            minute = "30" if i % 2 == 1 else "00"
            time_str = f"{hour:02d}:{minute}"
            desc = time_descriptions.get(i, "")
            print(f"{time_str} | {i:2d} | {score:+4d} | {desc}")

        print()
        print(f"✅ 15:00時点で{len(vibe_scores)}ブロックのデータ生成完了")
        print(f"   （それ以降のデータはまだ生成されていません）")
    else:
        print(f"❌ データが見つかりません")

    print("=" * 60)

if __name__ == "__main__":
    check_vibe_scores()
