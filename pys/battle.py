from playsound import *
import random
from player import *

''' 전역변수 설정 '''
battleturn = 0
hap_num = 0
player = None
enemy = None
enemyCSmon = None
sX, sY = 1, 0
bsX, bsY = 64, 18 #16:9 사이즈

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

def display_type(stdscr, y, x, type):
    if type == "전산이론":
        addstr_with_korean_support(stdscr, y, x, " CST ", curses.color_pair(21))
    elif type == "데이터 과학":
        addstr_with_korean_support(stdscr, y, x, " DTS ", curses.color_pair(22))
    elif type == "시스템-네트워크":
        addstr_with_korean_support(stdscr, y, x, " SYS ", curses.color_pair(23))
    elif type == "소프트웨어디자인":
        addstr_with_korean_support(stdscr, y, x, " SWD ", curses.color_pair(24))
    elif type == "시큐어컴퓨팅":
        addstr_with_korean_support(stdscr, y, x,  "     ", curses.color_pair(25))
        addstr_with_korean_support(stdscr, y, x+1, "S C", curses.color_pair(26))
        addstr_with_korean_support(stdscr, y, x+2,  "E", curses.color_pair(25))
    elif type == "비주얼컴퓨팅":
        addstr_with_korean_support(stdscr, y, x, " VSC ", curses.color_pair(27))
    elif type == "인공지능-정보서비스":
        addstr_with_korean_support(stdscr, y, x,  "     ", curses.color_pair(29))
        addstr_with_korean_support(stdscr, y, x+1, "A S", curses.color_pair(28))
        addstr_with_korean_support(stdscr, y, x+2,  "I", curses.color_pair(29))
    elif type == "소셜컴퓨팅":
        addstr_with_korean_support(stdscr, y, x, " SOC ", curses.color_pair(30))
    elif type == "인터랙티브컴퓨팅":
        addstr_with_korean_support(stdscr, y, x, " INT ", curses.color_pair(31))

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
        stdscr.addstr(y+1, x, f"({int(temp_hp)}/{max_hp})")
        stdscr.refresh()
        time.sleep(0.05)  # 애니메이션 속도 

def display_status(stdscr, detail=False):
    stdscr.clear()
    curses.flushinp()
    
    esX, esY = sX+bsX+2-25, sY+2
    psX, psY = sX+3, sY+bsY-4
    # 테두리
    addstr_with_korean_support(stdscr,  sY, sX, "┌"+"─"*bsX+"┐")
    for i in range(sY+1, sY+bsY+7):
        addstr_with_korean_support(stdscr, i,       sX, "│")
        addstr_with_korean_support(stdscr, i, sX+bsX+1, "│")
    addstr_with_korean_support(stdscr, sY+bsY+1, sX, "├"+"─"*bsX+"┤")
    addstr_with_korean_support(stdscr, sY+bsY+7, sX, "└"+"─"*bsX+"┘")
    
    # 배틀 정보 출력
    addstr_with_korean_support(stdscr, sY+1, sX+2, f"플레이어: {player.name}", curses.color_pair(5))
    addstr_with_korean_support(stdscr, sY+2, sX+2, f"스테이지 {battleturn}", curses.color_pair(4))
    addstr_with_korean_support(stdscr, sY+3, sX+2, f"턴 {hap_num}", curses.color_pair(3))
    
    # 적 상태 출력
    if isinstance(enemy, Player):
        for i, mymon in enumerate(enemy.csMons):
            addstr_with_korean_support(stdscr, sY+1, esX+1+i*2, "◒", curses.color_pair(1 if not mymon.is_alive() else 5 if mymon.dictNo == -1 else 99))
    if enemyCSmon.dictNo == -2:
        addstr_with_korean_support(stdscr, esY  , esX+7, "▗███████▖", curses.color_pair(1))
        addstr_with_korean_support(stdscr, esY+1, esX+7, "███▛ ▜███", curses.color_pair(1))
        addstr_with_korean_support(stdscr, esY+2, esX+7, "███▙▀▟███")
        addstr_with_korean_support(stdscr, esY+3, esX+7, "▝███████▘")
        addstr_with_korean_support(stdscr, esY+1, esX+11,    "▃")
    elif enemyCSmon.dictNo == -3:
        addstr_with_korean_support(stdscr, esY  , esX+8, "▗███████▖", curses.color_pair(1))
        addstr_with_korean_support(stdscr, esY+1, esX+8, "███▛ ▜███", curses.color_pair(1))
        addstr_with_korean_support(stdscr, esY+2, esX+8, "███▙▀▟███")
        addstr_with_korean_support(stdscr, esY+3, esX+8, "▝███████▘")
        addstr_with_korean_support(stdscr, esY+1, esX+12, "▃")
    elif enemyCSmon.grade == "보스":
        addstr_with_korean_support(stdscr, esY, esX, f"{enemyCSmon.name}(lv {enemyCSmon.level})", curses.color_pair(1))
        animate_health_bar(stdscr, esY+1, esX, enemyCSmon.nowhp, enemyCSmon.nowhp, enemyCSmon.HP)
        for i, j in enumerate(enemyCSmon.type):
            display_type(stdscr, esY+2, esX+17-i*6, j)
    elif enemyCSmon.grade == "중간 보스":
        addstr_with_korean_support(stdscr, esY, esX, f"{enemyCSmon.name}(lv {enemyCSmon.level})", curses.color_pair(2))
        animate_health_bar(stdscr, esY+1, esX, enemyCSmon.nowhp, enemyCSmon.nowhp, enemyCSmon.HP)
        for i, j in enumerate(enemyCSmon.type):
            display_type(stdscr, esY+2, esX+17-i*6, j)
    else:
        addstr_with_korean_support(stdscr, esY, esX, f"{enemyCSmon.name}(lv {enemyCSmon.level})")
        animate_health_bar(stdscr, esY+1, esX, enemyCSmon.nowhp, enemyCSmon.nowhp, enemyCSmon.HP)
        for i, j in enumerate(enemyCSmon.type):
            display_type(stdscr, esY+2, esX+17-i*6, j)
        

    # 플레이어 상태 출력
    for i, mymon in enumerate(player.csMons):
            addstr_with_korean_support(stdscr, psY, psX+1+i*2, "◒", curses.color_pair(1 if not mymon.is_alive() else 5 if mymon.dictNo == -1 else 99))
    addstr_with_korean_support(stdscr, psY+1, psX, f"{player.nowCSmon.name}(lv {player.nowCSmon.level})")
    animate_health_bar(stdscr, psY+2, psX, player.nowCSmon.nowhp, player.nowCSmon.nowhp, player.nowCSmon.HP)
    for i, j in enumerate(player.nowCSmon.type):
        display_type(stdscr, psY+3, psX+17-i*6, j)
    if detail:
        display_details(stdscr, player.nowCSmon, 68, "몬스터")

