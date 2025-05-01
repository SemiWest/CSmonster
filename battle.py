import subprocess
import sys
try:
    import curses
except ImportError:    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "windows-curses"])
    import curses
import unicodedata
import random
import time
import copy
from items import *

battleturn = 0

'''디스플레이'''
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

def animate_health_bar(stdscr, y, x, current_hp, target_hp, max_hp):
    """체력바를 부드럽게 애니메이션으로 업데이트"""
    current_ratio = int(current_hp * 20 / max_hp)
    target_ratio = int(target_hp * 20 / max_hp)
    steps = abs(current_ratio-target_ratio)  # 애니메이션 단계 수
    if steps == 0:
        addstr_with_korean_support(stdscr, y, x, f" {'█' * current_ratio}{' ' * (20 - current_ratio)} ", curses.color_pair(3 - target_ratio // 7))
        return

    for step in range(steps + 1):
        # 현재 체력 비율 계산
        interpolated_ratio = current_ratio + int((target_ratio - current_ratio) * step / steps)

        # 체력 상태에 따른 색상 선택
        if interpolated_ratio >= 14:  # 풀피 (70% 이상)
            color_pair = 1
        elif interpolated_ratio >= 7:  # 반피 (35% 이상)
            color_pair = 2
        else:  # 딸피 (35% 미만)
            color_pair = 3
        
        # 체력바 출력
        stdscr.addstr(y, x, f" {'█' * interpolated_ratio}{' ' * (20 - interpolated_ratio)} ", curses.color_pair(color_pair))
        stdscr.refresh()
        time.sleep(0.05)  # 애니메이션 속도 조절

def display_status(stdscr, player, enemy):
    stdscr.clear()

    addstr_with_korean_support(stdscr, 0, 0, "┌──────────────────────────────────────────────────────────────┐")
    addstr_with_korean_support(stdscr, 1, 2, f"스테이지 {battleturn}")
    # 적 상태 출력
    addstr_with_korean_support(stdscr, 2, 38, f"{enemy.name}(lv {enemy.level})")
    animate_health_bar(stdscr, 3, 38, enemy.nowhp, enemy.nowhp, enemy.Maxhp)

    # 플레이어 상태 출력
    addstr_with_korean_support(stdscr, 12, 4, f"{player.name}(lv {player.level})")
    animate_health_bar(stdscr, 13, 4, player.nowhp, player.nowhp, player.Maxhp)

    addstr_with_korean_support(stdscr, 15, 0, "└──────────────────────────────────────────────────────────────┘")
    for i in range(1, 15):
        addstr_with_korean_support(stdscr, i, 0, "│")
        addstr_with_korean_support(stdscr, i, 63, "│")
    
    stdscr.refresh()

def option_choice(stdscr, options, nowCSmon, enemy, description=None, styles=None):
    """옵션 선택 메뉴"""
    current_index = 0

    while True:
        display_status(stdscr, nowCSmon, enemy)  # 상태 출력
        for i, option in enumerate(options):
            if i == current_index:
                addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"> {option}", curses.A_REVERSE)  # 선택된 옵션 강조
                if description is not None:
                    if isinstance(description[i], list):  # description[i]가 리스트인 경우
                        for j, line in enumerate(description[i]):
                            addstr_with_korean_support(stdscr, 21 + j, 2, f"{line}", styles[i][j] if styles else 0)
                    else:  # description[i]가 문자열인 경우
                        addstr_with_korean_support(stdscr, 21, 2, f"{description[i]}")
            else:
                addstr_with_korean_support(stdscr, 17 + int(i / 2), 32 * (i % 2), f"  {option}")

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('\n'):  # Enter 키를 누르면 선택 완료
            return current_index
        if key == ord('\b'):  # BACKSPACE 키를 누르면 취소
            return -1
        elif len(options) == 1:  # 옵션이 하나일 경우
            current_index = 0
        elif key == curses.KEY_UP and (current_index > 1 and current_index < len(options)):
            current_index -= 2
        elif key == curses.KEY_DOWN and (current_index >=0 and current_index < len(options)-2):
            current_index += 2
        elif key == curses.KEY_LEFT and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
            current_index -= 1
        elif key == curses.KEY_RIGHT and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options)-1):
            current_index += 1
        
