from game_menu import *

''' 전역변수 설정 '''
battleturn = 0
hap_num = 0
player = None
enemy = None
enemyCSmon = None
sX, sY = 32, 32
stX = sX+20
stY = sY+568
esX, esY = sX+20, sY+36
psX, psY = sX+460, sY+347

BACKGROUND = pygame.image.load("../img/background.png")
STAT = pygame.image.load("../img/stat.png")
TEXT = pygame.image.load("../img/text.png")
CST = pygame.image.load("../img/CST.png")
DTS = pygame.image.load("../img/DTS.png")
AI = pygame.image.load("../img/AI.png")
PS = pygame.image.load("../img/PS.png")
SYS = pygame.image.load("../img/SYS.png")
EVENT = pygame.image.load("../img/EVENT.png")
ME = pygame.image.load("../img/monsters/ME.png")
ME = pygame.transform.scale_by(ME, 10)  # ME 이미지 크기 조정

def display_type(screen, y, x, type):
    """타입 표시 (pygame)"""
    if type == "전산이론":
        screen.blit(CST, (x, y))
    elif type == "데이터 과학":
        screen.blit(DTS, (x, y))
    elif type == "시스템-네트워크":
        screen.blit(SYS, (x, y))
    elif type == "소프트웨어디자인":
        screen.blit(EVENT, (x, y))
    elif type == "시큐어컴퓨팅":
        screen.blit(PS, (x, y))
    elif type == "비주얼컴퓨팅":
        screen.blit(EVENT, (x, y))
    elif type == "인공지능-정보서비스":
        screen.blit(AI, (x, y))
    elif type == "소셜컴퓨팅":
        screen.blit(EVENT, (x, y))
    elif type == "인터랙티브컴퓨팅":
        screen.blit(EVENT, (x, y))

def hpcolor(ratio):
    """체력 상태에 따른 색상 선택"""
    if ratio >= 14:  # 풀피 (70% 이상)
        color_pair = GREEN
    elif ratio >= 7:  # 반피 (35% 이상)
        color_pair = YELLOW
    else:  # 딸피 (35% 미만)
        color_pair = RED
    return color_pair

def animate_health_bar(screen, y, x, current_hp, target_hp, max_hp):
    """체력바를 부드럽게 애니메이션으로 업데이트 (pygame)"""
    current_ratio = int(current_hp * 31 / max_hp)
    target_ratio = int(target_hp * 31 / max_hp)
    steps = abs(current_ratio-target_ratio)  # 애니메이션 단계 수

    def draw_HP(surface, text, x, y, color, highlight=BLACK):
        fontforHP = pygame.font.Font("../neodgm.ttf", 20)
        """체력바 텍스트를 그리는 함수"""
        font_obj = fontforHP
        text_surface = font_obj.render(text, True, color, highlight)
        
        surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))
    
    if steps == 0:
        draw_HP(screen, f"{'█' * current_ratio}{' ' * (31 - current_ratio)}", x, y, hpcolor(current_ratio))
        # draw_text(screen, f"({int(current_hp)}/{max_hp})", x, y+40)
        return

    for step in range(steps + 1):
        # 현재 체력 비율 계산
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)
        # 체력바 출력
        draw_HP(screen, f"{'█' * interpolated_ratio}{' ' * (31 - interpolated_ratio)}", x, y, hpcolor(interpolated_ratio))
        # draw_text(screen, f"({int(temp_hp)}/{max_hp})", x, y+40)
        pygame.display.flip()
        time.sleep(0.05)  # 애니메이션 속도 