def display_details(stdscr, target, x, case="몬스터"):
    """상세 정보 출력"""
    if case == "몬스터":
        details = [
            (("이름", 0, 99), (f"{target.name}", 11, 4)),
            "타입",
            (("레벨", 0, 99), (f"{target.level}", 11, 4)),
            (("레벨업까지", 0, 99), (f"{target.max_exp - target.exp}", 11, 5), ("경험치 남음", 12 + len(f"{target.max_exp - target.exp}"), 99)),
            "",
            "체력",
            "",
            (("공격", 0, 99), (f"{target.ATK}", 11, 4), None if target.Rank[1]==0 else ((("+" if target.Rank[1]>0 else "-") + f"{abs(target.Rank[1])}"), 12 + len(f"{target.ATK}"), min(7-target.Rank[1], 7+target.Rank[1]))),
            (("방어", 0, 99), (f"{target.DEF}", 11, 4), None if target.Rank[2]==0 else ((("+" if target.Rank[2]>0 else "-") + f"{abs(target.Rank[2])}"), 12 + len(f"{target.DEF}"), min(7-target.Rank[2], 7+target.Rank[2]))),
            (("특공", 0, 99), (f"{target.SP_ATK}", 11, 4), None if target.Rank[3]==0 else ((("+" if target.Rank[3]>0 else "-") + f"{abs(target.Rank[3])}"), 12 + len(f"{target.SP_ATK}"), min(7-target.Rank[3], 7+target.Rank[3]))),
            (("특방", 0, 99), (f"{target.SP_DEF}", 11, 4), None if target.Rank[4]==0 else ((("+" if target.Rank[4]>0 else "-") + f"{abs(target.Rank[4])}"), 12 + len(f"{target.SP_DEF}"), min(7-target.Rank[4], 7+target.Rank[4]))),
            (("속도", 0, 99), (f"{target.SPD}", 11, 4), None if target.Rank[5]==0 else ((("+" if target.Rank[5]>0 else "-") + f"{abs(target.Rank[5])}"), 12 + len(f"{target.SPD}"), min(7-target.Rank[5], 7+target.Rank[5]))),
            "",
            (("등급", 0, 99), (f"{target.grade}", 11, 99 if target.grade == "일반" else 2 if target.grade == "중간 보스" else 1)),
            (("만난 곳", 0, 99), (f"스테이지 {target.stage}", 11, 4) if isinstance(target.stage, int) else (f"{target.stage}", 11, 4)),
            (("설명", 0, 99), (f"{target.description}", 11, 99)),
        ]
        for i, detailes in enumerate(details):
            if isinstance(detailes, tuple):  # detail이 튜플인 경우
                for detail in detailes:
                    if not isinstance(detail, tuple) and not isinstance(detail, str):  # detail이 문자열인 경우
                        continue
                    start_x = x + detail[1]
                    max_width = 113
                    current_line = ""
                    line_offset = 0
                    current_width = 0  # 현재 줄의 문자 폭
                    for char in detail[0]:
                        char_width = 2 if unicodedata.east_asian_width(char) in ['F', 'W'] else 1
                        if current_width + char_width > max_width - start_x:
                            # 현재 줄 출력
                            addstr_with_korean_support(stdscr, sY+2 + i + line_offset, start_x, current_line, curses.color_pair(detail[2]))
                            current_line = char  # 새로운 줄 시작
                            current_width = char_width
                            line_offset += 1
                        else:
                            current_line += char
                            current_width += char_width
                    if current_line:
                        # 마지막 줄 출력
                        addstr_with_korean_support(stdscr, sY+2 + i + line_offset, start_x, current_line, curses.color_pair(detail[2]))

            elif isinstance(detailes, str):  # detail이 문자열인 경우
                if detailes == "체력":
                    current_ratio = int(target.nowhp * 20 / target.HP)
                    addstr_with_korean_support(stdscr, sY+2 + i, 68, "체력")
                    addstr_with_korean_support(stdscr, sY+2 + i, 79, f" {'█' * current_ratio}{' ' * (20 - current_ratio)} ", curses.color_pair(hpcolor(current_ratio)))
                    addstr_with_korean_support(stdscr, sY+2 + i + 1, 79, f"({int(target.nowhp)}/{target.HP})")
                elif detailes == "타입":
                    addstr_with_korean_support(stdscr, sY+2 + i, 68, "타입")
                    for j, type in enumerate(target.type):
                        display_type(stdscr, sY+2 + i, 79+j*6, type)
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
            else: pass
        
