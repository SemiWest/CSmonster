from playsound import *
import random
from player import *

''' 전역변수 설정 '''
battleturn = 0
hap_num = 0

''' 디스플레이 '''
def addstr_with_korean_support(stdscr, y, x, text, attr=0):
    curses.curs_set(0)  # 커서를 숨김
    """한글과 영어를 구분하여 출력 위치를 조정하는 함수"""
    try:
        current_x = x
        for char in text:
            if unicodedata.east_asian_width(char) in ['F', 'W']:  # Fullwidth, Wide (한글)
                stdscr.addstr(y, current_x, char, attr)
                stdscr.addstr(y, current_x + 1, " ", attr)  # 한글 뒤에 공백 추가
                current_x += 2
            else:
                stdscr.addstr(y, current_x, char, attr)
                current_x += 1
    except curses.error:
        pass  # 터미널 크기 초과 시 무시

def hpcolor(ratio):
        # 체력 상태에 따른 색상 선택
        if ratio >= 14:  # 풀피 (70% 이상)
            color_pair = 11
        elif ratio >= 7:  # 반피 (35% 이상)
            color_pair = 12
        else:  # 딸피 (35% 미만)
            color_pair = 13
        return color_pair

def animate_health_bar(stdscr, y, x, current_hp, target_hp, max_hp):
    """체력바를 부드럽게 애니메이션으로 업데이트"""
    current_ratio = int(current_hp * 20 / max_hp)
    target_ratio = int(target_hp * 20 / max_hp)
    temp_hp = current_hp
    steps = abs(current_ratio-target_ratio)  # 애니메이션 단계 수

    if steps == 0:
        addstr_with_korean_support(stdscr, y, x, f" {'█' * current_ratio}{' ' * (20 - current_ratio)} ", curses.color_pair(hpcolor(current_ratio)))
        addstr_with_korean_support(stdscr, y+1, x, f"({int(current_hp)}/{max_hp})")
        return

    for step in range(steps + 1):
        # 현재 체력 비율 계산
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)
        temp_hp = current_hp + int((target_hp - current_hp) * step / steps)
        # 체력바 출력
        stdscr.addstr(y, x, f" {'█' * interpolated_ratio}{' ' * (20 - interpolated_ratio)} ", curses.color_pair(hpcolor(interpolated_ratio)))
        stdscr.addstr(y+1, x, f"({temp_hp}/{max_hp})")    
        stdscr.refresh()
        time.sleep(0.05)  # 애니메이션 속도 조절

def display_status(stdscr, player, enemy, detail=False):
    stdscr.clear()
    curses.flushinp()
    # 테두리
    addstr_with_korean_support(stdscr, 0, 0, "┌──────────────────────────────────────────────────────────────┐")
    addstr_with_korean_support(stdscr, 15, 0, "└──────────────────────────────────────────────────────────────┘")
    for i in range(1, 15):
        addstr_with_korean_support(stdscr, i, 0, "│")
        addstr_with_korean_support(stdscr, i, 63, "│")
    
    # 배틀 정보 출력
    addstr_with_korean_support(stdscr, 1, 2, f"플레이어: {player.name}", curses.color_pair(5))
    addstr_with_korean_support(stdscr, 2, 2, f"스테이지 {battleturn}", curses.color_pair(4))
    addstr_with_korean_support(stdscr, 3, 2, f"턴 {hap_num}", curses.color_pair(3))
    
    # 적 상태 출력
    if enemy.name == "monsterball":
        addstr_with_korean_support(stdscr, 2, 46, "▗███████▖", curses.color_pair(1))
        addstr_with_korean_support(stdscr, 3, 46, "███▛ ▜███", curses.color_pair(1))
        addstr_with_korean_support(stdscr, 4, 46, "███▙▀▟███")
        addstr_with_korean_support(stdscr, 5, 46, "▝███████▘")
        addstr_with_korean_support(stdscr, 3, 50, "▃")
    elif enemy.name == "noneoutput":
        addstr_with_korean_support(stdscr, 2, 45, "▗███████▖", curses.color_pair(1))
        addstr_with_korean_support(stdscr, 3, 45, "███▛ ▜███", curses.color_pair(1))
        addstr_with_korean_support(stdscr, 4, 45, "███▙▀▟███")
        addstr_with_korean_support(stdscr, 5, 45, "▝███████▘")
        addstr_with_korean_support(stdscr, 3, 49, "▃")
    elif enemy.grade == "보스":
        addstr_with_korean_support(stdscr, 2, 38, f"{enemy.name}(lv {enemy.level})", curses.color_pair(1))
        animate_health_bar(stdscr, 3, 38, enemy.nowhp, enemy.nowhp, enemy.Maxhp)
    elif enemy.grade == "중간 보스":
        addstr_with_korean_support(stdscr, 2, 38, f"{enemy.name}(lv {enemy.level})", curses.color_pair(2))
        animate_health_bar(stdscr, 3, 38, enemy.nowhp, enemy.nowhp, enemy.Maxhp)
    else:
        addstr_with_korean_support(stdscr, 2, 38, f"{enemy.name}(lv {enemy.level})")
        animate_health_bar(stdscr, 3, 38, enemy.nowhp, enemy.nowhp, enemy.Maxhp)

    # 플레이어 상태 출력
    addstr_with_korean_support(stdscr, 11, 4, f"{player.nowCSmon.name}(lv {player.nowCSmon.level})")
    animate_health_bar(stdscr, 12, 4, player.nowCSmon.nowhp, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)
    for i, mymon in enumerate(player.csMons):
            addstr_with_korean_support(stdscr, 10, 5+i*2, "◒", curses.color_pair(1 if not mymon.is_alive() else 5 if mymon.name == "빈 슬롯" else 99))
    if detail:
        display_details(stdscr, player.nowCSmon, 68, "몬스터")