''' 스킬 '''
def skill_message(stdscr, user, target, skill, counter_skill=None):
    """스킬 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 스킬 메시지 출력
    if skill.effect_type == "reflect":
        if counter_skill is not None:
            if counter_skill.effect_type == "damage":
                if skill.skW == 0:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}가 {target.name}의 {counter_skill.name}을 방어했다.")
                else:
                    damage = counter_skill.damage(user, target)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}가 {target.name}의 {counter_skill.name}을 반사!")
                    stdscr.refresh()
                    stdscr.getch()
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}가 {damage}의 데미지를 입었다!                                    ")
            else:
                addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")

    elif skill.effect_type == "damage":
        damage = skill.damage(target, user)
        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}가 {damage}의 데미지를 입었다!")

    elif skill.effect_type == "halve_hp":
        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 반으로 줄었다!")

    elif skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.Maxhp)
        addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 체력이 {heal_amount} 회복되었다!")

    elif skill.effect_type == "buff":
        addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 공격력이 {skill.skW}배가 되었다!")

    stdscr.refresh()
    stdscr.getch()  # 메시지를 잠시 보여줌

def select_skill_with_arrows(stdscr, player, enemy):
    """방향키로 스킬 선택"""
    curses.curs_set(0)  # 커서를 숨김
    stdscr.keypad(True)
    stdscr.clear()

    skills = list(player.skills.keys())
    descriptions = [player.skills[skill].description for skill in skills]  # 스킬 설명 리스트
    display_status(stdscr, player, enemy)
    index = option_choice(stdscr, skills, player, enemy, descriptions)  # 스킬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    return skills[index]  # 선택된 스킬 이름 반환

def use_skill(user, target, skill, counter_skill=None):
    """스킬 효과를 처리 (체력 계산만 수행)"""
    # reflect 스킬 처리
    if skill.effect_type == "reflect":
        if counter_skill is not None:
            if counter_skill.effect_type == "damage":
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
        heal_amount = int(skill.skW * user.Maxhp)
        user.nowhp = min(user.Maxhp, user.nowhp + heal_amount)
        return False

    # buff 스킬 처리
    if skill.effect_type == "buff":
        user.ad *= skill.skW
        return False

    return False

def skill_phase(stdscr, nowCSmon, enemy):
    # 플레이어 스킬 선택
    selected_skill = select_skill_with_arrows(stdscr, nowCSmon, enemy)
    if selected_skill == -1:
        return -1  # BACKSPACE 키를 누르면 취소
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
        addstr_with_korean_support(stdscr, 17, 0, f"  {nowCSmon.name}의 {nowCSmon_skill.name}!")
        stdscr.refresh()
        stdscr.getch()

        stop = use_skill(nowCSmon, enemy, nowCSmon_skill, enemy_skill)
        animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
        animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
        skill_message(stdscr, nowCSmon, enemy, nowCSmon_skill, enemy_skill)

        # 적이 살아있으면 반격
        if enemy.is_alive() and not stop:
            playerCurrentHP = nowCSmon.nowhp
            enemyCurrentHP = enemy.nowhp
            display_status(stdscr, nowCSmon, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
            stdscr.refresh()
            stdscr.getch()

            stop = use_skill(enemy, nowCSmon, enemy_skill)
            animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
            animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
            skill_message(stdscr, enemy, nowCSmon, enemy_skill)
    else:
        # 적 스킬 먼저 발동
        playerCurrentHP = nowCSmon.nowhp
        enemyCurrentHP = enemy.nowhp
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
        stdscr.refresh()
        stdscr.getch()

        stop = use_skill(enemy, nowCSmon, enemy_skill, nowCSmon_skill)
        animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
        animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
        skill_message(stdscr, enemy, nowCSmon, enemy_skill, nowCSmon_skill)

        # 플레이어가 살아있으면 반격
        if nowCSmon.is_alive() and not stop:
            playerCurrentHP = nowCSmon.nowhp
            enemyCurrentHP = enemy.nowhp
            display_status(stdscr, nowCSmon, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {nowCSmon.name}의 {nowCSmon_skill.name}!")
            stdscr.refresh()
            stdscr.getch()

            stop = use_skill(nowCSmon, enemy, nowCSmon_skill)
            animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
            animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
            skill_message(stdscr, nowCSmon, enemy, nowCSmon_skill)

''' 교체 '''
def select_monster_with_arrows(stdscr, player, enemy, nowCSmon):
    """방향키로 전산몬 선택"""
    stdscr.keypad(True)
    stdscr.clear()

    monsters = [m for m in player if m is not None]  # None이 아닌 전산몬만 선택]
    name_monsters = [m.name for m in monsters]  # 전산몬 이름 리스트
    
    descriptions = []
    styles = []  # 전산몬 설명 리스트
    
    for m in monsters:
        hpratio = int(m.nowhp * 20 / m.Maxhp)  # 체력 비율 계산
        descriptions.append([f"{m.name}", f"lv {m.level}", f" {'█' * hpratio}{' ' * (20 - hpratio)} "])
        styles.append([0, 0, curses.color_pair(3 - hpratio // 7)])
    
    display_status(stdscr, nowCSmon, enemy)
    index = option_choice(stdscr, name_monsters, nowCSmon, enemy, descriptions, styles)  # 전산몬 선택
    return index  # 선택된 전산몬 인덱스 반환

def swap_phase(stdscr, player, enemy, currentCSmon):
    """전산몬 교체 단계"""
    # 플레이어 전산몬 선택
    selected_monster = select_monster_with_arrows(stdscr, player, enemy, currentCSmon)
    if selected_monster == -1:
        if currentCSmon.is_alive() == False:
            display_status(stdscr, currentCSmon, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}는 쓰러져서 교체해야 해!")
            stdscr.refresh()
            stdscr.getch()
            return swap_phase(stdscr, player, enemy, currentCSmon)  # 다시 선택
        return currentCSmon  # BACKSPACE 키를 누르면 취소
    new_monster = player[selected_monster]
    if new_monster.is_alive() == False:
        display_status(stdscr, currentCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {new_monster.name}는 이미 쓰러졌어!")
        stdscr.refresh()
        stdscr.getch()
        return swap_phase(stdscr, player, enemy, currentCSmon)  # 다시 선택
    elif new_monster == currentCSmon:
        display_status(stdscr, currentCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}는 이미 나와 있어!")
        stdscr.refresh()
        stdscr.getch()
        return currentCSmon

    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    display_status(stdscr, currentCSmon, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  수고했어, {currentCSmon.name}!")
    stdscr.refresh()
    stdscr.getch()
    display_status(stdscr, new_monster, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  나와라, {new_monster.name}!")
    stdscr.refresh()
    stdscr.getch()
    
    playerCurrentHP = new_monster.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, new_monster, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    stdscr.refresh()
    stdscr.getch()

    use_skill(enemy, new_monster, enemy_skill)
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 13, 4, playerCurrentHP, new_monster.nowhp, new_monster.Maxhp)    
    skill_message(stdscr, enemy, new_monster, enemy_skill)
    stdscr.refresh()
    stdscr.getch()
    return new_monster

''' 아이템 사용 '''
def use_item(item, target):
    """아이템 효과를 처리 (체력 계산만 수행)"""
    # heal 아이템 처리
    if item.effect == "heal":
        heal_amount = max(5, target.Maxhp * 0.2)  # 5 또는 최대 체력의 20% 중 큰 값
        target.nowhp = min(target.Maxhp, target.nowhp + heal_amount)
        return False

    return False

def item_message(stdscr, item, target):
    """아이템 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 아이템 메시지 출력
    if item.effect == "heal":
        heal_amount = max(5, target.Maxhp * 0.2)  # 5 또는 최대 체력의 20% 중 큰 값
        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 {heal_amount} 회복되었다!")
    stdscr.refresh()
    stdscr.getch()  # 메시지를 잠시 보여줌

