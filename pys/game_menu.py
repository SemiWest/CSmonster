from playsound import *
font = None
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = None
font = None

def init_pygame_screen():
    """pygame 화면을 초기화하는 함수"""
    global screen, font
    if screen is None:
        # pygame 초기화 (playsound에서 이미 초기화되었는지 확인)
        if not pygame.get_init():
            pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("전산몬스터")
        
        # 폰트 설정
        font = pygame.font.Font("../neodgm.ttf", 32)

def draw_text(surface, text, x, y, color=BLACK, highlight=False, size=32, align='left'):
    """pygame 화면에 텍스트를 그리는 함수""" 
    font_obj = font
    if size != 32:
        font_obj = pygame.font.Font("../neodgm.ttf", size)
    
    if highlight:
        text_surface = font_obj.render(text, True, color, highlight)
    else:
        text_surface = font_obj.render(text, True, color)
    
    if align == 'center':
        text_rect = text_surface.get_rect(centerx=x, top=y)
    elif align == 'right':
        text_rect = text_surface.get_rect(right=x, top=y)
    else:  # 'left' 또는 기타
        text_rect = text_surface.get_rect(topleft=(x, y))
    
    surface.blit(text_surface, text_rect.topleft)
    return text_rect

def draw_wrapped_text(surface, text, x, y, color, max_width, font_size=32, line_spacing=10):
    """설명 텍스트가 max_width를 넘지 않게 자동 줄바꿈해서 출력"""
    font = pygame.font.Font("../neodgm.ttf", font_size)
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    for i, line in enumerate(lines):
        surface.blit(font.render(line.strip(), True, color), (x, y + i * (font_size + line_spacing)))