def display_details(stdscr, target, x, case="몬스터"):
    """상세 정보 출력"""
    if case == "몬스터":
        details = [
            (("이름", 0, 99), (f"{target.name}", 11, 4)),
            (("레벨", 0, 99), (f"{target.level}", 11, 4)),
            (("레벨업까지", 0, 99), (f"{target.max_exp - target.exp}", 11, 5), ("경험치 남음", 12 + len(f"{target.max_exp - target.exp}"), 99)),
            "",
            "체력",
            "",
            (("공격력", 0, 99), (f"{target.ad}", 11, 4)),
            (("스피드", 0, 99), (f"{target.sp}", 11, 4)),
            "",
            (("등급", 0, 99), (f"{target.grade}", 11, 99 if target.grade == "일반" else 2 if target.grade == "중간 보스" else 1)),
            (("만난 곳", 0, 99), (f"스테이지 {target.stage}", 11, 4) if isinstance(target.stage, int) else (f"{target.stage}", 11, 4)),
            (("설명", 0, 99), (f"{target.description}", 11, 99)),
        ]
        for i, detailes in enumerate(details):
            if isinstance(detailes, tuple):  # detail이 튜플인 경우
                for detail in detailes:
                    start_x = x + detail[1]
                    max_width = 113
                    current_line = ""
                    line_offset = 0
                    current_width = 0  # 현재 줄의 문자 폭
                    for char in detail[0]:
                        char_width = 2 if unicodedata.east_asian_width(char) in ['F', 'W'] else 1
                        if current_width + char_width > max_width - start_x:
                            # 현재 줄 출력
                            addstr_with_korean_support(stdscr, 3 + i + line_offset, start_x, current_line, curses.color_pair(detail[2]))
                            current_line = char  # 새로운 줄 시작
                            current_width = char_width
                            line_offset += 1
                        else:
                            current_line += char
                            current_width += char_width
                    if current_line:
                        # 마지막 줄 출력
                        addstr_with_korean_support(stdscr, 3 + i + line_offset, start_x, current_line, curses.color_pair(detail[2]))

            elif isinstance(detailes, str):  # detail이 문자열인 경우
                if detailes == "체력":
                    current_ratio = int(target.nowhp * 20 / target.Maxhp)
                    addstr_with_korean_support(stdscr, 3 + i, 68, "체력")
                    addstr_with_korean_support(stdscr, 3 + i, 79, f" {'█' * current_ratio}{' ' * (20 - current_ratio)} ", curses.color_pair(hpcolor(current_ratio)))
                    addstr_with_korean_support(stdscr, 3 + i + 1, 79, f"({target.nowhp}/{target.Maxhp})")
                else:
                    # 120칸 제한을 넘으면 줄바꿈 처리
                    start_x = 68
                    max_width = 114
                    current_line = ""
                    line_offset = 0
                    current_width = 0  # 현재 줄의 문자 폭
                    for char in detailes:
                        char_width = 2 if unicodedata.east_asian_width(char) in ['F', 'W'] else 1
                        if current_width + char_width > max_width - start_x:
                            # 현재 줄 출력
                            addstr_with_korean_support(stdscr, 3 + i + line_offset, start_x, current_line)
                            current_line = char  # 새로운 줄 시작
                            current_width = char_width
                            line_offset += 1
                        else:
                            current_line += char
                            current_width += char_width
                    if current_line:
                        # 마지막 줄 출력
                        addstr_with_korean_support(stdscr, 3 + i + line_offset, start_x, current_line)
        