def select_item_with_arrows(stdscr, player, enemy, items):
    """방향키로 아이템 선택"""
    stdscr.keypad(True)
    stdscr.clear()

    myitems = [i for i in items if i is not None]  # None이 아닌 아이템만 선택
    items_name = [i.name for i in myitems]  # 예시 아이템 리스트
    descriptions = [i.description for i in myitems]  # 아이템 설명 리스트
    display_status(stdscr, player, enemy)
    index = option_choice(stdscr, items_name, player, enemy, descriptions)  # 아이템 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    return index  # 선택된 아이템 이름 반환

def item_phase(stdscr, player, enemy, nowCSmon):
    """아이템 사용 단계"""
    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    playerCurrentHP = nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    item_num = select_item_with_arrows(stdscr, nowCSmon, enemy, player.items)  # 아이템 선택
    if item_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    mon_num = select_monster_with_arrows(stdscr, player.csMons, enemy, nowCSmon)  # 전산몬 선택
    if mon_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    display_status(stdscr, nowCSmon, enemy)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {player.items[item_num].name}을 {player.csMons[mon_num].name}에게 사용했다!")
    stdscr.refresh()
    stdscr.getch()

    use_item(player.items[item_num], player.csMons[mon_num])  # 아이템 사용
    
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)
    display_status(stdscr, nowCSmon, enemy)  # 상태 출력
    item_message(stdscr, player.items[item_num], player.csMons[mon_num])  # 아이템 메시지 출력
    player.items[item_num] = None  # 사용한 아이템 삭제
    stdscr.refresh()
    stdscr.getch()


    playerCurrentHP = nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, nowCSmon, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    stdscr.refresh()
    stdscr.getch()

    use_skill(enemy, nowCSmon, enemy_skill)

    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
    skill_message(stdscr, enemy, nowCSmon, enemy_skill)
    stdscr.refresh()
    stdscr.getch()