def display_status(screen, detail=False):
    """상태 화면 표시 (pygame)"""
    # 화면 배경 초기화
    screen.fill((113,113,113))
    
    screen.blit(BACKGROUND, (sX, sY))

    # 배틀 정보 출력
    draw_text(screen, f"플레이어: {player.name}", sX, sY+920, VIOLET)
    draw_text(screen, f"스테이지 {battleturn}", sX, sY+960, BLUE)
    draw_text(screen, f"턴 {hap_num}", sX, sY+1000, CYAN)
    
    screen.blit(STAT, (esX, esY))
    image = pygame.image.load(enemyCSmon.image)  # 몬스터 이미지 로드
    image = pygame.transform.scale_by(image, 8)  # 이미지 크기 조정
    screen.blit(image, (esX+860-image.get_width()//2, esY+310-image.get_height()))
    draw_text(screen, f"{enemyCSmon.name}", esX+64, esY+52, WHITE)
    draw_text(screen, f"lv.{enemyCSmon.level}", esX+384, esY+52, WHITE)
    animate_health_bar(screen, esY+104, esX+135, enemyCSmon.nowhp, enemyCSmon.nowhp, enemyCSmon.HP)
    for i, j in enumerate(enemyCSmon.type):
        display_type(screen, esY, esX+470+i*124, j)
            
        
    # 플레이어 상태 출력
    screen.blit(STAT, (psX, psY))
    screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
    for i, mymon in enumerate(player.csMons):
        color = RED if not mymon.is_alive() else BLUE if mymon.dictNo == -1 else BLACK
        draw_text(screen, "◒", psX+64+i*32, psY+16, RED)
    draw_text(screen, f"{player.nowCSmon.name}", psX+64, psY+52, WHITE)
    draw_text(screen, f"lv.{player.nowCSmon.level}", psX+384, psY+52, WHITE)
    animate_health_bar(screen, psY+104, psX+135, player.nowCSmon.nowhp, player.nowCSmon.nowhp, player.nowCSmon.HP)
    for i, j in enumerate(player.nowCSmon.type):
        display_type(screen, psY, psX+470+i*124, j)
        
    if detail:
        display_details(screen, player.nowCSmon, sX+1264, "몬스터")

    screen.blit(TEXT, (sX+9, sY+536))

def display_details(screen, target, x, case="몬스터"):
    """상세 정보 출력 (pygame)"""
    if case == "몬스터":
        details = [
            (("이름", 0, 99), (f"{target.name}", 192, CYAN)),
            (("레벨", 0, 99), (f"{target.level}", 192, CYAN)),
            (("레벨업까지", 0, 99), (f"{target.max_exp - target.exp}", 192, BLUE), ("경험치 남음", 352, 99)),
            "",
            "체력",
            (("공격", 0, 99), (f"{target.ATK}", 192, CYAN), None if target.Rank[1]==0 else ((("+" if target.Rank[1]>0 else "-") + f"{abs(target.Rank[1])}"), 200, min(7-target.Rank[1], 7+target.Rank[1]))),
            (("방어", 0, 99), (f"{target.DEF}", 192, CYAN), None if target.Rank[2]==0 else ((("+" if target.Rank[2]>0 else "-") + f"{abs(target.Rank[2])}"), 200, min(7-target.Rank[2], 7+target.Rank[2]))),
            (("특공", 0, 99), (f"{target.SP_ATK}", 192, CYAN), None if target.Rank[3]==0 else ((("+" if target.Rank[3]>0 else "-") + f"{abs(target.Rank[3])}"), 200, min(7-target.Rank[3], 7+target.Rank[3]))),
            (("특방", 0, 99), (f"{target.SP_DEF}", 192, CYAN), None if target.Rank[4]==0 else ((("+" if target.Rank[4]>0 else "-") + f"{abs(target.Rank[4])}"), 200, min(7-target.Rank[4], 7+target.Rank[4]))),
            (("속도", 0, 99), (f"{target.SPD}", 192, CYAN), None if target.Rank[5]==0 else ((("+" if target.Rank[5]>0 else "-") + f"{abs(target.Rank[5])}"), 200, min(7-target.Rank[5], 7+target.Rank[5]))),
            "",
            (("등급", 0, 99), (f"{target.grade}", 192, WHITE if target.grade == "일반" else YELLOW if target.grade == "중간 보스" else RED)),
            (("만난 곳", 0, 99), (f"스테이지 {target.stage}", 192, CYAN) if isinstance(target.stage, int) else (f"{target.stage}", 192, CYAN)),
            (("설명", 0, 99), (f"{target.description}", 192, 99)),
        ]
        for i, detail_item in enumerate(details):
            y_pos = sY + 50 + i * 40
            if isinstance(detail_item, tuple):  # detail이 튜플인 경우
                for detail in detail_item:
                    if not isinstance(detail, tuple) and not isinstance(detail, str):
                        continue
                    draw_text(screen, detail[0], x + detail[1], y_pos, detail[2])
            elif isinstance(detail_item, str):  # detail이 문자열인 경우
                if detail_item == "체력":
                    current_ratio = int(target.nowhp * 20 / target.HP)
                    draw_text(screen, "체력", x, y_pos)
                    draw_text(screen, f"{'█' * current_ratio}{' ' * (20 - current_ratio)}", x + 192, y_pos, hpcolor(current_ratio))
                else:
                    draw_text(screen, detail_item, x, y_pos)

def wait_for_key():
    """키 입력 대기 (pygame)"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'enter'
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return 'escape'
                elif event.key == pygame.K_UP:
                    return 'up'
                elif event.key == pygame.K_DOWN:
                    return 'down'
                elif event.key == pygame.K_LEFT:
                    return 'left'
                elif event.key == pygame.K_RIGHT:
                    return 'right'
        pygame.time.wait(50)

def option_choice(screen, option_case, description=None, coloring=None, temp=None):
    """옵션 선택 메뉴 (pygame)"""
    current_index = 0
    
    while True:
        display_status(screen)  # 상태 출력

        if option_case == "스킬":
            display_status(screen, True)  # 상태 출력
            options = player.nowCSmon.skills.values()
            for i, option in enumerate(options):
                x_pos = stX + (300 * (i % 2))
                y_pos = stY + int(i / 2) * 56
                
                color = WHITE
                if coloring != None and coloring[i] != False:
                    color = coloring[i]
                
                prefix = "> " if i == current_index else "  "
                draw_text(screen, f"{prefix}{option.name}", x_pos, y_pos, color)
                
                if i == current_index:
                    # 선택된 스킬의 상세정보 표시
                    draw_text(screen, f"{description[i][0]}", sX+30, stY+120)
                    display_type(screen, stY, sX+900-100, option.skill_type)
                    draw_text(screen, "물리   " if option.effect_type == "Pdamage" else "특수" if option.effect_type == "Sdamage" else "----", sX+900-40, stY)
                    draw_text(screen, f"pp     {option.nowpp}/{option.pp}", sX+900-100, stY+25)
                    if description[i][1] != None:
                        draw_text(screen, f"위력   {description[i][1]}", sX+900-100, stY+50)
                    else:
                        draw_text(screen, f"위력   ----", sX+900-100, stY+50)
                    draw_text(screen, f"명중률 {option.acc if option.acc != -1 else '----'}", sX+900-100, stY+75)
        
        elif option_case == "몬스터":
            options = player.csMons
            for i, option in enumerate(options):
                x_pos = stX + (300 * (i % 2))
                y_pos = stY + int(i / 2) * 56
                
                color = 0
                if coloring != None and coloring[i] != False:
                    color = coloring[i]
                elif option.dictNo == -1:
                    color = 4
                
                prefix = "> " if i == current_index else "  "
                draw_text(screen, f"{prefix}{option.name}", x_pos, y_pos, color)
                
                if i == current_index and option.dictNo != -1:
                    display_details(screen, option, sX+1264, "몬스터")  # 상세 정보 출력
                    
            if temp != None:
                draw_text(screen, f"잡은 전산몬: {temp.name}(lv {temp.level})", sX+900-200, stY+75)
              
                
        elif option_case == "아이템":
            options = player.items
            for i, option in enumerate(options):
                x_pos = stX + (300 * (i % 2))
                y_pos = stY + int(i / 2) * 56
                
                color = 0
                if coloring != None and coloring[i] != False:
                    color = coloring[i]
                elif option.grade == "아이템아님":  # 빈 슬롯인 경우
                    color = 4
                
                prefix = "> " if i == current_index else "  "
                draw_text(screen, f"{prefix}{option.name}", x_pos, y_pos, color)
                
                if i == current_index:
                    if temp != None:
                        grade_color = 2 if temp.grade == "레전더리" else 6 if temp.grade == "에픽" else 3 if temp.grade == "레어" else 0
                        draw_text(screen, f"얻은 아이템: {temp.name}", sX+900-200, stY+75, grade_color)
                    draw_text(screen, f"{description[i]}", sX+30, stY+120)
            
             
        elif option_case == "배틀옵션":
            display_status(screen, True)  # 상태 출력
            options = ["스킬 사용", "전산몬 교체", "아이템 사용", "전산몬 포획"]
            for i, option in enumerate(options):
                x_pos = stX + (300 * (i % 2))
                y_pos = stY + int(i / 2) * 56
                
                prefix = "> " if i == current_index else "  "
                draw_text(screen, f"{prefix}{option}", x_pos, y_pos, WHITE)

        pygame.display.flip()
        
        key = wait_for_key()
        if key == 'enter':  # Enter 키를 누르면 선택 완료
            option_select_sound()
            return current_index
        if key == 'escape':  # ESC 키를 누르면 취소
            if option_case == "배틀옵션":
                continue
            option_escape_sound()
            return -1
        elif len(options) == 1:  # 옵션이 하나일 경우
            current_index = 0
        elif key == 'up' and (current_index > 1 and current_index < len(options)):
            current_index -= 2
            option_change_sound()
        elif key == 'down' and (current_index >=0 and current_index < len(options)-2):
            current_index += 2
            option_change_sound()
        elif key == 'left' and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == 'right' and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options)-1):
            current_index += 1
            option_change_sound()

def select_skill(screen):
    """방향키로 스킬 선택 (pygame)"""
    skills = list(player.nowCSmon.skills.keys())
    coloring = [False]*len(skills)  # 스킬 색상 리스트
    for i, skill in enumerate(skills):
        Cskill = player.nowCSmon.skills[skill]
        if Cskill.effect_type == "Pdamage" or Cskill.effect_type == "Sdamage":
            if Cskill.Comp(enemyCSmon) >= 2:
                coloring[i] = 2  # 적에게 효과가 굉장한 스킬 표시
            elif Cskill.Comp(enemyCSmon) == 0:
                coloring[i] = 6  # 적에게 효과가 없는 스킬 표시
            elif Cskill.Comp(enemyCSmon) <= 0.5:
                coloring[i] = 5  # 적에게 효과가 별로인 스킬 표시
    descriptions = [[
        player.nowCSmon.skills[skill].description,
        player.nowCSmon.skills[skill].skW if player.nowCSmon.skills[skill].effect_type == "Pdamage" or player.nowCSmon.skills[skill].effect_type == "Sdamage" else None
        ] for skill in skills]  # 스킬 설명 리스트
    display_status(screen, True)  # 상태 출력
    index = option_choice(screen, "스킬", descriptions, coloring)  # 스킬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    return skills[index]  # 선택된 스킬 이름 반환

def select_monster(screen, temp=None):
    """방향키로 전산몬 선택 (pygame)"""
    # 현재 전산몬 표시
    coloring = [False, False, False, False, False, False]
    for i in range(6):
        if player.csMons[i].dictNo == -1:
            coloring[i] = 4 # 빈 슬롯 표시
        elif player.csMons[i].is_alive() == False:
            coloring[i] = 1  # 죽은 전산몬 표시
        elif player.csMons[i] == player.nowCSmon:
            coloring[i] = 5  # 현재 전산몬 표시

    display_status(screen)
    index = option_choice(screen, "몬스터", coloring = coloring, temp=temp)  # 전산몬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[index].dictNo == -1:
        display_status(screen)
        draw_text(screen, "  빈 슬롯이다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return select_monster(screen, temp)
    return index  # 선택된 전산몬 인덱스 반환

def select_item(screen, temp=None):
    """방향키로 아이템 선택 (pygame)"""
    descriptions = [i.description for i in player.items]  # 아이템 설명 리스트
    coloring = [False]*len(player.items)  # 아이템 색상 리스트
    for i in range(len(player.items)):
        if player.items[i].name == "빈 슬롯":
            coloring[i] = 4
        elif player.items[i].grade == "레어":
            coloring[i] = 3
        elif player.items[i].grade == "에픽":
            coloring[i] = 6
        elif player.items[i].grade == "레전더리":
            coloring[i] = 2
    display_status(screen)
    index = option_choice(screen, "아이템", descriptions, coloring, temp)  # 아이템 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.items[index].name == "빈 슬롯":
        display_status(screen)
        draw_text(screen, "  빈 슬롯이다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return select_item(screen, temp)
    return index  # 선택된 아이템 이름 반환

def select_action(screen):
    """행동 선택 메뉴 (pygame)"""
    display_status(screen, detail=True)  # 상태 출력
    index = option_choice(screen, "배틀옵션")  # 행동 선택
    return index

''' 스킬 '''
def skill_message(screen, user, target, skill, counter_skill=None, damage = None, crit = None):
    """스킬 메시지를 출력하기 전에 상태를 먼저 출력 (pygame)"""
    if damage != None:
        damage = int(damage)
    # 스킬 메시지 출력
    display_status(screen, True)  # 상태 출력
    
    if skill.effect_type == "reflect":
        if damage == -121:
            draw_text(screen, "  하지만 실패했다!", stX, stY, WHITE)
        elif counter_skill is not None:
            if counter_skill.effect_type == "Pdamage" or counter_skill.effect_type == "Sdamage":
                if skill.skW == 0:
                    draw_text(screen, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 방어했다.", stX, stY, WHITE)
                else:
                    draw_text(screen, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 반사!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    display_status(screen, True)  # 상태 출력 
                    if damage  == False:
                        if counter_skill.Comp(user) == 0:
                            draw_text(screen, "  효과가 없는 것 같다...", stX, stY, WHITE)
                        else:
                            draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
                    else:
                        if counter_skill.Comp(user) >= 2:
                            draw_text(screen, "  효과가 굉장했다!", stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            display_status(screen, True)  # 상태 출력
                        elif counter_skill.Comp(user) < 1:
                            draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            display_status(screen, True)  # 상태 출력
                        draw_text(screen, f"  {target.name}이/가 {damage}의 데미지를 입었다.", stX, stY, WHITE)
            else:
                draw_text(screen, "  그러나 아무 일도 일어나지 않았다!", stX, stY, WHITE)
        else:
            draw_text(screen, "  그러나 아무 일도 일어나지 않았다!", stX, stY, WHITE)

    elif skill.effect_type == "Pdamage" or skill.effect_type == "Sdamage":
        if damage  == False:
            if skill.Comp(target) == 0:
                draw_text(screen, "  효과가 없는 것 같다...", stX, stY, WHITE)
            else:
                draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
        else:
            if skill.Comp(target) >= 2:
                draw_text(screen, "  효과가 굉장했다!", stX, stY, WHITE)
            elif skill.Comp(target) <= 0.5:
                draw_text(screen, "  효과가 별로인 듯 하다...", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)  # 상태 출력
            draw_text(screen, f"  {target.name}이/가 {damage}의 데미지를 입었다.", stX, stY, WHITE)

    elif skill.effect_type == "halve_hp":
        if damage == False:
            draw_text(screen, f"  그러나 {user.name}의 공격은 빗나갔다!", stX, stY, WHITE)
        else:
            draw_text(screen, f"  {target.name}의 체력이 반으로 줄었다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen, True)  # 상태 출력
            draw_text(screen, f"  {target.name}이/가 {damage}의 데미지를 입었다!", stX, stY, WHITE)
    
    elif skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.HP)
        draw_text(screen, f"  {user.name}의 체력이 {heal_amount} 회복되었다!", stX, stY, WHITE)

    elif skill.effect_type == "buff":
        if isinstance(skill.skW, tuple):
            for B in skill.skW:
                if B % 8 == 0:
                    draw_text(screen, f"  {user.name}의 급소율이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 1:
                    draw_text(screen, f"  {user.name}의 공격이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 2:
                    draw_text(screen, f"  {user.name}의 방어가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 3:
                    draw_text(screen, f"  {user.name}의 특수공격이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 4:
                    draw_text(screen, f"  {user.name}의 특수방어가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 5:
                    draw_text(screen, f"  {user.name}의 스피드가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 6:
                    draw_text(screen, f"  {user.name}의 회피율이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif B % 8 == 7:
                    draw_text(screen, f"  {user.name}의 명중률이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                if B != skill.skW[-1]:
                    pygame.display.flip()
                    wait_for_key()
                    display_status(screen, True)  # 상태 출력
        else:
            if skill.skW % 8 == 0:
                draw_text(screen, f"  {user.name}의 급소율이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 1:
                draw_text(screen, f"  {user.name}의 공격이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 2:
                draw_text(screen, f"  {user.name}의 방어가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 3:
                draw_text(screen, f"  {user.name}의 특수공격이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 4:
                draw_text(screen, f"  {user.name}의 특수방어가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 5:
                draw_text(screen, f"  {user.name}의 스피드가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 6:
                draw_text(screen, f"  {user.name}의 회피율이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif skill.skW % 8 == 7:
                draw_text(screen, f"  {user.name}의 명중률이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()  # 메시지를 잠시 보여줌
    if crit:
        display_status(screen, True)  # 상태 출력
        draw_text(screen, f"  급소에 맞았다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

def use_skill(user, target, skill, counter_skill):
    """스킬 효과를 처리 (체력 계산만 수행)"""
    skill.nowpp -= 1
    if user.usedskill is not None:
        if user.usedskill.name == skill.name:
            skill.consecutive_uses += 1
        else:
            skill.consecutive_uses = 1
    else: 
        skill.consecutive_uses = 1
    user.usedskill = skill

    # reflect 스킬 처리
    if skill.effect_type == "reflect":
        if random.random() > skill.acc*(0.5**(skill.consecutive_uses-1))/100:
            return False, -121, False

        if counter_skill is not None:
            if counter_skill.effect_type == "Pdamage" or counter_skill.effect_type == "Sdamage":
                damage, crit= counter_skill.damage(user, target)
                damage = damage * skill.skW
                target.nowhp = max(0, int(target.nowhp - damage))       
                if crit: Critical()     
                elif damage > target.HP//2: Damage_strong()
                elif damage > 0: Damage_weak()
                if target.hpShield and target.nowhp<=target.HP//2:
                    target.nowhp = target.HP//2
                    target.hpShield = False
                return True, damage, crit
            else: pass
        else:
            return False, 0, False

    # damage 스킬 처리
    if skill.effect_type == "Pdamage" or skill.effect_type == "Sdamage":
        damage, crit = skill.damage(target, user)
        target.nowhp = max(0, int(target.nowhp - damage))
        if crit: Critical()
        elif damage > 10: Damage_strong()
        elif damage > 0: Damage_weak()
        if target.hpShield and target.nowhp<=target.HP//2:
            target.nowhp = target.HP//2
            target.hpShield = False
        return False, damage, crit

    # halve_hp 스킬 처리
    if skill.effect_type == "halve_hp":
        if skill.is_hit(target, user) == False:
            return False, False, False
        current_hp = target.nowhp
        target.nowhp = max(0, target.nowhp // 2)
        if target.nowhp > 10: Damage_strong()
        elif target.nowhp > 0: Damage_weak()
        if target.hpShield and target.nowhp<=target.HP//2:
            target.nowhp = target.HP//2
            target.hpShield = False
        damage = current_hp - target.nowhp
        return False, damage, False

    # heal 스킬 처리
    if skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.HP)
        Heal()
        user.nowhp = min(user.HP, user.nowhp + heal_amount)
        return False, 0, False

    # buff 스킬 처리
    if skill.effect_type == "buff":
        if isinstance(skill.skW, tuple):
            for B in skill.skW:
                user.Rank[B % 8] = max(-6,min(6, user.Rank[B % 8] + B//8 + 1))
                if B % 8 == 0:
                    user.Rank[0] = max(0,min(3, user.Rank[0]))
        else:
            user.Rank[skill.skW % 8] = max(-6,min(6, user.Rank[skill.skW % 8] + skill.skW//8 + 1))
            if skill.skW % 8 == 0:
                user.Rank[0] = max(0,min(3, user.Rank[0]))
        return False, 0, False

    return False, 0, False

def skillstep_player(screen, myskill, yourskill):
    nowCSmon_skill = myskill
    enemyCSmon_skill = yourskill

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    display_status(screen, True)  # 상태 출력
    draw_text(screen, f"  {player.nowCSmon.name}의 {nowCSmon_skill.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    display_status(screen, True)  # 상태 출력
    stop, damage, crit = use_skill(player.nowCSmon, enemyCSmon, nowCSmon_skill, enemyCSmon_skill)
    animate_health_bar(screen, esY+104, esX+135,enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)  
    skill_message(screen,  player.nowCSmon, enemyCSmon, nowCSmon_skill, enemyCSmon_skill, damage, crit)

    return stop

def skillstep_enemy(screen, myskill, yourskill):
    nowCSmon_skill = myskill
    enemyCSmon_skill = yourskill

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    display_status(screen, True)  # 상태 출력
    draw_text(screen, f"  {enemyCSmon.name}의 {enemyCSmon_skill.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    display_status(screen, True)  # 상태 출력
    stop, damage, crit = use_skill(enemyCSmon, player.nowCSmon, enemyCSmon_skill, nowCSmon_skill)
    animate_health_bar(screen, esY+104, esX+135,enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)    
    skill_message(screen,  enemyCSmon, player.nowCSmon, enemyCSmon_skill, nowCSmon_skill, damage, crit)

    return stop

def enemyskill(): 
    # 적 스킬 랜덤 선택
    enemyCSmon_skill_name = random.choice(list(enemyCSmon.skills.keys()))
    enemyCSmon_skill = enemyCSmon.skills[enemyCSmon_skill_name]
    if enemyCSmon_skill.nowpp == 0:
        # 스킬 포인트가 없으면 다른 스킬 선택
        enemyskill()
    return enemyCSmon_skill
    
def skill_phase(screen):
    # 플레이어 스킬 선택
    selected_skill = select_skill(screen)
    if selected_skill == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    nowCSmon_skill = player.nowCSmon.skills[selected_skill]
    if nowCSmon_skill.nowpp == 0:
        display_status(screen)
        draw_text(screen, f"  {nowCSmon_skill.name}의 스킬 포인트가 없어!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return skill_phase(screen)
    if nowCSmon_skill.effect_type == "buff":
        if isinstance(nowCSmon_skill.skW, tuple):
            for B in nowCSmon_skill.skW:
                if player.nowCSmon.Rank[B % 8] == 6 and B//8 >= 0 or player.nowCSmon.Rank[B % 8] == -6 and B//8 <= -2:
                    display_status(screen)
                    draw_text(screen, f"  {player.nowCSmon.name}의 "
                                        +("공격은"       if B % 8 == 1 else
                                            "방어는"        if B % 8 == 2 else
                                            "특수공격은"    if B % 8 == 3 else
                                            "특수방어는"    if B % 8 == 4 else
                                            "스피드는"      if B % 8 == 5 else
                                            "회피율은"      if B % 8 == 6 else
                                            "명중률은"      if B % 8 == 7 else
                                            "급소율은") + " 이미 최대치야!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    return skill_phase(screen)
        else:
            if player.nowCSmon.Rank[nowCSmon_skill.skW % 8] == 6 and nowCSmon_skill.skW//8 >= 0 or player.nowCSmon.Rank[nowCSmon_skill.skW % 8] == -6 and nowCSmon_skill.skW//8 <= -2:
                display_status(screen)
                draw_text(screen, f"  {player.nowCSmon.name}의 "
                                        +("공격은"       if nowCSmon_skill.skW % 8 == 1 else
                                            "방어는"        if nowCSmon_skill.skW % 8 == 2 else
                                            "특수공격은"    if nowCSmon_skill.skW % 8 == 3 else
                                            "특수방어는"    if nowCSmon_skill.skW % 8 == 4 else
                                            "스피드는"      if nowCSmon_skill.skW % 8 == 5 else
                                            "회피율은"      if nowCSmon_skill.skW % 8 == 6 else
                                            "명중률은"      if nowCSmon_skill.skW % 8 == 7 else
                                            "급소율은") + " 이미 최대치야!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                return skill_phase(screen)
    enemyCSmon_skill = enemyskill()
    # 우선순위 비교
    if nowCSmon_skill.priority > enemyCSmon_skill.priority or (nowCSmon_skill.priority == enemyCSmon_skill.priority and player.nowCSmon.CSPD >= enemyCSmon.CSPD):
        stop = skillstep_player(screen, nowCSmon_skill, enemyCSmon_skill)
        if enemyCSmon.is_alive() and not stop:
            skillstep_enemy(screen, nowCSmon_skill, enemyCSmon_skill)
    else:
        stop = skillstep_enemy(screen, nowCSmon_skill, enemyCSmon_skill)
        if player.nowCSmon.is_alive() and not stop:
            skillstep_player(screen, nowCSmon_skill, enemyCSmon_skill)

''' 교체 '''
def swap_phase(screen, must_swap=False):
    """전산몬 교체 단계"""
    currentCSmon = player.nowCSmon  # 현재 전산몬

    # 교체할 전산몬 선택
    selected_monster = select_monster(screen)
    
    # 선택시 예외 처리
    if selected_monster == -1:
        if must_swap:
            display_status(screen)
            draw_text(screen, f"  {currentCSmon.name}은/는 쓰러져서 교체해야 해!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            return swap_phase(screen, must_swap)  # 다시 선택
        return -1
    if player.csMons[selected_monster].dictNo == -1:
        display_status(screen, currentCSmon, enemy)
        draw_text(screen, f"  빈 슬롯이다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return swap_phase(screen, must_swap)  # 다시 선택

    new_monster = player.csMons[selected_monster]
    
    # 교체할 전산몬 관련 예외 처리
    if new_monster.is_alive() == False:
        display_status(screen)
        draw_text(screen, f"  {new_monster.name}은/는 이미 쓰러졌어!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return swap_phase(screen, must_swap)  # 다시 선택
    elif new_monster == currentCSmon:
        display_status(screen)
        draw_text(screen, f"  {currentCSmon.name}은/는 이미 나와 있어!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return swap_phase(screen, must_swap)  # 다시 선택
    
    display_status(screen)
    draw_text(screen, f"  수고했어, {currentCSmon.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    # 교체
    player.nowCSmon = new_monster

    display_status(screen)
    draw_text(screen, f"  나와라, {new_monster.name}!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    # 강제로 교체해야 했던 경우 턴 소모 없이 즉시 교체
    if must_swap: 
        return   

    # 적 스킬 랜덤 선택
    display_status(screen)
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(screen, None, enemyCSmon_skill)  # 적 스킬 사용
    return

''' 아이템 사용 '''
def use_item(item, target):
    # heal 아이템 처리
    if item.effect == "heal":
        heal_amount = max(item.fixed, int(target.HP * item.varied))
        target.nowhp = min(target.HP, target.nowhp + heal_amount)
        Heal()
    elif item.effect == "buff":
        if isinstance(item.varied, tuple):
            for v in item.varied:
                target.Rank[v % 8] = max(-6, min(6, target.Rank[v % 8] + v//8 + 1))
        else: 
            target.Rank[item.varied % 8] = max(-6,min(6, target.Rank[item.varied % 8] + item.varied//8 + 1))
    return False

def item_message(screen, item, target):
    """아이템 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 아이템 메시지 출력
    if item.effect == "heal":
        heal_amount = max(item.fixed, int(target.HP * item.varied))
        if item.canuse_on_fainted == True:
            draw_text(screen, f"  {target.name}이/가 부활했다!", stX, stY, WHITE)
        else:
            draw_text(screen, f"  {target.name}의 체력이 {heal_amount} 회복되었다!", stX, stY, WHITE)
    elif item.effect == "buff":
        if isinstance(item.varied, tuple):
            for v in item.varied:
                if v % 8 == 0:
                    draw_text(screen, f"  {target.name}의 급소율이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 1:
                    draw_text(screen, f"  {target.name}의 공격이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 2:
                    draw_text(screen, f"  {target.name}의 방어가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 3:
                    draw_text(screen, f"  {target.name}의 특수공격이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 4:
                    draw_text(screen, f"  {target.name}의 특수방어가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 5:
                    draw_text(screen, f"  {target.name}의 스피드가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 6:
                    draw_text(screen, f"  {target.name}의 회피율이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                elif v % 8 == 7:
                    draw_text(screen, f"  {target.name}의 명중률이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
        else:
            if item.varied % 8 == 0:
                draw_text(screen, f"  {target.name}의 급소율이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 1:
                draw_text(screen, f"  {target.name}의 공격이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 2:
                draw_text(screen, f"  {target.name}의 방어가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 3:
                draw_text(screen, f"  {target.name}의 특수공격이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 4:
                draw_text(screen, f"  {target.name}의 특수방어가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 5:
                draw_text(screen, f"  {target.name}의 스피드가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 6:
                draw_text(screen, f"  {target.name}의 회피율이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            elif item.varied % 8 == 7:
                draw_text(screen, f"  {target.name}의 명중률이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"), stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()  # 메시지를 잠시 보여줌

def item_phase(screen):
    """아이템 사용 단계"""
    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    item_num = select_item(screen)  # 아이템 선택
    if item_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    mon_num = select_monster(screen)  # 전산몬 선택
    if mon_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[mon_num].nowhp == 0:
        if player.items[item_num].canuse_on_fainted == False:
            display_status(screen)
            draw_text(screen, f"  쓰러진 전산몬에게는 이 아이템을 사용할 수 없다.", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            return item_phase(screen)
    display_status(screen)  # 상태 출력
    draw_text(screen, f"  {player.items[item_num].name}을/를 {player.csMons[mon_num].name}에게 사용했다!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    use_item(player.items[item_num], player.csMons[mon_num])  # 아이템 사용
    
    animate_health_bar(screen, esY+104, esX+135,enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(screen, psY+104, psX+135, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)
    display_status(screen)  # 상태 출력
    item_message(screen, player.items[item_num], player.csMons[mon_num])  # 아이템 메시지 출력
    player.items[item_num] = items["빈 슬롯"]  # 사용한 아이템 삭제

    # 적 스킬 랜덤 
    display_status(screen, True)  # 상태 출력
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(screen, None, enemyCSmon_skill)  # 적 스킬 사용

''' 포획 '''
def catch_monster(screen):
    """포획 시도"""
    display_status(screen)  # 상태 출력
    draw_text(screen, f"  가랏, 몬스터볼!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()  # 메시지를 잠시 보여줌

    enemydictNo = enemyCSmon.dictNo  # 적 몬스터 이름
    enemyCSmon.dictNo = -2  # 포획 중에는 몬스터볼로 표시
    display_status(screen)  # 상태 출력
    draw_text(screen, f"  {enemyCSmon.name}을/를 포획 시도 중", stX, stY, WHITE)
    # 포획 성공 확률 계산 (체력이 낮을수록 성공 확률 증가)
    # 플레이어 레벨
    max_level = max(player.csMons, key=lambda x: x.level).level
    catch_rate = max(1, 100 + max_level - enemyCSmon.level - int((enemyCSmon.nowhp / enemyCSmon.HP) * 75))  # 최소 25%, 최대 100%
    successes = [random.randint(1, 100)**(1/3) <= catch_rate**(1/3), 
                 random.randint(1, 100)**(1/3) <= catch_rate**(1/3),  
                 random.randint(1, 100)**(1/3) <= catch_rate**(1/3)]

    # 몬스터볼 반짝거리는 연출
    for i in range(6):  # 6번 반복 (반짝거림 효과)
        time.sleep(0.3)  # 0.3초 대기
        if i % 2 == 0:
            catching()
            blink_times = int(2**((6-i)/2))
            for j in range(blink_times):  # 몬스터볼이 반짝이는 효과
                enemyCSmon.dictNo = -3  # 반짝이는 상태
                display_status(screen)
                draw_text(screen, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}", stX, stY, WHITE)
                pygame.display.flip()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
                enemyCSmon.dictNo = -2  # 반짝이는 상태
                display_status(screen)
                draw_text(screen, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}", stX, stY, WHITE)
                pygame.display.flip()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
            if successes[i//2] == False:
                break
        else:
            enemyCSmon.dictNo = -2  # 반짝이는 상태
            display_status(screen)
            draw_text(screen, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}", stX, stY, WHITE)
            pygame.display.flip()
        display_status(screen)
        draw_text(screen, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}", stX, stY, WHITE)
        pygame.display.flip()
    time.sleep(0.5)  # 포획 시도 중 메시지 출력 후 대기

    success = successes[0] and successes[1] and successes[2]  # 포획 성공 여부
    
    if success:
        caught()
        display_status(screen)
        draw_text(screen, f"  {enemyCSmon.name}이/가 잡혔다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()

        # 플레이어 몬스터 슬롯에 추가
        for i in range(len(player.csMons)):
            if player.csMons[i].dictNo == -1:
                player.csMons[i] = copy.deepcopy(enemyCSmon)
                player.csMons[i].dictNo = enemydictNo
                break
        else:
            display_status(screen)
            draw_text(screen, "  몬스터 슬롯이 가득 찼다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            display_status(screen)
            draw_text(screen, f"  놓아줄 몬스터를 선택하자.", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            # 몬스터 교체
            tempmon = copy.deepcopy(enemyCSmon)
            tempmon.dictNo = enemydictNo
            selected_monster = select_monster(screen, tempmon)
            if selected_monster == -1:
                display_status(screen)
                draw_text(screen, f"  포획을 취소했다.", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
            else:
                display_status(screen)
                draw_text(screen, f"  {player.csMons[selected_monster].name}, 그리울거야!", stX, stY, WHITE)
                if player.nowCSmon == player.csMons[selected_monster]:
                    player.csMons[selected_monster] = tempmon
                    player.nowCSmon = player.csMons[selected_monster]  # 교체된 몬스터로 변경
                else:
                    player.csMons[selected_monster] = tempmon
                    player.csMons[selected_monster].dictNo = enemydictNo
                pygame.display.flip()
                wait_for_key()
        return True
    else:
        # 포획 실패 시 적 몬스터 이름 복원
        enemyCSmon.dictNo = enemydictNo
        display_status(screen)
        # 포획 실패 메시지 출력
        draw_text(screen, f"  앗, {enemyCSmon.name}이/가 몬스터볼에서 나왔다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        return False

def catch_phase(screen):
    """포획 단계"""
    
    res = catch_monster(screen) 
    if res:
        return True
    
    # 적 스킬 랜덤 선택
    display_status(screen, True)  # 상태 출력
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(screen, None, enemyCSmon_skill)  # 적 스킬 사용
    pygame.display.flip()
    wait_for_key()  # 메시지를 잠시 보여줌
    return False  # 포획 실패

    # 포획 시도

''' 종합 '''
def drop_item(screen):
    droppable_items = []
    for i in range(100):
        if i<30:
            droppable_items.append(items["빈 슬롯"])
        elif i<70:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "노말")))
        elif i<90:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "레어")))
        elif i<98:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "에픽")))
        else:
            droppable_items.append(random.choice(list(item for item in items.values() if item.grade == "레전더리")))
    droppedtem = copy.deepcopy(random.choice(droppable_items))
    if droppedtem.name == "빈 슬롯":
        return
    
    # 드랍된 아이템 메시지 출력
    display_status(screen)
    draw_text(screen, f"  {droppedtem.name}을/를 획득했다!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

    # 아이템을 슬롯에 추가
    for i in range(len(player.items)):
        if player.items[i].name == "빈 슬롯":
            player.items[i] = copy.deepcopy(droppedtem)
            break
    else:
        # 아이템 슬롯이 가득 찼을 때
        display_status(screen)
        draw_text(screen, "  그러나 아이템 슬롯이 가득 차있다!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        display_status(screen)
        draw_text(screen, f"  버릴 아이템을 선택하자!", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
        # 몬스터 교체
        selected_item = select_item(screen, droppedtem)
        if selected_item == -1:
            display_status(screen)
            draw_text(screen, f"  {droppedtem.name}의 획득을 포기했다.", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
        else:
            display_status(screen)
            draw_text(screen, f"  {player.items[selected_item].name}을/를 버렸다!", stX, stY, WHITE)
            player.items[selected_item] = droppedtem  # 교체된 아이템으로 변경 
            pygame.display.flip()
            wait_for_key()

def exp_gain(screen):
    """경험치 획득"""
    # 현재 전산몬(nowCSmon)에 대한 처리 먼저 수행
    mymon = player.nowCSmon
    monnum = player.csMons.index(mymon)
    max_level = max(player.csMons, key=lambda x: x.level).level
    enemyCSmon.drop_exp = int(enemyCSmon.drop_exp * max(1, enemyCSmon.level-max_level))  # 적 경험치 조정
    if mymon.level >= mymon.get_monster_max_level(battleturn):
        display_status(screen)
        draw_text(screen, f"  {mymon.name}은/는 이미 레벨 제한에 도달했다.", stX, stY, WHITE)
        pygame.display.flip()
        wait_for_key()
    else:
        if mymon.participated == False:  # 전투에 참여하지 않은 경우
            exp = int(enemyCSmon.drop_exp * player.concentration * player.knowhow / 10000)
        else:
            exp = int(enemyCSmon.drop_exp * player.knowhow / 100)
            for ev in enemyCSmon.giving_EV:
                mymon.EV[ev] =+ 1

        display_status(screen)
        draw_text(screen, f"  {mymon.name}이/가 {exp}의 경험치를 얻었다!", stX, stY, WHITE)
        mymon.exp += exp
        pygame.display.flip()
        wait_for_key()
        if mymon.exp >= mymon.max_exp:
            if mymon.level < mymon.get_monster_max_level(battleturn):
                Level_up()
                evocheck = mymon.level_up(battleturn)
                if evocheck == True:
                    evolution(screen, mymon, monnum, True)
                display_status(screen)
                draw_text(screen, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
            else:
                mymon.exp = 0

    # 나머지 전산몬에 대한 처리
    for monnum, mymon in enumerate(player.csMons):
        if monnum == player.csMons.index(player.nowCSmon):  # 이미 처리한 nowCSmon은 건너뜀
            continue
        if mymon.level >= mymon.get_monster_max_level(battleturn):
            continue
        if mymon.dictNo == -1:
            continue
        if mymon.is_alive():
            if mymon.participated == False:  # 전투에 참여하지 않은 경우
                mymon.exp += int(enemyCSmon.drop_exp * player.concentration * player.knowhow / 10000)
            else:
                mymon.exp += int(enemyCSmon.drop_exp * player.knowhow / 100)
                for ev in enemyCSmon.giving_EV:
                    if sum(mymon.EV) >= 510:
                        break
                    if mymon.EV[ev] < 255:
                        mymon.EV[ev] =+ 1
            if mymon.exp >= mymon.max_exp:
                if mymon.level < mymon.get_monster_max_level(battleturn):
                    Level_up()
                    evocheck = mymon.level_up(battleturn)
                    if evocheck == True:
                        evolution(screen, mymon, monnum, False)
                    display_status(screen)
                    draw_text(screen, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                else:
                    mymon.exp = 0

def evolution(screen, mymon, monnum, isnowCSmon):
    """진화"""
    display_status(screen)
    draw_text(screen, f"  {mymon.name}이/가 진화하려고 한다!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()
    tempmon = mymon
    evmon = copy.deepcopy(mymon.evomon)
    evmon.evomon = None
    evmon.IV = tempmon.IV
    evmon.EV = tempmon.EV
    evmon.grade = tempmon.grade
    evmon.level = tempmon.level
    evmon.exp = tempmon.exp
    evmon.stage = tempmon.stage
    mymon = evmon
    player.csMons[monnum] = evmon
    if isnowCSmon:
        player.nowCSmon = evmon
    mymon.update_fullreset()
    display_status(screen)
    draw_text(screen, f"  {tempmon.name}이/가 {mymon.name}으로 진화했다!", stX, stY, WHITE)
    pygame.display.flip()
    wait_for_key()

def battle(getplayer, getenemy, turn, endturn, screen=None):
    global battleturn, player, enemy, enemyCSmon
    battleturn = turn
    player = getplayer
    enemy = getenemy
    if isinstance(enemy, Monster):
        enemyCSmon = enemy
    else:
        enemyCSmon = enemy.nowCSmon
    
    # pygame window가 없으면 에러
    if screen is None:
        import game_menu
        screen = game_menu.screen
        
    def winOrLose(screen):
        if turn == 0:
            screen.fill((255, 255, 255))  # 하얀 배경
            # 테두리 그리기
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, sX, sY), 2)

            draw_text(screen, f"{player.name}은/는 전산 고수가 되기 위한 여정을 시작했다!", sX//2-200, sY//2, center=True)
            pygame.display.flip()
            wait_for_key()
            return 0
        if turn == endturn:
            screen.fill((255, 255, 255))  # 하얀 배경
            # 테두리 그리기
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, sX, sY), 2)
            
            stop_music()
            draw_text(screen, f"{player.name}은/는 전산 고수가 되기 위한 여정을 마쳤다.", sX//2-200, sY//2, center=True)
            pygame.display.flip()
            wait_for_key()
            
            screen.fill((255, 255, 255))  # 하얀 배경
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, sX, sY), 2)

            draw_text(screen, f"졸업 연구를 통해 그동안의 성과를 증명하자!", sX//2-200, sY//2, center=True)
            pygame.display.flip()
            wait_for_key()
            for mymon in player.csMons:
                mymon.update_fullreset()
            play_music("../music/bossbattle.wav")
            
        def battle_logic(screen):
            global hap_num, player, enemy, enemyCSmon
            hap_num = 1
            display_status(screen, detail=True)  # 초기 상태 출력
            if isinstance(enemy, Monster):
                draw_text(screen, f"  앗! 야생의 {enemyCSmon.name}이/가 나타났다!", stX, stY, WHITE)
            else:
                draw_text(screen, f"  앗!{enemy.Etype} {enemy.name}이/가 싸움을 걸어왔다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()  # 메시지를 잠시 보여줌
                display_status(screen, detail=True)  # 상태 출력
                draw_text(screen, battleScript[enemy.Etype], stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()  # 메시지를 잠시 보여줌
                display_status(screen, detail=True)  # 상태 출력
                draw_text(screen, f"  {enemy.Etype} {enemy.name}은/는 {enemyCSmon.name}을/를 꺼냈다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()
            for mymon in player.csMons:
                mymon.participated = False  # 전투 참여 여부 초기화
            
            while True:
                player.nowCSmon.participated = True  # 현재 전산몬 참여 표시
                if player.nowCSmon.nowhp < player.nowCSmon.HP*0.35:
                    HP_low()
                """ 행동 선택"""
                action = select_action(screen)
                # 스킬
                if action == 0:
                    esc = skill_phase(screen)
                    if esc == -1:
                        continue
                # 교체
                elif action == 1:
                    esc = swap_phase(screen)
                    if esc == -1:
                        continue
                # 아이템 사용
                elif action == 2:
                    if not any(i.name != "빈 슬롯" for i in player.items):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  아이템이 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                    else:
                        esc = item_phase(screen)
                        if esc == -1:
                            continue
                # 포획
                elif action == 3:
                    if isinstance(enemy, Player):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  다른 학생의 전산몬은 포획할 수 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        continue
                    if enemyCSmon.grade == "보스":
                        display_status(screen, detail=True)
                        draw_text(screen, f"  보스는 포획할 수 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        continue
                    if enemyCSmon.grade == "중간 보스" and enemyCSmon.nowhp>enemyCSmon.HP*0.5:
                        display_status(screen, detail=True)
                        draw_text(screen, f"  체력 보호막이 남은 중간보스는 포획할 수 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        continue
                    res = catch_phase(screen)
                    if res:
                        return True
                # 도망
                elif action == 4:
                    if isinstance(enemy, Player):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  다른 학생과의 전투에서는 도망칠 수 없다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                    else:
                        display_status(screen, detail=True)
                        draw_text(screen, f"  도망쳤다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                    return False
                
                """종료여부 확인"""
                # 적 생존 여부 확인
                if enemyCSmon.is_alive() == False:
                    display_status(screen, detail=True)
                    draw_text(screen, f"  적 {enemyCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()
                    exp_gain(screen)
                    if isinstance(enemy, Player):
                        if not any(m.dictNo != -1 and m.is_alive() for m in enemy.csMons):
                            display_status(screen, detail=True)
                            draw_text(screen, f"  {enemy.Etype} {enemy.name}은 더 이상 교체할 전산몬이 없다.", stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            display_status(screen, detail=True)
                            draw_text(screen, LoseScript[enemy.Etype], stX, stY, WHITE)
                            pygame.display.flip()
                            wait_for_key()
                            return True
                        enemy.nowCSmon = random.choice([m for m in enemy.csMons if m.is_alive() and m.dictNo != -1])
                        enemyCSmon = enemy.nowCSmon
                        display_status(screen, detail=True)
                        draw_text(screen, f"  {enemy.Etype} {enemy.name}은/는 {enemyCSmon.name}을/를 꺼냈다!", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()

                    else:
                        return True
                # 플레이어 현 전산몬 생존 여부 확인
                if player.nowCSmon.is_alive() == False:
                    display_status(screen, detail=True)
                    draw_text(screen, f"  {player.nowCSmon.name}이/가 쓰러졌다!", stX, stY, WHITE)
                    pygame.display.flip()
                    wait_for_key()

                    # 살아있는 전산몬이 있는지 확인
                    if not any(m.dictNo != -1 and m.is_alive() for m in player.csMons):
                        display_status(screen, detail=True)
                        draw_text(screen, f"  더 이상 교체할 전산몬이 없다.", stX, stY, WHITE)
                        pygame.display.flip()
                        wait_for_key()
                        return False

                    # 교체 가능한 전산몬이 있으면 교체
                    swap_phase(screen, must_swap=True)
                
                # 전투 턴 증가
                hap_num += 1
        
        battle_result = battle_logic(screen)
        
        if turn == endturn:
            stop_music()
            screen.fill((255, 255, 255))  # 하얀 배경
            pygame.display.flip()
            time.sleep(2)
            if enemyCSmon.grade == "보스":
                player.gpa = f"{(4.3*(enemyCSmon.HP-enemyCSmon.nowhp)/enemyCSmon.HP):.2f}"
            gpa = float(player.gpa)
            player.grade = "A+" if gpa >= 4.3 else "A" if gpa >= 4.0 else "A-" if gpa >= 3.7 else "B+" if gpa >= 3.3 else "B" if gpa >= 3.0 else "B-" if gpa >= 2.7 else "C+" if gpa >= 2.3 else "C" if gpa >= 2.0 else "C-" if gpa >= 1.7 else "D+" if gpa >= 1.3 else "D" if gpa >= 1.0 else "D-" if gpa >= 0.7 else "F"
            
            # 성적별 색상 (pygame에서는 실제 색상 RGB 값 사용)
            if player.grade == "A+" or player.grade == "A" or player.grade == "A-":
                color = (255, 0, 0)  # 빨간색
            elif player.grade == "B+" or player.grade == "B" or player.grade == "B-":
                color = (255, 255, 0)  # 노란색
            elif player.grade == "C+" or player.grade == "C" or player.grade == "C-":
                color = (0, 255, 0)  # 녹색
            elif player.grade == "D+" or player.grade == "D" or player.grade == "D-":
                color = (0, 255, 255)  # 시안색
            else:
                color = (255, 0, 255)  # 마젠타색

            screen.fill((255, 255, 255))
            draw_text(screen, f"졸업 연구가 끝났다.", sX//2, sY//2, center=True)
            pygame.display.flip()
            wait_for_key()

            play_music("../music/ending.wav")
            screen.fill((255, 255, 255))
            draw_text(screen, f"{player.name}은/는 최종 학점 {player.gpa}로 졸업했다.", sX//2, sY//2, center=True)
            pygame.display.flip()
            wait_for_key()

            screen.fill((255, 255, 255))
            draw_text(screen, f"{player.name}의 최종 성적: {player.grade}", sX//2, sY//2, center=True, color=color)
            pygame.display.flip()
            wait_for_key()

            # 간단한 엔딩 화면 표시 (ASCII 아트 대신 텍스트로)
            screen.fill((0, 255, 255))  # 시안 배경
            draw_text(screen, "KAIST", sX//2, sY//2-50, center=True, size=48)
            draw_text(screen, "전산몬스터", sX//2, sY//2, center=True, size=36)
            draw_text(screen, "졸업을 축하합니다!", sX//2, sY//2+50, center=True, size=24)
            pygame.display.flip()
            wait_for_key()

            return hap_num
        # 전투 결과에 따라 승리 또는 패배 처리
        elif battle_result:
            # 전투에서 승리한 경우
            display_status(screen)
            Battle_win()
            draw_text(screen, f"  승리했다!", stX, stY, WHITE)
            pygame.display.flip()
            wait_for_key()

            # 아이템 드랍
            drop_item(screen)

            # 경험치 획득
            for mymon in player.csMons:    
                if turn % 5 == 0:
                    mymon.update_fullreset()
                else: mymon.update()
            if turn % 5 == 0:
                display_status(screen)
                draw_text(screen, f"포켓몬들이 모두 회복했다!", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
                display_status(screen)
                draw_text(screen, f"  공부에 노하우가 생겼다! 경험치 획득량이 60% 증가했다.", stX, stY, WHITE)
                player.knowhow *= 1.60
                pygame.display.flip()
                wait_for_key()
            if turn % 10 == 0:
                display_status(screen)
                draw_text(screen, f"  영어 강의에 익숙해졌다! 전투에 참여하지 않은 전산몬도 경험치를 20% 추가 획득한다.", stX, stY, WHITE)
                player.concentration *= 1.20
                pygame.display.flip()
                wait_for_key()
        else:
            # 전투에서 패배한 경우
            if player.gameover():
                stop_music()
                display_status(screen)
                draw_text(screen, f"  눈 앞이 깜깜해졌다...", stX, stY, WHITE)
                pygame.display.flip()
                wait_for_key()
        
        # 전투 턴 수 반환
        return hap_num
    
    # pygame 화면을 받아서 실행
    return winOrLose(screen)