''' 선택 '''
def option_choice(stdscr, option_case, player, enemy, description=None, coloring=None, temp=None):
    """옵션 선택 메뉴"""
    current_index = 0
    while True:
        display_status(stdscr, player, enemy)  # 상태 출력
        if option_case == "스킬":
            display_status(stdscr, player, enemy, True)  # 상태 출력
            options = player.nowCSmon.skills.values()
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"> {option.name}", curses.A_REVERSE)
                    addstr_with_korean_support(stdscr, max(21, 17+int(len(options)/2)+2), 2, f"{description[i][0]}")
                    if description[i][1] != None: 
                        damage = description[i][1]
                        addstr_with_korean_support(stdscr, max(22, 17+int(len(options)/2)+3), 2, f"데미지")
                        addstr_with_korean_support(stdscr, max(22, 17+int(len(options)/2)+3), 9, f"{description[i][1]}", 
                                                   curses.color_pair(1 if damage>19 else 2 if damage>9 else 0))
        elif option_case == "몬스터":
            options = player.csMons
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                elif option.name == "빈 슬롯":
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}", curses.color_pair(4))
                else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"> {option.name}", curses.A_REVERSE)  # 선택된 옵션 강조
                    if option.name != "빈 슬롯":
                        display_details(stdscr, option, 68, "몬스터")  # 상세 정보 출력
            if temp != None:
                addstr_with_korean_support(stdscr, max(21, 17+int(len(options)/2)+2), 2, f"잡은 전산몬: {temp.name}(lv {temp.level})")
              
                
        elif option_case == "아이템":
            options = player.items
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                elif option.name == "빈 슬롯":
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}", curses.color_pair(4))
                else: addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option.name}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"> {option.name}", curses.A_REVERSE)
                    y = max(21, 17+int(len(options)/2)+2)
                    if temp != None:
                        addstr_with_korean_support(stdscr, y, 2, f"얻은 아이템: {temp.name}", curses.color_pair(
                            2 if temp.grade == "레전더리" else 6 if temp.grade == "에픽" else 3 if temp.grade == "레어" else 0
                            ))
                        y += 1
                    addstr_with_korean_support(stdscr, y, 2, f"{description[i]}")
            
             
        elif option_case == "배틀옵션":
            display_status(stdscr, player, enemy, True)  # 상태 출력
            options = ["스킬 사용", "전산몬 교체", "아이템 사용", "전산몬 포획","도망가기"]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"> {option}", curses.A_REVERSE)


        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('\n'):  # Enter 키를 누르면 선택 완료
            option_select_sound()
            return current_index
        if key == ord('\b') or key == 27 or key == ord("q"):  # BACKSPACE 키를 누르면 취소
            option_escape_sound()
            return -1
        elif len(options) == 1:  # 옵션이 하나일 경우
            current_index = 0
        elif key == curses.KEY_UP and (current_index > 1 and current_index < len(options)):
            current_index -= 2
            option_change_sound()
        elif key == curses.KEY_DOWN and (current_index >=0 and current_index < len(options)-2):
            current_index += 2
            option_change_sound()
        elif key == curses.KEY_LEFT and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
            current_index -= 1
            option_change_sound()
        elif key == curses.KEY_RIGHT and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options)-1):
            current_index += 1
            option_change_sound()

def select_skill(stdscr, player, enemy):
    """방향키로 스킬 선택"""
    curses.curs_set(0)  # 커서를 숨김
    stdscr.keypad(True)
    stdscr.clear()
    skills = list(player.nowCSmon.skills.keys())
    coloring = [False]*len(skills)  # 스킬 색상 리스트
    for i, skill in enumerate(skills):
        if player.nowCSmon.skills[skill].dom == enemy.name:
            coloring[i] = 2  # 적에게 효과가 있는 스킬 표시
    descriptions = [[
        player.nowCSmon.skills[skill].description, 
        player.nowCSmon.skills[skill].damage(enemy, player.nowCSmon) if player.nowCSmon.skills[skill].effect_type == "damage" else None
        ] for skill in skills]  # 스킬 설명 리스트
    display_status(stdscr, player, enemy, True)  # 상태 출력
    index = option_choice(stdscr, "스킬", player, enemy, descriptions, coloring)  # 스킬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    return skills[index]  # 선택된 스킬 이름 반환

def select_monster(stdscr, player, enemy, temp=None):
    """방향키로 전산몬 선택"""
    stdscr.keypad(True)
    stdscr.clear()

    # 현재 전산몬 표시
    coloring = [False, False, False, False, False, False]
    for i in range(6):
        if player.csMons[i].name == "빈 슬롯":
            coloring[i] = 4 # 빈 슬롯 표시
        elif player.csMons[i].is_alive() == False:
            coloring[i] = 1  # 죽은 전산몬 표시
        elif player.csMons[i] == player.nowCSmon:
            coloring[i] = 5  # 현재 전산몬 표시

    display_status(stdscr, player, enemy)
    index = option_choice(stdscr, "몬스터", player, enemy, coloring = coloring, temp=temp)  # 전산몬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[index].name == "빈 슬롯":
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return select_monster(stdscr, player, enemy, temp)
    return index  # 선택된 전산몬 인덱스 반환

