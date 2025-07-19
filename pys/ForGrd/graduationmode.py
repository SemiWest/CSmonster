from ForGrd.battleForGrd import *
import csv

# 전역 변수들
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

def wild_monster(lists):
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(lists))

def save_game_log_csv(filename, player, turn):
    # 절대 경로 생성
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 디렉터리
    filepath = os.path.join(base_dir, filename)  # 절대 경로로 파일 생성
    
    # CSV 파일에 게임 결과 저장
    with open(filepath, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 헤더가 없다면 헤더를 먼저 작성
        if os.path.getsize(filepath) == 0:
            writer.writerow(['이름', '최종 스테이지', '총 전투 횟수', 'GPA', '성적'])
        
        # 게임 결과 데이터 저장
        writer.writerow([player.name, turn, player.totalhap, player.gpa, player.grade])

def draw_text_input_box(screen, font, x, y, width, height, text, active):
    """텍스트 입력 박스를 그리는 함수"""
    color = BLUE if active else GRAY
    pygame.draw.rect(screen, WHITE, (x, y, width, height))
    pygame.draw.rect(screen, color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (x + 5, y + 5))

def get_text_input(screen, font, prompt):
    """pygame에서 텍스트 입력을 받는 함수"""
    clock = pygame.time.Clock()
    input_text = ""
    input_active = True
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 10:  # 10자 제한
                        input_text += event.unicode
        
        screen.fill(WHITE)
        
        # 프롬프트 텍스트 출력
        prompt_surface = font.render(prompt, True, BLACK)
        screen.blit(prompt_surface, (50, 100))
        
        # 입력 박스 그리기
        draw_text_input_box(screen, font, 50, 150, 640, 40, input_text, input_active)
        
        # 입력 안내 텍스트
        if len(input_text) > 10:
            error_text = font.render("이름은 10자 이내로 입력해주세요.", True, RED)
            screen.blit(error_text, (50, 200))
        elif len(input_text) == 0:
            help_text = font.render("이름을 입력해주세요. (Enter로 확인)", True, GRAY)
            screen.blit(help_text, (50, 200))
        else:
            help_text = font.render("Enter로 확인", True, GRAY)
            screen.blit(help_text, (50, 200))
        
        pygame.display.flip()
        clock.tick(60)

def show_game_result(screen, font, Me, turn, endturn):
    """게임 결과를 pygame 화면에 표시하는 함수"""
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return  # 아무 키나 누르면 종료
        
        screen.fill(WHITE)
        
        y_offset = 50
        
        # 게임 결과 제목
        title_surface = font.render("게임 결과", True, BLACK)
        screen.blit(title_surface, (50, y_offset))
        y_offset += 50
        
        # 클리어 여부
        if turn >= endturn:
            result_surface = font.render("클리어", True, GREEN)
            screen.blit(result_surface, (50, y_offset))
            y_offset += 30
            
            gpa_surface = font.render(f"졸업 GPA: {Me.gpa}", True, BLACK)
            screen.blit(gpa_surface, (50, y_offset))
            y_offset += 30
            
            grade_surface = font.render(f"졸업 성적: {Me.grade}", True, BLACK)
            screen.blit(grade_surface, (50, y_offset))
            y_offset += 30
        else:
            fail_surface = font.render("제적당하고 말았다...", True, RED)
            screen.blit(fail_surface, (50, y_offset))
            y_offset += 30
            
            stage_surface = font.render(f"최종 스테이지: {turn}", True, BLACK)
            screen.blit(stage_surface, (50, y_offset))
            y_offset += 30
        
        # 총 전투 횟수
        battle_surface = font.render(f"총 전투 횟수: {Me.totalhap}", True, BLACK)
        screen.blit(battle_surface, (50, y_offset))
        y_offset += 50
        
        # 나의 전산몬스터
        monsters_title = font.render("나의 전산몬스터:", True, BLACK)
        screen.blit(monsters_title, (50, y_offset))
        y_offset += 30
        
        for mymon in Me.csMons:
            if mymon.dictNo != -1:
                mon_text = f"{mymon.name} lv{mymon.level} 잡은 스테이지: {mymon.stage}"
                mon_surface = font.render(mon_text, True, BLACK)
                screen.blit(mon_surface, (70, y_offset))
                y_offset += 25
        
        # 종료 안내
        exit_text = font.render("아무 키나 눌러 메뉴로 돌아가기", True, GRAY)
        screen.blit(exit_text, (50, y_offset + 30))
        
        pygame.display.flip()
        clock.tick(60)

def game_start():
    # pygame 화면 초기화 강제 실행
    from game_menu import init_pygame_screen
    init_pygame_screen()
    
    # 이제 초기화된 pygame 전역 변수들 가져오기
    from game_menu import screen, font
    
    Me = Player()
    
    # 이름 입력
    while True:
        newname = get_text_input(screen, font, "이름을 입력하세요:")
        if len(newname) > 10:
            continue  # 10자 초과시 다시 입력
        elif len(newname) < 1:
            continue  # 빈 이름시 다시 입력
        else:
            Me.name = newname
            break
    
    Me.nowCSmon = Me.csMons[0]
    Me.nowCSmon.update_fullreset()
    
    # 게임 초기값 설정
    turn = 1
    endturn = 3  # 졸업 모드의 기본 스테이지 수
    
    # 배경음악 재생 시작
    play_music(["../music/Im_a_kaist_nonmelody.wav", "../music/Im_a_kaist_melody.wav"])
    
    while turn <= endturn:
        if turn == endturn:
            # 졸업 연구
            met_monster = copy.deepcopy(graduation)
            met_monster.update_fullreset()
        # elif turn == 3:
        #     met_monster = copy.deepcopy(Hanjin)
        else:
            if turn <= 10:
                # 1~10 스테이지
                meetable_monsters = []
                for i in range(100):
                    if i<40: meetable_monsters.append(monsters["프밍기"])
                    elif i<70: meetable_monsters.append(monsters["데이타구조"])
                    elif i<100: meetable_monsters.append(monsters["이산구조"])
            elif turn <= 20:
                meetable_monsters = []
                for i in range(100):
                    if i<20: meetable_monsters.append(monsters["프밍기"])
                    elif i<50: meetable_monsters.append(monsters["데이타구조"])
                    elif i<80: meetable_monsters.append(monsters["이산구조"])
                    elif i<100: meetable_monsters.append(monsters["시프"])
            elif turn <= 30:
                meetable_monsters = []
                for i in range(100):
                    if i<10: meetable_monsters.append(monsters["프밍기"])
                    elif i<40: meetable_monsters.append(monsters["데이타구조"])
                    elif i<70: meetable_monsters.append(monsters["이산구조"])
                    elif i<90: meetable_monsters.append(monsters["시프"])
                    elif i<95: meetable_monsters.append(monsters["OS"])
                    elif i<100: meetable_monsters.append(monsters["알고개"])

                
            met_monster = wild_monster(meetable_monsters)
            met_monster.level = random.randint(met_monster.get_monster_max_level(turn)-8, 
                                                (met_monster.get_monster_max_level(turn) + max(-8, (turn%10-11))))
            met_monster.stage = turn
            if turn % 10 == 0:
                met_monster.level = met_monster.get_monster_max_level(turn)
                met_monster.grade = "중간 보스"
                met_monster.hpShield = True
            met_monster.update_fullreset()
            
        battlehap = battle(Me, met_monster, turn, endturn, screen)
        if battlehap == 0:
            turn = 1
            player.totalhap = 0
            continue
        Me.totalhap += battlehap
        # 전투 종료 후 몬스터 상태 업데이트
        # 몬스터가 쓰러진 상태라면 게임오바
        if Me.gameover():
            break
        turn += 1
    
    stop_music()
    
    # 게임 결과를 pygame 화면에 표시
    show_game_result(screen, font, Me, turn, endturn)
    
    # 게임 로그 저장
    save_game_log_csv("game_log.csv", Me, turn)

    return Me