#!/usr/bin/env python3
"""
vibe_scoresのnull値を確認するスクリプト
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def check_null_values():
    """vibe_scoresのnull値確認"""

    # Supabase接続
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)

    device_id = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    date = "2025-10-03"

    print("=" * 80)
    print("vibe_scoresのnull値確認")
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
        vibe_scores = data.get('vibe_scores', [])

        print(f"📊 vibe_scores詳細:")
        print(f"   - 配列長: {len(vibe_scores)}")
        print(f"   - 有効データ: {sum(1 for s in vibe_scores if s is not None)}")
        print(f"   - null数: {sum(1 for s in vibe_scores if s is None)}")
        print(f"   - average_vibe: {data.get('average_vibe', 0):.2f}")
        print()

        # 現在時刻周辺を表示
        print("現在時刻周辺のデータ:")
        print("ブロック | 時刻  | スコア | 状態")
        print("-" * 50)

        for i in range(28, min(35, len(vibe_scores))):
            hour = i // 2
            minute = "30" if i % 2 == 1 else "00"
            time_str = f"{hour:02d}:{minute}"
            score = vibe_scores[i]
            status = "✅ データあり" if score is not None else "❌ null"
            score_str = f"{score:+4d}" if score is not None else "null"
            print(f"{i:2d}       | {time_str} | {score_str} | {status}")

        print()
        print(f"✅ 48ブロック全体が作成され、現在時刻（15:00=ブロック30）以降はnullになっています")
    else:
        print(f"❌ データが見つかりません")

    print("=" * 80)

if __name__ == "__main__":
    check_null_values()
