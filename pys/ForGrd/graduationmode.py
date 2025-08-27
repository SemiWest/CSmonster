import random
import csv
from ForGrd.battleForGrd import *
import copy

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

def addSeonSus(player, monster):
    for mon_num in monster.SeonSu:
        monster_name = NumToName(mon_num)
        if monster_name not in player.canBeMetMonsters and monster_name not in player.clearedMonsters:
            player.canBeMetMonsters.append(monster_name)

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
        description = ("당신은 카이스트에 갓 입학한 새내기입니다.", "전산학부에 걸맞는 인재인지 확인하기 위해 프밍기 학점인정시험을 신청했습니다.")
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
    if isinstance(description, tuple):
        for i, line in enumerate(description):
            draw_text(screen, line, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100 + i*40, WHITE, align='center')
    else:    
        draw_text(screen, description, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, WHITE, align='center')
    pygame.display.flip()
    wait_for_key()

    if semester_name == "3-여름방학":
        player.thisSemesterMonsters = ["몰입캠프"]
        return
    elif semester_name == "4-여름방학":
        player.thisSemesterMonsters = random.choice([["코옵"],["개별연구"]])
        return
 

    if "데이터베이스개론" in player.clearedMonsters and "2-2" in player.completed_semesters and "기계학습" not in player.clearedMonsters:
        player.canBeMetMonsters.append("기계학습")
    # 등장 과목 표시
    screen.fill(WHITE)
    draw_text(screen, f"현재 수강할 수 있는 과목들", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, BLACK, size=32, align='center')
    for i, monster_name in enumerate(player.canBeMetMonsters):
        if monster_name in player.clearedMonsters:
            draw_text(screen, f"{monster_name} (재수강)", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*40, GRAY, size=32, align='center')
        else:
            draw_text(screen, f"{monster_name}", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*40, BLACK, size=32, align='center')
    draw_text(screen, "아무 키나 눌러 넘어가기...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, align='center')
    pygame.display.flip()
    wait_for_key()

    get_current_semester_monsters(player)

    screen.fill(WHITE)
    draw_text(screen, "이번 학기에 수강할 과목", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, BLACK, align='center')    
    for i, monster_name in enumerate(player.thisSemesterMonsters):
        if monster_name in player.clearedMonsters:
            draw_text(screen, f"{monster_name} (재수강)", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*80, GRAY, size=64, align='center')
        else:
            draw_text(screen, f"{monster_name}", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*80, BLACK, size=64, align='center')
    draw_text(screen, "아무 키나 눌러 시작...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, align='center')
    pygame.display.flip()
    wait_for_key()

def semester_result_screen(player, screen):
    """학기 결과 화면"""
    screen.fill(WHITE)
    
    # 학기 결과 제목
    draw_text(screen, f"성적표", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
    
    # 이번 학기 수강 과목당 성적 표시
    y_offset = 240

    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-200, y_offset - 20), (SCREEN_WIDTH//2+200, y_offset - 20), 2)
    draw_text(screen,       f"과목명",                            SCREEN_WIDTH//2-200, y_offset)
    draw_text(screen,       f"성적",                              SCREEN_WIDTH//2+200, y_offset, align='right')
    y_offset += 60
    for i, monster_name in enumerate(player.thisSemesterMonsters):
        draw_text(screen,   f"{monster_name}",                      SCREEN_WIDTH//2-200, y_offset + i*40, BLACK)
        draw_text(screen,   f"{player.thisSemesterGpas[i][1]}",     SCREEN_WIDTH//2+200, y_offset + i*40, gpaColor(player.thisSemesterGpas[i][1]), align='right')
    
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
    if sem_gpa == "P":
        draw_text(screen, "이번 학기 전과목 P — GPA 산정에서 제외됩니다.", SCREEN_WIDTH//2, y_offset, BLUE, align='center')
    elif sem_gpa == "NR":
        draw_text(screen, "이번 학기 전과목 NR — GPA 산정에서 제외됩니다.", SCREEN_WIDTH//2, y_offset, GRAY, align='center')
    elif sem_gpa_num is not None:
        if sem_gpa_num > 4.3:
            draw_text(screen, "축하합니다! 이번 학기 딘즈를 받았습니다!", SCREEN_WIDTH//2, y_offset, GREEN, align='center')
            player.deans_count += 1
        elif sem_gpa_num < 2.7:
            draw_text(screen, "장짤을 당했습니다...", SCREEN_WIDTH//2, y_offset, RED, align='center')
            player.jangzal_count += 1
            if sem_gpa_num < 2.0:
                player.warning_count += 1
                draw_text(screen, "학사 경고까지 받았습니다...", SCREEN_WIDTH//2, y_offset + 40, RED, align='center')
        else:
            draw_text(screen, "없음", SCREEN_WIDTH//2, y_offset, BLACK, align='center')
    else:
        # 예외 방어 (혹시 모를 이상값)
        draw_text(screen, "GPA 계산 오류", SCREEN_WIDTH//2, y_offset, RED, align='center')

    pygame.display.flip()
    wait_for_key()

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
    draw_text(screen, f"처치한 과목: {len(player.clearedMonsters)}", SCREEN_WIDTH//2 - 96, y_offset + 120, BLACK)
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
    player = Player(name=Me_name)
    
    # 이름 입력
    newname = get_text_input(screen, "이름을 입력하세요:")

    # cheatmode 여부: cheat 입력
    if "cheat" in newname.lower():
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

        # 각 과목과 전투
        for i, monster_name in enumerate(player.thisSemesterMonsters):
            print(f"Debug: {monster_name}와 전투 시작")
            
            # 몬스터 생성
            if monster_name in monsters:
                enemy_monster = copy.deepcopy(monsters[monster_name])
            else:
                # 기본 몬스터 생성
                enemy_monster = copy.deepcopy(monsters["프밍기"])
                enemy_monster.name = monster_name
            
            # 전투 진행
            battle_result, gpa = battle(player, enemy_monster, screen)
            
            if battle_result == 1:  # 승리
                if monster_name in player.clearedMonsters:
                    player.gpas[player.clearedMonsters.index(monster_name)] = gpa
                else:
                    player.clearedMonsters.append(monster_name)
                    player.gpas.append(gpa)
                player.thisSemesterGpas.append(gpa)
                player.complete_monster(monster_name)
                addSeonSus(player, enemy_monster)  # 과목들 추가
            elif battle_result == 2:    # PNR
                player.clearedMonsters.append(monster_name)
                player.thisSemesterGpas.append(gpa)
                player.complete_monster(monster_name)
                player.gpas.append(gpa)
                addSeonSus(player, enemy_monster)  # 과목들 추가
            elif battle_result == 3 or battle_result == 4:      # 3: 드랍
                player.canBeMetMonsters.append(monster_name)  # 드랍
                player.thisSemesterGpas.append(gpa)
            elif battle_result == 0:            # NR, 패배
                player.thisSemesterGpas.append(gpa)
                player.canBeMetMonsters.append(monster_name)
                player.clearedMonsters.append(monster_name)
                player.gpas.append(gpa)
                player.update_fullreset()
            player.update()

        # 학기 결과 화면
        semester_result_screen(player, screen)
        # player.update_fullreset()
        # 학기 끝날때마다 체력 회복 일단 정지
        
        if not game_running:
            break
        
        # 다음 학기로 진행
        print(f"Debug: 현재 진행도 {player.semester_progress}/{len(player.semester_order)}")
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