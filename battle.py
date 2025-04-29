import curses
import unicodedata
import random
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def addstr_with_korean_support(stdscr, y, x, text, attr=0):
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

def animate_health_bar(stdscr, y, x, current_hp, target_hp, max_hp, color_pair_full, color_pair_half, color_pair_low):
    """체력바를 부드럽게 애니메이션으로 업데이트"""
    current_ratio = int(current_hp * 20 / max_hp)
    target_ratio = int(target_hp * 20 / max_hp)
    steps = current_ratio-target_ratio  # 애니메이션 단계 수
    if steps == 0:
        addstr_with_korean_support(stdscr, y, x, f" {'█' * current_ratio}{' ' * (20 - current_ratio)} ", curses.color_pair(3 - target_ratio // 7))
        return

    for step in range(steps + 1):
        # 현재 체력 비율 계산
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)

        # 체력 상태에 따른 색상 선택
        if interpolated_ratio >= 14:  # 풀피 (70% 이상)
            color_pair = color_pair_full
        elif interpolated_ratio >= 7:  # 반피 (35% 이상)
            color_pair = color_pair_half
        else:  # 딸피 (35% 미만)
            color_pair = color_pair_low
        
        # 체력바 출력
        stdscr.addstr(y, x, f" {'█' * interpolated_ratio}{' ' * (20 - interpolated_ratio)} ", curses.color_pair(color_pair))
        stdscr.refresh()
        time.sleep(0.05)  # 애니메이션 속도 조절

def display_status(stdscr, player, enemy):
    stdscr.clear()

    # 색상 초기화
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE) # 풀피 색상 (초록색)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_WHITE)  # 반피 색상 (노란색)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)    # 딸피 색상 (빨간색)
    
    addstr_with_korean_support(stdscr, 0, 0, "┌────────────────────────────────────────────────────────┐")
    
    # 적 상태 출력
    addstr_with_korean_support(stdscr, 2, 32, f"{enemy.name}(lv {enemy.level})")
    animate_health_bar(stdscr, 3, 32, enemy.nowhp, enemy.nowhp, enemy.Maxhp, 1, 2, 3)

    # 플레이어 상태 출력
    addstr_with_korean_support(stdscr, 9, 4, f"{player.name}(lv {player.level})")
    animate_health_bar(stdscr, 10, 4, player.nowhp, player.nowhp, player.Maxhp, 1, 2, 3)

    addstr_with_korean_support(stdscr, 12, 0, "└────────────────────────────────────────────────────────┘")
    for i in range(1, 12):
        addstr_with_korean_support(stdscr, i, 0, "│")
        addstr_with_korean_support(stdscr, i, 57, "│")
    
    stdscr.refresh()


def display_status_with_skills(stdscr, player, enemy, skills, current_index):
    """플레이어와 적의 상태를 출력하고 스킬 선택 창을 함께 표시"""
    # 스킬 선택 창 출력
    display_status(stdscr, player, enemy)
    for i, skill_name in enumerate(skills):
        if i == current_index:
            addstr_with_korean_support(stdscr, 14 + int(i/2), 27*(i%2), f"> {skill_name}", curses.A_REVERSE)  # 선택된 스킬 강조
            addstr_with_korean_support(stdscr, 17, 0, f"  {player.skills[skill_name].description}")
        else:
            addstr_with_korean_support(stdscr, 14 + int(i/2), 27*(i%2), f"  {skill_name}")

    stdscr.refresh()

