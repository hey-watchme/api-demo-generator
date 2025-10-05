#!/usr/bin/env python3
"""
Demo Data Generator API
複数のペルソナ（子供、大人、高齢者など）のデモデータを動的に生成するAPI

使用例:
- Lambda関数からAPI呼び出し
- 手動でペルソナ指定してデータ生成
- カタログとして複数ユーザーのデモデータ管理
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
import os

# FastAPIアプリ
app = FastAPI(
    title="WatchMe Demo Data Generator API",
    description="デモユーザーのdashboard_summaryデータを動的に生成",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_KEY")


# ペルソナ定義
PERSONAS = {
    "child_5yo": {
        "name": "5歳男児（幼稚園年長）",
        "device_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",  # デモ用UUID
        "description": "白幡幼稚園の年長さん、趣味はマインクラフト",
        "profile": {
            "age": 5,
            "gender": "male",
            "occupation": "幼稚園年長",
            "hobbies": ["マインクラフト", "ブロック遊び"]
        }
    },
    "adult_30s": {
        "name": "30代会社員（男性）",
        "device_id": "00000000-0000-0000-0001-000000000002",  # デモ用UUID
        "description": "IT企業勤務、在宅ワーク中心",
        "profile": {
            "age": 35,
            "gender": "male",
            "occupation": "会社員（エンジニア）",
            "hobbies": ["プログラミング", "読書", "ゲーム"]
        }
    },
    "elderly_70s": {
        "name": "70代高齢者（女性）",
        "device_id": "00000000-0000-0000-0001-000000000003",  # デモ用UUID
        "description": "退職後、趣味の園芸を楽しむ",
        "profile": {
            "age": 72,
            "gender": "female",
            "occupation": "退職",
            "hobbies": ["園芸", "散歩", "読書"]
        }
    }
}


# リクエスト/レスポンスモデル
class GenerateRequest(BaseModel):
    persona_id: str
    date: Optional[str] = None  # YYYY-MM-DD形式、省略時は今日
    time_block: Optional[str] = None  # HH-MM形式、省略時は現在時刻


class PersonaInfo(BaseModel):
    persona_id: str
    name: str
    device_id: str
    description: str
    profile: dict


# ユーティリティ関数
def get_jst_time():
    """JSTタイムゾーンで現在時刻を取得"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)


def calculate_time_block(jst_time: datetime) -> tuple:
    """現在時刻から時刻ブロック番号と文字列を計算"""
    block_index = (jst_time.hour * 2) + (1 if jst_time.minute >= 30 else 0)
    block_str = f"{jst_time.hour:02d}-{'30' if jst_time.minute >= 30 else '00'}"
    return block_index, block_str


def generate_vibe_scores_until(block_index: int, persona_id: str) -> List:
    """ペルソナと時刻に応じたvibe_scoresを生成（48ブロック、現在時刻以降はnull）"""

    if persona_id == "child_5yo":
        # 5歳児の1日のパターン（48ブロック = 24時間）
        base_pattern = [
            # 00:00-06:30 (0-12): 睡眠中 -5〜+5
            0, -2, -3, -5, -2, 0, 2, 3, 5, 2, 0, -2, 3,
            # 07:00-08:30 (13-16): 起床・朝食 ピーク
            10, 25, 30, 35,
            # 09:00-11:30 (17-22): 午前活動（幼稚園）
            20, 15, 25, 30, 20, 15,
            # 12:00-13:30 (23-26): 昼食 ピーク
            35, 40, 35, 30,
            # 14:00-16:30 (27-32): 午後活動（遊び）
            25, 20, 30, 25, 20, 15,
            # 17:00-18:30 (33-36): 夕方（少し疲れ）
            10, 5, 0, -5,
            # 19:00-20:30 (37-40): 夕食・家族時間 ピーク
            20, 30, 35, 25,
            # 21:00-23:30 (41-47): 就寝準備〜睡眠 下降
            15, 10, 5, 0, -2, -3, -5, 0
        ]
    else:
        # 他のペルソナは後で実装
        base_pattern = [0] * 48

    # 48ブロック全体を作成し、現在時刻以降をnullにする
    result = []
    for i in range(48):
        if i <= block_index:
            result.append(base_pattern[i])
        else:
            result.append(None)

    return result


