import csv
from ForGrd.battleForGrd import *
import copy
import logging
# [수정] datetime에서 필요한 클래스를 직접 가져옵니다.
import os, pygame, hashlib, time
from datetime import datetime, timezone, timedelta 
import qrcode
from typing import Optional
import requests
import json
import os
import dropbox
import numpy as np

logger = logging.getLogger(__name__)

NOTION_TOKEN = "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"
DATABASE_ID = "261e339f1ae5802ca71acd96446868d5"
# Dropbox API 인증 정보 (리프레시 토큰 방식)
# generate_refresh_token.py를 통해 얻은 값들을 여기에 입력합니다.
DROPBOX_APP_KEY = "1ii2zxyvjattedf"
DROPBOX_APP_SECRET = "8co8pfh4n6ibpun"
DROPBOX_REFRESH_TOKEN = "_NvgGhQ4hJoAAAAAAAAAAeyYKpolu93vrUu9Az9xCGOQLNxb5iH85LGSdnyccn9t"

# 아래 두 변수는 이제 사용하지 않으므로 주석 처리하거나 삭제합니다.
# DROPBOX_ACCESS_TOKEN = "sl.u.AF-2R..."
DROPBOX_UPLOAD_FOLDER = "/uploads/csmonster"


headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28", # 최신 버전을 확인하고 사용
}

def save_cropped_and_return_path(screen, player_name, crop_w, crop_h, top_margin, out_dir, prefix):
    """
    화면을 크롭하여 파일로 저장하고, 저장된 파일 경로만 반환합니다.
    """
    os.makedirs(out_dir, exist_ok=True)
    
    sw, sh = screen.get_size()
    left = max(0, (sw - crop_w) // 2)
    top = max(0, top_margin)
    if left + crop_w > sw:
        left = max(0, sw - crop_w)
    if top + crop_h > sh:
        top = max(0, sh - crop_h)

    rect = pygame.Rect(left, top, crop_w, crop_h)
    cropped = screen.subsurface(rect)

    name_hash = hashlib.sha256(player_name.encode()).hexdigest()[:8]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"{prefix}_{name_hash}_{ts}.png")

    pygame.image.save(cropped, path)
    logger.info(f"Debug: 임시 이미지 저장 완료: {path}")
    return path