def select_item(stdscr, player, enemy, temp=None):
    """방향키로 아이템 선택"""
    stdscr.keypad(True)
    stdscr.clear()
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
    display_status(stdscr, player, enemy)
    index = option_choice(stdscr, "아이템", player, enemy, descriptions, coloring, temp)  # 아이템 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.items[index].name == "빈 슬롯":
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return select_item(stdscr, player, enemy, temp)
    return index  # 선택된 아이템 이름 반환

def select_action(stdscr, player, enemy):
    """행동 선택 메뉴"""
    display_status(stdscr, player, enemy, detail=True)  # 상태 출력
    index = option_choice(stdscr, "배틀옵션", player, enemy)  # 행동 선택
    return index

''' 스킬 '''
def skill_message(stdscr, user, target, skill, counter_skill=None):
    """스킬 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 스킬 메시지 출력
    if skill.effect_type == "reflect":
        if counter_skill is not None:
            if counter_skill.effect_type == "damage":
                if skill.skW == 0:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 방어했다.")
                else:
                    damage = counter_skill.damage(user, target)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 반사!")
                    get_ch_with_sound(stdscr)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 {damage}의 데미지를 입었다!                                    ")
            else:
                addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")

    elif skill.effect_type == "damage":
        damage = skill.damage(target, user)
        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 {damage}의 데미지를 입었다!")

    elif skill.effect_type == "halve_hp":
        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 반으로 줄었다!")

    elif skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.Maxhp)
        addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 체력이 {heal_amount} 회복되었다!")

    elif skill.effect_type == "buff":
        addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 공격력이 {skill.skW}배가 되었다!")

    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌

def use_skill(user, target, skill, counter_skill=None):
    """스킬 효과를 처리 (체력 계산만 수행)"""
    # reflect 스킬 처리
    if skill.effect_type == "reflect":
        if counter_skill is not None:
            if counter_skill.effect_type == "damage":
                damage = counter_skill.damage(user, target)*skill.skW
                target.nowhp = max(0, target.nowhp - damage)
                if target.hpShield:
                    target.nowhp = target.Maxhp//2
                    target.hpShield = False
                return True
        else:
            return False

    # damage 스킬 처리
    if skill.effect_type == "damage":
        damage = skill.damage(target, user)
        target.nowhp = max(0, target.nowhp - damage)
        if target.hpShield:
            target.nowhp = target.Maxhp//2
            target.hpShield = False
        return False

    # halve_hp 스킬 처리
    if skill.effect_type == "halve_hp":
        target.nowhp = max(0, target.nowhp // 2)
        if target.hpShield:
            target.nowhp = target.Maxhp//2
            target.hpShield = False
        return False

    # heal 스킬 처리
    if skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.Maxhp)
        user.nowhp = min(user.Maxhp, user.nowhp + heal_amount)
        return False

    # buff 스킬 처리
    if skill.effect_type == "buff":
        user.ad = int(skill.skW * user.ad)
        return False

    return False

def skill_phase(stdscr, player, enemy):
    # 플레이어 스킬 선택
    selected_skill = select_skill(stdscr, player, enemy)
    if selected_skill == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    nowCSmon_skill = player.nowCSmon.skills[selected_skill]

    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    display_status(stdscr, player, enemy, True)  # 상태 출력
    # 우선순위 비교
    if nowCSmon_skill.priority > enemy_skill.priority or (nowCSmon_skill.priority == enemy_skill.priority and player.nowCSmon.sp >= enemy.sp):
        # 플레이어 스킬 먼저 발동
        playerCurrentHP = player.nowCSmon.nowhp
        enemyCurrentHP = enemy.nowhp
        addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}의 {nowCSmon_skill.name}!")
        get_ch_with_sound(stdscr)

        stop = use_skill(player.nowCSmon, enemy, nowCSmon_skill, enemy_skill)
        animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
        animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
        skill_message(stdscr, player.nowCSmon, enemy, nowCSmon_skill, enemy_skill)

        # 적이 살아있으면 반격
        if enemy.is_alive() and not stop:
            playerCurrentHP = player.nowCSmon.nowhp
            enemyCurrentHP = enemy.nowhp
            display_status(stdscr, player, enemy, True)  # 상태 출력
            addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
            get_ch_with_sound(stdscr)

            stop = use_skill(enemy, player.nowCSmon, enemy_skill)
            animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
            animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
            skill_message(stdscr, enemy, player.nowCSmon, enemy_skill)
    else:
        # 적 스킬 먼저 발동
        playerCurrentHP = player.nowCSmon.nowhp
        enemyCurrentHP = enemy.nowhp
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
        get_ch_with_sound(stdscr)

        stop = use_skill(enemy, player.nowCSmon, enemy_skill, nowCSmon_skill)
        animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
        animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
        skill_message(stdscr, enemy, player.nowCSmon, enemy_skill, nowCSmon_skill)

        # 플레이어가 살아있으면 반격
        if player.nowCSmon.is_alive() and not stop:
            playerCurrentHP = player.nowCSmon.nowhp
            enemyCurrentHP = enemy.nowhp
            display_status(stdscr, player, enemy, True)  # 상태 출력
            addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}의 {nowCSmon_skill.name}!")
            get_ch_with_sound(stdscr)

            stop = use_skill(player.nowCSmon, enemy, nowCSmon_skill)
            animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
            animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
            skill_message(stdscr, player.nowCSmon, enemy, nowCSmon_skill)

''' 교체 '''
def swap_phase(stdscr, player, enemy, must_swap=False):
    """전산몬 교체 단계"""
    currentCSmon = player.nowCSmon  # 현재 전산몬

    # 교체할 전산몬 선택
    selected_monster = select_monster(stdscr, player, enemy)
    
    # 선택시 예외 처리
    if selected_monster == -1:
        if must_swap:
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}은/는 쓰러져서 교체해야 해!")
            get_ch_with_sound(stdscr)
            return swap_phase(stdscr, player, enemy, must_swap)  # 다시 선택
        return -1
    if player.csMons[selected_monster].name == "빈 슬롯":
        display_status(stdscr, currentCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, player, enemy, must_swap)  # 다시 선택

    new_monster = player.csMons[selected_monster]
    
    # 교체할 전산몬 관련 예외 처리
    if new_monster.is_alive() == False:
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {new_monster.name}은/는 이미 쓰러졌어!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, player, enemy, must_swap)  # 다시 선택
    elif new_monster == currentCSmon:
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}은/는 이미 나와 있어!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, player, enemy, must_swap)  # 다시 선택
    
    display_status(stdscr, player, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  수고했어, {currentCSmon.name}!")
    get_ch_with_sound(stdscr)

    # 교체
    player.nowCSmon = new_monster

    display_status(stdscr, player, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  나와라, {new_monster.name}!")
    get_ch_with_sound(stdscr)

    # 강제로 교체해야 했던 경우 턴 소모 없이 즉시 교체
    if must_swap: 
        return   

    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, player, enemy, detail=True)
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    get_ch_with_sound(stdscr)

    use_skill(enemy, player.nowCSmon, enemy_skill)
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
    skill_message(stdscr, enemy, player.nowCSmon, enemy_skill)
    get_ch_with_sound(stdscr)
    return

''' 아이템 사용 '''
def use_item(item, target):
    # heal 아이템 처리
    if item.effect == "heal":
        heal_amount = max(item.fixed, int(target.Maxhp * item.varied))
        target.nowhp = min(target.Maxhp, target.nowhp + heal_amount)
    
    elif item.effect == "buff":
        if item.buffto == "ad":
            target.ad *= item.varied
        if item.buffto == "sp":
            target.sp *= item.varied

    return False

def item_message(stdscr, item, target):
    """아이템 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 아이템 메시지 출력
    if item.effect == "heal":
        heal_amount = max(item.fixed, int(target.Maxhp * item.varied))
        if item.canuse_on_fainted == True:
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 부활했다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 {heal_amount} 회복되었다!")
    elif item.effect == "buff":
        if item.buffto == "ad":
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 공격력이 {item.varied}배가 되었다!")
        if item.buffto == "sp":
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 속도가 {item.varied}배가 되었다!")
    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌

