import csv
from ForGrd.battleForGrd import *
import copy

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
        description = ("당신은 카이스트에 갓 입학한 새내기입니다.", "당신은 자신이 전산학부에 걸맞는 인재인지 확인하기 위해 프밍기 학점인정시험을 신청했습니다.")
    elif semester_name == "1-1":
        title = "1-1"
        description = ("프밍기 학점인정시험을 통과한 당신은 전산학도의 길을 걷기로 결심하였습니다.", "당신은 전산학부의 필수 과목 중 하나를 선택하여 미리 듣기로 하였습니다.")
    elif semester_name == "2-1":
        title = "2-1"
        description = ("당신은 드디어 2학년이 되어 전산학부를 주전공으로 선택했습니다.", "이제부터 진짜 대학 생활의 시작입니다. 행운을 빕니다.")
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
    draw_text(screen, "아무 키나 눌러 넘어가기...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, GRAY, align='center')
    pygame.display.flip()
    wait_for_key()

    if semester_name == "1-1":
        # 이산구조, 데이타구조, 시스템 프로그래밍 중 한 과목을 직접 선택
        options = ["이산구조", "데이타구조", "시프"]
        selected = 0
        while True:
            screen.fill(BLACK)
            draw_text(screen, "수강할 과목을 선택하세요", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, WHITE, align='center')
            for i, option in enumerate(options):
                color = typecolor_dict[monsters[option].type[0]] if i == selected else WHITE
                draw_text(screen, option, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*80, color, align='center', size=64)
                if i == selected:
                    display_Monster_Imge(screen, monsters[option], SCREEN_WIDTH//2 + len(option)*32+96, SCREEN_HEIGHT//2 - 68 + i*80, size=4)
            pygame.display.flip()
            key = wait_for_key()
            if key == 'enter':
                player.thisSemesterMonsters =  [options[selected]]
                player.canBeMetMonsters.remove(options[selected])
                player.starting = monsters[options[selected]].type[0]
                return
            elif key == 'up' and selected > 0:
                selected -= 1
                option_change_sound()
            elif key == 'down' and selected < len(options)-1:
                selected += 1
                option_change_sound()
            draw_text(screen, "방향키로 조작, Enter로 선택", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, GRAY, align='center')

    if semester_name == "3-여름방학":
        player.thisSemesterMonsters = ["몰입캠프"]
        return
    elif semester_name == "4-여름방학":
        player.thisSemesterMonsters = random.choice([["코옵"],["개별연구"]])
        return

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
    pygame.display.flip()
    wait_for_key()

    get_current_semester_monsters(player)

    screen.fill(WHITE)
    draw_text(screen, "이번 학기에 수강할 과목", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-200, BLACK, align='center')    
    for i, monster_name in enumerate(player.thisSemesterMonsters):
        if monster_name in player.clearedMonsters:
            draw_text(screen, f"{monster_name} (재수강)  ", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*80, GRAY, size=64, align='center')
            display_Monster_Imge(screen, monsters[monster_name], SCREEN_WIDTH//2 + len(monster_name)*32+160, SCREEN_HEIGHT//2 - 68 + i*80, size=4)
        else:
            draw_text(screen, f"{monster_name}  ", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100 + i*80, BLACK, size=64, align='center')
            display_Monster_Imge(screen, monsters[monster_name], SCREEN_WIDTH//2 + len(monster_name)*32+32, SCREEN_HEIGHT//2 - 68 + i*80, size=4)
    draw_text(screen, "아무 키나 눌러 시작...", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, align='center')
    pygame.display.flip()
    wait_for_key()

def semester_result_screen(player, screen):
    """학기 결과 화면"""
    mute_music()
    screen.fill(WHITE)
    if monsters[player.thisSemesterMonsters[0]].type[0] == "EVENT":
        if player.thisSemesterGpas[0][1] == "성공!":
            Report()
            draw_text(screen, f"{player.thisSemesterMonsters[0]} 이벤트에 성공하였습니다!", SCREEN_WIDTH//2, 120, BLACK, size=64, align='center')
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
    """최종 결과 화면"""
    # 졸업 또는 게임 오버 여부 판정
    # 프밍기 패배 또는 일반적인 게임오버(학사경고 3회)인 경우
    if player.gameover() or player.ending_type == "프밍기 패배":
        screen.fill(WHITE)
        Lose()
        draw_text(screen, "게임 오버", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-32, RED, size=64, align = 'center')
        pygame.display.flip()
        pygame.time.wait(2000)
        # '프밍기 패배' 엔딩 메시지 추가
        if player.ending_type == "프밍기 패배":
            draw_text(screen, "당신은 프밍기 학인시를 처참하게 실패했습니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, BLACK, align='center')
            draw_text(screen, "전산과로의 진학을 포기하였습니다...", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+140, BLACK, align='center')
        elif player.warning_count >= 3:
            draw_text(screen, "학사 경고 3회로 제적되었습니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, BLACK, align='center')
    else:
        screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.wait(1000)
        draw_text(screen, f"{player.name}은 졸업 조건을 모두 채웠습니다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-32, WHITE, size=64, align='center')
        pygame.display.flip()
        wait_for_key()
        # 화면 전체 페이드 효과-검은색->흰색, 0.4초간 점점 빠르게
        for flash_frame in range(160):
            screen.fill((flash_frame**2//100, flash_frame**2//100, flash_frame**2//100))  # 흰색으로 페이드
            pygame.display.flip()
            pygame.time.wait(2)  # 0.01초 대기

        play_music("../music/ending.wav")
        screen.fill(WHITE)
        draw_text(screen, f"{player.name}은/는 최종 학점 {player.calcGPA(2)}로 졸업했다.", SCREEN_WIDTH//2, SCREEN_HEIGHT//2-32, BLACK, WHITE, 64, 'center')
        pygame.display.flip()
        wait_for_key()

        # 엔딩 화면 = Graduation.jpg * 8배 사이즈
        graduation_image = pygame.image.load("../img/Graduation.png")
        graduation_image = pygame.transform.scale(graduation_image, (graduation_image.get_width() * 8, graduation_image.get_height() * 8))
        screen.blit(graduation_image, (0, 0))
        pygame.display.flip()
        wait_for_key()
        
        # 엔딩 타입 표시
        ending = player.get_final_ending()
        draw_text(screen, f"엔딩: {ending}", SCREEN_WIDTH//2 - len(ending)*16 - 32, 140, BLUE)
    pygame.display.flip()
    wait_for_key()
    
    # 최종 통계
    y_offset = 100
    screen.fill(WHITE)
    draw_text(screen, "=== 졸업 성적표 ===", SCREEN_WIDTH//2, y_offset, BLACK, size=48, align='center')
    y_offset += 60
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
    y_offset += 12
    draw_text(screen,       f"과목명",                            SCREEN_WIDTH//2-450, y_offset)
    draw_text(screen,       f"성적",                              SCREEN_WIDTH//2-50 , y_offset, align='right')
    draw_text(screen,       f"과목명",                            SCREEN_WIDTH//2+50 , y_offset)
    draw_text(screen,       f"성적",                              SCREEN_WIDTH//2+450, y_offset, align='right')
    current = None
    oneSemMonsters= 0
    for i, Semestername in enumerate(player.clearedSemesters):
        if Semestername != current:
            current = Semestername
            oneSemMonsters = 0
            y_offset += 40
            pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)
            y_offset += 8
            draw_text(screen, f"{current}", SCREEN_WIDTH//2, y_offset, BLACK, align='center')
            y_offset += 40
        draw_text(screen,   f"{player.clearedMonsters[i]}", SCREEN_WIDTH//2-450+(500*oneSemMonsters%2), y_offset, BLACK)
        draw_text(screen,   f"{player.gpas[i][1]}",         SCREEN_WIDTH//2-50 +(500*oneSemMonsters%2), y_offset, gpaColor(player.gpas[i][1]), align='right')
        oneSemMonsters += 1
        if oneSemMonsters%2 == 0:
            y_offset += 40
    
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset), (SCREEN_WIDTH//2+500, y_offset), 2)

    cum_gpa = player.calcGPA(2)
    draw_text(screen,       f"최종 GPA", SCREEN_WIDTH//2-200, y_offset + 40)
    draw_text(screen,       f"{cum_gpa}", SCREEN_WIDTH//2+200, y_offset + 40, gpaColor(cum_gpa), align='right')
    
    pygame.draw.line(screen, BLACK, (SCREEN_WIDTH//2-500, y_offset + 80), (SCREEN_WIDTH//2+500, y_offset + 80), 2)
    y_offset += 100

    draw_text(screen, "비고", SCREEN_WIDTH//2, y_offset, BLACK, size=32, align='center')
    y_offset += 40
    draw_text(screen, f"이름: {player.name}", SCREEN_WIDTH//2-200, y_offset, BLACK)
    draw_text(screen, f"최종 레벨: {player.level}", SCREEN_WIDTH//2, y_offset, BLACK, align='center')
    draw_text(screen, f"딘즈 달성: {player.deans_count}회", SCREEN_WIDTH//2+200, y_offset, BLACK, align='right')
    
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
                return "플레이어"  # Or another default value
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # If the escape key is pressed
                    return None  # Return None to signal going back
                elif event.key == pygame.K_RETURN and input_text.strip():
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
            draw_text(screen, "Enter로 확인, ESC로 뒤로가기", SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100, GRAY, 32, align='center')
        
        pygame.display.flip()
        pygame.time.wait(50)

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
    newname = get_text_input(screen, "이름을 입력하세요:")
    
    if newname is None:
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
            print(f"Debug: {monster_name}와 전투 시작")
            
            # 몬스터 생성
            if monster_name in monsters:
                enemy_monster = copy.deepcopy(monsters[monster_name])
                enemy_monster.level = random.randint(player.level-1+player.level//10, player.level+1+(player.level//10)*2)
                enemy_monster.update_fullreset()
            else:
                # 기본 몬스터 생성
                enemy_monster = copy.deepcopy(monsters["프밍기"])
                enemy_monster.name = monster_name
            
            # 전투 진행
            battle_result, gpa = battle(player, enemy_monster, screen)

            # 프밍기 패배 또는 드랍 시 게임 오버 처리
            if monster_name == "프밍기" and battle_result in [0, 3, 5]: # 0: 패배, 3: 드랍, 5: NR
                player.ending_type = "프밍기 패배"
                game_running = False
                break
        

            if battle_result == 1:  # 승리
                if monster_name in player.clearedMonsters:
                    _remove_cleared_entry(player, monster_name)
                    if gpa[1] == "A+" or gpa[1] == "A0":
                        gpa[1] = "A-"
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
                player.thisSemesterGpas.append(gpa)
                player.canBeMetMonsters.append(monster_name)
                player.clearedMonsters.append(monster_name)
                player.clearedSemesters.append(player.current_semester)
                player.gpas.append(gpa)
                player.update_fullreset()

            player.update()
            if need_skill_change:
                show_skill_change(screen, player)
        
        if not game_running:
            break

        # 학기 결과 화면
        semester_result_screen(player, screen)
        
         # 다음 학기로 진행 (수정된 로직)
        print(f"Debug: 현재 진행도 {player.semester_progress}/{len(player.semester_order)}")
        
        # 남은 몬스터 수가 0인 경우
        if len(player.clearedMonsters) >= 14:
            if player.current_semester in ["4-1", "4-여름방학", "4-2"]:
                print("Debug: 모든 학점 취득 완료. 정상 졸업.")
                break # 게임 루프 종료
            else:
                print("Debug: 모든 학점 취득 완료. 조기 졸업!")
                player.ending_type = "조기"
                break # 게임 루프 종료
        
        # 학기 진행
        if not player.advance_semester():
            # 모든 학기(4-2) 완료 후에도 몬스터가 남았을 때
            if len(player.canBeMetMonsters) > 0:
                print("Debug: 연차초과! 추가 학기 시작.")
                player.ending_type = "연차초과"
                # 추가 학기 로직을 여기에 구현
                # 예: 5-1, 5-2, 6-1, 6-2 학기를 직접 추가
                player.semester_order = player.semester_order + ["5-1", "5-2", "6-1", "6-2"]
                player.current_semester = player.semester_order[-4] # 5-1 학기로 설정
                continue
            else:
                print("Debug: 모든 학기 완료!")
                break
        
        # 6-2 학기까지 왔는데도 몬스터가 남았을 경우 제적
        if player.current_semester == "졸업" and len(player.canBeMetMonsters) > 0:
            print("Debug: 모든 추가 학기 실패. 제적!")
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
        print(f"Debug: available skills: {skill['name']}")

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

        draw_text(screen, f"  그리고", stX, stY, color= WHITE)
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
        dark_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 180))  # 마지막 값(120)은 투명도, 0~255
        screen.blit(dark_overlay, (0, 0))

        draw_text(screen, "  잊어 버릴 기술을 선택하자.", stX, stY, YELLOW)

        available_skills = player.get_available_skills()
        skills_without_new = [skill for skill in available_skills if skill != newskill]
        skills_ordered = skills_without_new + [newskill]

        for i, skill in enumerate(skills_ordered):

            prefix = "> " if i == current_index else "  "
            prefix_color = WHITE 
            # 현재 가지고 있는 색

            if i != len(skills_ordered)-1:
                draw_text(screen, prefix, stX, stY-350 + i * 60, prefix_color)
                draw_text(screen, f"  {skill['name']}", stX, stY-350 + i * 60, typecolor_dict[skill['type']])
                draw_text(screen, f"{skill['type']}", stX + 500, stY-350 + i * 60, typecolor_dict[skill['type']])
                draw_text(screen, f"위력: {skill['skW']}", stX + 600, stY-350 + i * 60, WHITE)

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