def load_title_image():
    """타이틀 이미지를 로드하는 함수"""
    # 상대경로로 이미지 로드
    image = pygame.image.load("../img/전산몬스터.PNG")
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


        while running:
            if main_menu_reload:
                main_menu_animation()
                main_menu_reload = False
            
            if musicOnOff:
                if pygame.mixer.music.get_busy() == 0:
                    play_music("../music/menu.wav")
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
            options = ["졸업 모드", "기록 보기", "모험 모드", "스태프 롤", "환경 설정", " *도움말 "]
            
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
    filepath = os.path.join(base_dir, "game_log.csv")
    
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
            if len(row) > 2 and row[2] == "클리어":
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
        draw_text(screen, f"    플레이 난이도 {record[1]} | 졸업 GPA {record[3]} | 총 전투 횟수 {record[4]}", 50, y_pos, BLACK)
        y_pos += 40
        draw_text(screen, "    잡은 전산몬스터", 50, y_pos, BLACK)
        y_pos += 40
        
        # 잡은 몬스터 표시
        for i in range(5, len(record), 3):
            if i+2 < len(record) and record[i] != "빈 슬롯":
                monster_text = f"       {record[i]} lv {record[i+1]}  잡은 스테이지: {record[i+2]}"
                draw_text(screen, monster_text, 50, y_pos, BLACK)
                y_pos += 40
        
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
    LeftAlign = SCREEN_WIDTH*3 //8
    RightAlign = SCREEN_WIDTH*5 //8

    draw_text(screen, "배급", SCREEN_WIDTH // 2 - (32*4)/2, y_center, BLACK, highlight=False, size=64)
    y_center += 70
    startingpoint = SCREEN_WIDTH // 2 - (32*19)/2
    draw_text(screen, "전산학부 ", startingpoint, y_center, BLUE, highlight=False, size=64)
    startingpoint += 32*9
    draw_text(screen, "집행위원회", startingpoint, y_center, SOCBLUE, highlight=False, size=64)
    y_center += 140

    ystart = y_center
    draw_text(screen, "개발", LeftAlign - (16*4)/2, y_center, BLACK)
    y_center += 40
    draw_text(screen, "이준서", LeftAlign - (16*6)/2, y_center, MYMINT)
    y_center += 80

    draw_text(screen, "기획", LeftAlign - (16*4)/2, y_center, BLACK)
    y_center += 40
    startingpoint = LeftAlign - (16*20)/2
    draw_text(screen, "이준서", startingpoint, y_center, MYMINT)
    startingpoint += 16*7
    draw_text(screen, "조원준", startingpoint, y_center, WONJUN)
    startingpoint+= 16*7
    draw_text(screen, "박지민", startingpoint, y_center, JIMIN)
    y_center += 80

    draw_text(screen, "시나리오", LeftAlign - (16*8)/2, y_center, BLACK)
    y_center += 40
    startingpoint = LeftAlign - (16*13)/2
    draw_text(screen, "박지민" , startingpoint, y_center, JIMIN)
    startingpoint += 16*7
    draw_text(screen, "조원준", startingpoint, y_center, WONJUN)
    y_center += 80

    draw_text(screen, "밸런싱", LeftAlign - (16*6)/2, y_center, BLACK)
    y_center += 40
    draw_text(screen, "조원준", LeftAlign - (16*6)/2, y_center, WONJUN)
    y_center += 80

    y_center = ystart

    draw_text(screen, "음악", RightAlign - (16*4)/2, y_center, BLACK)
    y_center += 40
    draw_text(screen, "이준서", RightAlign - (16*6)/2, y_center, MYMINT)
    y_center += 80

    draw_text(screen, "디자인", RightAlign - (16*6)/2, y_center, BLACK)
    y_center += 40
    startingpoint = RightAlign - (16*20)/2
    draw_text(screen, "김민범", startingpoint, y_center, MINBEOM)
    startingpoint += 16*7
    draw_text(screen, "황윤정", startingpoint, y_center, YUNJEONG)
    startingpoint += 16*7
    draw_text(screen, "이준서", startingpoint, y_center, MYMINT)
    y_center += 80

    draw_text(screen, "QA", RightAlign - (16*2)/2, y_center, BLACK)
    y_center += 40
    startingpoint = RightAlign - (16*20)/2
    draw_text(screen, "탁한진", startingpoint, y_center, TAK)
    startingpoint += 16*7
    draw_text(screen, "이승민", startingpoint, y_center, SEUNGMIN)
    startingpoint += 16*7
    draw_text(screen, "정민호", startingpoint, y_center, MINHO)
    y_center += 80

    draw_text(screen, "Special Thanks", RightAlign - (16*14)/2, y_center, BLACK)
    y_center += 40
    startingpoint = RightAlign - (16*16)/2
    draw_text(screen, "EWWrim", startingpoint, y_center, EWERED)
    startingpoint += 16*7
    draw_text(screen, "& ", startingpoint, y_center, BLACK)
    startingpoint += 16*2
    draw_text(screen, "kmc7468", startingpoint, y_center, KMC)
    y_center += 80
    
    draw_text(screen, "Enter를 눌러 메뉴로 돌아가기", 50, SCREEN_HEIGHT - 100, GRAY)
    
    pygame.display.flip()
    #엔터 키를 눌러 메뉴로 돌아가기
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

def show_help():
    """도움말을 pygame으로 표시"""
    init_pygame_screen()
    
    # 첫 번째 페이지
    screen.fill(WHITE)
    
    y_pos = 50
    draw_text(screen, "도움말", 50, y_pos, BLACK)
    y_pos += 80
    
    help_texts = [
        "전산몬스터는 포켓몬스터의 패러디 게임입니다.",
        "졸업 모드는 30턴의 전투를 거쳐 좋은 성적으로 졸업하는 것이 목표입니다.",
        "무한 모드는 무한으로 전투를 진행하는 모드입니다.",
        "기록 보기에서는 졸업 모드에서 클리어한 기록을 보여줍니다.",
        "",
        "폰트 설정: D2coding, 폰트 크기: 32",
        "조작키 정보: 방향키로 조작, enter키로 선택, esc키/q키/backspace키로 종료 및 취소",
        "스크립트 넘기기: 아무 키나 누르기"
    ]
    
    for text in help_texts:
        if text:  # 빈 줄이 아닌 경우
            draw_text(screen, text, 50, y_pos, BLACK)
        y_pos += 40
    
    draw_text(screen, "아무 키나 눌러 다음 페이지로", 50, y_pos + 40, GRAY)
    
    pygame.display.flip()
    wait_for_key()
    
    # 두 번째 페이지 - 상성표
    screen.fill(WHITE)
    
    y_pos = 50
    draw_text(screen, "상성표", 200, y_pos, BLACK)
    y_pos += 80
    
    # 상성표 헤더
    from monster import type_chart, type_dict
    header_text = "     DTS SYS CST SWD SEC VSC AIS SOC INT"
    draw_text(screen, header_text, 50, y_pos, BLACK)
    y_pos += 40
    
    # 상성표 내용
    for types in type_chart:
        line_text = f"{type_dict[types]} "
        for comps in type_chart[types]:
            comp = type_chart[types][comps]
            if comp == 4:
                line_text += " ◎ "
            elif comp == 1:
                line_text += " △ "
            elif comp == 0:
                line_text += " × "
            else:
                line_text += "   "
        draw_text(screen, line_text, 50, y_pos, BLACK)
        y_pos += 40
        
        if types == "인터랙티브컴퓨팅":
            break
    
    y_pos += 40
    draw_text(screen, "가로: 공격 받는 전산몬 타입 | 세로: 스킬 타입", 50, y_pos, BLACK)
    y_pos += 40
    draw_text(screen, "◎: 효과가 굉장함 | △: 효과가 별로임 | ×: 효과가 없음", 50, y_pos, BLACK)
    y_pos += 80
    
    # 타입 약어 설명
    draw_text(screen, "DTS: 데이터 과학         | SYS: 시스템-네트워크  | CST: 전산이론", 50, y_pos, BLACK)
    y_pos += 40
    draw_text(screen, "SWD: 소프트웨어디자인    | SEC: 시큐어컴퓨팅     | VSC: 비주얼컴퓨팅", 50, y_pos, BLACK)
    y_pos += 40
    draw_text(screen, "AIS: 인공지능-정보서비스 | SOC: 소셜컴퓨팅       | INT: 인터랙티브컴퓨팅", 50, y_pos, BLACK)
    y_pos += 40
    
    draw_text(screen, "아무 키나 눌러 메뉴로 돌아가기", 50, y_pos, GRAY)
    
    pygame.display.flip()
    wait_for_key()