def item_phase(stdscr, player, enemy):
    """아이템 사용 단계"""
    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    item_num = select_item(stdscr, player, enemy)  # 아이템 선택
    if item_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    mon_num = select_monster(stdscr, player, enemy)  # 전산몬 선택
    if mon_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[mon_num].nowhp == 0:
        if player.items[item_num].canuse_on_fainted == False:
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  쓰러진 전산몬에게는 이 아이템을 사용할 수 없다.")
            get_ch_with_sound(stdscr)
            return item_phase(stdscr, player, enemy)
    display_status(stdscr, player, enemy)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {player.items[item_num].name}을/를 {player.csMons[mon_num].name}에게 사용했다!")
    get_ch_with_sound(stdscr)

    use_item(player.items[item_num], player.csMons[mon_num])  # 아이템 사용
    
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)
    display_status(stdscr, player, enemy)  # 상태 출력
    item_message(stdscr, player.items[item_num], player.csMons[mon_num])  # 아이템 메시지 출력
    player.items[item_num] = items["빈 슬롯"]  # 사용한 아이템 삭제
    get_ch_with_sound(stdscr)

    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]
    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, player, enemy, True)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    get_ch_with_sound(stdscr)

    use_skill(enemy, player.nowCSmon, enemy_skill)

    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
    skill_message(stdscr, enemy, player.nowCSmon, enemy_skill)
    get_ch_with_sound(stdscr)
 
