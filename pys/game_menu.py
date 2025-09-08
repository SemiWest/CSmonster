from playsound import *
import numpy as np
import logging, random

logger = logging.getLogger(__name__)

font = None
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = None
NOTION_TOKEN = "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"
DATABASE_ID = "261e339f1ae5802ca71acd96446868d5"
GPACOLOR = {
    "A+": (255, 215, 0),    # Gold
    "A0": (255, 215, 0),    # Gold
    "A-": (255, 215, 0),    # Gold
    "B+": (192, 192, 192),  # Silver
    "B0": (192, 192, 192), # Silver
    "B-": (192, 192, 192), # Silver
    "C+": (205, 127, 50),  # Bronze
    "C0": (205, 127, 50),  # Bronze
    "C-": (205, 127, 50), # Bronze
    "F": (255, 0, 0),       # Red
    "W": (128, 128, 128),   # Gray
    "-": (0, 0, 0),         # Black
    "P": (0, 255, 0),       # Green
    "NR": (0, 0, 0)          # Black
}


import requests, datetime, csv

logger = logging.getLogger(__name__)

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_leaderboard_from_notion_all():
    """
    Notion 데이터베이스에서 모든 기록을 페이지네이션으로 가져옵니다.
    반환: [{'날짜':..., 'name':..., 'gpa':..., 'level':..., ...}, ...]
    """
    if not all([NOTION_TOKEN, DATABASE_ID]):
        logger.debug("Debug: [Warning!] Notion 토큰 또는 DB ID가 설정되지 않았습니다.")
        return []

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "page_size": 100,
        # 정렬 옵션(최신 날짜 내림차순) — 필요시 켜세요.
        # "sorts": [{"property": "날짜", "direction": "descending"}]
    }
    has_more = True
    next_cursor = None
    results_all = []

    try:
        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            for page in results:
                props = page.get("properties", {})

                record_date = props.get("날짜", {}).get("date", {}).get("start", "")
                # 안전하게 title 추출
                title_arr = props.get("이름", {}).get("title", [])
                name = ""
                if title_arr and "text" in title_arr[0]:
                    name = title_arr[0]["text"].get("content", "")

                gpa = props.get("최종 GPA", {}).get("number", 0.0)
                level = props.get("최종 레벨", {}).get("number", 0)
                deans_count   = props.get("딘즈 횟수", {}).get("number", 0)
                jangzal_count = props.get("장짤 횟수", {}).get("number", 0)
                warning_count = props.get("학사경고 횟수", {}).get("number", 0)

                semester_text = props.get("최종 학기", {}).get("rich_text", [])
                semester = semester_text[0].get("text", {}).get("content", "") if semester_text else ""

                ending_type_text = props.get("엔딩 타입", {}).get("rich_text", [])
                ending_type = ending_type_text[0].get("text", {}).get("content", "") if ending_type_text else ""

                results_all.append({
                    "날짜": record_date,
                    "name": name,
                    "gpa": float(gpa) if gpa is not None else 0.0,
                    "level": level,
                    "deans_count": deans_count,
                    "jangzal_count": jangzal_count,
                    "warning_count": warning_count,
                    "semester": semester,
                    "ending_type": ending_type,
                })

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor", None)

        return results_all

    except requests.exceptions.RequestException as e:
        logger.error(f"Debug: 조회 오류: Notion API 조회 실패 - {e}")
        return []

def init_pygame_screen():
    """pygame 화면을 초기화하는 함수"""
    global screen, font
    if screen is None:
        # pygame 초기화 (playsound에서 이미 초기화되었는지 확인)
        if not pygame.get_init():
            pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_icon(load_image("resources/img/ICON.png"))
        pygame.display.set_caption("전산몬스터")
        
        # 폰트 설정
        font = load_font("resources/neodgm.ttf", 32)