def generate_behavior_summary(block_index: int, persona_id: str) -> dict:
    """behavior_summary用のデータを生成"""
    if persona_id != "child_5yo":
        # child_5yo以外は空データを返す
        return {
            "summary_ranking": [],
            "time_blocks": {}
        }

    # 一般的な子供の行動イベントパターン
    all_events = [
        {"event": "話し声", "category": "voice", "priority": True},
        {"event": "子供の話し声", "category": "voice", "priority": True},
        {"event": "赤ちゃんの喃語", "category": "voice", "priority": True},
        {"event": "歌声", "category": "voice", "priority": True},
        {"event": "沸騰する音", "category": "daily_life", "priority": True},
        {"event": "Water sounds", "category": "daily_life", "priority": True},
        {"event": "Dishes", "category": "daily_life", "priority": True},
        {"event": "食器棚の開閉", "category": "daily_life", "priority": True},
        {"event": "低周波ノイズ", "category": "other", "priority": False},
        {"event": "動物", "category": "other", "priority": False},
        {"event": "室内（小部屋）", "category": "other", "priority": False},
        {"event": "音楽", "category": "other", "priority": False},
    ]

    # 時間帯ごとのイベントパターン（48ブロック）
    time_blocks = {}
    for i in range(48):
        hour = i // 2
        minute = "30" if i % 2 == 1 else "00"
        block_key = f"{hour:02d}-{minute}"

        # 現在時刻以降はスキップ（後でnullにする）
        if i > block_index:
            continue

        # 時間帯に応じたイベント
        events = []

        # 睡眠時間（00:00-06:30）
        if 0 <= i <= 12:
            events = [{"count": 3 + (i % 3), "event": "低周波ノイズ"}]
        # 朝の準備（07:00-08:30）
        elif 13 <= i <= 16:
            events = [
                {"count": 1, "event": "食器棚の開閉"},
                {"count": 2, "event": "話し声"},
                {"count": 1, "event": "Water sounds"}
            ]
        # 登園・活動時間（09:00-11:30）
        elif 17 <= i <= 22:
            events = [
                {"count": 6, "event": "話し声"},
                {"count": 2 + (i % 2), "event": "子供の話し声"}
            ]
        # 昼食時間（12:00-13:30）
        elif 23 <= i <= 26:
            events = [
                {"count": 6, "event": "話し声"},
                {"count": 2, "event": "Dishes"},
                {"count": 1, "event": "食器棚の開閉"}
            ]
        # 午後の活動（14:00-16:30）
        elif 27 <= i <= 32:
            events = [
                {"count": 4 + (i % 3), "event": "話し声"},
                {"count": 2, "event": "動物"}
            ]
        # 夕方（17:00-18:30）
        elif 33 <= i <= 36:
            events = [
                {"count": 5, "event": "Water sounds"},
                {"count": 2, "event": "音楽"},
                {"count": 1, "event": "Dishes"}
            ]
        # 夕食・家族時間（19:00-20:30）
        elif 37 <= i <= 40:
            events = [
                {"count": 6, "event": "話し声"},
                {"count": 2, "event": "Dishes"},
                {"count": 2, "event": "室内（小部屋）"}
            ]
        # 就寝準備（21:00-23:30）
        else:
            events = [
                {"count": 3, "event": "歌声"},
                {"count": 2, "event": "低周波ノイズ"}
            ]

        time_blocks[block_key] = events

    # summary_rankingを生成（全イベントの集計）
    summary_ranking = []
    event_counts = {}

    for block_events in time_blocks.values():
        for event_data in block_events:
            event_name = event_data["event"]
            if event_name not in event_counts:
                event_counts[event_name] = 0
            event_counts[event_name] += event_data["count"]

    # ランキング形式に変換
    for event_name, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        event_info = next((e for e in all_events if e["event"] == event_name),
                         {"category": "other", "priority": False})
        summary_ranking.append({
            "count": count,
            "event": event_name,
            "category": event_info["category"],
            "priority": event_info["priority"]
        })

    return {
        "summary_ranking": summary_ranking,
        "time_blocks": time_blocks
    }