''' 선택 '''
def option_choice(stdscr, option_case, description=None, coloring=None, temp=None):
    """옵션 선택 메뉴"""
    current_index = 0
    stY = sY+bsY+3
    while True:
        display_status(stdscr)  # 상태 출력
        if option_case == "스킬":
            display_status(stdscr, True)  # 상태 출력
            options = player.nowCSmon.skills.values()
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(     stdscr, stY + int(i / 2)*2, sX + 2 + ((bsX-10)//2) * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(   stdscr, stY + int(i / 2)*2, sX + 2 + ((bsX-10)//2) * (i % 2), f"  {option.name}")
                else: addstr_with_korean_support(       stdscr, stY + int(i / 2)*2, sX + 2 + ((bsX-10)//2) * (i % 2), f"  {option.name}")
                
                if i == current_index:
                    addstr_with_korean_support(         stdscr, stY + int(i / 2)*2, sX + 2 + ((bsX-10)//2) * (i % 2), f"> {option.name}", curses.A_REVERSE)
                    
                    # 설명 및 상세정보
                    addstr_with_korean_support(stdscr,                               stY+6,      sX+3, f"{description[i][0]}")
                    display_type(              stdscr,                                 stY, sX+bsX-13, option.skill_type)
                    addstr_with_korean_support(stdscr,                                 stY,  sX+bsX-4, f"물리   " if option.effect_type == "Pdamage" else "특수" if option.effect_type == "Sdamage" else "----")    
                    addstr_with_korean_support(stdscr,                               stY+1, sX+bsX-13, f"pp     "+f"{option.nowpp}/{option.pp}".rjust(6))
                    if description[i][1] != None: addstr_with_korean_support(stdscr, stY+2, sX+bsX-13, f"위력   "+f"{description[i][1]}".rjust(6))
                    else:                         addstr_with_korean_support(stdscr, stY+2, sX+bsX-13, f"위력   "+"----".rjust(6))
                    addstr_with_korean_support(stdscr,                               stY+3, sX+bsX-13, f"명중률 "+(f"{option.acc}".rjust(6) if option.acc != -1 else f"----".rjust(6)))
        
        elif option_case == "몬스터":
            options = player.csMons
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(     stdscr, stY + int(i / 2), sX + 2 + (bsX//2) * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(   stdscr, stY + int(i / 2), sX + 2 + (bsX//2) * (i % 2), f"  {option.name}")
                elif option.dictNo == -1:
                    addstr_with_korean_support(         stdscr, stY + int(i / 2), sX + 2 + (bsX//2) * (i % 2), f"  {option.name}", curses.color_pair(4))
                else: addstr_with_korean_support(       stdscr, stY + int(i / 2), sX + 2 + (bsX//2) * (i % 2), f"  {option.name}")
                if i == current_index:
                    addstr_with_korean_support(         stdscr, stY + int(i / 2), sX + 2 + (bsX//2) * (i % 2), f"> {option.name}", curses.A_REVERSE)  # 선택된 옵션 강조
                    if option.dictNo != -1:
                        display_details(stdscr, option, sX+bsX+4, "몬스터")  # 상세 정보 출력
            if temp != None:
                addstr_with_korean_support(stdscr, stY+3, sX+bsX-len(f"잡은 전산몬: {temp.name}(lv {temp.level})"), f"잡은 전산몬: {temp.name}(lv {temp.level})")
              
                
        elif option_case == "아이템":
            options = player.items
            for i, option in enumerate(options):
                if coloring != None:
                    if coloring[i] != False:
                        addstr_with_korean_support(     stdscr, stY + int(i / 2), (bsX//2) * (i % 2), f"  {option.name}", curses.color_pair(coloring[i]))
                    else: addstr_with_korean_support(   stdscr, stY + int(i / 2), (bsX//2) * (i % 2), f"  {option.name}")
                elif option.dictNo == -1:
                    addstr_with_korean_support(         stdscr, stY + int(i / 2), (bsX//2) * (i % 2), f"  {option.name}", curses.color_pair(4))
                else: addstr_with_korean_support(       stdscr, stY + int(i / 2), (bsX//2) * (i % 2), f"  {option.name}")
                if i == current_index:
                    addstr_with_korean_support(         stdscr, stY + int(i / 2), (bsX//2) * (i % 2), f"> {option.name}", curses.A_REVERSE)
                    if temp != None:
                        addstr_with_korean_support(stdscr, stY+3, sX+bsX-len(f"얻은 아이템: {temp.name}"), f"얻은 아이템: {temp.name}", curses.color_pair(
                            2 if temp.grade == "레전더리" else 6 if temp.grade == "에픽" else 3 if temp.grade == "레어" else 0
                            ))
                    addstr_with_korean_support(stdscr, stY+6, sX+3, f"{description[i]}")
            
             
        elif option_case == "배틀옵션":
            display_status(stdscr, True)  # 상태 출력
            options = ["스킬 사용", "전산몬 교체", "아이템 사용", "전산몬 포획","도망가기"]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, stY + int(i / 2)*2, (bsX//2) * (i % 2)+2, f"  {option}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, stY + int(i / 2)*2, (bsX//2) * (i % 2)+2, f"> {option}", curses.A_REVERSE)


        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('\n'):  # Enter 키를 누르면 선택 완료
            option_select_sound()
            return current_index
        if key == ord('\b') or key == 27 or key == ord("q"):  # BACKSPACE 키를 누르면 취소
            if option_case == "배틀옵션":
                continue
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

def select_skill(stdscr):
    """방향키로 스킬 선택"""
    curses.curs_set(0)  # 커서를 숨김
    stdscr.keypad(True)
    stdscr.clear()
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
    display_status(stdscr, True)  # 상태 출력
    index = option_choice(stdscr, "스킬", descriptions, coloring)  # 스킬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    return skills[index]  # 선택된 스킬 이름 반환

def select_monster(stdscr, temp=None):
    """방향키로 전산몬 선택"""
    stdscr.keypad(True)
    stdscr.clear()

    # 현재 전산몬 표시
    coloring = [False, False, False, False, False, False]
    for i in range(6):
        if player.csMons[i].dictNo == -1:
            coloring[i] = 4 # 빈 슬롯 표시
        elif player.csMons[i].is_alive() == False:
            coloring[i] = 1  # 죽은 전산몬 표시
        elif player.csMons[i] == player.nowCSmon:
            coloring[i] = 5  # 현재 전산몬 표시

    display_status(stdscr)
    index = option_choice(stdscr, "몬스터", coloring = coloring, temp=temp)  # 전산몬 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[index].dictNo == -1:
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return select_monster(stdscr, temp)
    return index  # 선택된 전산몬 인덱스 반환

def select_item(stdscr, temp=None):
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
    display_status(stdscr)
    index = option_choice(stdscr, "아이템", descriptions, coloring, temp)  # 아이템 선택
    if index == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.items[index].name == "빈 슬롯":
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return select_item(stdscr, temp)
    return index  # 선택된 아이템 이름 반환

def select_action(stdscr):
    """행동 선택 메뉴"""
    display_status(stdscr, detail=True)  # 상태 출력
    index = option_choice(stdscr, "배틀옵션")  # 행동 선택
    return index

''' 스킬 '''
def skill_message(stdscr, user, target, skill, counter_skill=None, damage = None, crit = None):
    """스킬 메시지를 출력하기 전에 상태를 먼저 출력"""
    if damage != None:
        damage = int(damage)
    # 스킬 메시지 출력
    display_status(stdscr, True)  # 상태 출력
    if skill.effect_type == "reflect":
        if damage == -121:
            addstr_with_korean_support(stdscr, 17, 0, f"  하지만 실패했다!")
        elif counter_skill is not None:
            if counter_skill.effect_type == "Pdamage" or counter_skill.effect_type == "Sdamage":
                if skill.skW == 0:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 방어했다.")
                else:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}이/가 {target.name}의 {counter_skill.name}을/를 반사!")
                    get_ch_with_sound(stdscr)
                    display_status(stdscr, True)  # 상태 출력 
                    if damage  == False:
                        if counter_skill.Comp(user) == 0:
                            addstr_with_korean_support(stdscr, 17, 0, f"  효과가 없는 것 같다...")
                        else:
                            addstr_with_korean_support(stdscr, 17, 0, f"  그러나 {user.name}의 공격은 빗나갔다!")
                    else:
                        if counter_skill.Comp(user) >= 2:
                            addstr_with_korean_support(stdscr, 17, 0, f"  효과가 굉장했다!")
                            get_ch_with_sound(stdscr)
                            display_status(stdscr, True)  # 상태 출력
                        elif counter_skill.Comp(user) < 1:
                            addstr_with_korean_support(stdscr, 17, 0, f"  효과가 별로인 듯 하다...")
                            get_ch_with_sound(stdscr)
                            display_status(stdscr, True)  # 상태 출력
                        addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 {damage}의 데미지를 입었다.")
            else:
                addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, "  그러나 아무 일도 일어나지 않았다!")

    elif skill.effect_type == "Pdamage" or skill.effect_type == "Sdamage":
        if damage  == False:
            if skill.Comp(target) == 0:
                addstr_with_korean_support(stdscr, 17, 0, f"  효과가 없는 것 같다...")
            else:
                addstr_with_korean_support(stdscr, 17, 0, f"  그러나 {user.name}의 공격은 빗나갔다!")
        else:
            if skill.Comp(target) >= 2:
                addstr_with_korean_support(stdscr, 17, 0, f"  효과가 굉장했다!")
            elif skill.Comp(target) <= 0.5:
                addstr_with_korean_support(stdscr, 17, 0, f"  효과가 별로인 듯 하다...")
            get_ch_with_sound(stdscr)
            display_status(stdscr, True)  # 상태 출력
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 {damage}의 데미지를 입었다.")

    elif skill.effect_type == "halve_hp":
        if damage == False:
            addstr_with_korean_support(stdscr, 17, 0, f"  그러나 {user.name}의 공격은 빗나갔다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 반으로 줄었다!")
            get_ch_with_sound(stdscr)
            display_status(stdscr, True)  # 상태 출력
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 {damage}의 데미지를 입었다!")
    
    elif skill.effect_type == "heal":
        heal_amount = int(skill.skW * user.HP)
        addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 체력이 {heal_amount} 회복되었다!")

    elif skill.effect_type == "buff":
        if isinstance(skill.skW, tuple):
            for B in skill.skW:
                if B % 8 == 0:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 급소율이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 1:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 공격이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 2:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 방어가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 3:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 특수공격이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 4:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 특수방어가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 5:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 스피드가 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 6:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 회피율이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                elif B % 8 == 7:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 명중률이 " + (f"{B//8 + 1}랭크 증가했다!" if B//8 >= 0 else f"{-(B//8 + 1)}랭크 감소했다!"))
                if B != skill.skW[-1]:
                    get_ch_with_sound(stdscr)
                    display_status(stdscr, True)  # 상태 출력
        else:
            if skill.skW % 8 == 0:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 급소율이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 1:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 공격이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 2:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 방어가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 3:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 특수공격이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 4:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 특수방어가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 5:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 스피드가 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 6:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 회피율이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
            elif skill.skW % 8 == 7:
                addstr_with_korean_support(stdscr, 17, 0, f"  {user.name}의 명중률이 " + (f"{skill.skW//8 + 1}랭크 증가했다!" if skill.skW//8 >= 0 else f"{-(skill.skW//8 + 1)}랭크 감소했다!"))
    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌
    if crit:
        display_status(stdscr, True)  # 상태 출력
        addstr_with_korean_support(stdscr, 17, 0, f"  급소에 맞았다!")
        get_ch_with_sound(stdscr)

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

def skillstep_player(stdscr, myskill, yourskill):
    nowCSmon_skill = myskill
    enemyCSmon_skill = yourskill

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    display_status(stdscr, True)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}의 {nowCSmon_skill.name}!")
    get_ch_with_sound(stdscr)

    display_status(stdscr, True)  # 상태 출력
    stop, damage, crit = use_skill(player.nowCSmon, enemyCSmon, nowCSmon_skill, enemyCSmon_skill)
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)  
    skill_message(stdscr,  player.nowCSmon, enemyCSmon, nowCSmon_skill, enemyCSmon_skill, damage, crit)

    return stop

def skillstep_enemy(stdscr, myskill, yourskill):
    nowCSmon_skill = myskill
    enemyCSmon_skill = yourskill

    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    display_status(stdscr, True)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}의 {enemyCSmon_skill.name}!")
    get_ch_with_sound(stdscr)

    display_status(stdscr, True)  # 상태 출력
    stop, damage, crit = use_skill(enemyCSmon, player.nowCSmon, enemyCSmon_skill, nowCSmon_skill)
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)    
    skill_message(stdscr,  enemyCSmon, player.nowCSmon, enemyCSmon_skill, nowCSmon_skill, damage, crit)

    return stop

def enemyskill(): 
    # 적 스킬 랜덤 선택
    enemyCSmon_skill_name = random.choice(list(enemyCSmon.skills.keys()))
    enemyCSmon_skill = enemyCSmon.skills[enemyCSmon_skill_name]
    if enemyCSmon_skill.nowpp == 0:
        # 스킬 포인트가 없으면 다른 스킬 선택
        enemyskill()
    return enemyCSmon_skill
    
def skill_phase(stdscr):
    # 플레이어 스킬 선택
    selected_skill = select_skill(stdscr)
    if selected_skill == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    nowCSmon_skill = player.nowCSmon.skills[selected_skill]
    if nowCSmon_skill.nowpp == 0:
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {nowCSmon_skill.name}의 스킬 포인트가 없어!")
        get_ch_with_sound(stdscr)
        return skill_phase(stdscr)
    if nowCSmon_skill.effect_type == "buff":
        if isinstance(nowCSmon_skill.skW, tuple):
            for B in nowCSmon_skill.skW:
                if player.nowCSmon.Rank[B % 8] == 6 and B//8 >= 0 or player.nowCSmon.Rank[B % 8] == -6 and B//8 <= -2:
                    display_status(stdscr)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}의 "
                                        +("공격은"       if B % 8 == 1 else
                                            "방어는"        if B % 8 == 2 else
                                            "특수공격은"    if B % 8 == 3 else
                                            "특수방어는"    if B % 8 == 4 else
                                            "스피드는"      if B % 8 == 5 else
                                            "회피율은"      if B % 8 == 6 else
                                            "명중률은"      if B % 8 == 7 else
                                            "급소율은") + " 이미 최대치야!")
                    get_ch_with_sound(stdscr)
                    return skill_phase(stdscr)
        else:
            if player.nowCSmon.Rank[nowCSmon_skill.skW % 8] == 6 and nowCSmon_skill.skW//8 >= 0 or player.nowCSmon.Rank[nowCSmon_skill.skW % 8] == -6 and nowCSmon_skill.skW//8 <= -2:
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}의 "
                                        +("공격은"       if nowCSmon_skill.skW % 8 == 1 else
                                            "방어는"        if nowCSmon_skill.skW % 8 == 2 else
                                            "특수공격은"    if nowCSmon_skill.skW % 8 == 3 else
                                            "특수방어는"    if nowCSmon_skill.skW % 8 == 4 else
                                            "스피드는"      if nowCSmon_skill.skW % 8 == 5 else
                                            "회피율은"      if nowCSmon_skill.skW % 8 == 6 else
                                            "명중률은"      if nowCSmon_skill.skW % 8 == 7 else
                                            "급소율은") + " 이미 최대치야!")
                get_ch_with_sound(stdscr)
                return skill_phase(stdscr)
    enemyCSmon_skill = enemyskill()
    # 우선순위 비교
    if nowCSmon_skill.priority > enemyCSmon_skill.priority or (nowCSmon_skill.priority == enemyCSmon_skill.priority and player.nowCSmon.CSPD >= enemyCSmon.CSPD):
        stop = skillstep_player(stdscr, nowCSmon_skill, enemyCSmon_skill)
        if enemyCSmon.is_alive() and not stop:
            skillstep_enemy(stdscr, nowCSmon_skill, enemyCSmon_skill)
    else:
        stop = skillstep_enemy(stdscr, nowCSmon_skill, enemyCSmon_skill)
        if player.nowCSmon.is_alive() and not stop:
            skillstep_player(stdscr, nowCSmon_skill, enemyCSmon_skill)

''' 교체 '''
def swap_phase(stdscr, must_swap=False):
    """전산몬 교체 단계"""
    currentCSmon = player.nowCSmon  # 현재 전산몬

    # 교체할 전산몬 선택
    selected_monster = select_monster(stdscr)
    
    # 선택시 예외 처리
    if selected_monster == -1:
        if must_swap:
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}은/는 쓰러져서 교체해야 해!")
            get_ch_with_sound(stdscr)
            return swap_phase(stdscr, must_swap)  # 다시 선택
        return -1
    if player.csMons[selected_monster].dictNo == -1:
        display_status(stdscr, currentCSmon, enemy)
        addstr_with_korean_support(stdscr, 17, 0, f"  빈 슬롯이다!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, must_swap)  # 다시 선택

    new_monster = player.csMons[selected_monster]
    
    # 교체할 전산몬 관련 예외 처리
    if new_monster.is_alive() == False:
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {new_monster.name}은/는 이미 쓰러졌어!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, must_swap)  # 다시 선택
    elif new_monster == currentCSmon:
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {currentCSmon.name}은/는 이미 나와 있어!")
        get_ch_with_sound(stdscr)
        return swap_phase(stdscr, must_swap)  # 다시 선택
    
    display_status(stdscr)
    addstr_with_korean_support(stdscr, 17, 0, f"  수고했어, {currentCSmon.name}!")
    get_ch_with_sound(stdscr)

    # 교체
    player.nowCSmon = new_monster

    display_status(stdscr)
    addstr_with_korean_support(stdscr, 17, 0, f"  나와라, {new_monster.name}!")
    get_ch_with_sound(stdscr)

    # 강제로 교체해야 했던 경우 턴 소모 없이 즉시 교체
    if must_swap: 
        return   

    # 적 스킬 랜덤 선택
    display_status(stdscr)
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(stdscr, None, enemyCSmon_skill)  # 적 스킬 사용
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

def item_message(stdscr, item, target):
    """아이템 메시지를 출력하기 전에 상태를 먼저 출력"""
    # 아이템 메시지 출력
    if item.effect == "heal":
        heal_amount = max(item.fixed, int(target.HP * item.varied))
        if item.canuse_on_fainted == True:
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}이/가 부활했다!")
        else:
            addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 체력이 {heal_amount} 회복되었다!")
    elif item.effect == "buff":
        if isinstance(item.varied, tuple):
            for v in item.varied:
                if v % 8 == 0:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 급소율이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 1:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 공격이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 2:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 방어가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 3:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 특수공격이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 4:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 특수방어가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 5:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 스피드가 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 6:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 회피율이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                elif v % 8 == 7:
                    addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 명중률이 " + (f"{v//8 + 1}랭크 증가했다!" if v//8 >= 0 else f"{-(v//8 + 1)}랭크 감소했다!"))
                get_ch_with_sound(stdscr)
        else:
            if item.varied % 8 == 0:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 급소율이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 1:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 공격이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 2:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 방어가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 3:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 특수공격이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 4:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 특수방어가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 5:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 스피드가 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 6:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 회피율이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            elif item.varied % 8 == 7:
                addstr_with_korean_support(stdscr, 17, 0, f"  {target.name}의 명중률이 " + (f"{item.varied//8 + 1}랭크 증가했다!" if item.varied//8 >= 0 else f"{-(item.varied//8 + 1)}랭크 감소했다!"))
            get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌

def item_phase(stdscr):
    """아이템 사용 단계"""
    playerCurrentHP = player.nowCSmon.nowhp
    enemyCurrentHP = enemyCSmon.nowhp
    item_num = select_item(stdscr)  # 아이템 선택
    if item_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    mon_num = select_monster(stdscr)  # 전산몬 선택
    if mon_num == -1:
        return -1  # BACKSPACE 키를 누르면 취소
    if player.csMons[mon_num].nowhp == 0:
        if player.items[item_num].canuse_on_fainted == False:
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  쓰러진 전산몬에게는 이 아이템을 사용할 수 없다.")
            get_ch_with_sound(stdscr)
            return item_phase(stdscr)
    display_status(stdscr)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {player.items[item_num].name}을/를 {player.csMons[mon_num].name}에게 사용했다!")
    get_ch_with_sound(stdscr)

    use_item(player.items[item_num], player.csMons[mon_num])  # 아이템 사용
    
    animate_health_bar(stdscr, 3, 38, enemyCurrentHP, enemyCSmon.nowhp, enemyCSmon.HP)
    animate_health_bar(stdscr, 12, 4, playerCurrentHP, player.nowCSmon.nowhp, player.nowCSmon.HP)
    display_status(stdscr)  # 상태 출력
    item_message(stdscr, player.items[item_num], player.csMons[mon_num])  # 아이템 메시지 출력
    player.items[item_num] = items["빈 슬롯"]  # 사용한 아이템 삭제

    # 적 스킬 랜덤 
    display_status(stdscr, True)  # 상태 출력
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(stdscr, None, enemyCSmon_skill)  # 적 스킬 사용

''' 포획 '''
def catch_monster(stdscr):
    """포획 시도"""
    display_status(stdscr)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  가랏, 몬스터볼!")
    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌

    enemydictNo = enemyCSmon.dictNo  # 적 몬스터 이름
    enemyCSmon.dictNo = -2  # 포획 중에는 몬스터볼로 표시
    display_status(stdscr)  # 상태 출력
    addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}을/를 포획 시도 중")
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
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}")
                stdscr.refresh()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
                enemyCSmon.dictNo = -2  # 반짝이는 상태
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}")
                stdscr.refresh()
                time.sleep(0.3/blink_times)  # 몬스터볼이 반짝이는 효과
            if successes[i//2] == False:
                break
        else:
            enemyCSmon.dictNo = -2  # 반짝이는 상태
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}")
            stdscr.refresh()
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}을/를 포획 시도 중{'.'*(i//2+1)}")
        stdscr.refresh()
    time.sleep(0.5)  # 포획 시도 중 메시지 출력 후 대기

    success = successes[0] and successes[1] and successes[2]  # 포획 성공 여부
    
    if success:
        caught()
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {enemyCSmon.name}이/가 잡혔다!")
        curses.flushinp()
        get_ch_with_sound(stdscr)

        # 플레이어 몬스터 슬롯에 추가
        for i in range(len(player.csMons)):
            if player.csMons[i].dictNo == -1:
                player.csMons[i] = copy.deepcopy(enemyCSmon)
                player.csMons[i].dictNo = enemydictNo
                break
        else:
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, "  몬스터 슬롯이 가득 찼다!")
            get_ch_with_sound(stdscr)
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  놓아줄 몬스터를 선택하자.")
            get_ch_with_sound(stdscr)
            # 몬스터 교체
            tempmon = copy.deepcopy(enemyCSmon)
            tempmon.dictNo = enemydictNo
            selected_monster = select_monster(stdscr, tempmon)
            if selected_monster == -1:
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  포획을 취소했다.")
                get_ch_with_sound(stdscr)
            else:
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  {player.csMons[selected_monster].name}, 그리울거야!")
                if player.nowCSmon == player.csMons[selected_monster]:
                    player.csMons[selected_monster] = tempmon
                    player.nowCSmon = player.csMons[selected_monster]  # 교체된 몬스터로 변경
                else:
                    player.csMons[selected_monster] = tempmon
                    player.csMons[selected_monster].dictNo = enemydictNo
                get_ch_with_sound(stdscr)
        return True
    else:
        # 포획 실패 시 적 몬스터 이름 복원
        enemyCSmon.dictNo = enemydictNo
        display_status(stdscr)
        # 포획 실패 메시지 출력
        addstr_with_korean_support(stdscr, 17, 0, f"  앗, {enemyCSmon.name}이/가 몬스터볼에서 나왔다!")
        get_ch_with_sound(stdscr)
        return False

def catch_phase(stdscr):
    """포획 단계"""
    
    res = catch_monster(stdscr) 
    if res:
        return True
    
    # 적 스킬 랜덤 선택
    display_status(stdscr, True)  # 상태 출력
    enemyCSmon_skill = enemyskill()
    skillstep_enemy(stdscr, None, enemyCSmon_skill)  # 적 스킬 사용
    get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌
    return False  # 포획 실패

    # 포획 시도

''' 종합 '''
def drop_item(stdscr):
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
    display_status(stdscr)
    addstr_with_korean_support(stdscr, 17, 0, f"  {droppedtem.name}을/를 획득했다!")
    get_ch_with_sound(stdscr)

    # 아이템을 슬롯에 추가
    for i in range(len(player.items)):
        if player.items[i].name == "빈 슬롯":
            player.items[i] = copy.deepcopy(droppedtem)
            break
    else:
        # 아이템 슬롯이 가득 찼을 때
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, "  그러나 아이템 슬롯이 가득 차있다!")
        get_ch_with_sound(stdscr)
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  버릴 아이템을 선택하자!")
        get_ch_with_sound(stdscr)
        # 몬스터 교체
        selected_item = select_item(stdscr, droppedtem)
        if selected_item == -1:
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  {droppedtem.name}의 획득을 포기했다.")
            get_ch_with_sound(stdscr)
        else:
            display_status(stdscr)
            addstr_with_korean_support(stdscr, 17, 0, f"  {player.items[selected_item].name}을/를 버렸다!")
            player.items[selected_item] = droppedtem  # 교체된 아이템으로 변경 
            get_ch_with_sound(stdscr)

def exp_gain(stdscr):
    """경험치 획득"""
    # 현재 전산몬(nowCSmon)에 대한 처리 먼저 수행
    mymon = player.nowCSmon
    monnum = player.csMons.index(mymon)
    max_level = max(player.csMons, key=lambda x: x.level).level
    enemyCSmon.drop_exp = int(enemyCSmon.drop_exp * max(1, enemyCSmon.level-max_level))  # 적 경험치 조정
    if mymon.level >= mymon.get_monster_max_level(battleturn):
        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}은/는 이미 레벨 제한에 도달했다.")
        get_ch_with_sound(stdscr)
    else:
        if mymon.participated == False:  # 전투에 참여하지 않은 경우
            exp = int(enemyCSmon.drop_exp * player.concentration * player.knowhow / 10000)
        else:
            exp = int(enemyCSmon.drop_exp * player.knowhow / 100)
            for ev in enemyCSmon.giving_EV:
                mymon.EV[ev] =+ 1

        display_status(stdscr)
        addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {exp}의 경험치를 얻었다!")
        mymon.exp += exp
        get_ch_with_sound(stdscr)
        if mymon.exp >= mymon.max_exp:
            if mymon.level < mymon.get_monster_max_level(battleturn):
                Level_up()
                evocheck = mymon.level_up(battleturn)
                if evocheck == True:
                    evolution(stdscr, mymon, monnum, True)
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!")
                get_ch_with_sound(stdscr)
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
                        evolution(stdscr, mymon, monnum, False)
                    display_status(stdscr)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 {mymon.level}레벨로 올랐다!")
                    get_ch_with_sound(stdscr)
                else:
                    mymon.exp = 0

def evolution(stdscr, mymon, monnum, isnowCSmon):
    """진화"""
    display_status(stdscr)
    addstr_with_korean_support(stdscr, 17, 0, f"  {mymon.name}이/가 진화하려고 한다!")
    get_ch_with_sound(stdscr)
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
    display_status(stdscr)
    addstr_with_korean_support(stdscr, 17, 0, f"  {tempmon.name}이/가 {mymon.name}으로 진화했다!")
    get_ch_with_sound(stdscr)

def battle(getplayer, getenemy, turn, endturn):
    global battleturn, player, enemy, enemyCSmon
    battleturn = turn
    player = getplayer
    enemy = getenemy
    if isinstance(enemy, Monster):
        enemyCSmon = enemy
    else:
        enemyCSmon = enemy.nowCSmon
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
            stop_music()
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
            for mymon in player.csMons:
                mymon.update_fullreset()
            play_music("../music/bossbattle.wav")
            
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
            curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_CYAN)  # 엔딩 화면
            curses.init_pair(8, curses.COLOR_RED, curses.COLOR_CYAN)  # 엔딩 화면2
            # type list: 데이터 과학 / 시스템-네트워크 / 전산이론 / 소프트웨어디자인 / 시큐어컴퓨팅 / 비주얼컴퓨팅 / 인공지능-정보서비스 / 소셜컴퓨팅 / 인터랙티브컴퓨팅

            curses.init_pair(21, curses.COLOR_BLACK, curses.COLOR_WHITE)  # 전산이론-하양
            curses.init_pair(22, curses.COLOR_BLACK, curses.COLOR_RED)  # 데이터 과학-빨강
            curses.init_pair(23, curses.COLOR_WHITE, curses.COLOR_BLUE)  # 시스템-네트워크-파랑
            curses.init_pair(24, curses.COLOR_WHITE, curses.COLOR_GREEN)  # 소프트웨어디자인-초록
            curses.init_pair(25, curses.COLOR_BLACK, curses.COLOR_CYAN)  # 시큐어컴퓨팅1
            curses.init_pair(26, curses.COLOR_BLACK, curses.COLOR_WHITE)  # 시큐어컴퓨팅2-청회
            curses.init_pair(27, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # 비주얼컴퓨팅-자홍
            curses.init_pair(28, curses.COLOR_BLACK, curses.COLOR_RED)  # 인공지능-정보서비스1
            curses.init_pair(29, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # 인공지능-정보서비스2-주황
            curses.init_pair(30, curses.COLOR_BLACK, curses.COLOR_CYAN)  # 소셜컴퓨팅-하늘
            curses.init_pair(31, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # 인터랙티브컴퓨팅-노랑

            curses.init_pair(99, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 흰색
            curses.curs_set(0)  # 커서를 숨김
            global hap_num, player, enemy, enemyCSmon
            hap_num = 1
            display_status(stdscr, detail=True)  # 초기 상태 출력
            if isinstance(enemy, Monster):
                addstr_with_korean_support(stdscr, 17, 0, f"  앗! 야생의 {enemyCSmon.name}이/가 나타났다!")
            else:
                addstr_with_korean_support(stdscr, 17, 0, f"  앗!{enemy.Etype} {enemy.name}이/가 싸움을 걸어왔다!")
                get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌
                display_status(stdscr, detail=True)  # 상태 출력
                addstr_with_korean_support(stdscr, 17, 2, battleScript[enemy.Etype], curses.color_pair(2))
                get_ch_with_sound(stdscr)  # 메시지를 잠시 보여줌
                display_status(stdscr, detail=True)  # 상태 출력
                addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.Etype} {enemy.name}은/는 {enemyCSmon.name}을/를 꺼냈다!")
            get_ch_with_sound(stdscr)
            for mymon in player.csMons:
                mymon.participated = False  # 전투 참여 여부 초기화
            
            while True:
                curses.flushinp()  # 입력 버퍼 비우기
                player.nowCSmon.participated = True  # 현재 전산몬 참여 표시
                if player.nowCSmon.nowhp < player.nowCSmon.HP*0.35:
                    HP_low()
                """ 행동 선택"""
                action = select_action(stdscr)
                # 스킬
                if action == 0:
                    esc = skill_phase(stdscr)
                    if esc == -1:
                        continue
                # 교체
                elif action == 1:
                    esc = swap_phase(stdscr)
                    if esc == -1:
                        continue
                # 아이템 사용
                elif action == 2:
                    if not any(i.name != "빈 슬롯" for i in player.items):
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  아이템이 없다!")
                        get_ch_with_sound(stdscr)
                    else:
                        esc = item_phase(stdscr)
                        if esc == -1:
                            continue
                # 포획
                elif action == 3:
                    if isinstance(enemy, Player):
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  다른 학생의 전산몬은 포획할 수 없다!")
                        get_ch_with_sound(stdscr)
                        continue
                    if enemyCSmon.grade == "보스":
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  보스는 포획할 수 없다!")
                        get_ch_with_sound(stdscr)
                        continue
                    if enemyCSmon.grade == "중간 보스" and enemyCSmon.nowhp>enemyCSmon.HP*0.5:
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  체력 보호막이 남은 중간보스는 포획할 수 없다!")
                        get_ch_with_sound(stdscr)
                        continue
                    res = catch_phase(stdscr)
                    if res:
                        return True
                # 도망
                elif action == 4:
                    if isinstance(enemy, Player):
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  다른 학생과의 전투에서는 도망칠 수 없다!")
                        get_ch_with_sound(stdscr)
                    else:
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  도망쳤다!")
                        get_ch_with_sound(stdscr)
                    return False
                
                """종료여부 확인"""
                # 적 생존 여부 확인
                if enemyCSmon.is_alive() == False:
                    display_status(stdscr, detail=True)
                    addstr_with_korean_support(stdscr, 17, 0, f"  적 {enemyCSmon.name}이/가 쓰러졌다!")
                    get_ch_with_sound(stdscr)
                    exp_gain(stdscr)
                    if isinstance(enemy, Player):
                        if not any(m.dictNo != -1 and m.is_alive() for m in enemy.csMons):
                            display_status(stdscr, detail=True)
                            addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.Etype} {enemy.name}은 더 이상 교체할 전산몬이 없다.")
                            get_ch_with_sound(stdscr)
                            display_status(stdscr, detail=True)
                            addstr_with_korean_support(stdscr, 17, 2, LoseScript[enemy.Etype], curses.color_pair(2))
                            get_ch_with_sound(stdscr)
                            return True
                        enemy.nowCSmon = random.choice([m for m in enemy.csMons if m.is_alive() and m.dictNo != -1])
                        enemyCSmon = enemy.nowCSmon
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  {enemy.Etype} {enemy.name}은/는 {enemyCSmon.name}을/를 꺼냈다!")
                        get_ch_with_sound(stdscr)

                    else:
                        return True
                # 플레이어 현 전산몬 생존 여부 확인
                if player.nowCSmon.is_alive() == False:
                    display_status(stdscr, detail=True)
                    addstr_with_korean_support(stdscr, 17, 0, f"  {player.nowCSmon.name}이/가 쓰러졌다!")
                    get_ch_with_sound(stdscr)

                    # 살아있는 전산몬이 있는지 확인
                    if not any(m.dictNo != -1 and m.is_alive() for m in player.csMons):
                        display_status(stdscr, detail=True)
                        addstr_with_korean_support(stdscr, 17, 0, f"  더 이상 교체할 전산몬이 없다.")
                        get_ch_with_sound(stdscr)
                        return False

                    # 교체 가능한 전산몬이 있으면 교체
                    swap_phase(stdscr, must_swap=True)
                
                # 전투 턴 증가
                hap_num += 1
        
        battle_result = battle_logic(stdscr)
        
        if turn == endturn:
            stop_music()
            stdscr.clear()
            stdscr.refresh()
            time.sleep(2)
            if enemyCSmon.grade == "보스":
                player.gpa = f"{(4.3*(enemyCSmon.HP-enemyCSmon.nowhp)/enemyCSmon.HP):.2f}"
            gpa = float(player.gpa)
            player.grade = "A+" if gpa >= 4.3 else "A" if gpa >= 4.0 else "A-" if gpa >= 3.7 else "B+" if gpa >= 3.3 else "B" if gpa >= 3.0 else "B-" if gpa >= 2.7 else "C+" if gpa >= 2.3 else "C" if gpa >= 2.0 else "C-" if gpa >= 1.7 else "D+" if gpa >= 1.3 else "D" if gpa >= 1.0 else "D-" if gpa >= 0.7 else "F"
            if player.grade == "A+" or player.grade == "A" or player.grade == "A-":
                color = 1
            elif player.grade == "B+" or player.grade == "B" or player.grade == "B-":
                color = 2
            elif player.grade == "C+" or player.grade == "C" or player.grade == "C-":
                color = 3
            elif player.grade == "D+" or player.grade == "D" or player.grade == "D-":
                color = 4
            else:
                color = 5

            def center_print(text):
                toprint = text
                lentoprint = 0
                for i, char in enumerate(text):
                    lentoprint += 1
                    if unicodedata.east_asian_width(char) in ['F', 'W']:
                        lentoprint += 1
                addstr_with_korean_support(stdscr, 14, 60-lentoprint//2, toprint)
                return lentoprint
            
            center_print(f"졸업 연구가 끝났다.")
            get_ch_with_sound(stdscr)

            play_music("../music/ending.wav")
            stdscr.clear()
            center_print(f"{player.name}은/는 최종 학점 {player.gpa}로 졸업했다.")
            get_ch_with_sound(stdscr)

            stdscr.clear()
            xx = center_print(f"{player.name}의 최종 성적: {player.grade}")
            addstr_with_korean_support(stdscr, 14, 60-xx//2+xx-len(f"{player.grade}"), f"{ player.grade}", curses.color_pair(color))
            get_ch_with_sound(stdscr)

            stdscr.clear()
            picture = "⡨⠢⡑⢌⠆⡕⢌⠆⡕⢌⠢⡑⡐⢅⠢⠡⢂⢂⠢⢂⠅⡢⢂⢂⢂⠢⡂⢆⢂⢂⠄⢐⠠⠑⠄⠕⢌⠢⡑⢔⠡⠂⡂⠄⠠⠄⠄⠠⠠⠄⢂⠠⠄⡂⡐⢐⢐⢐⢅⠂⢆⢂⠪⢐⠐⢅⢂⠪⠐⢌⢂⠪⡐⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑\n⠜⢌⠌⡆⠕⡌⡢⢱⠨⠢⡑⢌⢂⠢⠡⢑⢐⠐⠅⡢⢑⠨⡂⡢⢡⢑⢌⠢⡑⡐⢅⠢⡂⢅⢅⠣⡡⡑⢌⢂⠂⢅⢀⠂⠠⠁⠌⠄⠅⠨⠄⠄⢂⠂⡂⣔⣦⡽⠖⠅⢅⠂⢅⠢⢑⢐⠐⠅⠅⢕⠠⡑⠄⢕⠨⡨⢂⠕⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢜⠨⡨⢌\n⢊⢪⢨⢘⢌⠢⡑⡑⡌⡪⢐⠅⡂⡊⢌⠐⠄⢅⢑⢐⠅⡪⡐⡌⢆⢕⠰⡡⠣⡑⢅⠕⡌⠆⡆⢕⠰⡨⢂⠢⡑⡐⠄⠅⠅⢅⠅⡅⠅⠅⠅⡊⡐⡨⢐⠜⢕⠨⢊⠌⡢⠡⡑⠨⡐⠄⢅⠅⠕⡐⡁⡂⡑⠄⢕⠨⡂⢅⠅⢕⠨⡂⠕⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢\n⡡⡱⡐⢕⢐⠅⢕⠡⡂⡪⢐⠅⡢⠨⢐⠨⡈⡢⢑⠔⡑⢔⢌⢌⠆⢆⠣⡊⡪⡘⢔⠱⡘⡌⡌⡢⡑⢌⠢⡑⢌⠢⡑⠅⢕⠡⠪⡐⢅⠣⡑⡐⢅⠌⣲⣅⠕⡨⠐⢌⢐⠡⢂⠅⡂⢅⢑⠨⠨⢐⢐⠐⠌⢌⠂⢅⠪⡐⠅⢕⠨⡂⢕⠡⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑⢌⠢⡑\n⢔⢑⢌⢢⠡⡑⢅⠕⡨⢂⢑⠌⡐⠡⢂⢂⢂⢊⠢⡑⢌⠆⢆⠕⢌⠢⡱⢨⠢⡑⡅⡣⡑⡌⡢⡑⢌⠆⡃⣊⠢⡑⢌⢊⢢⢑⠕⢌⢢⠱⡨⡨⢂⣿⣿⣿⢈⠢⠡⠡⡂⠌⡂⢌⢐⠐⠄⢅⢑⠐⠄⢅⢑⢐⢅⢑⠌⡢⠡⡑⡐⢌⢐⠌⡢⢑⢌⢐⠅⡪⢐⠅⠪⡐⢅⠪⠨⠢⡑⢌\n⢊⢆⠕⠔⡅⢕⢑⠌⡢⢑⠄⢕⠨⠨⢐⢐⠐⢅⠕⢌⠆⡣⡑⢌⠆⠕⢌⠢⡑⡑⢌⢢⠱⡨⠢⡑⢅⠥⡑⢔⢑⠌⢆⢕⢑⢌⢪⢘⢔⢑⠔⢬⣾⣿⣷⠟⠄⠅⢅⢑⠄⢅⢂⢂⠢⠡⡁⡂⠢⠡⡑⡰⢐⠅⡂⡢⢑⢈⢂⠢⠨⡐⡐⢌⠐⢅⢂⠢⢑⠨⡐⠌⡊⠔⡐⠅⢕⠑⢌⠢\n⡱⠰⡑⠕⡌⡢⠢⡑⠌⡂⢕⠐⢌⢐⠐⠄⠅⠕⢌⠢⡑⢔⠸⡐⢕⠩⡢⡑⠔⢌⠢⡡⢱⠨⢪⠨⡢⡑⢌⠆⡅⡣⡱⡐⢕⢌⢢⢑⠔⢅⢕⣿⡿⣯⣿⠨⡊⢌⠢⢂⠪⢐⢐⢐⠨⢐⠐⠌⢌⠪⡐⢌⣦⡵⣈⠢⡁⡂⡢⢑⢑⢐⠌⠄⢅⠑⠄⠅⠅⡊⠔⡡⠨⡂⠪⠨⡂⢅⠕⡨\n⠜⡌⡪⡘⡐⢌⠪⡐⢅⠪⠠⡑⡐⡐⠨⡈⡪⢘⠄⠕⢌⠢⡃⡪⡂⢇⠢⠪⡘⢔⢑⠌⢆⠣⡡⠱⡐⢜⢐⠕⢌⢆⠪⡨⠢⡊⡢⡡⡑⡑⣾⣿⢿⠟⢅⠕⡈⡂⠅⠅⡊⠔⡐⡐⠌⠄⠅⡑⡐⣅⣺⣿⣿⣷⡢⡁⡂⠢⠨⢐⠐⠅⠌⢌⢐⠨⠨⡈⠢⡈⡂⠪⡐⠌⢌⠪⡐⠅⡊⠔\n⢊⢆⢊⠢⡡⡑⠨⡐⡐⠡⡑⡐⡐⢄⢑⢐⠌⡢⢡⣷⣷⣳⣾⣶⣎⠢⠣⡑⢌⠢⡡⡑⢅⢕⢘⢌⢊⢢⢑⢅⠣⡂⡣⠪⠨⡂⡊⡢⡑⡑⢝⠕⣂⠣⡑⢌⠐⠌⠌⡂⠌⡂⢂⠂⠅⡊⡐⡐⣾⢿⣟⣿⣾⣿⣇⠂⠌⠌⡨⠠⠡⠡⢑⢐⢐⢈⠢⡈⡂⢆⢊⢌⣦⡕⢅⠊⢔⠡⢊⠌\n⡱⡐⢅⢕⠰⡈⡂⡢⢈⢂⢂⢂⢂⢂⠢⢑⠨⣶⣿⣿⣟⣿⣟⣿⣿⠨⡑⢌⠢⡑⢔⠅⡕⡰⢑⢌⢊⠆⡕⢔⢑⠌⡢⠑⢅⠢⢑⠰⡨⡊⡢⡑⢔⢑⢌⠐⠌⠌⡐⠄⠅⢂⢂⠡⢁⢂⢂⠢⣿⣿⣿⢿⣻⣾⣿⡌⠌⡐⠄⠅⡊⠌⡐⡐⡐⡐⢅⠢⢊⠔⠠⣽⡟⡳⡑⢌⢂⠪⡐⠅\n⠰⡨⡂⢆⠕⡐⢔⠨⢐⢐⢐⢐⠐⠄⡑⠄⣿⣟⣯⣷⣿⣿⣟⣿⣟⡇⡪⢐⢑⠌⢆⠕⢌⢌⠆⢕⢌⢊⢢⢑⠔⡑⠌⠌⡂⢌⠢⡑⠔⢌⠢⡊⡢⡑⢄⠅⠅⠅⡂⠅⡊⢐⠠⢊⠔⡐⠄⠅⣿⣿⣾⣿⣿⣿⣻⢁⠂⡂⠅⡂⢂⠅⡂⡢⢑⠌⡂⡑⠄⠅⢅⠭⢑⠌⢌⢂⠢⡑⡐⢅\n⠨⡂⠪⡐⡑⢌⢂⠪⢐⢐⣠⣦⣾⣶⣶⢁⣿⣿⡿⣿⣿⣽⣿⣟⡟⡐⠌⡢⠡⡑⡑⢌⢢⠡⡑⡑⠔⡅⢕⠔⢅⠊⠌⡂⡂⡂⡂⡪⠨⡂⠕⢌⠢⡊⡢⠡⠡⡁⡂⠅⡐⠄⡑⡐⢅⠢⠡⠡⡙⢿⣯⣿⣿⣾⣿⠔⠨⢐⠐⢄⢑⠌⢔⢨⣦⣬⣴⣬⣬⣈⠢⡊⠔⡨⢂⠪⡐⢌⠢⠡\n⢈⢂⠑⠌⢌⠢⡑⠌⣂⣶⣟⣿⣯⣿⣿⠠⢸⣿⡿⣿⣯⣿⣾⠏⡲⣿⣇⢊⠌⠢⠡⡑⢔⠡⡡⡑⢕⢘⢔⢑⠅⢕⣡⣦⣦⡂⠪⡐⠅⢌⠌⡂⡑⡐⢌⠪⡈⡂⡂⠅⡂⠅⠢⡈⡂⠅⢅⢑⢐⢐⠨⠩⡘⠫⡐⠌⡪⠐⢅⢑⠄⠕⠄⠕⢿⣿⢿⣿⢿⣿⣷⣔⠡⠨⡂⢅⠢⡑⠌⢌\n⢐⠠⠡⠑⢄⢑⢐⢥⣿⣷⣿⣿⣻⣽⡿⡈⡢⡑⢍⠪⠨⡉⡢⢁⠂⠇⡂⠂⠅⠅⠕⡈⡢⢑⠌⢜⢐⢑⢐⠅⣅⣽⣿⣟⣿⡿⠨⢐⠡⢑⠨⡐⠌⠌⡂⠕⡐⠌⠢⡑⠨⡈⡂⢂⠂⡑⡐⡐⡐⠄⠡⠡⢈⠂⡂⠅⠂⠅⡂⠂⠌⡐⠡⢁⢿⣿⡿⣿⡿⣿⣾⣿⣷⡑⠄⢕⠐⠌⠌⡂\n⠐⠄⠅⠌⠔⡐⡡⣿⣿⣽⣾⣿⢿⠫⠨⡂⡢⢊⠔⡡⢑⠌⡐⠄⠅⠡⠄⠅⡁⠅⠅⡂⡊⡢⡑⢅⠪⢐⠡⢪⣾⣿⣯⣿⣿⡇⠌⡂⠌⡐⡐⠠⢁⢂⠢⢑⠨⡈⡂⠌⡐⠄⢂⠂⢂⠂⡂⡢⢂⠅⠅⠌⠄⢂⠐⡈⠄⠡⡠⢡⠁⠄⡑⢐⠠⢛⢿⣿⡿⣿⣯⣷⣿⣿⠌⡂⠅⠅⠕⠨\n⠨⢊⠌⠌⢌⢐⢘⠟⢏⢛⢙⠍⣆⢅⢃⠆⡪⢐⠡⢊⠔⠡⡂⠅⠌⠠⠁⡂⢐⠨⠐⢌⠢⡂⠪⢐⠨⠠⡑⣽⣿⣿⣽⣿⣾⠇⠅⡂⠅⡂⡐⠡⡂⠢⡑⠄⢅⠂⡂⠡⠐⡈⠄⠨⠄⢌⠐⠌⢔⠨⠂⠅⢌⢐⠨⠐⡈⠢⣱⢱⠈⡐⡀⡂⠌⡐⡐⡉⠫⢛⠡⢑⠡⢁⢂⢂⠅⠅⠅⠅\n⠨⠐⡈⠌⠄⢂⠢⡈⡂⡢⢂⢊⠝⡳⠞⢌⠢⡁⡪⢐⠨⢐⠠⠑⡈⠄⠡⠐⡐⡈⠌⡐⠌⠌⢌⢐⠨⠐⣐⣿⣿⣾⣿⣯⠟⡈⡂⡂⢅⠢⠨⠨⡂⠕⡐⡑⠄⠅⢂⠁⣑⢆⠨⡀⠅⠂⠌⠌⡐⡨⠨⠨⡐⠐⡈⢐⠠⠡⢱⡳⡐⡐⠠⠂⠅⡂⠢⠨⢈⢐⠈⠄⠨⢐⠠⡑⠨⠨⠨⠨\n⠄⠅⢐⠠⡁⡂⡂⡂⡪⢐⠡⡂⢕⠨⡨⠢⡱⡐⢌⠔⡨⢐⠠⢁⠂⠌⢌⢐⢐⠠⠂⡂⠡⢁⢂⠂⢌⠐⠌⡋⠷⠟⡁⡂⠔⡐⡐⠌⡐⠨⠨⡈⡂⠅⡂⠂⠌⡐⠠⢂⢸⡪⡐⡐⢈⠌⠌⡂⠢⠨⡈⡂⡂⠡⠐⡀⠂⠌⡐⡵⡱⡨⡌⠨⠐⡀⠅⠨⢀⠂⢌⠨⢈⢒⢜⠄⠅⡊⠌⠌\n⠄⠅⡀⢂⡇⡢⢂⠢⠨⡂⢅⠪⠠⡑⢌⢸⢜⢞⠰⡡⢂⠢⠨⢐⠨⡈⡂⢂⠐⡀⠡⠐⠈⠄⡂⠌⡂⢅⢑⠨⠨⠸⡀⡂⠅⡂⢂⠅⠌⢌⠌⢔⢆⠡⡐⠡⢁⠂⠅⠢⢸⡪⡐⢐⠐⠨⢐⠨⡈⡂⡂⡐⠄⠅⡂⠄⠅⢥⣶⣗⢮⠪⢂⢁⢂⠐⡈⠌⡐⢈⠄⠂⡂⢌⣾⡮⢐⠠⠡⠡\n⠠⢁⢐⡲⣕⠆⡑⠌⡂⡪⠐⠌⢌⢂⢂⢪⡳⡍⠍⡂⠅⠌⢌⠐⢌⢐⠐⡀⠂⡀⢂⠈⠌⡐⠐⡅⡂⡂⡂⠅⠅⣅⢂⠄⠅⢂⠂⠌⠌⡂⠌⣸⢐⢘⠠⢁⠂⠌⡈⠌⢸⣮⣐⠠⠈⠌⡐⢐⠐⡐⠠⠂⠅⡡⠠⠡⢈⣾⣿⣮⣗⠅⠂⡀⢂⠐⡐⢐⠄⡂⠨⠐⣼⣯⣿⣻⡔⠠⠡⢈\n⠈⢄⢂⠏⡂⠌⡐⠡⢂⠊⠌⠌⡂⢂⠂⣮⡮⣦⣅⢂⠡⠨⠠⢑⢐⠐⠐⡀⠡⠄⡂⠌⡐⠄⠅⡯⡂⢔⠠⢁⢪⢿⡔⠈⠌⡐⠨⡈⡂⡂⡥⣼⣢⠔⢁⢐⠠⠁⡐⠈⣸⣿⡾⣕⣌⡐⡐⢐⠐⡈⠨⢈⠐⡀⠂⣦⣿⣿⣾⣻⣿⣄⠂⢂⠐⡀⢂⠂⠌⠂⣵⡽⣮⢷⣻⣽⣽⠠⡁⠢\n⢐⡐⡜⠄⢂⠡⠈⠌⠄⠅⡡⠁⠔⡀⢪⣿⣿⣿⣿⣆⠄⠡⢈⢤⠰⣈⠠⠐⢀⠡⠐⡀⠂⠌⠠⣹⡪⠂⠌⡀⡾⣽⣿⢌⠐⠨⢐⠐⠔⣨⣻⣳⡗⠨⠠⠐⠄⢂⠄⡂⢸⣿⣟⣷⣻⣿⢾⡄⢂⠐⣈⠠⠐⠄⡁⣿⣿⣷⣿⣿⣽⣿⣎⢄⠢⠬⢦⡂⠅⡡⣿⢯⣿⣟⣯⣿⣽⡐⠨⡈\n⣿⣿⢿⣔⡀⢂⠁⠅⠨⠐⡀⠅⠂⠄⣽⣿⣿⣿⣿⣿⡀⠌⡌⢤⣇⠠⢣⡂⠄⠂⠐⡀⠡⢈⠐⣷⢕⡁⢂⠠⠈⠛⠩⠁⠌⠨⠄⠌⢄⣗⣗⣿⣿⣐⠐⡈⢀⠂⠠⠐⠈⢿⣿⣽⡽⣟⣿⣟⠊⢄⣄⠝⢆⠁⠄⣿⣿⣾⣿⣿⣯⣿⣿⢧⠡⡭⡆⠪⣷⡐⢻⣿⢷⣿⣟⣯⣿⡎⡐⢐\n⣿⣽⡿⡟⢒⠠⠈⠠⠁⢂⠄⢂⠁⢄⣿⣽⣾⣿⣿⣿⡃⣼⡦⡖⡔⣬⡺⠣⠐⠈⠠⠐⠄⢂⣞⡯⣗⣧⢥⠚⡑⢈⠄⡁⠄⢩⠂⣅⢾⣺⣾⣻⣿⣿⣷⠄⡖⡔⠄⠂⠁⢿⣿⢿⣟⣿⣿⡳⢅⢪⢨⢀⢊⠂⡂⣿⣾⣿⣿⣾⣿⣿⣿⣿⣵⢲⢒⠡⠑⠄⠩⣿⣟⣯⣿⣿⢿⡧⠐⠠\n⣿⣯⣿⠠⠲⣑⠈⠠⠈⡀⠐⢀⠐⢿⢿⣿⣿⣿⣿⣿⠈⠉⠉⠉⠈⠘⠙⠉⠂⢁⠐⢈⣖⣷⢵⣟⡽⣪⢿⣻⣶⣶⠛⠚⢍⢎⣪⣾⣿⣿⣾⣯⣿⣿⣿⢉⡢⡸⣞⢴⡱⡪⡿⣿⣿⢿⡝⠈⡀⠈⢀⠁⠁⠁⣖⣿⣿⣿⣿⣿⣽⣿⣷⠁⡉⠁⢀⢐⠠⣑⣵⣿⣿⣟⣿⣟⢋⠡⢈⠐\n⣿⣟⠷⠙⠹⣼⠔⠄⠂⢀⠈⢀⠄⡈⢿⣯⣷⣿⣿⣮⣐⠄⡂⠡⠂⠄⢦⣷⣧⣀⠂⣺⣽⣿⣗⣗⣯⣞⣵⣽⣾⠿⢀⠠⠄⣅⠑⣿⣷⣿⣿⡷⣿⣿⡟⠈⠺⠽⠸⡱⡓⢳⢯⢿⣿⣿⡳⢅⠢⡑⡔⠆⡐⡨⠩⡻⣿⣯⣷⣿⣿⡿⣿⣔⢔⢅⢂⢢⢱⣻⣿⣿⣿⣟⣿⠃⡀⡂⢂⠈\n"
            x, y = 10, 1
            for i, str in enumerate(picture):
                if str == "\n":
                    y += 1
                    x = 10
                    continue
                stdscr.addstr(y, x, str, curses.color_pair(7))
                x += 1
                
            picture2 = "         ⣀⣀⣰⣆⣀⣀    ⣤⣤⣤⣤⣤⣤⡄ ⣠⣤⣤⣄ ⢠⡄   ⣀⣀⣀⣦⣀⣀⡀         \n         ⣠⠟⠁ ⠹⢆    ⠰⠏ ⡄⠈⠷  ⣯  ⣹⠒⢺⡇   ⢠⡞⠁ ⠙⢦⡀         \n        ⠐⠒⠒⢲⡖⠒⠒⠒  ⠘⣛⣛⣛⣛⣛⣛⡛ ⣉⠛⠛⠉ ⢘⡃  ⠐⠒⠒⠒⡶⠒⠒⠒         \n         ⠛⠛⠛⠛⠛⢻    ⣶⠶⠶⠶⠶⠾⠇ ⣺⠒⠒⠒⠒⢺⡇   ⠛⠛⠛⠛⠛⢻⡇         \n              ⠈    ⠉⠉⠉⠉⠉⠉⠁ ⠈⠉⠉⠉⠉⠉         ⠈⠁         "
            x=34
            y=1
            for i, str in enumerate(picture2):
                if str == "\n":
                    y += 1
                    x = 34
                    continue
                stdscr.addstr(y, x, str, curses.color_pair(8))
                x += 1
            get_ch_with_sound(stdscr)

            return hap_num
        # 전투 결과에 따라 승리 또는 패배 처리
        elif battle_result:
            # 전투에서 승리한 경우
            display_status(stdscr)
            Battle_win()
            addstr_with_korean_support(stdscr, 17, 0, f"  승리했다!")
            get_ch_with_sound(stdscr)

            # 아이템 드랍
            drop_item(stdscr)

            # 경험치 획득
            for mymon in player.csMons:    
                if turn % 5 == 0:
                    mymon.update_fullreset()
                else: mymon.update()
            if turn % 5 == 0:
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 2, f"포켓몬들이 모두 회복했다!")
                get_ch_with_sound(stdscr)
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  공부에 노하우가 생겼다! 경험치 획득량이 60% 증가했다.")
                player.knowhow *= 1.60
                get_ch_with_sound(stdscr)
            if turn % 10 == 0:
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  영어 강의에 익숙해졌다! 전투에 참여하지 않은 전산몬도 경험치를 20% 추가 획득한다.")
                player.concentration *= 1.20
                get_ch_with_sound(stdscr)
        else:
            # 전투에서 패배한 경우
            if player.gameover():
                stop_music()
                display_status(stdscr)
                addstr_with_korean_support(stdscr, 17, 0, f"  눈 앞이 깜깜해졌다...")
                get_ch_with_sound(stdscr)
        
        # 전투 턴 수 반환
        return hap_num
    
    return curses.wrapper(winOrLose)