''' 포획 '''
def catch_monster(stdscr, player, enemy):
    """포획 시도"""
    display_status(stdscr, player, enemy)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  가랏, 몬스터볼!")
    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌

    enemy_normname = enemy.name  # 적 몬스터 이름
    enemy.name = "monsterball"  # 포획 중에는 몬스터볼로 표시
    display_status(stdscr, player, enemy)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}을/를 포획 시도 중")
    # 몬스터볼 반짝거리는 연출
    for i in range(6):  # 6번 반복 (반짝거림 효과)
        time.sleep(0.3)  # 0.3초 대기
        if i % 2 == 0:
            blink_times = int(2**((6-i)/2))
            for j in range(blink_times):  # 몬스터볼이 반짝이는 효과
                enemy.name = "noneoutput"  # 반짝이는 상태
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}을/를 포획 시도 중{'.'*(i//2+1)}")
                stdscr.refresh()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
                enemy.name = "monsterball"  # 반짝이는 상태
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}을/를 포획 시도 중{'.'*(i//2+1)}")
                stdscr.refresh()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
        else:
            enemy.name = "monsterball"  # 반짝이는 상태
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}을/를 포획 시도 중{'.'*(i//2+1)}")
            stdscr.refresh()
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}을/를 포획 시도 중{'.'*(i//2+1)}")
        stdscr.refresh()
    time.sleep(0.5)  # 포획 시도 중 메시지 출력 후 대기

    # 포획 성공 확률 계산 (체력이 낮을수록 성공 확률 증가)
    catch_rate = 100 - int((enemy.nowhp / enemy.Maxhp) * 75)  # 최소 25%, 최대 100%
    success = random.randint(1, 100) <= catch_rate

    if success:
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy_normname}이/가 잡혔다!")
        curses.flushinp()
        get_ch_with_sound(stdscr)

        # 플레이어 몬스터 슬롯에 추가
        for i in range(len(player.csMons)):
            if player.csMons[i].name == "빈 슬롯":
                player.csMons[i] = copy.deepcopy(enemy)
                player.csMons[i].name = enemy_normname
                break
        else:
            addstr_with_korean_support(stdscr, 17, 0, "  몬스터 슬롯이 가득 찼다!")
            get_ch_with_sound(stdscr)
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  놓아줄 몬스터를 선택하자.")
            get_ch_with_sound(stdscr)
            # 몬스터 교체
            tempmon = copy.deepcopy(enemy)
            tempmon.name = enemy_normname
            selected_monster = select_monster(stdscr, player, enemy, tempmon)
            if selected_monster == -1:
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  포획을 취소했다.")
                get_ch_with_sound(stdscr)
            else:
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {player.csMons[selected_monster].name}, 그리울거야!")
                if player.nowCSmon == player.csMons[selected_monster]:
                    player.csMons[selected_monster] = tempmon
                    player.nowCSmon = player.csMons[selected_monster]  # 교체된 몬스터로 변경
                else:
                    player.csMons[selected_monster] = tempmon
                    player.csMons[selected_monster].name = enemy_normname
                get_ch_with_sound(stdscr)
        return True
    else:
        # 포획 실패 시 적 몬스터 이름 복원
        enemy.name = enemy_normname
        display_status(stdscr, player, enemy)
        # 포획 실패 메시지 출력
        addstr_with_korean_support(stdscr, 17, 0, f"  앗, {enemy.name}이/가 몬스터볼에서 나왔다!")
        curses.flushinp()
        get_ch_with_sound(stdscr)
        return False

def catch_phase(stdscr, player, enemy):
    """포획 단계"""
    
    res = catch_monster(stdscr, player, enemy) 
    if res:
        return True
    
    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, player, enemy, detail=True)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    get_ch_with_sound(stdscr)

    use_skill(enemy, player.nowCSmon, enemy_skill)

    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.Maxhp)    
    skill_message(stdscr, enemy, player.nowCSmon, enemy_skill)
    get_ch_with_sound(stdscr)
    return False  # 포획 실패

    # 포획 시도

''' 종합 '''
def drop_item(stdscr, player, enemy):
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
    display_status(stdscr, player, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  {droppedtem.name}을/를 획득했다!")
    get_ch_with_sound(stdscr)

    # 아이템을 슬롯에 추가
    for i in range(len(player.items)):
        if player.items[i].name == "빈 슬롯":
            player.items[i] = copy.deepcopy(droppedtem)
            break
    else:
        # 아이템 슬롯이 가득 찼을 때
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, "  그러나 아이템 슬롯이 가득 차있다!")
        get_ch_with_sound(stdscr)
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  버릴 아이템을 선택하자!")
        get_ch_with_sound(stdscr)
        # 몬스터 교체
        selected_item = select_item(stdscr, player, enemy, droppedtem)
        if selected_item == -1:
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {droppedtem.name}의 획득을 포기했다.")
            get_ch_with_sound(stdscr)
        else:
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {player.items[selected_item].name}을/를 버렸다!")
            player.items[selected_item] = droppedtem  # 교체된 아이템으로 변경 
            get_ch_with_sound(stdscr)

def exp_gain(stdscr, player, enemy):
    """경험치 획득"""
    # 현재 전산몬(nowCSmon)에 대한 처리 먼저 수행
    mymon = player.nowCSmon
    if mymon.level == mymon.get_monster_max_level(battleturn):
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}은/는 이미 레벨 제한에 도달했다.")
        get_ch_with_sound(stdscr)
    else:
        if mymon.participated == False:  # 전투에 참여하지 않은 경우
            exp = int(enemy.drop_exp * player.concentration * player.knowhow / 10000)
        else:
            exp = int(enemy.drop_exp * player.knowhow / 100)
        display_status(stdscr, player, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {exp}의 경험치를 얻었다!")
        mymon.exp += exp
        get_ch_with_sound(stdscr)
        if mymon.exp >= mymon.max_exp:
            if mymon.level < mymon.get_monster_max_level(battleturn):
                mymon.level_up(battleturn)
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!")
                get_ch_with_sound(stdscr)
            else:
                mymon.exp = 0

    # 나머지 전산몬에 대한 처리
    for mymon in player.csMons:
        if mymon == player.nowCSmon:  # 이미 처리한 nowCSmon은 건너뜀
            continue
        if mymon.level == mymon.get_monster_max_level(battleturn):
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}은/는 이미 레벨 제한에 도달했다.")
            get_ch_with_sound(stdscr)
            continue
        if mymon.is_alive():
            if mymon.participated == False:  # 전투에 참여하지 않은 경우
                mymon.exp += int(enemy.drop_exp * player.concentration * player.knowhow / 10000)
            else:
                mymon.exp += int(enemy.drop_exp * player.knowhow / 100)
            if mymon.exp >= mymon.max_exp:
                if mymon.level < mymon.get_monster_max_level(battleturn):
                    mymon.level_up(battleturn)
                    display_status(stdscr, player, enemy)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!")
                    get_ch_with_sound(stdscr)
                else:
                    mymon.exp = 0
                    
def battle(player, enemy, turn, endturn):
    global battleturn
    battleturn = turn
    def winOrLose(stdscr):
        if turn == 0:
            stdscr.clear()
            # 테두리
            addstr_with_korean_support(stdscr, 0, 0, "┌──────────────────────────────────────────────────────────────┐")
            addstr_with_korean_support(stdscr, 15, 0, "└──────────────────────────────────────────────────────────────┘")
            for i in range(1, 15):
                addstr_with_korean_support(stdscr, i, 0, "│")
                addstr_with_korean_support(stdscr, i, 63, "│")

            addstr_with_korean_support(stdscr, 17, 2, f"{player.name}은/는 전산 고수가 되기 위한 여정을 시작했다!")
            get_ch_with_sound(stdscr)
            return 0
        if turn == endturn:
            stdscr.clear()
            # 테두리
            addstr_with_korean_support(stdscr, 0, 0, "┌──────────────────────────────────────────────────────────────┐")
            addstr_with_korean_support(stdscr, 15, 0, "└──────────────────────────────────────────────────────────────┘")
            for i in range(1, 15):
                addstr_with_korean_support(stdscr, i, 0, "│")
                addstr_with_korean_support(stdscr, i, 63, "│")

            addstr_with_korean_support(stdscr, 17, 2, f"{player.name}은/는 전산 고수가 되기 위한 여정을 마쳤다.")
            get_ch_with_sound(stdscr)
            stdscr.clear()
            addstr_with_korean_support(stdscr, 0, 0, "┌──────────────────────────────────────────────────────────────┐")
            addstr_with_korean_support(stdscr, 15, 0, "└──────────────────────────────────────────────────────────────┘")
            for i in range(1, 15):
                addstr_with_korean_support(stdscr, i, 0, "│")
                addstr_with_korean_support(stdscr, i, 63, "│")

            addstr_with_korean_support(stdscr, 17, 2, f"졸업 연구를 통해 그동안의 성과를 증명하자!")
            get_ch_with_sound(stdscr)
            
            
        def battle_logic(stdscr):
            curses.start_color()
            curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_WHITE) # 풀피 색상 (초록색)
            curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_WHITE)  # 반피 색상 (노란색)
            curses.init_pair(13, curses.COLOR_RED, curses.COLOR_WHITE)    # 딸피 색상 (빨간색)
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)  # 기본 색상 (스테이지 색상)
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)  # 현재 전산몬 (파란색)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 녹색
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # 빨간색
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 노란색
            curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # 보라색
            curses.init_pair(99, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 흰색
            curses.curs_set(0)  # 커서를 숨김
            global hap_num
            hap_num = 1
            display_status(stdscr, player, enemy, detail=True)  # 초기 상태 출력

            addstr_with_korean_support(stdscr, 17, 0, f"  앗! 야생의 {enemy.name}이/가 나타났다!")
            get_ch_with_sound(stdscr)
            for mymon in player.csMons:
                mymon.participated = False  # 전투 참여 여부 초기화
            
            while True:
                curses.flushinp()  # 입력 버퍼 비우기
                player.nowCSmon.participated = True  # 현재 전산몬 참여 표시
                """ 행동 선택"""
                action = select_action(stdscr, player, enemy)
                # 스킬
                if action == 0:
                    esc = skill_phase(stdscr, player, enemy)
                    if esc == -1:
                        continue
                # 교체
                elif action == 1:
                    esc = swap_phase(stdscr, player, enemy)
                    if esc == -1:
                        continue
                # 아이템 사용
                elif action == 2:
                    if not any(i.name != "빈 슬롯" for i in player.items):
                        display_status(stdscr, player, enemy, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  아이템이 없다!")
                        get_ch_with_sound(stdscr)
                    else:
                        esc = item_phase(stdscr, player, enemy)
                        if esc == -1:
                            continue
                # 포획
                elif action == 3:
                    if enemy.grade == "보스":
                        display_status(stdscr, player, enemy, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  보스는 포획할 수 없다!")
                        get_ch_with_sound(stdscr)
                        continue
                    if enemy.grade == "중간 보스" and enemy.nowhp>enemy.Maxhp*0.5:
                        display_status(stdscr, player, enemy, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  체력이 절반 이상 남은 중간 보스는 포획할 수 없다!")
                        get_ch_with_sound(stdscr)
                        continue

                    res = catch_phase(stdscr, player, enemy)
                    if res:
                        return True
                # 도망
                elif action == 4:
                    display_status(stdscr, player, enemy, detail=True)
                    addstr_with_korean_support(stdscr, 17, 0, f"  도망쳤다!")
                    get_ch_with_sound(stdscr)
                    return False
                elif action == -1:
                    continue
                
                """종료여부 확인"""
                # 적 생존 여부 확인
                if enemy.is_alive() == False:
                    display_status(stdscr, player, enemy, detail=True)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}이/가 쓰러졌다!")
                    get_ch_with_sound(stdscr)
                    return True
                # 플레이어 현 전산몬 생존 여부 확인
                if player.nowCSmon.is_alive() == False:
                    display_status(stdscr, player, enemy, detail=True)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}이/가 쓰러졌다!")
                    get_ch_with_sound(stdscr)

                    # 살아있는 전산몬이 있는지 확인
                    if not any(m.name != "빈 슬롯" and m.is_alive() for m in player.csMons):
                        display_status(stdscr, player, enemy, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  더 이상 교체할 전산몬이 없다.")
                        get_ch_with_sound(stdscr)
                        return False

                    # 교체 가능한 전산몬이 있으면 교체
                    swap_phase(stdscr, player, enemy, must_swap=True)
                
                # 전투 턴 증가
                hap_num += 1
        
        battle_result = battle_logic(stdscr)
        
        if turn == endturn:
            if enemy.grade == "보스":
                player.gpa = f"{(4.3*(enemy.Maxhp-enemy.nowhp)/9999):.2f}"
            return hap_num
        # 전투 결과에 따라 승리 또는 패배 처리
        elif battle_result:
            # 전투에서 승리한 경우
            display_status(stdscr, player, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  승리했다!")
            get_ch_with_sound(stdscr)

            # 아이템 드랍
            drop_item(stdscr, player, enemy)
            # 경험치 획득
            exp_gain(stdscr, player, enemy)
            for mymon in player.csMons:    
                if turn % 5 == 0:
                    mymon.update_fullhp()
                else: mymon.update()
            if turn % 5 == 0:
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 2, f"포켓몬들이 모두 회복했다!")
                get_ch_with_sound(stdscr)
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  공부에 노하우가 생겼다! 경험치 획득량이 60% 증가했다.")
                player.knowhow += 60
                get_ch_with_sound(stdscr)
            if turn % 10 == 0:
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  영어 강의에 익숙해졌다! 전투에 참여하지 않은 전산몬도 경험치를 20% 추가 획득한다.")
                player.concentration += 20
                get_ch_with_sound(stdscr)
        else:
            # 전투에서 패배한 경우
            if player.gameover():
                display_status(stdscr, player, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  눈 앞이 깜깜해졌다...")
                get_ch_with_sound(stdscr)
        
        # 전투 턴 수 반환
        return hap_num
    
    return curses.wrapper(winOrLose)