def generate_emotion_graph(block_index: int, persona_id: str) -> List:
    """emotion_opensmile_summary用の感情グラフを生成（48ブロック）"""
    if persona_id != "child_5yo":
        # child_5yo以外は空配列を返す
        return []

    # 8感情のベースパターン（joy, fear, anger, trust, disgust, sadness, surprise, anticipation）
    # 子供の1日の感情パターン
    emotion_patterns = []

    for i in range(48):
        hour = i // 2
        minute = "30" if i % 2 == 1 else "00"
        time_str = f"{hour:02d}:{minute}"

        # 時間帯に応じた感情スコア
        # 睡眠時間（00:00-06:30）
        if 0 <= i <= 12:
            emotions = {"joy": 10, "fear": 0, "anger": 5, "trust": 5, "disgust": 1, "sadness": 0, "surprise": 2, "anticipation": 3}
        # 起床時間（07:00-08:30）
        elif 13 <= i <= 16:
            emotions = {"joy": 5, "fear": 1, "anger": 2, "trust": 4, "disgust": 0, "sadness": 3, "surprise": 2, "anticipation": 3}
        # 活動時間（09:00-11:30）
        elif 17 <= i <= 22:
            emotions = {"joy": 10, "fear": 0, "anger": 0, "trust": 5, "disgust": 0, "sadness": 2, "surprise": 2, "anticipation": 3}
        # 昼食時間（12:00-13:30）
        elif 23 <= i <= 26:
            emotions = {"joy": 7, "fear": 2, "anger": 5, "trust": 3, "disgust": 1, "sadness": 8, "surprise": 2, "anticipation": 2}
        # 午後の活動（14:00-16:30）
        elif 27 <= i <= 32:
            emotions = {"joy": 0, "fear": 0, "anger": 10, "trust": 0, "disgust": 2, "sadness": 0, "surprise": 0, "anticipation": 0}
        # 夕方（17:00-18:30）
        elif 33 <= i <= 36:
            emotions = {"joy": 10, "fear": 1, "anger": 5, "trust": 5, "disgust": 2, "sadness": 2, "surprise": 2, "anticipation": 4}
        # 夕食・家族時間（19:00-20:30）
        elif 37 <= i <= 40:
            emotions = {"joy": 0, "fear": 0, "anger": 10, "trust": 0, "disgust": 2, "sadness": 0, "surprise": 0, "anticipation": 0}
        # 就寝準備（21:00-23:30）
        else:
            emotions = {"joy": 10, "fear": 1, "anger": 3, "trust": 5, "disgust": 1, "sadness": 5, "surprise": 2, "anticipation": 3}

        # 現在時刻以降はnullにする
        if i <= block_index:
            emotion_data = {**emotions, "time": time_str}
            emotion_patterns.append(emotion_data)
        else:
            # 将来的にはnullを入れる予定だが、配列なので要素自体を追加しない
            pass

    return emotion_patterns


def generate_prompt(persona_id: str, date: str, block_index: int) -> str:
    """ペルソナと時刻に応じたプロンプトを生成"""
    persona = PERSONAS.get(persona_id)
    if not persona:
        return "Unknown persona"

    # TODO: ペルソナと時刻に応じた動的プロンプト生成
    return f"""## 1日全体の総合分析依頼

### 分析対象
観測対象者: {persona['name']}
日付: {date}
時刻ブロック: {block_index + 1}/48

### プロファイル
- 年齢: {persona['profile']['age']}歳
- 性別: {persona['profile']['gender']}
- 職業/所属: {persona['profile']['occupation']}
- 趣味: {', '.join(persona['profile']['hobbies'])}

[動的に生成されたプロンプト内容がここに入ります]
"""


def generate_demo_data(persona_id: str, date: str, block_index: int, block_str: str) -> dict:
    """デモデータを生成"""
    persona = PERSONAS.get(persona_id)
    if not persona:
        raise ValueError(f"Unknown persona: {persona_id}")

    vibe_scores = generate_vibe_scores_until(block_index, persona_id)

    # nullを除外してaverage_vibeを計算
    valid_scores = [score for score in vibe_scores if score is not None]
    average_vibe = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    # burst_eventsを生成（大きな変化点を検出）
    burst_events = []
    for i in range(1, len(vibe_scores)):
        if vibe_scores[i] is not None and vibe_scores[i-1] is not None:
            change = vibe_scores[i] - vibe_scores[i-1]
            # 変化量が15以上、またはスコアのゼロクロス時にバーストイベントとして記録
            if abs(change) >= 15 or (vibe_scores[i-1] * vibe_scores[i] < 0):
                hour = i // 2
                minute = "30" if i % 2 == 1 else "00"
                time_str = f"{hour:02d}:{minute}"

                # イベント説明を生成
                if persona_id == "child_5yo":
                    if i == 14:
                        event = "朝の起床・準備で機嫌が上昇した"
                    elif i == 24:
                        event = "園での昼食時間で気分が大幅に向上"
                    elif i == 13:
                        event = "起床時の気分向上"
                    else:
                        if change > 0:
                            event = "気分が向上した"
                        else:
                            event = "気分が落ち着いた"
                else:
                    event = "気分の変化"

                burst_events.append({
                    "time": time_str,
                    "event": event,
                    "score_change": change,
                    "from_score": vibe_scores[i-1],
                    "to_score": vibe_scores[i]
                })

    # analysis_resultを生成
    analysis_result = {
        "raw_response": "デモデータのため省略",
        "processing_error": None,
        "extracted_content": f"デモユーザー（{persona['name']}）の分析結果"
    }

    # insightsを生成
    if persona_id == "child_5yo":
        insights = "朝から昼にかけて、徐々に機嫌が高まり、起床・準備での前向きさが見られた。午前中の園での活動を経て気分は安定域に達し、午後の遊び時間で活発な様子が続いた。デモデータとして生成されたパターンです。"
    else:
        insights = f"{persona['name']}のデモデータ（{block_str}時点）"

    data = {
        "device_id": persona["device_id"],
        "date": date,
        "prompt": generate_prompt(persona_id, date, block_index),
        "processed_count": block_index + 1,
        "last_time_block": block_str,
        "created_at": get_jst_time().isoformat(),
        "updated_at": get_jst_time().isoformat(),
        "average_vibe": average_vibe,
        "insights": insights,
        "analysis_result": analysis_result,
        "vibe_scores": vibe_scores,
        "burst_events": burst_events
    }

    return data


