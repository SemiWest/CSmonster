NOTION_TOKEN = "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"
DATABASE_ID = "261e339f1ae5802ca71acd96446868d5"

import unittest
import os
import requests
import json
import datetime
import time

# requests 라이브러리를 사용해 Notion API와 통신
def save_game_log_to_notion(player_name, final_gpa, final_level):
    """게임 결과를 Notion 데이터베이스에 저장"""
    if not all([NOTION_TOKEN, DATABASE_ID]):
        print("Notion 토큰 또는 DB ID가 설정되지 않았습니다. 환경 변수를 확인해주세요.")
        return False

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Notion 데이터베이스의 속성명에 맞게 데이터 구성
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "날짜": {
                "date": {
                    "start": datetime.datetime.now().isoformat()
                }
            },
            "이름": {
                "title": [
                    {
                        "text": {
                            "content": player_name
                        }
                    }
                ]
            },
            "최종 GPA": {
                "number": float(final_gpa) if final_gpa and str(final_gpa).replace('.', '').isdigit() else 0.0
            },
            "최종 레벨": {
                "number": final_level
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ 성공: {player_name}의 기록이 Notion에 저장되었습니다.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류: Notion API 호출 실패 - {e}")
        return False

def get_leaderboard_from_notion():
    """Notion 데이터베이스에서 순위 정보를 불러옴"""
    if not all([NOTION_TOKEN, DATABASE_ID]):
        print("Notion 토큰 또는 DB ID가 설정되지 않았습니다.")
        return []

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # 최종 GPA를 기준으로 내림차순 정렬
    sort_data = {
        "sorts": [
            {
                "property": "최종 GPA",
                "direction": "descending"
            }
        ]
    }

    try:
        print("🔗 Notion 데이터베이스에서 순위표를 조회합니다...")
        response = requests.post(url, headers=headers, json=sort_data)
        response.raise_for_status()
        results = response.json().get("results", [])

        leaderboard = []
        for page in results:
            props = page.get("properties", {})
            name = props.get("이름", {}).get("title", [{}])[0].get("text", {}).get("content", "")
            gpa = props.get("최종 GPA", {}).get("number", 0.0)
            if name and gpa is not None:
                leaderboard.append({"name": name, "gpa": gpa})

        return leaderboard
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류: Notion API 순위 조회 실패 - {e}")
        return []

# --- 테스트 실행 ---
if __name__ == '__main__':
    # 테스트에 사용할 가상 플레이어 데이터 생성
    test_player_name = f"테스트_{datetime.datetime.now().strftime('%H%M%S')}"
    test_gpa = 4.0 + (datetime.datetime.now().second % 6) * 0.1
    test_level = 10

    # 1단계: 더미 데이터 입력
    print("--- Notion DB에 기록 입력 테스트 ---")
    save_game_log_to_notion(test_player_name, test_gpa, test_level)
    print("\n")
    time.sleep(2) # Notion API가 업데이트될 시간을 2초간 기다림

    # 2단계: 입력한 데이터 포함, 전체 데이터베이스 조회
    print("--- Notion DB에서 기록 조회 테스트 ---")
    leaderboard = get_leaderboard_from_notion()

    if leaderboard:
        print("✅ 순위표 조회 성공!")
        for i, entry in enumerate(leaderboard):
            print(f"  {i+1}. 이름: {entry['name']}, GPA: {entry['gpa']}")
    else:
        print("❌ 순위표 조회 실패 또는 데이터가 없습니다.")