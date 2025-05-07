import subprocess
import sys
try:
    import curses
except ImportError:    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "windows-curses"])
    import curses
import unicodedata
from player import *

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


def main_menu():
    def menu_logic(stdscr):
        # Initialize the curses screen
        stdscr = curses.initscr()
        curses.flushinp()  # Clear input buffer
        curses.noecho()  # Disable automatic echoing of typed characters
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.clear()

        # Set up colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        # Main menu loop
        current_index = 0
        while True:
            stdscr.clear()
            
            stdscr.addstr(5, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ⢰⣶⠒⡖⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
            stdscr.addstr(6, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ⢸⣿⠀⡇⣿⡇⢠⡖⠒⠒⣦⠀⣶⠤⠒⢲⡄⢠⣶⠒⠒⠦⠄⢺⣿⠒⠂⠀⢠⣴⣒⣒⣦⡄⣶⡦⠒⢲⣦")
            stdscr.addstr(7, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ⢸⣿⠀⡇⣿⡇⢸⡇⠀⠀⣿⠀⣿⠀⠀⢸⡇⢈⣛⠒⠒⣦⡄⢸⣿⠀⢀⣀⢸⣿⠉⠉⣉⡁⣿⡇⠀⠈⠉")
            stdscr.addstr(8, 5, "⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀⠀⠀⠻⣇⠤⠤⠤⠤⠤⠤⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ⠘⠛⠀⠃⠛⠃⠀⠛⠛⠛⠃⠀⠛⠀⠀⠘⠃⠀⠛⠛⠛⠃⠀⠀⠘⠛⠛⠀⠀⠘⠛⠛⠃⠀⠛⠃⠀⠀⠀")
            stdscr.addstr(5, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ", curses.color_pair(1))
            stdscr.addstr(6, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ", curses.color_pair(1))
            stdscr.addstr(7, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ", curses.color_pair(1))
            stdscr.addstr(8, 5, "⠸⠧⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⢿⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⢿⣇⣀⣀⣀⣀⣀⣀⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ", curses.color_pair(1))
            stdscr.addstr(5, 27, "⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀  ")
            stdscr.addstr(6, 27, "⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀     ")
            stdscr.addstr(7, 27, "⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀    ")
            stdscr.addstr(8, 27, "⠀⠻⠧⠤⠤⠤⠤⠤⠤⠄⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⠿⠇⠀     ")
            stdscr.addstr(5, 4, " ⠉⠉⣿⡏⠉⠁ ⢸⣿    ⣿⡇   ⣿⡇⠀⠀", curses.color_pair(1))
            stdscr.addstr(6, 4, " ⣠⡴⠛⠳⣤⡈⠉⢹⣿  ⣀⡴⠛⠳⢦⡀ ⣿⡏⠉⠁", curses.color_pair(1))
            stdscr.addstr(7, 4, " ⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀", curses.color_pair(1))
            stdscr.addstr(8, 4, " ⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀", curses.color_pair(1))
            options = ["졸업 모드", "기록 보기", "무한 모드", " 제작자  ", "환경 설정"]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, 16 + int(i // 2) * 2, 20 * (i % 2) + 44, f"  {option}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 16 + int(i // 2) * 2, 20 * (i % 2) + 44, f"> {option}", curses.A_REVERSE)

            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('\n'):  # Enter 키를 누르면 선택 완료
                return options[current_index]
            elif key == ord('\b'):  # 'q' 키를 누르면 종료
                return False
            elif key == curses.KEY_UP and (current_index > 1 and current_index < len(options)):
                current_index -= 2
            elif key == curses.KEY_DOWN and (current_index >= 0 and current_index < len(options) - 2):
                current_index += 2
            elif key == curses.KEY_LEFT and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
                current_index -= 1
            elif key == curses.KEY_RIGHT and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options) - 1):
                current_index += 1

    return curses.wrapper(menu_logic)
