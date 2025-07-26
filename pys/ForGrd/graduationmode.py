import random
import csv
from playsound import *
from ForGrd.battleForGrd import *
from game_menu import *
import copy

# 나의 흔적

def wait_for_key():
    """키 입력 대기 - 스페이스바나 엔터키만 인식"""
    pygame.event.clear()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return pygame.K_ESCAPE
            elif event.type == pygame.KEYDOWN:
                # 스페이스바나 엔터키만 허용
                if (event.key == pygame.K_SPACE or 
                    event.key == pygame.K_RETURN or 
                    event.key == pygame.K_KP_ENTER):
                    return event.key
        pygame.time.wait(50)

def save_game_log_csv(filename, player, final_semester):
    """게임 결과를 CSV에 저장"""
    try:
        # 절대 경로 생성
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, filename)
        
        # 파일이 없으면 헤더 작성 필요
        write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
        
        # CSV 파일에 게임 결과 저장
        with open(filepath, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 헤더 작성
            if write_header:
                writer.writerow([
                    '이름', '최종학기', '레벨', '처치과목수', '딘즈달성', 
                    '장짤횟수', '학사경고', '획득칭호', '최종엔딩', '저장시간'
                ])
            
            # 게임 결과 데이터 저장
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            writer.writerow([
                player.name,
                final_semester,
                player.level,
                len(player.defeated_monsters),
                player.deans_count,
                player.jangzal_count,
                player.warning_count,
                ', '.join(player.titles) if player.titles else '없음',
                player.get_final_ending(),
                now
            ])
            
        return True, f"게임 결과가 {filename}에 저장되었습니다."
        
    except Exception as e:
        return False, f"저장 실패: {str(e)}"

def semester_intro_screen(player, screen):
    """학기 시작 화면"""
    screen.fill(BLACK)
    
    semester_name = player.current_semester
    
    # 학기별 제목 설정
    if semester_name == "새터":
        title = "새터"
        description = "당신은 카이스트에 갓 입학한 새내기입니다. "
    elif semester_name == "3-여름방학":
        title = "몰입캠프"
        description = "당신은 몰입캠프 참가에 성공했습니다. 한달 간 코딩 실력을 키워봅시다."
    elif semester_name == "4-여름방학":
        title = "4-여름방학"
        description = "4-여름방학"
    else:
        title = f"{semester_name}"
        description = f"{semester_name}"
    
    # 제목과 설명 표시
    draw_text(screen, title, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-70, WHITE, size=64, align='center')
    draw_text(screen, description, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, WHITE, align='center')
    
    # 등장 과목 표시
    monsters = player.get_current_semester_monsters()
    y_offset = 320
    draw_text(screen, "이번 학기 과목:", SCREEN_WIDTH//2 - 112, y_offset, BLACK)
    
    for i, monster_name in enumerate(monsters):
        draw_text(screen, f"- {monster_name}", SCREEN_WIDTH//2 - 96, y_offset + 40 + i*40, BLACK)
    
    # 플레이어 정보 표시
    info_y = SCREEN_HEIGHT - 200
    draw_text(screen, f"레벨: {player.level}  체력: {player.currentHp}/{player.maxHp}", 
             SCREEN_WIDTH//2 - 200, info_y, BLACK)
    draw_text(screen, f"딘즈: {player.deans_count}회  장짤: {player.jangzal_count}/3", 
             SCREEN_WIDTH//2 - 200, info_y + 40, BLACK)
    
    draw_text(screen, "아무 키나 눌러 시작...", SCREEN_WIDTH//2 - 144, SCREEN_HEIGHT - 60, BLACK)
    
    pygame.display.flip()
    wait_for_key()

def coop_individual_selection_screen(player, screen):
    """코옵/개별연구 선택 화면"""
    selected_index = 0
    options = [
        ("코옵", "승리 시 '회사원' 칭호 획득"),
        ("개별연구", "승리 시 '대학원생' 칭호 획득"),
        ("건너뛰기", "이벤트를 건너뜀")
    ]
    
    while True:
        screen.fill(WHITE)
        
        # 제목
        draw_text(screen, "특별 이벤트 선택", SCREEN_WIDTH//2 - 128, 150, BLACK)
        draw_text(screen, "코옵 또는 개별연구를 선택하세요", SCREEN_WIDTH//2 - 192, 200, BLACK)
        
        # 옵션 표시
        for i, (option, desc) in enumerate(options):
            y_pos = 280 + i * 80
            color = BLACK
            
            if i == selected_index:
                # 선택된 항목 하이라이트
                pygame.draw.rect(screen, BLACK, 
                               (SCREEN_WIDTH//2 - 180, y_pos - 5, 360, 35))
                color = WHITE
            
            draw_text(screen, f"{i+1}. {option}", SCREEN_WIDTH//2 - 160, y_pos, color)
            draw_text(screen, desc, SCREEN_WIDTH//2 - 160, y_pos + 30, BLACK)
        
        draw_text(screen, "↑↓ 키로 선택, Enter로 확인", 
                 SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 60, BLACK)
        
        pygame.display.flip()
        
        # 키 입력 처리
        key = wait_for_key()
        
        if key == pygame.K_UP and selected_index > 0:
            selected_index -= 1
        elif key == pygame.K_DOWN and selected_index < len(options) - 1:
            selected_index += 1
        elif key == pygame.K_RETURN:
            if selected_index == 2:  # 건너뛰기
                return None
            else:
                return options[selected_index][0]
        elif key == pygame.K_ESCAPE:
            return None

def semester_result_screen(player, screen):
    """학기 결과 화면"""
    screen.fill(WHITE)
    
    # 학기 결과 제목
    draw_text(screen, f"{player.current_semester} 학기 결과", SCREEN_WIDTH//2 - 128, 120, BLACK)
    
    # 처치한 과목 수
    total_monsters = len(player.get_current_semester_monsters())
    passed_monsters = player.semester_progress
    
    draw_text(screen, f"처치한 과목: {passed_monsters} / {total_monsters}", 
             SCREEN_WIDTH//2 - 128, 180, BLACK)
    
    # 성적 정보
    if player.current_semester in player.semester_grades:
        grade_info = player.semester_grades[player.current_semester]
        grade_color = GREEN if grade_info["gpa"] >= 3.0 else RED
        
        draw_text(screen, f"학기 성적: {grade_info['grade']} (GPA {grade_info['gpa']})", 
                 SCREEN_WIDTH//2 - 160, 220, grade_color)
    
    # 딘즈 달성 여부
    hp_percentage = (player.currentHp / player.maxHp) * 100
    current_gpa = player.semester_grades.get(player.current_semester, {}).get("gpa", 0.0)
    
    if current_gpa >= 4.2 or hp_percentage >= 90:
        draw_text(screen, "★ 딘즈 리스트 달성! ★", SCREEN_WIDTH//2 - 128, 260, GREEN)
    
    # 장짤 경고
    if passed_monsters == 0 and total_monsters >= 2:
        draw_text(screen, "⚠ 장짤 발생! ⚠", SCREEN_WIDTH//2 - 96, 300, RED)
        draw_text(screen, f"장짤 누적: {player.jangzal_count}/3", SCREEN_WIDTH//2 - 96, 330, RED)
    
    # 학사 경고 상태
    if player.warning_count > 0:
        draw_text(screen, f"학사 경고: {player.warning_count}/3", SCREEN_WIDTH//2 - 96, 370, RED)
    
    # 플레이어 상태
    draw_text(screen, f"레벨: {player.level}  체력: {player.currentHp}/{player.maxHp}", 
             SCREEN_WIDTH//2 - 160, 420, BLACK)
    
    # PNR 사용 상태
    if player.pnr_used:
        draw_text(screen, "PNR 사용함", SCREEN_WIDTH//2 - 80, 460, BLUE)
    elif player.can_use_pnr():
        draw_text(screen, "PNR 사용 가능", SCREEN_WIDTH//2 - 96, 460, GREEN)
    
    draw_text(screen, "아무 키나 눌러 계속...", SCREEN_WIDTH//2 - 128, SCREEN_HEIGHT - 60, BLACK)
    
    pygame.display.flip()
    wait_for_key()

def show_battle_start_message(screen, monster_name, current, total):
    """전투 시작 메시지"""
    screen.fill(WHITE)
    
    draw_text(screen, f"과목 {current}/{total}: {monster_name}", SCREEN_WIDTH//2 - 128, 300, BLACK)
    draw_text(screen, "전투를 시작합니다!", SCREEN_WIDTH//2 - 112, 360, BLACK)
    
    pygame.display.flip()
    pygame.time.wait(1500)

def show_final_result(player, screen):
    """최종 결과 화면"""
    screen.fill(WHITE)
    
    # 졸업 여부 판정
    if player.gameover():
        draw_text(screen, "게임 오버", SCREEN_WIDTH//2 - 64, 100, RED)
        if player.warning_count >= 3:
            draw_text(screen, "학사 경고 3회로 제적되었습니다.", SCREEN_WIDTH//2 - 176, 140, BLACK)
        else:
            draw_text(screen, "체력이 0이 되어 졸업에 실패했습니다.", SCREEN_WIDTH//2 - 208, 140, BLACK)
    else:
        draw_text(screen, "졸업 축하합니다!", SCREEN_WIDTH//2 - 112, 100, GREEN)
        
        # 엔딩 타입 표시
        ending = player.get_final_ending()
        draw_text(screen, f"엔딩: {ending}", SCREEN_WIDTH//2 - len(ending)*16 - 32, 140, BLUE)
    
    # 최종 통계
    y_offset = 200
    draw_text(screen, "=== 최종 통계 ===", SCREEN_WIDTH//2 - 112, y_offset, BLACK)
    
    draw_text(screen, f"최종 레벨: {player.level}", SCREEN_WIDTH//2 - 96, y_offset + 40, BLACK)
    draw_text(screen, f"완료 학기: {len(player.completed_semesters)}", SCREEN_WIDTH//2 - 96, y_offset + 80, BLACK)
    draw_text(screen, f"처치한 과목: {len(player.defeated_monsters)}", SCREEN_WIDTH//2 - 96, y_offset + 120, BLACK)
    draw_text(screen, f"딘즈 달성: {player.deans_count}회", SCREEN_WIDTH//2 - 96, y_offset + 160, BLACK)
    
    if player.pnr_used:
        draw_text(screen, "PNR 사용함", SCREEN_WIDTH//2 - 80, y_offset + 200, BLUE)
    
    # 획득 칭호
    if player.titles:
        draw_text(screen, "획득 칭호:", SCREEN_WIDTH//2 - 80, y_offset + 240, BLACK)
        for i, title in enumerate(player.titles[:3]):  # 최대 3개만 표시
            draw_text(screen, f"- {title}", SCREEN_WIDTH//2 - 64, y_offset + 280 + i*30, BLUE)
    
    # 결과 저장
    success, message = save_game_log_csv("graduation_results.csv", player, player.current_semester)
    
    if success:
        draw_text(screen, "✓ 결과가 저장되었습니다", SCREEN_WIDTH//2 - 144, SCREEN_HEIGHT - 120, GREEN)
    else:
        draw_text(screen, "✗ 저장 실패", SCREEN_WIDTH//2 - 72, SCREEN_HEIGHT - 120, RED)
    
    draw_text(screen, "아무 키나 눌러 메인메뉴로...", SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 60, BLACK)
    
    pygame.display.flip()
    wait_for_key()

def get_text_input(screen, prompt):
    """pygame에서 텍스트 입력을 받는 함수"""
    input_text = ""
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "플레이어"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_text.strip():
                    return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif len(input_text) < 10 and event.unicode.isprintable():
                    input_text += event.unicode
        
        screen.fill(BLACK)
        
        # 프롬프트 텍스트 출력
        draw_text(screen, prompt, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-100, WHITE, 32, align='center')
        
        # 입력 박스 그리기
        box_x = SCREEN_WIDTH//2 - 160
        box_y = SCREEN_HEIGHT//2
        box_width = 320
        box_height = 40
        
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, BLUE, (box_x, box_y, box_width, box_height), 2)
        
        # 입력된 텍스트 표시
        if input_text:
            draw_text(screen, input_text + "_", box_x + 8, box_y + 8, BLACK)
        else:
            draw_text(screen, "_", box_x + 8, box_y + 8, GRAY)
        
        # 안내 텍스트
        if len(input_text) == 0:
            draw_text(screen, "이름을 입력해주세요 (최대 10자)", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, GRAY, 32, align='center')
        else:
            draw_text(screen, "Enter로 확인", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, GRAY, 32, align='center')
        
        pygame.display.flip()
        pygame.time.wait(50)

def game_start(screen, Me_name="넙죽이"):
    """새로운 졸업모드 메인 게임 로직"""
    # pygame 화면 초기화 강제 실행
    init_pygame_screen()

    # 새로운 플레이어 생성
    player = Player(name=Me_name, Etype="학생")
    
    # 이름 입력
    newname = get_text_input(screen, "이름을 입력하세요:")
    player.name = newname
    
    # 배경음악 재생 시작
    play_music(["../music/Im_a_kaist_nonmelody.wav", "../music/Im_a_kaist_melody.wav"])
    
    # 메인 게임 루프
    game_running = True
    while game_running and not player.gameover():
        # 학기 시작 화면
        semester_intro_screen(player, screen)
        
        # 특별 이벤트 처리
        if player.current_semester == "코옵/개별":
            choice = coop_individual_selection_screen(player, screen)
            if choice:
                player.coop_or_individual = choice
            else:
                # 건너뛰기 선택 시 다음 학기로
                if not player.advance_semester():
                    break
                continue
        
        # 학기별 전투 진행
        semester_monsters = player.get_current_semester_monsters()
        
        print(f"Debug: {player.current_semester} 학기, 과목들: {semester_monsters}")
        
        if not semester_monsters:
            print(f"Debug: {player.current_semester}에 과목이 없습니다!")
            # 과목이 없으면 자동으로 다음 학기로
            if not player.advance_semester():
                break
            continue
        
        # 각 과목과 전투
        for i, monster_name in enumerate(semester_monsters):
            print(f"Debug: {monster_name}와 전투 시작")
            
            # 몬스터 생성
            if monster_name in monsters:
                enemy_monster = copy.deepcopy(monsters[monster_name])
            else:
                # 기본 몬스터 생성
                enemy_monster = copy.deepcopy(monsters["프밍기"])
                enemy_monster.name = monster_name
            
            # 전투 시작 메시지
            show_battle_start_message(screen, monster_name, i+1, len(semester_monsters))
            
            # 전투 진행
            battle_result = battle(player, enemy_monster, 0, screen)
            
            if battle_result == "승리" or battle_result == "PNR":
                player.complete_monster(monster_name)
            elif battle_result == "도망":
                # 도망친 경우 처치하지 않은 것으로 간주
                pass
            else:  # 패배
                if player.gameover():
                    print("Debug: 게임 오버!")
                    game_running = False
                    break
        
        if not game_running:
            break
        
        # 학기 결과 화면
        semester_result_screen(player, screen)
        
        # 다음 학기로 진행
        print(f"Debug: 현재 진행도 {player.semester_progress}/{len(semester_monsters)}")
        if not player.advance_semester():
            # 모든 학기 완료
            print("Debug: 모든 학기 완료!")
            break
        else:
            print(f"Debug: 다음 학기로 진행 - {player.current_semester}")
    
    # 음악 정지
    stop_music()
    
    # 게임 종료 화면
    show_final_result(player, screen)
    
    return player