def combine_for_share(background_path, transcript_path, deans_list_path, player_name, out_dir="results/combined_images"):
    """
    졸업 성적표와 딘즈 리스트 이미지를 하나의 배경 이미지에 합성하여 저장합니다.
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # 이미지 로드
    try:
        bg_image = pygame.image.load(background_path)
        transcript_img = pygame.image.load(transcript_path)
        deans_list_img = pygame.image.load(deans_list_path)
    except pygame.error as e:
        logger.error(f"Debug: 이미지 로드 오류 - {e}")
        return None

    # 이미지 비율 조정 (리사이즈)
    transcript_resized = pygame.transform.smoothscale(transcript_img, (800, 640))
    deans_list_resized = pygame.transform.smoothscale(deans_list_img, (560, 793))

    # 배경 이미지에 합성
    # background 이미지의 크기 (1080x1920)
    bg_width, bg_height = bg_image.get_size()

    # 가로 중앙 정렬
    transcript_x = (bg_width - transcript_resized.get_width()) // 2
    deans_list_x = (bg_width - deans_list_resized.get_width()) // 2
    
    # 세로 위치 계산
    deans_list_y = 291  # 윗 끝부분 마진 291
    transcript_y = bg_height - transcript_resized.get_height() - 135 # 아래 끝부분 마진 135

    # 합성
    bg_image.blit(deans_list_resized, (deans_list_x, deans_list_y))
    bg_image.blit(transcript_resized, (transcript_x, transcript_y))

    # 최종 이미지 저장
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_hash = hashlib.sha256(player_name.encode()).hexdigest()[:8]
    final_filename = f"combined_{name_hash}_{ts}.png"
    final_path = os.path.join(out_dir, final_filename)
    
    pygame.image.save(bg_image, final_path)
    logger.info(f"Debug: 합성 이미지 저장 완료: {final_path}")
    
    return final_path

def save_game_log_to_notion(player):
    """
    게임 결과를 Notion 데이터베이스에 저장하고, 생성된 페이지의 ID를 반환합니다.
    player 객체에서 필요한 정보를 추출하여 Notion API에 전송합니다.
    """
    url = "https://api.notion.com/v1/pages"

    # player 객체로부터 데이터 추출 (기존과 동일)
    gpa = player.calcGPA(2)
    # [수정됨] 한국 시간(KST, GMT+9)을 명시적으로 설정합니다.
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst).isoformat() # datetime을 한번 더 써줌
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "날짜": {"date": {"start": now}},
            "이름": {"title": [{"text": {"content": player.name}}]},
            "인스타그램": {"rich_text": [{"text": {"content": player.instagram_id or ""}}]},
            "최종 GPA": {"number": float(gpa) if gpa and str(gpa).replace('.', '').isdigit() else 0.0},
            "최종 레벨": {"number": player.level},
            "딘즈 횟수": {"number": player.deans_count},
            "장짤 횟수": {"number": player.jangzal_count},
            "학사경고 횟수": {"number": player.warning_count},
            "최종 학기": {"rich_text": [{"text": {"content": player.current_semester}}]},
            "엔딩 타입": {"rich_text": [{"text": {"content": player.ending_type}}]},
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        page_id = response.json().get("id") # 생성된 페이지의 ID 추출
        logger.info(f"'{player.name}'의 게임 기록을 Notion에 저장했습니다.")
        return True, page_id  # 성공 여부와 페이지 ID를 함께 반환
    except requests.exceptions.RequestException as e:
        logger.error(f"Notion API 호출 실패: {e}")
        return False, None # 실패 시 ID는 None

def update_notion_page_with_results(page_id, image_url):
    """
    주어진 page_id를 가진 Notion 페이지에 결과 이미지와 인스타그램 태그를 업데이트합니다.
    """
    if not page_id or not image_url:
        logger.error("Debug: 업데이트 실패: 페이지 ID 또는 이미지 URL이 없습니다.")
        return False

    url = f"https://api.notion.com/v1/pages/{page_id}"

    properties_to_update = {
        "properties": {
            "결과": {
                # [수정됨] "결과" 속성을 rich_text 타입으로 설정
                "rich_text": [
                    {
                        "text": {
                            "content": image_url
                        }
                    }
                ]
            }
        }
    }

    try:
        # 페이지를 업데이트할 때는 POST가 아닌 PATCH 메서드를 사용합니다.
        response = requests.patch(url, headers=headers, json=properties_to_update)
        response.raise_for_status()
        logger.info("Debug: 업데이트 성공: Notion 페이지에 이미지와 태그가 추가되었습니다.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Debug: 업데이트 오류: Notion 페이지 업데이트 실패 - {e}")
        # 오류 발생 시 응답 내용 출력
        if response is not None:
            logger.error(f"Debug: Notion Response: {response.json()}")
        return False
    
def get_leaderboard_from_notion():
    """
    Notion 데이터베이스에서 모든 기록을 '끝까지' 가져옵니다. (페이지네이션 지원)
    반환값 형식은 기존과 동일: list[dict]
    """
    if not all([NOTION_TOKEN, DATABASE_ID]):
        logger.warning("Debug: [Warning!] Notion 토큰 또는 DB ID가 설정되지 않았습니다.")
        return []

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    # 한 번에 100개씩 가져오되, has_more/next_cursor로 반복
    payload = {
        "page_size": 100,
        # 필요하면 정렬 추가 (예: 날짜 내림차순)
        # "sorts": [{"property": "날짜", "direction": "descending"}]
    }

    results_all = []
    next_cursor = None
    has_more = True

    try:
        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            pages = data.get("results", [])
            for page in pages:
                props = page.get("properties", {})

                # 안전한 추출 유틸
                def safe_title(p):
                    arr = p.get("title", [])
                    if arr and "text" in arr[0]:
                        return arr[0]["text"].get("content", "")
                    # 다른 경우도 대비(예: plain_text)
                    if arr and "plain_text" in arr[0]:
                        return arr[0].get("plain_text", "")
                    return ""

                def safe_rich_text(p):
                    arr = p.get("rich_text", [])
                    if arr:
                        t = arr[0].get("text", {})
                        return t.get("content", "") or arr[0].get("plain_text", "")
                    return ""

                record_date = props.get("날짜", {}).get("date", {}).get("start", "")
                name = safe_title(props.get("이름", {}))
                gpa = props.get("최종 GPA", {}).get("number", 0.0)
                level = props.get("최종 레벨", {}).get("number", 0)
                deans_count = props.get("딘즈 횟수", {}).get("number", 0)
                jangzal_count = props.get("장짤 횟수", {}).get("number", 0)
                warning_count = props.get("학사경고 횟수", {}).get("number", 0)
                semester = safe_rich_text(props.get("최종 학기", {}))
                ending_type = safe_rich_text(props.get("엔딩 타입", {}))

                results_all.append({
                    '날짜': record_date,
                    'name': name,
                    'gpa': float(gpa) if gpa is not None else 0.0,
                    'level': level,
                    'deans_count': deans_count,
                    'jangzal_count': jangzal_count,
                    'warning_count': warning_count,
                    'semester': semester,
                    'ending_type': ending_type,
                })

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor", None)

        return results_all

    except requests.exceptions.RequestException as e:
        logger.error(f"Debug: 조회 오류: Notion API 순위 조회 실패 - {e}")
        return []

def update_and_save_csv(notion_records, filename="deans_list.csv", out_dir="results/deans"):
    """
    Notion 기록을 가져와 기존 CSV와 병합하고 새로운 기록을 식별하여 저장합니다.
    """
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    
    existing_records = []
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_records = [row for row in reader]

    existing_identifiers = set()
    for row in existing_records:
        identifier = (row.get('날짜', ''), row.get('이름', ''), str(row.get('최종 GPA', '')))
        existing_identifiers.add(identifier)

    new_records_to_add = []
    for record in notion_records:
        identifier = (record.get('날짜', ''), record.get('이름', ''), str(record.get('최종 GPA', '')))
        if identifier not in existing_identifiers:
            new_records_to_add.append(record)

    if not new_records_to_add:
        logger.info("Debug: CSV에 추가할 새로운 기록이 없습니다.")
        return True, "CSV 파일이 최신 상태입니다."

    write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    with open(filepath, 'a', newline='', encoding='utf-8') as file:
        fieldnames = list(notion_records[0].keys()) if notion_records else []
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if write_header:
            writer.writeheader()
        
        writer.writerows(new_records_to_add)

    logger.info(f"Debug: CSV 파일이 업데이트되었습니다. 새로운 기록 {len(new_records_to_add)}개 추가.")
    return True, f"게임 결과가 {filename}에 저장되었습니다."

def show_deans_list(player, screen, leaderboard, stats):
    """
    Deans List를 화면에 표시합니다.
    - 상위 10위 표기 (1~3등: 금/은/동 텍스트 색)
    - 플레이어 기록을 현재 순위표에 반영(없으면 추가 / 있으면 최신 GPA로 업데이트)
    - 플레이어가 10위권에 들면 축하 메시지(1~3등은 강렬 버전)
    - 플레이어가 10위 밖이지만 꼴찌 3명(불명예)도 아니면, 상/하 섹션 사이에 플레이어 등수/점수 표기
    - 불명예의 전당: GPA==0 이거나 정렬상 뒤에서 3명 안에 포함 시 붉은색으로 표기
    - 전체 기록 통계 및 플레이어의 상대적 위치(시그마) 표시
    """
    # 내부 유틸: 상위 랭크 색상 (Gold/Silver/Bronze)
    def _rank_color_for_top(rank: int):
        if rank == 1:
            return (255, 215, 0)   # Gold
        elif rank == 2:
            return (192, 192, 192) # Silver
        elif rank == 3:
            return (205, 127, 50)  # Bronze
        return BLACK

    def _gpa_color_default(gpa_value: float):
        try:
            return gpaColor(f"{gpa_value:.2f}")
        except Exception:
            return BLACK

    screen.fill(WHITE)
    draw_text(screen, "명예의 전당: Deans List", SCREEN_WIDTH // 2, 60, BLACK, size=48, align='center')
    draw_text(screen, "최종 GPA 기준", SCREEN_WIDTH // 2, 120, GRAY, size=24, align='center')

    # --- 통계 정보 표시 추가 ---
    stats_text = (
        f"전체 평균: {stats.get('mean', 0):.2f} | "
        f"중간값: {stats.get('median', 0):.2f} | "
        f"표준편차: {stats.get('std', 0):.2f}"
    )
    player_z_score = stats.get('z_score', 0)
    z_score_text = f"내 성적 위치: 평균으로부터 {player_z_score:+.2f}sigma"

    draw_text(screen, stats_text, SCREEN_WIDTH // 2, 150, (60, 60, 60), size=20, align='center')
    z_color = BLUE if player_z_score >= 0 else RED
    draw_text(screen, z_score_text, SCREEN_WIDTH // 2, 175, z_color, size=22, align='center')
    
    y_offset = 220  # 통계 표시 공간 확보를 위해 y_offset 조정
    # ---------------------------


    # 0) 플레이어 GPA/이름 확보
    player_name = getattr(player, 'name', None)
    try:
        player_gpa = float(player.calcGPA(2))
    except Exception:
        player_gpa = 0.0

    # 1) 플레이어 기록을 순위표에 반영(동명이인/미세 오차 고려)
    combined = []
    found = False
    for e in leaderboard:
        name = e.get('name')
        gpa  = float(e.get('gpa', 0.0))
        if not found and name == player_name and abs(gpa - player_gpa) < 1e-6:
            found = True
            combined.append({'name': name, 'gpa': player_gpa})
        else:
            combined.append({'name': name, 'gpa': gpa})
    if not found and player_name is not None:
        combined.append({'name': player_name, 'gpa': player_gpa})

    # 2) 정렬: 4.3 GPA를 최우선으로, 그 외는 GPA 내림차순, 동점 시 이름 오름차순
    combined.sort(key=lambda x: (x.get('gpa', 0.0) != 4.3, -x.get('gpa', 0.0), x.get('name', '')))

    # 3) 플레이어 순위 찾기 (1-indexed)
    player_rank = None
    player_entry = None
    for i, e in enumerate(combined, start=1):
        if e['name'] == player_name and abs(e['gpa'] - player_gpa) < 1e-6:
            player_rank = i
            player_entry = e
            break

    # 4) 상위 10위 출력
    top_k = min(10, len(combined))
    for i in range(top_k):
        e = combined[i]
        rank = i + 1
        rank_color = _rank_color_for_top(rank)
        
        name_color = rank_color if rank <= 3 else BLACK
        gpa_color  = rank_color if rank <= 3 else _gpa_color_default(e['gpa'])

        is_player_in_top10 = (player_entry and e['name'] == player_entry['name'] and abs(e['gpa'] - player_entry['gpa']) < 1e-6)
        is_bold = is_player_in_top10
        name_font_size = 36 if is_bold else 32
        
        draw_text(screen, f"{rank}.",            SCREEN_WIDTH//2 - 250, y_offset + i * 40, rank_color, size=32)
        draw_text(screen, e['name'],              SCREEN_WIDTH//2 - 180, y_offset + i * 40, name_color, size=name_font_size, bold=is_bold)
        draw_text(screen, f"{e['gpa']:.2f}",      SCREEN_WIDTH//2 + 200, y_offset + i * 40, gpa_color,  size=32, align='right')

    # 5) 플레이어 축하/안내 메시지 또는 중간 표기
    after_top_y = y_offset + top_k * 40
    message_lines = []
    if player_rank is not None and player_rank <= 10:
        if player_rank == 1:
            message_lines.append(("전설의 1위! 새로운 딘즈 리스트 정상에 올랐습니다!", (255, 215, 0)))
        elif player_rank == 2:
            message_lines.append(("2위 달성! 환상적인 성적입니다!", (192, 192, 192)))
        elif player_rank == 3:
            message_lines.append(("3위 입성! 탑 티어에 합류했습니다!", (205, 127, 50)))
        else:
            message_lines.append(("축하합니다! 새로운 딘즈 리스트 Top 10에 올랐습니다!", GREEN))
    elif player_entry is not None:
        bottom_count = min(3, len(combined))
        bottom_start_rank = len(combined) - bottom_count + 1
        is_in_disgrace_by_rank = (player_rank is not None and player_rank >= bottom_start_rank)
        is_in_disgrace_by_zero = (player_entry['gpa'] == 0)
        if not (is_in_disgrace_by_rank or is_in_disgrace_by_zero):
            y_mid = after_top_y + 28
            draw_text(screen, "----------------------------------", SCREEN_WIDTH//2, y_mid, GRAY, size=24, align='center')
            y_mid += 28
            draw_text(screen, f"{player_rank}.",            SCREEN_WIDTH//2 - 250, y_mid, BLUE, size=32)
            draw_text(screen, player_entry['name'],         SCREEN_WIDTH//2 - 180, y_mid, BLUE, size=32)
            draw_text(screen, f"{player_entry['gpa']:.2f}", SCREEN_WIDTH//2 + 200, y_mid, BLUE, size=32, align='right')
            after_top_y = y_mid + 28 

    if message_lines:
        y_msg = after_top_y + 28
        for text, color in message_lines:
            for line in text.splitlines():
                draw_text(screen, line, SCREEN_WIDTH//2, y_msg, color, size=28, align='center')
                y_msg += 36
        after_top_y = y_msg

    # 6) 불명예의 전당
    if len(combined) > 0:
        bottom_count = min(3, len(combined))
        disgrace_entries = combined[-bottom_count:]

        need_append_player_zero = False
        if player_entry is not None and player_entry['gpa'] == 0:
            if player_entry not in disgrace_entries:
                need_append_player_zero = True

        y_bottom = after_top_y + 28
        draw_text(screen, "----- 불명예의 전당 -----", SCREEN_WIDTH//2, y_bottom, RED, size=28, align='center')
        y_bottom += 28

        disgrace_rank_start = len(combined) - len(disgrace_entries) + 1
        for i, e in enumerate(disgrace_entries):
            rank = disgrace_rank_start + i
            draw_text(screen, f"{rank}.",       SCREEN_WIDTH//2 - 250, y_bottom + i * 40, RED, size=32)
            draw_text(screen, e['name'],         SCREEN_WIDTH//2 - 180, y_bottom + i * 40, RED, size=32)
            draw_text(screen, f"{e['gpa']:.2f}", SCREEN_WIDTH//2 + 200, y_bottom + i * 40, RED, size=32, align='right')

        if need_append_player_zero:
            y_extra = y_bottom + bottom_count * 40 + 20
            draw_text(screen, f"(특별) {player_rank}.",            SCREEN_WIDTH//2 - 250, y_extra, RED, size=28)
            draw_text(screen, player_entry['name'],                   SCREEN_WIDTH//2 - 180, y_extra, RED, size=28)
            draw_text(screen, f"{player_entry['gpa']:.2f}",          SCREEN_WIDTH//2 + 200, y_extra, RED, size=28, align='right')

    # 하단 안내
    draw_text(screen, "아무 키나 눌러 다음으로 넘어갑니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, GRAY, size=24, align='center')

    pygame.display.flip()
    wait_for_key()



def save_cropped_center(screen, player_name, crop_w=1200, crop_h=800, top_margin=60,
                        final_name=None, out_dir="results_screenshots", prefix="crop"):
    os.makedirs(out_dir, exist_ok=True)

    sw, sh = screen.get_size()  # 화면 해상도
    # 가로: 가운데 정렬
    left = max(0, (sw - crop_w) // 2)
    # 세로: 위에서 60px 지점부터 시작
    top = max(0, top_margin)

    # 화면 밖으로 나가지 않게 보정
    if left + crop_w > sw:
        left = max(0, sw - crop_w)
    if top + crop_h > sh:
        top = max(0, sh - crop_h)

    rect = pygame.Rect(left, top, crop_w, crop_h)
    cropped = screen.subsurface(rect)  # 일부분만 잘라오기

    if final_name:
        path = os.path.join(out_dir, final_name)
    else:
        # 파일명: 사용자 이름 해시 + 타임스탬프
        name_hash = hashlib.sha256(player_name.encode()).hexdigest()[:8]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"{prefix}_{name_hash}_{ts}.png")

    pygame.image.save(cropped, path)
    logger.info(f"[Saved] {path} @ {rect}")
    return path

# -----------------------------
# 2) Catbox 업로드 (영구 or Litterbox 임시)
#    - userhash가 있으면 계정 업로드
#    - temporary=True면 Litterbox(1h/12h/24h/72h)
# -----------------------------
import dropbox
import os

# upload_to_dropbox 함수를 찾아서 아래와 같이 수정합니다.

def upload_to_dropbox(file_path, dropbox_folder_path):
    """
    Dropbox에 파일을 업로드하고 공유 가능한 링크를 반환합니다.
    (리프레시 토큰을 사용하여 자동으로 액세스 토큰을 갱신합니다.)

    Args:
        file_path (str): 업로드할 로컬 파일의 경로.
        dropbox_folder_path (str): Dropbox 내에 파일을 저장할 경로 (예: '/uploads/').

    Returns:
        str: 공유 가능한 URL.
    """
    # Dropbox 객체 생성 시, 리프레시 토큰과 앱 키/시크릿을 전달합니다.
    # 이렇게 하면 라이브러리가 알아서 최신 액세스 토큰을 유지합니다.
    try:
        dbx = dropbox.Dropbox(
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
            oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
        )
        dbx.users_get_current_account() # 토큰 유효성 검사
        logger.info("Dropbox 계정 연결 성공 (토큰 자동 갱신).")
    except dropbox.exceptions.AuthError as e:
        logger.error(f"오류: 인증 정보(앱 키, 시크릿, 리프레시 토큰)가 유효하지 않습니다. {e}")
        return None

    # 파일 업로드 (이하 로직은 동일)
    try:
        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            dropbox_path = os.path.join(dropbox_folder_path, file_name).replace('\\', '/')

            logger.info(f"'{file_path}' 파일을 Dropbox의 '{dropbox_path}' 경로에 업로드 중...")

            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            logger.info("업로드 완료!")

        share_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        share_link = share_link_metadata.url
        logger.info(f"공유 링크 생성: {share_link}")

        download_link = share_link.replace('?dl=0', '?dl=1')
        logger.info(f"직접 다운로드 링크: {download_link}")

        return download_link

    except Exception as e:
        logger.error(f"파일 업로드 또는 링크 생성 중 오류 발생: {e}")
        return None

def make_qr(url, out_path="qr.png", target_px=300, border=4):
    # out_path가 속한 디렉토리가 없다면 생성
    dir_path = os.path.dirname(out_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,  # 임시값
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    modules = qr.modules_count + border * 2
    box_size = max(1, target_px // modules)  # 목표 픽셀에 맞춰 박스크기 재계산
    qr.box_size = box_size

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)
    return out_path


def _cleanup_old_files(dir_path: str, older_than_hours: int = 24) -> None:
    if not dir_path or not os.path.isdir(dir_path):
        return
    cutoff = time.time() - older_than_hours * 3600
    for name in os.listdir(dir_path):
        path = os.path.join(dir_path, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except Exception:
            # 조용히 무시(권한/사용중 파일 등)
            pass

def export_screen_to_catbox_qr(
    screen,
    player_name: str,
    crop_w: int = 1000,
    crop_h: int = 800,
    top_margin: int = 60,
    userhash: Optional[str] = None,
    temporary: bool = False,
    temp_time: str = "24h",
    out_dir: str = "screenshots",     # 스크린샷 폴더
    prefix: str = "transcript",
    qr_out_dir: str = "qrcodes",      # QR 전용 폴더 (screenshots와 분리)
    keep_hours: int = 24,             # 24시간 지난 파일은 삭제
):
    # 0) 디렉토리 준비 및 정리
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(qr_out_dir, exist_ok=True)
    _cleanup_old_files(out_dir, older_than_hours=keep_hours)
    _cleanup_old_files(qr_out_dir, older_than_hours=keep_hours)

    # 1) 화면 동기화
    pygame.display.flip()

    # 2) 공통 식별자(타임스탬프 + 이름 해시) — 스크린샷/QR 둘 다 동일 타임스탬프 사용
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_hash = hashlib.sha256(player_name.encode()).hexdigest()[:8]

    # 3) 크롭 저장 (파일명: prefix_namehash_ts.png)
    #    save_cropped_center 내부에서 파일명을 만들고 싶다면, 동일 규칙으로 수정하세요.
    #    여기서는 out_dir/prefix_namehash_ts.png 로 저장되었다고 가정해 경로를 강제 지정합니다.
    #    (save_cropped_center 가 반환하는 경로 대신, 아래와 같이 직접 저장하고 싶다면
    #     subsurface + pygame.image.save 로 구현해도 됩니다.)
    cropped_path = save_cropped_center(
        screen,
        player_name,
        crop_w=crop_w,
        crop_h=crop_h,
        top_margin=top_margin,
        final_name=f"{prefix}_{name_hash}_{ts}.png",
        out_dir=out_dir,
        prefix=prefix,
    )

    # 4) Catbox 업로드 (영구/임시)
    url = upload_to_dropbox(
    file_path=cropped_path,
    dropbox_folder_path=DROPBOX_UPLOAD_FOLDER
    )
    logger.info(url)
    # 5) QR 저장 (파일명: prefix_namehash_urlhash_ts.png, 저장 위치는 qr_out_dir)
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
    qr_name = f"{prefix}_{name_hash}_{url_hash}_{ts}.png"
    qr_path = os.path.join(qr_out_dir, qr_name)
    make_qr(url, out_path=qr_path)

    return {
        "image_path": cropped_path,  # screenshots/prefix_namehash_ts.png
        "url": url,                  # catbox URL
        "qr_path": qr_path,          # qrcodes/prefix_namehash_urlhash_ts.png
    }

def addSeonSus(player, monster):
    for mon_num in monster.SeonSu:
        monster_name = NumToName(mon_num)
        if monster_name not in player.canBeMetMonsters and monster_name not in player.clearedMonsters:
            player.canBeMetMonsters.append(monster_name)

def display_Monster_Imge(screen, monster, x, y, size=1):
    img = pygame.image.load(monster.image)
    img = pygame.transform.scale_by(img, size)
    height = img.get_height()
    screen.blit(img, (x, y-height//2))

def save_game_log_csv(filename, player):
    """게임 결과를 CSV에 저장"""
    # 절대 경로 생성
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, filename)

    # 파일이 저장될 디렉토리 경로
    dir_path = os.path.dirname(filepath)
    
    # 디렉토리가 없으면 생성 (재귀적으로 생성)
    os.makedirs(dir_path, exist_ok=True)
    
    # 파일이 없거나 비어 있으면 헤더 작성
    write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    
    # CSV 파일에 게임 결과 저장
    with open(filepath, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 헤더 작성
        if write_header:
            writer.writerow([
                '날짜', '이름', '최종 GPA', '최종 레벨', '딘즈 횟수', '장짤 횟수', '학사경고 횟수',
                '최종 학기', '엔딩 타입', '스킬1', '스킬1레벨', '스킬2', '스킬2레벨',
                '스킬3', '스킬3레벨', '스킬4', '스킬4레벨'
            ])
        
        # 게임 결과 데이터 저장
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        skillresult = []
        for skill, level in player.learned_skills.items():
            if level > 0:
                skillresult.append(skill)
                skillresult.append(str(level))
        gpa = player.calcGPA(2)
        logger.info(gpa)
        writer.writerow([
            now,
            player.name,
            gpa,
            player.level,
            player.deans_count,
            player.jangzal_count,
            player.warning_count,
            player.current_semester,
            player.ending_type,
            skillresult[0] if len(skillresult) > 0 else '',
            skillresult[1] if len(skillresult) > 1 else '',
            skillresult[2] if len(skillresult) > 2 else '',
            skillresult[3] if len(skillresult) > 3 else '',
            skillresult[4] if len(skillresult) > 4 else '',
            skillresult[5] if len(skillresult) > 5 else '',
            skillresult[6] if len(skillresult) > 6 else '',
            skillresult[7] if len(skillresult) > 7 else ''
        ])
        
    return True, f"게임 결과가 {filename}에 저장되었습니다."

def get_current_semester_monsters(player):
    length = len(player.canBeMetMonsters)
    if length <= 0:
        return False
    elif length == 1:
        player.thisSemesterMonsters = [player.canBeMetMonsters.pop()]
    else:
        a = player.canBeMetMonsters.pop(random.randint(0, length-1))
        b = player.canBeMetMonsters.pop(random.randint(0, length-2))
        player.thisSemesterMonsters = [a, b]
    return True

def semester_intro_screen(player, screen):
    """학기 시작 화면"""
    screen.fill(BLACK)
    
    semester_name = player.current_semester
    
    # 학기별 제목 설정
    if semester_name == "새터":
        title = "새터"
        description = ("당신은 카이스트에 갓 입학한 새내기입니다.", "당신은 자신이 전산학부에 걸맞는 인재인지 확인하기 위해 프로그래밍 기초 학점인정시험을 신청했습니다.")
    elif semester_name == "1-1":
        title = "1-1"
        description = ("프로그래밍 기초 학점인정시험을 통과한 당신은 전산학도의 길을 걷기로 결심하였습니다.", "당신은 전산학부의 필수 과목 중 하나를 선택하여 미리 듣기로 하였습니다.")
    elif semester_name == "2-1":
        title = "2-1"
        description = ("당신은 드디어 2학년이 되어 전산학부를 주전공으로 선택했습니다.", "이제부터 진짜 대학 생활의 시작입니다. 행운을 빕니다.")
    elif semester_name == "3-여름방학":
        title = "몰입 캠프"
        description = "당신은 몰입캠프 참가에 성공했습니다. 한달 간 코딩 실력을 키워봅시다."
    elif semester_name == "4-여름방학":
        title = "4-여름방학"
        description = "4-여름방학"
    else:
        title = f"{semester_name}"
        description = f"{semester_name}"
    
    # 제목과 설명 표시
    draw_text(screen, title, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-70, WHITE, size=64, align='center')
    if isinstance(description, tuple):
        for i, line in enumerate(description):
            draw_text(screen, line, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100 + i*40, WHITE, align='center')
    else:    
        draw_text(screen, description, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, WHITE, align='center')
    draw_text(screen, "아무 키나 눌러 넘어가기...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, GRAY, align='center')
    pygame.display.flip()
    wait_for_key()

    if "시프" in player.clearedMonsters and "2-1" in player.completed_semesters and "기계학습" not in player.clearedMonsters and "기계학습" not in player.canBeMetMonsters:
        player.canBeMetMonsters.append("기계학습")
    
    # 등장 과목 표시
    screen.fill(WHITE)
    draw_text(screen, f"현재 수강할 수 있는 과목들", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, BLACK, size=32, align='center')
    for i, monster_name in enumerate(player.canBeMetMonsters):
        if monster_name in player.clearedMonsters:
            draw_text(screen, f"{monster_name} (재수강)  ", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*40, GRAY, size=32, align='center')
            display_Monster_Imge(screen, monsters[monster_name], SCREEN_WIDTH//2 + len(monster_name)*16+80, SCREEN_HEIGHT//2 - 84 + i*40, size=2)
        else:
            draw_text(screen, f"{monster_name}  ", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*40, BLACK, size=32, align='center')
            display_Monster_Imge(screen, monsters[monster_name], SCREEN_WIDTH//2 + len(monster_name)*16+16, SCREEN_HEIGHT//2 - 84 + i*40, size=2)
    if player.cheatmode :
        draw_text(screen, "현재 이미 클리어한 과목들", SCREEN_WIDTH//2 + 500, SCREEN_HEIGHT//2-200, BLACK, size=32, align='center')
        for i, monster_name in enumerate(player.clearedMonsters):
            draw_text(screen, f"{monster_name}", SCREEN_WIDTH//2 + 500, SCREEN_HEIGHT//2 - 100 + i*40, BLUE, size=32, align='center')
            draw_text(screen, f"{player.gpas[i][0]}학점 {player.gpas[i][1]}", SCREEN_WIDTH//2 + 500 + 300, SCREEN_HEIGHT//2 - 100 + i*40, BLUE, size=32, align='right')
    draw_text(screen, "아무 키나 눌러 넘어가기...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, align='center')
    if semester_name != "새터":
        draw_text(screen, f"현재까지 받은 학사경고 횟수 {player.warning_count} / 3", SCREEN_WIDTH//2, SCREEN_HEIGHT - 120, align='center', color = RED, size=48)

    pygame.display.flip()
    wait_for_key()

    # 이번 학기 수강 과목 선택
    player.thisSemesterMonsters = []
    if semester_name == "3-여름방학":
        player.thisSemesterMonsters = ["몰입 캠프"]
        return
    elif semester_name == "4-여름방학":
        player.thisSemesterMonsters = random.choice([["Co-op"],["개별 연구"]])
        return
    else:
        # 수강신청
        options = player.canBeMetMonsters.copy()
        selected = 0
        text = "수강할 과목을 선택하세요. \n 최대 두 개의 과목을 선택할 수 있습니다. \n (선택: Enter / 초기화: Esc / 확정: -> / 조작: 방향키)"
        alartColor = WHITE
        while True:
            screen.fill(BLACK)
            
            draw_wrapped_text(screen, text, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-300, alartColor, 1300, align='center')
            
            if player.cheatmode :
                for i, monster_name in enumerate(player.canBeMetMonsters):
                    if monster_name in player.clearedMonsters:
                        draw_text(screen, f"{monster_name} (재수강)  ", SCREEN_WIDTH//2 + 500, SCREEN_HEIGHT//2 + i*40, GRAY, size=32, align='center')
                    else:
                        draw_text(screen, f"{monster_name}  ", SCREEN_WIDTH//2 + 500, SCREEN_HEIGHT//2 + i*40, WHITE, size=32, align='center')
                for i, monster_name in enumerate(player.thisSemesterMonsters):
                    draw_text(screen, f"{monster_name}", SCREEN_WIDTH//2 + 700, SCREEN_HEIGHT//2 + i*40, RED, size=32, align='center')
                
            for i, option in enumerate(options):
                color = typecolor_dict[monsters[option].type[0]] if i == selected or option in player.thisSemesterMonsters else WHITE
                draw_text(screen, option, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 32 - (len(options)-1)*40 + i*80, color, highlight = DARKGRAY if option in player.thisSemesterMonsters else None, align='center', size=64)
                if i == selected:
                    draw_text(screen, ">", SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 32 - (len(options)-1)*40 + i*80, WHITE, size=64)
                if i == selected or option in player.thisSemesterMonsters:
                    display_Monster_Imge(screen, monsters[option], SCREEN_WIDTH//2 + len(option)*32+96, SCREEN_HEIGHT//2 - (len(options)-1) * 40 + i*80, size=4)
            
            draw_text(screen, "방향키로 조작, Enter로 선택", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, GRAY, align='center')
            draw_text(screen, f"현재까지 받은 학사경고 횟수 {player.warning_count} / 3", SCREEN_WIDTH//2, SCREEN_HEIGHT - 120, align='center', color = RED, size=48)
            pygame.display.flip()
            key = wait_for_key(sound = False)
            if key == 'enter':
                if options[selected] in player.thisSemesterMonsters:
                    option_escape_sound()
                    # 옵션을 canBeMetMonsters의 원래 위치에 다시 삽입
                    player.canBeMetMonsters=options.copy()
                    player.thisSemesterMonsters.remove(options[selected])
                    for mon in player.thisSemesterMonsters:
                        player.canBeMetMonsters.remove(mon)
                else:
                    option_select_sound()
                    if len(player.thisSemesterMonsters) >= 2:
                        text = "최대 두 개의 과목까지만 선택할 수 있습니다!"
                        alartColor = RED
                        catching()
                        continue
                    if len(player.thisSemesterMonsters) >= 1 and player.current_semester == "1-1":
                        text = "1-1학기에는 한 과목만 수강할 수 있습니다!"
                        alartColor = RED
                        catching()
                        continue
                    player.thisSemesterMonsters.append(options[selected])
                    player.canBeMetMonsters.remove(options[selected])
            elif key == 'escape':
                option_escape_sound()
                # 옵션을 canBeMetMonsters의 원래 위치에 다시 삽입
                player.canBeMetMonsters=options.copy()
                player.thisSemesterMonsters = []
            elif key == 'up' and selected > 0:
                selected -= 1
                option_change_sound()
            elif key == 'down' and selected < len(options)-1:
                selected += 1
                option_change_sound()
            elif key == 'right':
                if len(player.thisSemesterMonsters) < 1:
                    text = "최소 한 개의 과목을 선택해야 합니다!"
                    alartColor = RED
                    catching()
                    continue
                option_select_sound()
                draw_wrapped_text(screen, "\n 정말로 수강 신청을 확정하시겠습니까? \n (예: 오른쪽 방향키 / 아니요: 왼쪽 방향키)", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-300, WHITE, 1300, align='center')
                pygame.display.flip()
                checkkey = wait_for_key(sound = False)
                if checkkey == 'right':
                    option_select_sound()
                    if player.current_semester == "1-1":
                        player.starting = monsters[player.thisSemesterMonsters[0]].type[0]
                    break
                elif checkkey == 'left':
                    option_escape_sound()
                    continue
            if len(player.thisSemesterMonsters) >= 1 or len(player.canBeMetMonsters) < 1: 
                text = "수강할 과목 선택이 완료되었다면 오른쪽 방향키를 입력해주세요."
                alartColor = GREEN
            else: 
                text = "수강할 과목을 선택하세요. \n 최대 세 개의 과목을 선택할 수 있습니다. \n (선택: Enter / 초기화: Esc / 확정: -> / 조작: 방향키)"
                alartColor = WHITE

    screen.fill(WHITE)

    draw_text(screen, "이번 학기에 수강할 과목", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, BLACK, align='center') 
    for i, monster_name in enumerate(player.thisSemesterMonsters):
        if monster_name in player.clearedMonsters:
            draw_text(screen, f"{monster_name} (재수강)",           SCREEN_WIDTH//2,                            SCREEN_HEIGHT//2 - 32 - (len(player.thisSemesterMonsters)-1)*40 + i*80, GRAY, size=64, align='center')
            display_Monster_Imge(screen, monsters[monster_name],    SCREEN_WIDTH//2 + len(monster_name)*32+288, SCREEN_HEIGHT//2 - (len(player.thisSemesterMonsters)-1)*40 + i*80, size=4)
        else:
            draw_text(screen, f"{monster_name}",                    SCREEN_WIDTH//2,                            SCREEN_HEIGHT//2 - 32 - (len(player.thisSemesterMonsters)-1)*40 + i*80, BLACK, size=64, align='center')
            display_Monster_Imge(screen, monsters[monster_name],    SCREEN_WIDTH//2 + len(monster_name)*32+96,  SCREEN_HEIGHT//2 - (len(player.thisSemesterMonsters)-1)*40 + i*80, size=4)
    draw_text(screen, "아무 키나 눌러 시작...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, align='center')
    if semester_name != "새터":
        draw_text(screen, f"현재까지 받은 학사경고 횟수 {player.warning_count} / 3", SCREEN_WIDTH//2, SCREEN_HEIGHT - 120, align='center', color = RED, size=48)
    pygame.display.flip()
    wait_for_key()

def semester_result_screen(player, screen):
    """학기 결과 화면"""
    mute_music()
    screen.fill(WHITE)
    if monsters[player.thisSemesterMonsters[0]].type[0] == "EVENT":
        if player.thisSemesterGpas[0][1] == "성공!":
            Report()
            lup_amt = player.molcam
            boolean = player.event_success
            if lup_amt > 0 or boolean:
                draw_text(screen, f"{player.thisSemesterMonsters[0]} 이벤트에 성공하였습니다!", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
            else:
                draw_text(screen, f"{player.thisSemesterMonsters[0]} 이벤트를 노력했으나 결실을 맺지 못했다...", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
            draw_text(screen, f"{monsters[player.thisSemesterMonsters[0]].reward}", SCREEN_WIDTH//2, 200, BLUE, align='center')
        else:
            Lose()
            draw_text(screen, f"{monsters[player.thisSemesterMonsters[0]].name} 이벤트에 실패하였습니다...", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
        
    else: 
        # 학기 결과 제목
        draw_text(screen, f"성적표", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
        
        # 이번 학기 수강 과목당 성적 표시
        y_offset = 240

        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-200, y_offset - 20), (SCREEN_WIDTH//2+200, y_offset - 20), 2)
        draw_text(screen,       f"과목명",                            SCREEN_WIDTH//2-200, y_offset)
        draw_text(screen,       f"성적",                              SCREEN_WIDTH//2+200, y_offset, align='right')
        y_offset += 60
        for i in range(min(len(player.thisSemesterMonsters), len(player.thisSemesterGpas))):
            monster_name = player.thisSemesterMonsters[i]
            gpa_data = player.thisSemesterGpas[i]

            draw_text(screen,   f"{monster_name}",                      SCREEN_WIDTH//2-200, y_offset + i*40, BLACK)
            display_Monster_Imge(screen, monsters[monster_name], SCREEN_WIDTH//2 -200 + len(monster_name)*32+32, y_offset + i*40 + 16, size=2)
            draw_text(screen,   f"{gpa_data[1]}",                       SCREEN_WIDTH//2+200, y_offset + i*40, gpaColor(gpa_data[1]), align='right')
                
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-200, y_offset + len(player.thisSemesterMonsters)*40 + 20), (SCREEN_WIDTH//2+200, y_offset + len(player.thisSemesterMonsters)*40 + 20), 2)
        y_offset += len(player.thisSemesterMonsters)*40 + 60

        # GPA 계산(문자 또는 숫자 문자열 가능)
        sem_gpa = player.calcGPA(1)     # "P" / "NR" / "3.85" 등
        cum_gpa = player.calcGPA(2)

        draw_text(screen,       f"학기 GPA", SCREEN_WIDTH//2-200, y_offset)
        draw_text(screen,       f"{sem_gpa}", SCREEN_WIDTH//2+200, y_offset, gpaColor(sem_gpa), align='right')
        draw_text(screen,       f"누적 GPA", SCREEN_WIDTH//2-200, y_offset + 40)
        draw_text(screen,       f"{cum_gpa}", SCREEN_WIDTH//2+200, y_offset + 40, gpaColor(cum_gpa), align='right')
        
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-200, y_offset + 100), (SCREEN_WIDTH//2+200, y_offset + 100), 2)
        y_offset += 140

        draw_text(screen, "비고", SCREEN_WIDTH//2, y_offset, BLACK, size=32, align='center')
        y_offset += 40

        # 안전한 숫자 변환
        def _to_float_or_none(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return None

        sem_gpa_num = _to_float_or_none(sem_gpa)

        # 비고 로직
        y_offset_before = y_offset
        if player.current_semester == "새터":
            draw_text(screen, f"새터를 무사히 통과해 체력을 모두 회복하였습니다.", SCREEN_WIDTH//2, y_offset, BLACK, align='center')
            player.current_hp = player.update_fullreset()
            y_offset += 40
        if player.mylevelup != None:
            draw_text(screen, f"레벨 {player.mylevelup}로 레벨업했습니다!", SCREEN_WIDTH//2, y_offset, GREEN, align='center')
            y_offset += 40
        if any(player.skilllevelup):
            subjects = ["*", "CT", "DS", "SYS", "PS", "AI"]
            for i, improved in enumerate(player.skilllevelup):
                if improved:
                    nowSkillLevel = player.learned_skills[subjects[i]]
                    draw_text(screen, f"{type_dict[subjects[i]]} 스킬이 레벨업했습니다!", SCREEN_WIDTH//2, y_offset, BLUE, align='center')
                    if nowSkillLevel==1:
                        draw_text(screen, f"- -> {PLAYER_SKILLS[subjects[i]][0]['name']}", SCREEN_WIDTH//2, y_offset + 40, typecolor_dict[subjects[i]], align='center')
                    elif nowSkillLevel>1:
                        draw_text(screen, f"{PLAYER_SKILLS[subjects[i]][nowSkillLevel-2]['name']} -> {PLAYER_SKILLS[subjects[i]][nowSkillLevel-1]['name']}", SCREEN_WIDTH//2, y_offset + 40, typecolor_dict[subjects[i]], align='center')
                    y_offset += 80
        
        if sem_gpa_num is None:
            if all(gpa[1] != "P" for gpa in player.thisSemesterGpas):
                Lose()
                draw_text(screen, "이수 학점 미달로 장짤을 당했습니다...", SCREEN_WIDTH//2, y_offset, RED, align='center')
                draw_text(screen, "학사 경고까지 받았습니다...", SCREEN_WIDTH//2, y_offset + 40, RED, align='center')
                player.jangzal_count += 1
                player.warning_count += 1
                y_offset += 80
            else: Report()
        elif sem_gpa_num is not None:
            if sem_gpa_num < 2.7:
                Lose()
                draw_text(screen, "장짤을 당했습니다...", SCREEN_WIDTH//2, y_offset, RED, align='center')
                player.jangzal_count += 1
                y_offset += 40
                if sem_gpa_num < 2.0:
                    player.warning_count += 1
                    draw_text(screen, "학사 경고까지 받았습니다...", SCREEN_WIDTH//2, y_offset, RED, align='center')
                    y_offset += 40
            else: Report()
            if sem_gpa_num >= 4.3:
                draw_text(screen, "축하합니다! 이번 학기 딘즈를 받았습니다!", SCREEN_WIDTH//2, y_offset, GREEN, align='center')
                player.deans_count += 1
                y_offset += 40
        if y_offset == y_offset_before:
            draw_text(screen, "없음", SCREEN_WIDTH//2, y_offset, BLACK, align='center')

    draw_text(screen, "아무 키나 눌러 넘어가기...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, BLACK, align='center')

    pygame.display.flip()
    wait_for_key()
    unmute_music()

def show_final_result(player, screen):
    """최종 결과 화면 (수정된 버전)"""
    # 졸업 또는 게임 오버 여부에 따라 적절한 사운드 재생
    is_game_over = player.gameover() or player.ending_type == "프밍기 패배"
    if is_game_over:
        Lose()
    else:
        play_music("../music/ending.wav")

    # --- 화면 표시 로직 시작 ---
    screen.fill(WHITE)
    
    # 1. 최종 성적표 그리기
    y_offset = 100
    draw_text(screen, "=== 졸업 성적표 ===", SCREEN_WIDTH//2, y_offset, BLACK, size=48, align='center')
    y_offset += 60
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
    y_offset += 12
    # 성적표 헤더
    draw_text(screen, "학기", SCREEN_WIDTH//2-450 - 20, y_offset, align='center')
    draw_text(screen, "과목명", SCREEN_WIDTH//2-450 + 40, y_offset)
    draw_text(screen, "성적", SCREEN_WIDTH//2-50 + 40, y_offset, align='right')
    draw_text(screen, "과목명", SCREEN_WIDTH//2+50, y_offset)
    draw_text(screen, "성적", SCREEN_WIDTH//2+450, y_offset, align='right')
    
    current = None
    oneSemMonsters = 0
    # 이수한 과목 목록 표시
    for i, Semestername in enumerate(player.clearedSemesters):
        if Semestername != current:
            current = Semestername
            oneSemMonsters = 0
            y_offset += 40
            pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
            y_offset += 10
            draw_text(screen, f"{current}", SCREEN_WIDTH//2 - 450 - 20, y_offset, BLACK, align='center')

        draw_text(screen,   f"{player.clearedMonsters[i]}", SCREEN_WIDTH//2-450 + 40+(470*(oneSemMonsters%2)), y_offset, BLACK)
        display_Monster_Imge(screen, monsters[player.clearedMonsters[i]], SCREEN_WIDTH//2 -450 + 40+(470*(oneSemMonsters%2)) + len(player.clearedMonsters[i]) * 32 + 32, y_offset+16, size=2)
        draw_text(screen,   f"{player.gpas[i][1]}",         SCREEN_WIDTH//2-50 + 40 +(470*(oneSemMonsters%2)), y_offset, gpaColor(player.gpas[i][1]), align='right')
        oneSemMonsters += 1

    y_offset += 40    
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)

    # 최종 GPA 표시
    cum_gpa = player.calcGPA(2)
    y_offset += 60 
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
    y_offset += 10
    draw_text(screen, "최종 GPA", SCREEN_WIDTH//2-200, y_offset)
    draw_text(screen, f"{cum_gpa}", SCREEN_WIDTH//2+200, y_offset, gpaColor(cum_gpa), align='right')
    y_offset += 40
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
    y_offset += 10

    # 비고란 표시
    draw_text(screen, "비고", SCREEN_WIDTH//2, y_offset, BLACK, size=32, align='center')
    y_offset += 40
    draw_text(screen, f"이름: {player.name}", SCREEN_WIDTH//2-450, y_offset, BLACK)
    draw_text(screen, f"최종 레벨: {player.level}", SCREEN_WIDTH//2, y_offset, BLACK, align='center')
    draw_text(screen, f"딘즈 달성: {player.deans_count}회", SCREEN_WIDTH//2+450, y_offset, BLACK, align='right')
    y_offset += 60 # 다음 텍스트를 위한 추가 간격

    # 2. 게임 결과 (졸업/게임 오버 사유)를 성적표 아래에 추가
    if is_game_over:
        # 게임 오버 사유 표시
        if player.ending_type == "프밍기 패배":
            draw_text(screen, "프로그래밍 기초한테 졌습니다. 전산과로 진학하지 못했습니다.", SCREEN_WIDTH//2, y_offset, RED, size=32, align='center')
        elif player.warning_count >= 3:
            draw_text(screen, "학사 경고 3회로 제적당했습니다.", SCREEN_WIDTH//2, y_offset, RED, size=32, align='center')
        else:
            # 기타 게임오버 상황
            draw_text(screen, "게임 오버", SCREEN_WIDTH//2, y_offset, RED, size=32, align='center')
    else:
        # 졸업 성공 메시지 및 엔딩 표시
        ending = player.get_final_ending()
        draw_text(screen, f"{player.name}은(는) 최종 학점 {player.calcGPA(2)}로 졸업했습니다.", SCREEN_WIDTH//2, y_offset, BLACK, size=32, align='center')
        y_offset += 40
        draw_text(screen, f"엔딩: {ending}", SCREEN_WIDTH//2, y_offset, BLUE, size=32, align='center')
        
    # --- 화면 표시 로직 종료 ---

    # 3. 결과 저장 및 다음 단계 안내
    success, message = save_game_log_csv("../results/graduation/graduation_results.csv", player)
    success_notion, page_id = save_game_log_to_notion(player)
    if success_notion:
        # [수정됨] success가 True일 때, page_id 유무를 추가로 확인
        if page_id:
            # 1. 가장 이상적인 성공 사례
            logger.info(f"Notion 기록 저장 성공. Page ID: {page_id}")
            draw_text(screen, "O 결과가 저장되었습니다", SCREEN_WIDTH//2 - 144, SCREEN_HEIGHT - 120, GREEN)
        else:
            # 2. API는 성공했으나 ID를 받지 못한 예외 사례
            logger.warning("Notion API는 성공을 반환했으나 Page ID를 얻지 못했습니다. 확인이 필요합니다.")
            # 사용자에게는 성공으로 보이되, 개발자는 로그를 보고 문제를 인지할 수 있음
            draw_text(screen, "O 결과가 저장되었습니다", SCREEN_WIDTH//2 - 144, SCREEN_HEIGHT - 120, GREEN)
    else:
        # 3. 명백한 실패 사례
        logger.error("Notion 기록 저장에 실패했습니다.")
        draw_text(screen, "X 저장 실패", SCREEN_WIDTH//2 - 72, SCREEN_HEIGHT - 120, RED)
    
    draw_text(screen, "아무 키나 눌러 다음으로...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, BLACK, align='center')
    
    # Notion에서 모든 기록을 가져와 CSV 업데이트 및 순위표 생성
    notion_records = get_leaderboard_from_notion()
    if notion_records:
        update_and_save_csv(notion_records)

    # 통계 계산 로직 추가
    stats = {'mean': 0.0, 'median': 0.0, 'std': 0.0, 'z_score': 0.0}
    if notion_records:
        all_gpas = [float(record['gpa']) for record in notion_records if record.get('gpa') is not None]
        if all_gpas:
            import numpy as np
            stats['mean'] = np.mean(all_gpas)
            stats['median'] = np.median(all_gpas)
            stats['std'] = np.std(all_gpas)
            
            try:
                player_gpa = float(player.calcGPA(2))
                if stats['std'] > 0:
                    stats['z_score'] = (player_gpa - stats['mean']) / stats['std']
            except (ValueError, TypeError):
                pass
    
    leaderboard = sorted(notion_records, key=lambda x: x.get('gpa', 0.0), reverse=True)
    
    pygame.display.flip()

    # 4. 후속 화면으로 넘어가기 (QR 생성, 딘즈리스트 등)
    # 1. 졸업 성적표 이미지 저장 (QR/업로드 없이 로컬에만 임시 저장)
    transcript_path = save_cropped_and_return_path(
        screen,
        player.name,
        crop_w=1100, crop_h=880, top_margin=60,
        out_dir="results/screenshots/temp_images",
        prefix="transcript"
    )
    wait_for_key()

    # 2. 딘즈 리스트 화면 표시 (계산된 통계 정보 전달)
    show_deans_list(player, screen, leaderboard, stats)
    
    # 3. 딘즈 리스트 화면 이미지 저장 (QR/업로드 없이 로컬에만 임시 저장)
    deans_list_path = save_cropped_and_return_path(
        screen,
        player.name,
        crop_w=600, crop_h=880, top_margin=30,
        out_dir="results/screenshots/temp_images",
        prefix="deans_list"
    )
    
    # 4. 두 이미지를 배경에 합성하여 최종 이미지 생성
    background_image_path = "../img/instagram_background.png"
    final_combined_path = combine_for_share(background_image_path, transcript_path, deans_list_path, player.name)
    logger.info(f"최종 합성 이미지 경로: {final_combined_path}")

    # 5. 합성에 사용된 임시 이미지 파일 삭제
    try:
        if os.path.exists(transcript_path): os.remove(transcript_path)
        if os.path.exists(deans_list_path): os.remove(deans_list_path)
        logger.debug("Debug: 임시 이미지 파일 삭제 완료.")
    except OSError as e:
        logger.error(f"Debug: 임시 파일 삭제 실패: {e.filename}")

    # 6. 최종 합성 이미지를 Dropbox에 업로드하고 QR 코드 생성
    upload_url = upload_to_dropbox(
        file_path=final_combined_path, 
        dropbox_folder_path=DROPBOX_UPLOAD_FOLDER
    )
    
    # 6.5. 업로드 성공 시, 받아온 페이지 ID를 이용해 Notion 페이지 업데이트
    if success_notion and page_id and upload_url:
        update_notion_page_with_results(page_id, upload_url)
    else:
        if not page_id:
            logger.error("Debug: Notion 페이지 ID가 없어 업데이트를 건너뜁니다.")
        if not upload_url:
            logger.error("Debug: 업로드 URL이 없어 Notion 업데이트를 건너뜁니다.")


    if upload_url:
        logger.info(f"업로드 완료! 공유 URL: {upload_url}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/qrcode/share_{timestamp}.png"
        qr_path = make_qr(upload_url, out_path=filename)
        logger.info(f"Debug: 최종 합성 이미지의 QR 코드 경로: {qr_path}")
    else:
        logger.error("Debug: 업로드에 실패했습니다.")
        qr_path = None # 업로드 실패 시 QR 경로 없음

    # 7. QR 링크 화면 표시
    screen.fill(WHITE)
    draw_text(screen, "! 졸업 결과 공유하기 !", SCREEN_WIDTH//2, 120, BLACK, size=48, align='center')

    try:
        if qr_path:
            qr_image = pygame.image.load(qr_path).convert() 
            qr_image = pygame.transform.smoothscale(qr_image, (300, 300))
            qr_rect = qr_image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(qr_image, qr_rect)
        else:
            draw_text(screen, "QR 코드 생성에 실패했습니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, RED, align='center')
    except Exception as e:
        draw_text(screen, f"QR 불러오기 실패: {e}", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, RED, align='center')
    
    draw_text(screen, "위 QR을 스캔하면 결과 이미지를 얻을 수 있습니다.", SCREEN_WIDTH//2, 320, BLACK, size=28, align='center')
    draw_text(screen, "인스타 스토리에 @in.cs.tagram과 @kaist_kamf를 태그해서 공유해보세요!", SCREEN_WIDTH//2, 370, BLACK, size=28, align='center')
    draw_text(screen, "아무 키나 눌러 메인 메뉴로 돌아갑니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, GRAY, size=24, align='center')

    pygame.display.flip()
    wait_for_key()

def get_player_info(screen, prompts):
    """
    pygame에서 이름과 인스타그램 ID 입력을 함께 받는 함수.
    """
    inputs = [""] * len(prompts)
    active_field = 0
    font_size = 32

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (None,) * len(prompts) # 종료 시 None 튜플 반환
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return (None,) * len(prompts)
                elif event.key == pygame.K_RETURN:
                    if inputs[0].strip():  # 이름은 필수 항목
                        return tuple(i.strip() for i in inputs)
                elif event.key in (pygame.K_UP, pygame.K_TAB):
                    active_field = (active_field - 1) % len(prompts)
                elif event.key == pygame.K_DOWN:
                    active_field = (active_field + 1) % len(prompts)
                elif event.key == pygame.K_BACKSPACE:
                    inputs[active_field] = inputs[active_field][:-1]
                elif event.unicode.isprintable():
                    # 필드별 글자 수 제한
                    if active_field == 0 and len(inputs[active_field]) < 10: # 이름
                        inputs[active_field] += event.unicode
                    elif active_field == 1 and len(inputs[active_field]) < 30: # 인스타그램 ID
                        inputs[active_field] += event.unicode

        screen.fill(BLACK)
        draw_text(screen, "플레이어 정보를 입력하세요", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200, WHITE, size=40, align='center')

        box_width = 400
        box_height = 40
        start_y = SCREEN_HEIGHT // 2 - 100

        for i, prompt in enumerate(prompts):
            is_active = (i == active_field)
            prompt_y = start_y + i * 100
            box_y = prompt_y + 30

            # 프롬프트 텍스트
            draw_text(screen, prompt, SCREEN_WIDTH // 2, prompt_y, WHITE, size=font_size, align='center')

            # 입력 박스
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            border_color = BLUE if is_active else WHITE
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2)

            # 입력된 텍스트와 커서
            text_to_show = inputs[i]
            if is_active:
                text_to_show += "_"
            
            if text_to_show:
                draw_text(screen, text_to_show, box_x + 8, box_y + (box_height - font_size)//2 + 2, BLACK, size=font_size)
            elif not is_active and i == 1: # 인스타그램 필드가 비활성 상태일 때
                 draw_text(screen, "선택사항", box_x + 8, box_y + (box_height - font_size)//2 + 2, GRAY, size=font_size)

        draw_text(screen, "방향키(혹은 Tab)로 이동, Enter로 확인, ESC로 뒤로가기", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, GRAY, size=24, align='center')
        pygame.display.flip()
        pygame.time.wait(30)

def _remove_cleared_entry(player, monster_name):
    # 같은 과목이 중복으로 들어간 경우까지 안전하게 모두 제거
    while monster_name in player.clearedMonsters:
        idx = player.clearedMonsters.index(monster_name)
        player.clearedMonsters.pop(idx)
        if idx < len(player.clearedSemesters):
            player.clearedSemesters.pop(idx)
        if idx < len(player.gpas):
            player.gpas.pop(idx)

def _add_cleared_entry(player, monster_name, semester, gpa):
    player.clearedMonsters.append(monster_name)
    player.clearedSemesters.append(semester)
    player.gpas.append(gpa)

def game_start(screen, Me_name="넙죽이", debug_config=None):
    """새로운 졸업모드 메인 게임 로직"""
    if logger.isEnabledFor(logging.INFO):
        logger.info(f"졸업 모드 게임 시작: 플레이어={Me_name}")
    
    # pygame 화면 초기화 강제 실행
    init_pygame_screen()

    # 새로운 플레이어 생성
    player = Player(name=Me_name)
    
    # 디버그 설정 초기화
    if debug_config is None:
        from typing import NamedTuple
        class DebugConfig(NamedTuple):
            debug: bool
            damage: bool
            skip: bool
        debug_config = DebugConfig(debug=False, damage=True, skip=False)
    
    # 이름 입력
    prompts = ["이름 (최대 10자)", "인스타그램 ID (선택사항)"]
    newname, instagram_id = get_player_info(screen, prompts)
    player.instagram_id = instagram_id if instagram_id else None
    if newname is None: # ESC를 누르거나 창을 닫으면 newname이 None이 됨
        return

    # 디버그 설정을 플레이어에 연결
    player.debug_config = debug_config
    
    # cheat/admin/debug 키워드가 이름에 하나라도 포함되면 치트모드 활성화 (기존 호환성)
    if any(k in newname.lower() for k in ("cheat", "admin", "debug")):
        player.cheatmode = True
    
    # CLI 디버그 모드 활성화
    if debug_config.debug:
        player.cheatmode = True

    player.name = newname
    
    # 배경음악 재생 시작
    play_music(["../music/Im_a_kaist_nonmelody.wav", "../music/Im_a_kaist_melody.wav"])
    
    # 메인 게임 루프
    game_running = True
    while game_running and not player.gameover():
        # 학기 시작 화면
        player.pnr_used = False
        semester_intro_screen(player, screen)
        player.thisSemesterGpas = []
        
        need_skill_change = False  # 루프 시작 전에 초기화

        # 각 과목과 전투
        for i, monster_name in enumerate(player.thisSemesterMonsters):
            logger.debug(f"Debug: {monster_name}와 전투 시작")

            # 몰캠 레벨
            mol_lev = player.molcam if player.molcam != None else 0
            
            # 몬스터 생성
            if monster_name in monsters:
                enemy_monster = copy.deepcopy(monsters[monster_name])
                enemy_monster.level = random.randint(player.level-1+player.level//10, player.level+1+(player.level//10)*2) - mol_lev
                enemy_monster.update_fullreset()
            else:
                # 기본 몬스터 생성
                enemy_monster = copy.deepcopy(monsters["프로그래밍 기초"])
                enemy_monster.name = monster_name
            
            # 전투 진행
            battle_result, gpa = battle(player, enemy_monster, screen)

            # 프밍기 패배 또는 드랍 시 게임 오버 처리
            if monster_name == "프로그래밍 기초" and battle_result in [0, 3, 5]: # 0: 패배, 3: 드랍, 5: NR
                player.ending_type = "프밍기 패배"
                game_running = False
                break
            
            need_skill_change = False  # 각 전투 후에 초기화

            if battle_result == 1:  # 승리
                if monster_name in player.clearedMonsters:
                    _remove_cleared_entry(player, monster_name)
                _add_cleared_entry(player, monster_name, player.current_semester, gpa)
                player.thisSemesterGpas.append(gpa)
                need_skill_change = player.complete_monster(monster_name)
                addSeonSus(player, enemy_monster)

            elif battle_result == 2:  # P (패스)
                if monster_name in player.clearedMonsters:
                    _remove_cleared_entry(player, monster_name)
                _add_cleared_entry(player, monster_name, player.current_semester, gpa)
                player.thisSemesterGpas.append(gpa)
                need_skill_change = player.complete_monster(monster_name)
                addSeonSus(player, enemy_monster)

            elif battle_result == 3:  # 드랍
                player.canBeMetMonsters.append(monster_name)
                player.thisSemesterGpas.append(gpa)

            elif battle_result == 4:  # 이벤트
                player.thisSemesterGpas.append(gpa)
                if gpa[1] == "성공!":
                    need_skill_change = player.complete_monster(monster_name)

            elif battle_result == 5:  # NR
                player.canBeMetMonsters.append(monster_name)
                player.thisSemesterGpas.append(gpa)

            elif battle_result == 0:  # 패배
                if monster_name in player.clearedMonsters:
                    _remove_cleared_entry(player, monster_name)
                player.thisSemesterGpas.append(gpa)
                player.canBeMetMonsters.append(monster_name)
                _add_cleared_entry(player, monster_name, player.current_semester, gpa)
                player.update_fullreset()

            player.update()
            if need_skill_change:
                show_skill_change(screen, player)
        
        if not game_running:
            break

        # 학기 결과 화면
        semester_result_screen(player, screen)
        
         # 다음 학기로 진행 (수정된 로직)
        logger.info(f"Debug: 현재 진행도 {player.semester_progress}/{len(player.semester_order)}")
        
        # 남은 몬스터 수가 0인 경우
        if len(player.clearedMonsters) >= 14:
            if player.current_semester in ["4-1", "4-여름방학", "4-2"]:
                logger.info("Debug: 모든 학점 취득 완료. 정상 졸업.")
                break # 게임 루프 종료
            else:
                logger.info("Debug: 모든 학점 취득 완료. 조기 졸업!")
                player.ending_type = "조기"
                break # 게임 루프 종료
        
        # 학기 진행
        if not player.advance_semester():
            # 모든 학기(4-2) 완료 후에도 몬스터가 남았을 때
            if len(player.canBeMetMonsters) > 0:
                logger.info("Debug: 연차초과! 추가 학기 시작.")
                player.ending_type = "연차초과"
                # 추가 학기 로직을 여기에 구현
                # 예: 5-1, 5-2, 6-1, 6-2 학기를 직접 추가
                player.semester_order = player.semester_order + ["5-1", "5-2", "6-1", "6-2"]
                player.current_semester = player.semester_order[-4] # 5-1 학기로 설정
                continue
            else:
                logger.info("Debug: 모든 학기 완료!")
                break
        
        # 6-2 학기까지 왔는데도 몬스터가 남았을 경우 제적
        if player.current_semester == "졸업" and len(player.canBeMetMonsters) > 0:
            logger.info("Debug: 모든 추가 학기 실패. 제적!")
            player.warning_count = 3 # 제적 조건 충족
            break # 게임 루프 종료
    
    # 음악 정지
    stop_music()
    
    # 게임 종료 화면
    show_final_result(player, screen)
    
    return player

def show_skill_change(screen, player):

    newskill_boolean = player.skilllevelup
    type_index = newskill_boolean.index(True)
    newskill_type = ['*', 'CT', 'DS', 'SYS', 'PS', 'AI'][type_index]

    newskill_level = player.current_skills[newskill_type]

    newskill = PLAYER_SKILLS[newskill_type][newskill_level-1]



    for _, skill in enumerate(player.get_available_skills()):
        logger.info(f"Debug: available skills: {skill['name']}")

    pygame.display.flip()
    display_status(screen)

    draw_text(screen, f"  {player.name}은/는 {newskill['name']} 을/를 배우고 싶다...", stX, stY, color= WHITE)
    pygame.display.flip()
    wait_for_key()
    display_status(screen)

    draw_text(screen, f"  하지만 기술 슬롯이 모두 가득 찼다!", stX, stY, color= WHITE)
    pygame.display.flip()
    wait_for_key()
    display_status(screen)

    draw_text(screen, f"  어떤 기술을 잊어버릴까?", stX, stY, color= WHITE)
    pygame.display.flip()
    wait_for_key()
    display_status(screen)
    

    replace_skill = display_skill_change(screen, newskill, player)

    pygame.display.flip()
    display_status(screen)

    # 새로운 기술을 배우지 않음
    if replace_skill == newskill:
        draw_text(screen, f"  {newskill['name']} 을/를 배우지 않았다!", stX, stY, color= WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)

        player.current_skills[newskill['type']] = 0

    # 새로운 기술을 배움 (가지고 있는 기술을 버림)
    else:
        draw_text(screen, f"  3.. 2.. 1..", stX, stY, color= WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)

        draw_text(screen, f"  {player.name}은/는 {replace_skill['name']} 을/를 까맣게 잊어버렸다!", stX, stY, color= WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)

        draw_text(screen, f"  그리고...", stX, stY, color= WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)

        draw_text(screen, f"  {newskill['name']} 을/를 배웠다!", stX, stY, color= WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)

        player.current_skills[replace_skill['type']] = 0

    
def display_skill_change(screen, newskill, player):
    current_index = 0

    while True:
        display_status(screen)
        apply_alpha_overlay(screen, (sX, sY, 2*psX + 4, 2*psY - 221))

        draw_text(screen, "  잊어 버릴 기술을 선택하자.", stX, stY, YELLOW)

        available_skills = player.get_available_skills()
        skills_without_new = [skill for skill in available_skills if skill != newskill]
        skills_ordered = skills_without_new + [newskill]

        for i, skill in enumerate(skills_ordered):

            prefix = "> " if i == current_index else "  "
            prefix_color = WHITE 
            # 현재 가지고 있는 색

            if i != len(skills_ordered)-1:
                draw_text(screen, prefix, stX, stY-400 + i * 60, prefix_color)
                draw_text(screen, f"  {skill['name']}", stX, stY-400 + i * 60, typecolor_dict[skill['type']])
                draw_text(screen, f"{skill['type']}", stX + 500, stY-400 + i * 60, typecolor_dict[skill['type']])
                draw_text(screen, f"위력: {skill['skW']}", stX + 600, stY-400 + i * 60, WHITE)

            else:
                draw_text(screen, prefix, stX, stY + 40, prefix_color)
                draw_text(screen, f"  {newskill['name']}", stX, stY+40, typecolor_dict[newskill['type']])
                draw_text(screen, f"{newskill['type']}", stX + 500, stY+40, typecolor_dict[newskill['type']])
                draw_text(screen, f"위력: {newskill['skW']}", stX + 600, stY+40, WHITE)

        pygame.display.flip()
        key = wait_for_key()
        if key == 'enter':
            return available_skills[current_index]
        elif key == 'up' and current_index > 0:
            current_index -= 1
            option_change_sound()
        elif key == 'down' and current_index < len(available_skills)-1:
            current_index += 1
            option_change_sound()