''' 포획 '''
def catch_monster(stdscr, player, enemy, nowCSmon):
    """포획 시도"""
    display_status(stdscr, nowCSmon, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}를 포획 시도 중...")
    stdscr.refresh()
    stdscr.getch()

    # 포획 성공 확률 계산 (체력이 낮을수록 성공 확률 증가)
    catch_rate = 100 - int((enemy.nowhp / enemy.Maxhp) * 75)  # 최소 25%, 최대 100%
    success = random.randint(1, 100) <= catch_rate

    if success:
        display_status(stdscr, nowCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}를 포획했다!")
        stdscr.refresh()
        stdscr.getch()

        # 플레이어 몬스터 슬롯에 추가
        for i in range(len(player.csMons)):
            if player.csMons[i] is None:
                player.csMons[i] = copy.deepcopy(enemy)
                break
        else:
            addstr_with_korean_support(stdscr, 17, 0, "  몬스터 슬롯이 가득 찼다!")
            stdscr.refresh()
            stdscr.getch()
            display_status(stdscr, nowCSmon, enemy)
            addstr_with_korean_support(stdscr, 17, 0, f"  놓아줄 몬스터를 선택하자!")
            stdscr.refresh()
            stdscr.getch()
            # 몬스터 교체
            selected_monster = select_monster_with_arrows(stdscr, player.csMons, enemy, nowCSmon)
            if selected_monster == -1:
                display_status(stdscr, nowCSmon, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  포획을 취소했다.")
                stdscr.refresh()
                stdscr.getch()
            else:
                display_status(stdscr, nowCSmon, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {player.csMons[selected_monster].name}, 그리울거야!")
                if nowCSmon == player.csMons[selected_monster]:
                    player.csMons[selected_monster] = copy.deepcopy(enemy)
                    nowCSmon = player.csMons[selected_monster]  # 교체된 몬스터로 변경
                else: player.csMons[selected_monster] = copy.deepcopy(enemy)
                stdscr.refresh()
                stdscr.getch()

        return True
    else:
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name} 포획에 실패했다!")
        stdscr.refresh()
        stdscr.getch()
        return False

def catch_phase(stdscr, player, enemy, nowCSmon):
    """포획 단계"""
    
    if catch_monster(stdscr, player, enemy, nowCSmon):
        return True

    # 적 스킬 랜덤 선택
    enemy_skill_name = random.choice(list(enemy.skills.keys()))
    enemy_skill = enemy.skills[enemy_skill_name]

    playerCurrentHP = nowCSmon.nowhp
    enemyCurrentHP = enemy.nowhp
    display_status(stdscr, nowCSmon, enemy)
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}의 {enemy_skill.name}!")
    stdscr.refresh()
    stdscr.getch()

    use_skill(enemy, nowCSmon, enemy_skill)

    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemy.nowhp, enemy.Maxhp)
    animate_health_bar(stdscr, 13, 4, playerCurrentHP, nowCSmon.nowhp, nowCSmon.Maxhp)    
    skill_message(stdscr, enemy, nowCSmon, enemy_skill)
    stdscr.refresh()
    stdscr.getch()

    # 포획 시도

'''종합 액션'''
def select_action(stdscr, player, enemy):
    """행동 선택 메뉴"""
    actions = ["스킬 사용", "전산몬 교체", "아이템 사용", "전산몬 포획","도망가기"]
    display_status(stdscr, player, enemy)
    index = option_choice(stdscr, actions, player, enemy)  # 행동 선택
    if index == -1:
        return -1 # BACKSPACE 키를 누르면 취소
    return actions[index]