def show_deans_list_from_notion(player=None):
    """Notion DB 기반 Deans List 화면"""

    def rank_color_for_top(rank: int):
        # RGB: Gold, Silver, Bronze, 그 외는 Black
        if rank == 1:
            return (255, 215, 0)   # Gold
        elif rank == 2:
            return (192, 192, 192) # Silver
        elif rank == 3:
            return (205, 127, 50)  # Bronze
        return BLACK

    init_pygame_screen()

    # 1) 데이터 가져오기
    leaderboard = get_leaderboard_from_notion_all()
    if not leaderboard:
        screen.fill(WHITE)
        draw_text(screen, "명예의 전당 기록이 없습니다.", SCREEN_WIDTH // 2, 200, BLACK, align='center')
        draw_text(screen, "아무 키나 눌러 메뉴로 돌아가기", SCREEN_WIDTH // 2, 240, GRAY, align='center')
        pygame.display.flip()
        wait_for_key()
        return

    # 2) 정렬: GPA 내림차순, 동점이면 이름 오름차순
    leaderboard.sort(key=lambda x: (-x["gpa"], x["name"]))

    # 3) GPA 색상 기본 함수 (상위권 외에는 기본 gpaColor 적용)
    def color_for_gpa(gpa_value: float):
        try:
            return GPACOLOR[f"{gpa_value:.2f}"]
        except Exception:
            return BLACK

    # 4) 화면 그리기
    screen.fill(WHITE)
    draw_text(screen, "명예의 전당: Deans List", SCREEN_WIDTH // 2, 80, BLACK, size=48, align='center')
    draw_text(screen, "최종 GPA 기준", SCREEN_WIDTH // 2, 140, GRAY, size=24, align='center')

    y_offset = 200
    top_k = min(10, len(leaderboard))
    for i in range(top_k):
        entry = leaderboard[i]
        rank = i + 1

        # 1~3등은 금/은/동 색, 그 외는 기본
        rank_color = rank_color_for_top(rank)
        name_color = rank_color
        gpa_color  = rank_color if rank <= 3 else color_for_gpa(entry["gpa"])

        # 순위 번호
        draw_text(screen, f"{rank}.",            SCREEN_WIDTH//2 - 250, y_offset + i * 40, rank_color, size=32)
        # 이름
        draw_text(screen, entry["name"],         SCREEN_WIDTH//2 - 180, y_offset + i * 40, name_color, size=32)
        # GPA
        draw_text(screen, f"{entry['gpa']:.2f}", SCREEN_WIDTH//2 + 200, y_offset + i * 40, gpa_color, size=32, align='right')

    # 5) 불명예의 전당
    if len(leaderboard) > 0:
        y_offset_bottom = y_offset + top_k * 40 + 60
        draw_text(screen, "----- 불명예의 전당 -----", SCREEN_WIDTH//2, y_offset_bottom,
                  RED, size=28, align='center')
        y_offset_bottom += 40

        # GPA 0인 사람 필터링
        zero_gpa_entries = [e for e in leaderboard if e["gpa"] == 0.0]

        if len(zero_gpa_entries) > 3:
            # GPA 0인 사람 중 랜덤 3명 선택
            bottom_entries = random.sample(zero_gpa_entries, 3)
        else:
            # 기존 꼴찌 3명 로직
            bottom_count = min(3, len(leaderboard))
            bottom_entries = leaderboard[-bottom_count:]

        # 불명예 명단 출력
        for j, entry in enumerate(bottom_entries, start=0):
            # 원래 순위 계산 (leaderboard 내 위치 기반)
            try:
                rank = leaderboard.index(entry) + 1
            except ValueError:
                rank = "?"

            draw_text(screen, f"{rank}.",            SCREEN_WIDTH//2 - 250, y_offset_bottom + j * 40, RED, size=32)
            draw_text(screen, entry["name"],         SCREEN_WIDTH//2 - 180, y_offset_bottom + j * 40, RED, size=32)
            draw_text(screen, f"{entry['gpa']:.2f}", SCREEN_WIDTH//2 + 200, y_offset_bottom + j * 40, RED, size=32, align='right')

    draw_text(screen, "아무 키나 눌러 메뉴로 돌아갑니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, GRAY, size=24, align='center')
    pygame.display.flip()
    wait_for_key()

def draw_text(surface, text, x, y, color=BLACK, highlight=None, size=32, align='left', bold=False):
    """pygame 화면에 텍스트를 그리는 함수"""
    font_obj = font
    if size != 32:
        font_obj = load_font("resources/neodgm.ttf", size)
    
    # 여기서 폰트 객체에 볼드체 속성을 설정합니다.
    font_obj.set_bold(bold)

    text_surface = font_obj.render(text, True, color, highlight)
    
    if align == 'center':
        text_rect = text_surface.get_rect(centerx=x, top=y)
    elif align == 'right':
        text_rect = text_surface.get_rect(right=x, top=y)
    else:  # 'left' 또는 기타
        text_rect = text_surface.get_rect(topleft=(x, y))
    
    surface.blit(text_surface, text_rect.topleft)
    return text_rect

def draw_wrapped_text(surface, text, x, y, color, max_width, font_size=32, line_spacing=10, align='left'):
    """설명 텍스트가 max_width를 넘지 않게 자동 줄바꿈해서 출력"""
    font_obj = font
    if font_size != 32:
        font_obj = load_font("resources/neodgm.ttf", font_size)
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if word == '\n':
            lines.append(current_line)
            current_line = ""
            continue
        test_line = current_line + word + " "
        if font_obj.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    for i, line in enumerate(lines):
        text_surface = font_obj.render(line.strip(), True, color)
        if align == 'center':
            text_rect = text_surface.get_rect(centerx=x, top=y)
        elif align == 'right':
            text_rect = text_surface.get_rect(right=x, top=y)
        else:  # 'left' 또는 기타
            text_rect = text_surface.get_rect(topleft=(x, y))
        finalXY = (text_rect.topleft[0], text_rect.topleft[1] + i * (font_size + line_spacing))
        surface.blit(text_surface, finalXY)


def apply_alpha_overlay(screen, rect, alpha=180, color=(0,0,0)):
    x, y, w, h = rect
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((*color, alpha))  # color + alpha
    screen.blit(overlay, (x, y))

def load_title_image():
    """타이틀 이미지를 로드하는 함수"""
    # 상대경로로 이미지 로드
    image = load_image("resources/img/전산몬스터.PNG")
    # 이미지 크기 조정 (화면 크기에 맞게)
    image_width = SCREEN_WIDTH # 화면 너비의 절반 또는 600px 중 작은 값
    image_height = int(image.get_height() * (image_width / image.get_width()))
    image = pygame.transform.scale(image, (image_width, image_height))
    return image

def create_flash_effect(surface, intensity):
    """화면 플래시 효과를 만드는 함수"""
    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flash_surface.fill(WHITE)  # 흰색 플래시
    flash_surface.set_alpha(intensity)
    surface.blit(flash_surface, (0, 0))

def main_menu():
    def menu_logic():
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("메인 메뉴 초기화 시작")
        init_pygame_screen()
        main_menu_reload = True
        clock = pygame.time.Clock()
        
        def main_menu_animation():
            """메인 메뉴 애니메이션 - 타이틀 이미지가 떨어지고 플래시 효과"""
            title_image = load_title_image()
            # 애니메이션 파라미터
            image_rect = title_image.get_rect()
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            start_y = -image_rect.height  # 화면 위쪽에서 시작
            end_y = center_y - image_rect.height * 0.7 # 화면 중앙보다 조금 위
            
            # 총 애니메이션 프레임 수 (중력 가속도로 떨어짐)
            total_frames = 60
            gravity = 0.8  # 중력 가속도
            velocity = 0   # 초기 속도
            current_y = start_y
            
            for frame in range(total_frames):
                # 화면 지우기 (흰색 배경)
                screen.fill(WHITE)
                
                # 물리 기반 애니메이션 (중력 가속도)
                velocity += gravity
                current_y += velocity
                
                # 목표 지점에 도달하면 정지
                if current_y >= end_y:
                    current_y = end_y
                    break
                image_x = center_x - image_rect.width // 2
                # 이미지 그리기
                screen.blit(title_image, (image_x, current_y))
                
                pygame.display.flip()
                clock.tick(60)  # 60 FPS
                
                # 이벤트 처리 (애니메이션 중 종료 가능)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
            
            # 중앙 도달 시 플래시 효과와 게임 시작 사운드
            # 최종 이미지를 그리고 게임 시작 사운드 재생
            image_x = center_x - image_rect.width // 2
            screen.fill(WHITE)
            screen.blit(title_image, (image_x, current_y))
            pygame.display.flip()
            
            game_started()  # 게임 시작 사운드 재생
    # The code `draw_text` is likely a function or method call in Python that is used to display text
    # on the screen or in a graphical user interface. Without seeing the implementation of the
    # `draw_text` function or method, it is difficult to provide more specific details about what it
    # does.
            
            # 플래시 효과 (여러 프레임에 걸쳐)
            for flash_frame in range(64):
                screen.fill(WHITE)
                screen.blit(title_image, (image_x, current_y))
                
                # 플래시 강도 (점점 약해짐)
                flash_intensity = 255 - (flash_frame * 4)
                if flash_intensity > 0:
                    create_flash_effect(screen, flash_intensity)
                    
                pygame.display.flip()
                pygame.time.wait(3)

            # 2초 정적 (이미지만 표시)
            screen.fill(WHITE)
            screen.blit(title_image, (image_x, current_y))
            pygame.display.flip()
            pygame.time.wait(2000)
                    
        # Main menu loop
        current_index = 0
        running = True
        pygame.event.clear()
        global font
        font = load_font("resources/neodgm.ttf", 32)

        while running:
            if main_menu_reload:
                main_menu_animation()
                pygame.event.clear()
                main_menu_reload = False
            
            if musicOnOff:
                if pygame.mixer.music.get_busy() == 0:
                    play_music("resources/music/menu.wav")
            else:
                stop_music()
                if pygame.mixer.music.get_busy() == 1:
                    pygame.mixer.music.stop()
            
            # 화면 지우기 (흰색 배경)
            screen.fill(WHITE)
            
            # 타이틀 이미지를 배경으로 그리기
            title_image = load_title_image()
            image_rect = title_image.get_rect()
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            image_x = center_x - image_rect.width // 2
            image_y = center_y - image_rect.height * 0.7  # 조금 위쪽에 배치
            screen.blit(title_image, (image_x, image_y))
            
            # 메뉴 옵션들
            options = ["졸업 모드", "기록 보기", "스태프 롤", "환경 설정"]
            
            # 메뉴 옵션들을 2x3 격자로 배치
            for i, option in enumerate(options):
                x = 516 * (i % 2) + center_x - 376  # 2열 배치
                y = int(i // 2) * 60 + SCREEN_HEIGHT * 0.6  # 이미지 아래쪽에 배치
                
                if i == current_index:
                    draw_text(screen, f"> {option}", x, y, WHITE, BLACK)
                else:
                    draw_text(screen, f"  {option}", x, y, BLACK)  # 일반 텍스트는 검은색
            draw_text(screen, "방향키로 조작, Enter로 선택 및 확인, Esc|q|Backspace로 종료 및 취소", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, GRAY, align='center')
            pygame.display.flip()

            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Enter 키
                        if logger.isEnabledFor(logging.INFO):
                            logger.info(f"메뉴 선택: {options[current_index]}")
                        option_select_sound()
                        main_menu_reload = True
                        return options[current_index], screen
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q or event.key == pygame.K_BACKSPACE:
                        option_escape_sound()
                        return False
                    elif event.key == pygame.K_UP and current_index > 1:
                        option_change_sound()
                        current_index -= 2
                    elif event.key == pygame.K_DOWN and current_index < len(options) - 2:
                        option_change_sound()
                        current_index += 2
                    elif event.key == pygame.K_LEFT and current_index % 2 == 1:
                        option_change_sound()
                        current_index -= 1
                    elif event.key == pygame.K_RIGHT and current_index % 2 == 0 and current_index != len(options) - 1:
                        option_change_sound()
                        current_index += 1
            
            clock.tick(60)  # 60 FPS
    
    return menu_logic()

def show_records():
    """기록 보기 화면을 pygame으로 표시"""
    init_pygame_screen()
    
    # CSV 파일 경로 확인
    import os
    import csv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "ForGrd/graduation_results.csv")
    
    if not os.path.isfile(filepath):
        # 기록이 없는 경우
        screen.fill(WHITE)
        draw_text(screen, "기록이 없습니다.", 50, 200, BLACK)
        draw_text(screen, "아무 키나 눌러 메뉴로 돌아가기", 50, 240, GRAY)
        pygame.display.flip()
        wait_for_key()
        return
    
    # 클리어 기록 읽기
    clear_records = []
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # 헤더 스킵
        for row in reader:
            clear_records.append(row)
    
    if not clear_records:
        screen.fill(WHITE)
        draw_text(screen, "클리어 기록이 없습니다.", 50, 200, BLACK)
        draw_text(screen, "아무 키나 눌러 메뉴로 돌아가기", 50, 240, GRAY)
        pygame.display.flip()
        wait_for_key()
        return
    
    # 기록 표시 (페이지별로)
    current_page = 0
    while current_page < len(clear_records):
        screen.fill(WHITE)
        
        y_pos = 50
        draw_text(screen, "클리어 기록", 50, y_pos, BLACK)
        y_pos += 80  # 줄간격 40 * 2
        
        record = clear_records[current_page]
        draw_text(screen, f"{current_page + 1}. {record[0]}", 50, y_pos, BLACK)
        y_pos += 40
        draw_text(screen, f"    이름 {record[1]} | 졸업 GPA {record[2]} | 레벨 {record[3]}", 50, y_pos, BLACK)
        y_pos += 40
        draw_text(screen, f"    딘즈 {record[4]}회 | 장짤 {record[5]}회 | 학사경고 {record[6]}회", 50, y_pos, BLACK)
        y_pos += 40
        draw_text(screen, f"    최종 학기 {record[7]} | 엔딩 타입 {record[8]}", 50, y_pos, BLACK)
        y_pos += 40
        skills = []
        for i in range(9, len(record), 2):
            if record[i]:
                skills.append(f"{record[i]}타입 스킬 레벨 {record[i+1]}, ")
        draw_text(screen, f"    스킬: " + ", ".join(skills), 50, y_pos, BLACK)      
        y_pos += 40
        if current_page < len(clear_records) - 1:
            draw_text(screen, "아무 키나 눌러 다음 페이지로 (q키: 종료)", 50, y_pos, GRAY)
        else:
            draw_text(screen, "아무 키나 눌러 메뉴로 돌아가기", 50, y_pos, GRAY)
        
        pygame.display.flip()
        
        # 키 입력 대기
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
                    waiting = False
                    current_page += 1
                    break

def show_credits():
    """제작자 정보를 pygame으로 표시"""
    init_pygame_screen()
    
    screen.fill(WHITE)
    
    y_center = SCREEN_HEIGHT // 2 - (210+120*4-40)/2

    draw_text(screen, "배급", SCREEN_WIDTH // 2 - (32*4)/2, y_center, BLACK, size=64)
    y_center += 70
    startingpoint = SCREEN_WIDTH // 2
    draw_text(screen, "전산학부           ", startingpoint, y_center, BLUE, size=64, align='center')
    draw_text(screen, "         집행위원회", startingpoint, y_center, SOCBLUE, size=64, align='center')
    
    y_center = SCREEN_HEIGHT // 2 - 80
    draw_text(screen, "김민범", startingpoint-450, y_center, MINBEOM, align='center', size=64)
    draw_text(screen, "박지민", startingpoint-150, y_center, JIMIN, align='center', size=64)
    draw_text(screen, "이승민", startingpoint+150, y_center, SEUNGMIN, align='center', size=64)
    draw_text(screen, "이준서", startingpoint+450, y_center, MYMINT, align='center', size=64)
    y_center += 96
    draw_text(screen, "조원준", startingpoint-450, y_center, WONJUN, align='center', size=64)
    draw_text(screen, "정민호", startingpoint-150, y_center, MINHO, align='center', size=64)
    draw_text(screen, "탁한진", startingpoint+150, y_center, TAK, align='center', size=64)
    draw_text(screen, "황윤정", startingpoint+450, y_center, YUNJEONG, align='center', size=64)
    y_center += 200
    draw_text(screen, "Special Thanks", startingpoint, y_center, BLACK, align='center', size=64)
    y_center += 80
    startingpoint = startingpoint - (16*16)/2
    draw_text(screen, "EWWrim", startingpoint, y_center, EWERED)
    startingpoint += 16*7
    draw_text(screen, "& ", startingpoint, y_center, BLACK)
    startingpoint += 16*2
    draw_text(screen, "kmc7468", startingpoint, y_center, KMC)
    
    draw_text(screen, "Enter를 눌러 메뉴로 돌아가기", 50, SCREEN_HEIGHT - 100, GRAY)
    
    pygame.display.flip()
    #엔터 키를 눌러 메뉴로 돌아가기
    wait_for_key()