# APIエンドポイント
@app.get("/")
async def root():
    return {
        "service": "WatchMe Demo Data Generator API",
        "version": "1.0.0",
        "endpoints": {
            "personas": "/personas",
            "generate": "/generate"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": get_jst_time().isoformat()}


@app.get("/personas", response_model=List[PersonaInfo])
async def list_personas():
    """利用可能なペルソナ一覧を取得"""
    return [
        PersonaInfo(
            persona_id=pid,
            name=p["name"],
            device_id=p["device_id"],
            description=p["description"],
            profile=p["profile"]
        )
        for pid, p in PERSONAS.items()
    ]


@app.post("/generate")
async def generate_and_save(request: GenerateRequest):
    """デモデータを生成してSupabaseに保存（3つのテーブル）"""

    # Supabase接続確認
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")

    # ペルソナ確認
    if request.persona_id not in PERSONAS:
        raise HTTPException(status_code=404, detail=f"Persona '{request.persona_id}' not found")

    # child_5yo以外は一旦スキップ
    if request.persona_id != "child_5yo":
        raise HTTPException(status_code=400, detail=f"Only 'child_5yo' is currently supported")

    # 日付・時刻の決定
    jst_now = get_jst_time()
    date = request.date or str(jst_now.date())

    if request.time_block:
        # 手動指定の時刻ブロック
        try:
            hour, minute = map(int, request.time_block.split('-'))
            block_index = (hour * 2) + (1 if minute >= 30 else 0)
            block_str = request.time_block
        except:
            raise HTTPException(status_code=400, detail="Invalid time_block format. Use HH-MM")
    else:
        # 現在時刻から自動計算
        block_index, block_str = calculate_time_block(jst_now)

    try:
        # 1. dashboard_summaryのデータ生成
        demo_data = generate_demo_data(request.persona_id, date, block_index, block_str)

        # 2. behavior_summaryのデータ生成
        behavior_data = generate_behavior_summary(block_index, request.persona_id)
        behavior_record = {
            "device_id": PERSONAS[request.persona_id]["device_id"],
            "date": date,
            "summary_ranking": behavior_data["summary_ranking"],
            "time_blocks": behavior_data["time_blocks"]
        }

        # 3. emotion_opensmile_summaryのデータ生成
        emotion_graph = generate_emotion_graph(block_index, request.persona_id)
        emotion_record = {
            "device_id": PERSONAS[request.persona_id]["device_id"],
            "date": date,
            "emotion_graph": emotion_graph,
            "file_path": "",
            "created_at": get_jst_time().isoformat()
        }

        # Supabaseに保存（3つのテーブル）
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # dashboard_summaryに保存
        result1 = supabase.table("dashboard_summary").upsert(demo_data).execute()

        # behavior_summaryに保存
        result2 = supabase.table("behavior_summary").upsert(behavior_record).execute()

        # emotion_opensmile_summaryに保存
        result3 = supabase.table("emotion_opensmile_summary").upsert(emotion_record).execute()

        return {
            "success": True,
            "persona_id": request.persona_id,
            "device_id": demo_data["device_id"],
            "date": date,
            "time_block": block_str,
            "processed_count": demo_data["processed_count"],
            "tables_updated": ["dashboard_summary", "behavior_summary", "emotion_opensmile_summary"],
            "message": "Demo data generated and saved successfully to all tables"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating demo data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