def battle(player, enemy, now_csMon, turn):
    global battleturn
    battleturn = turn 
    def battle_logic(stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE) # 풀피 색상 (초록색)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_WHITE)  # 반피 색상 (노란색)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)    # 딸피 색상 (빨간색)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_MAGENTA)  # 기본 색상 (흰색)
        curses.curs_set(0)  # 커서를 숨김

        nowCSmon = now_csMon
        display_status(stdscr, nowCSmon, enemy)  # 초기 상태 출력

        addstr_with_korean_support(stdscr, 17, 0, f"  야생의 {enemy.name}가 나타났다!")
        stdscr.refresh()
        stdscr.getch()

        while enemy.is_alive():
            # 행동 선택
            if nowCSmon.is_alive() == False:
                display_status(stdscr, nowCSmon, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {nowCSmon.name}가 쓰러졌다!")
                stdscr.refresh()
                stdscr.getch()

                # 살아있는 전산몬이 있는지 확인
                if not any(m is not None and m.is_alive() for m in player.csMons):
                    display_status(stdscr, nowCSmon, enemy)
                    addstr_with_korean_support(stdscr, 17, 0, f"  더 이상 교체할 전산몬이 없다!")
                    stdscr.refresh()
                    stdscr.getch()
                    display_status(stdscr, nowCSmon, enemy)
                    addstr_with_korean_support(stdscr, 17, 0, f"  패배했다...")
                    stdscr.refresh()
                    stdscr.getch()
                    return False

                # 교체 가능한 전산몬이 있으면 교체
                nowCSmon = swap_phase(stdscr, player.csMons, enemy, nowCSmon)

            action = select_action(stdscr, nowCSmon, enemy)
            if action == -1:
                continue  # BACKSPACE 키를 누르면 취소

            if action == "스킬 사용":
                escape = skill_phase(stdscr, nowCSmon, enemy)
                if escape == -1:
                    continue
            elif action == "전산몬 교체":
                nowCSmon = swap_phase(stdscr, player.csMons, enemy, nowCSmon)
            elif action == "아이템 사용":
                if player.items.count(None) == 6:
                    display_status(stdscr, nowCSmon, enemy)
                    addstr_with_korean_support(stdscr, 17, 0, f"  아이템이 없다!")
                    stdscr.refresh()
                    stdscr.getch()
                else:
                    escape = item_phase(stdscr, player, enemy, nowCSmon)
                    if escape == -1:
                        continue
            elif action == "전산몬 포획":
                if catch_phase(stdscr, player, enemy, nowCSmon):
                    display_status(stdscr, nowCSmon, enemy)
                    droptem = items[random.choice(list(items.keys()))]  # 랜덤 아이템 드랍
                    if player.items.count(None) != 0:
                        for i in player.items:
                            if i is None:
                                player.items[player.items.index(i)] = droptem
                                break
                    else: 
                        addstr_with_korean_support(stdscr, 17, 0, f"  아이템 슬롯이 가득 찼다!")
                        return nowCSmon
                    addstr_with_korean_support(stdscr, 17, 0, f"  전투에서 승리했다! {droptem.name}을 획득했다!")
                    stdscr.refresh()
                    stdscr.getch()
                    return nowCSmon
            elif action == "도망가기":
                display_status(stdscr, nowCSmon, enemy)
                addstr_with_korean_support(stdscr, 17, 0, f"  {nowCSmon.name}가 도망쳤다!")
                stdscr.refresh()
                stdscr.getch()
                return nowCSmon
            

        # 전투 결과 출력
        display_status(stdscr, nowCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.name}가 쓰러졌다!")
        stdscr.refresh()
        stdscr.getch()

        display_status(stdscr, nowCSmon, enemy)
        droptem = items[random.choice(list(items.keys()))]  # 랜덤 아이템 드랍
        if player.items.count(None) != 0:
            for i in player.items:
                if i is None:
                    player.items[player.items.index(i)] = droptem
                    break
        else: 
            addstr_with_korean_support(stdscr, 17, 0, f"  아이템 슬롯이 가득 찼다!")
            stdscr.refresh()
            stdscr.getch()
            return nowCSmon
        addstr_with_korean_support(stdscr, 17, 0, f"  전투에서 승리했다! {droptem.name}을 획득했다!")
        stdscr.refresh()
        stdscr.getch()
        return nowCSmon

    return curses.wrapper(battle_logic)