def use_skill(user, target, skill, counter_skill=None):
    """스킬 효과를 처리 (체력 계산만 수행)"""
    # reflect 스킬 처리
    if skill.effect_type == "reflect":
        if counter_skill and counter_skill.effect_type == "damage":
            damage = counter_skill.damage(user, target)*skill.skW
            target.nowhp -= damage
            if target.nowhp < 0:
                target.nowhp = 0
            return True
        else:
            return False

    # damage 스킬 처리
    if skill.effect_type == "damage":
        damage = skill.damage(target, user)
        target.nowhp = max(0, target.nowhp - damage)
        return False

    # halve_hp 스킬 처리
    if skill.effect_type == "halve_hp":
        target.nowhp = max(0, target.nowhp // 2)
        return False

    # heal 스킬 처리
    if skill.effect_type == "heal":
        heal_amount = skill.skW * user.Maxhp
        user.nowhp = min(user.Maxhp, user.nowhp + heal_amount)
        return False

    # buff 스킬 처리
    if skill.effect_type == "buff":
        user.ad *= skill.skW
        return False

    return False

def skill_message(stdscr, user, target, skill, counter_skill=None):
    """스킬 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 스킬 메시지 출력
    if skill.effect_type == "reflect":
        if counter_skill.effect_type == "damage":
            if skill.skW == 0:
                addstr_with_korean_support(stdscr, 14, 0, f"  {user.name}가 {target.name}의 {counter_skill.name}을 방어했다.")
            else:
                damage = counter_skill.damage(user, target)
                addstr_with_korean_support(stdscr, 14, 0, f"  {user.name}가 {target.name}의 {counter_skill.name}을 반사!")
                addstr_with_korean_support(stdscr, 15, 0, f"  {target.name}가 {damage}의 데미지를 입었다!")
        else:
            addstr_with_korean_support(stdscr, 14, 0, "  그러나 아무 일도 일어나지 않았다!")

    elif skill.effect_type == "damage":
        damage = skill.damage(target, user)
        addstr_with_korean_support(stdscr, 14, 0, f"  {target.name}가 {damage}의 데미지를 입었다!")

    elif skill.effect_type == "halve_hp":
        addstr_with_korean_support(stdscr, 14, 0, f"  {target.name}의 체력이 반으로 줄었다!")

    elif skill.effect_type == "heal":
        heal_amount = skill.skW * user.Maxhp
        addstr_with_korean_support(stdscr, 14, 0, f"  {user.name}의 체력이 {heal_amount} 회복되었다!")

    elif skill.effect_type == "buff":
        addstr_with_korean_support(stdscr, 14, 0, f"  {user.name}의 공격력이 {skill.skW}배가 되었다!")

    stdscr.refresh()
    stdscr.getch()  # 메시지를 잠시 보여줌

def select_skill_with_arrows(stdscr, player, enemy):
    """방향키로 스킬 선택"""
    curses.curs_set(0)  # 커서를 숨김
    stdscr.keypad(True)
    stdscr.clear()

    skills = list(player.skills.keys())
    current_index = 0

    while True:
        display_status_with_skills(stdscr, player, enemy, skills, current_index)
        key = stdscr.getch()
        if key == curses.KEY_UP and (current_index == 2 or current_index == 3):
            current_index -= 2
        elif key == curses.KEY_DOWN and (current_index == 0 or current_index == 1):
            current_index += 2
        elif key == curses.KEY_LEFT and (current_index == 1 or current_index == 3):
            current_index -= 1
        elif key == curses.KEY_RIGHT and (current_index == 0 or current_index == 2):
            current_index += 1
        elif key == ord('\n'):  # Enter 키를 누르면 선택 완료
            return skills[current_index]

def battle(player, enemy):
    def battle_logic(stdscr):
        nowCSmon = player[0]
        display_status(stdscr, nowCSmon, enemy)  # 초기 상태 출력

        addstr_with_korean_support(stdscr, 14, 0, f"  야생의 {enemy.name}가 나타났다!")
        stdscr.refresh()
        stdscr.getch()

        while nowCSmon.is_alive() and enemy.is_alive():
            # 전투 상태 출력
            display_status(stdscr, nowCSmon, enemy)
            
            # 플레이어 스킬 선택
            selected_skill = select_skill_with_arrows(stdscr, nowCSmon, enemy)
            nowCSmon_skill = nowCSmon.skills[selected_skill]

            # 적 스킬 랜덤 선택
            enemy_skill_name = random.choice(list(enemy.skills.keys()))
            enemy_skill = enemy.skills[enemy_skill_name]

            display_status(stdscr, nowCSmon, enemy)
            # 우선순위 비교
            if nowCSmon_skill.priority > enemy_skill.priority or (nowCSmon_skill.priority == enemy_skill.priority and nowCSmon.sp >= enemy.sp):
                # 플레이어 스킬 먼저 발동
                playerCurrentHP = nowCSmon.nowhp
                enemyCurrentHP = enemy.nowhp
                addstr_with_korean_support(stdscr, 14, 0, f"  {nowCSmon.name}의 {nowCSmon_skill.name}!")
                stdscr.refresh()
                stdscr.getch()

                stop = use_skill(nowCSmon, enemy, nowCSmon_skill, enemy_skill)
                animate_health_bar(stdscr, 3, 32, enemyCurrentHP, enemy.nowhp, enemy.Maxhp, 1, 2, 3)
                animate_health_bar(stdscr, 10, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp, 1, 2, 3)    
                skill_message(stdscr, nowCSmon, enemy, nowCSmon_skill, enemy_skill)

                # 적이 살아있으면 반격
                if enemy.is_alive() and not stop:
                    playerCurrentHP = nowCSmon.nowhp
                    enemyCurrentHP = enemy.nowhp
                    display_status(stdscr, nowCSmon, enemy)
                    addstr_with_korean_support(stdscr, 14, 0, f"  {enemy.name}의 {enemy_skill.name}!")
                    stdscr.refresh()
                    stdscr.getch()

                    stop = use_skill(enemy, nowCSmon, enemy_skill)
                    animate_health_bar(stdscr, 3, 32, enemyCurrentHP, enemy.nowhp, enemy.Maxhp, 1, 2, 3)
                    animate_health_bar(stdscr, 10, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp, 1, 2, 3)    
                    skill_message(stdscr, enemy, nowCSmon, enemy_skill)
            else:
                # 적 스킬 먼저 발동
                playerCurrentHP = nowCSmon.nowhp
                enemyCurrentHP = enemy.nowhp
                addstr_with_korean_support(stdscr, 14, 0, f"  {enemy.name}의 {enemy_skill.name}!")
                stdscr.refresh()
                stdscr.getch()

                stop = use_skill(enemy, nowCSmon, enemy_skill, nowCSmon_skill)
                animate_health_bar(stdscr, 3, 32, enemyCurrentHP, enemy.nowhp, enemy.Maxhp, 1, 2, 3)
                animate_health_bar(stdscr, 10, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp, 1, 2, 3)    
                skill_message(stdscr, enemy, nowCSmon, enemy_skill, nowCSmon_skill)

                # 플레이어가 살아있으면 반격
                if nowCSmon.is_alive() and not stop:
                    playerCurrentHP = nowCSmon.nowhp
                    enemyCurrentHP = enemy.nowhp
                    display_status(stdscr, nowCSmon, enemy)
                    addstr_with_korean_support(stdscr, 14, 0, f"  {nowCSmon.name}의 {nowCSmon_skill.name}!")
                    stdscr.refresh()
                    stdscr.getch()

                    stop = use_skill(nowCSmon, enemy, nowCSmon_skill)
                    animate_health_bar(stdscr, 3, 32, enemyCurrentHP, enemy.nowhp, enemy.Maxhp, 1, 2, 3)
                    animate_health_bar(stdscr, 10, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp, 1, 2, 3)    
                    skill_message(stdscr, nowCSmon, enemy, nowCSmon_skill)

        # 전투 결과 출력
        display_status(stdscr, nowCSmon, enemy)
        if not nowCSmon.is_alive():
            addstr_with_korean_support(stdscr, 14, 0, f"  {nowCSmon.name}가 쓰러졌다!")
        elif not enemy.is_alive():
            addstr_with_korean_support(stdscr, 14, 0, f"  {enemy.name}가 쓰러졌다!")
        stdscr.refresh()
        stdscr.getch()
        addstr_with_korean_support(stdscr, 17, 0, "아무 키나 눌러 계속하기...")
        stdscr.getch()

    curses.wrapper(battle_logic)