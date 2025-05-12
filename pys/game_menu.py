from playsound import *
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
        main_menu_reload = True
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
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(99, curses.COLOR_WHITE, curses.COLOR_BLACK)
        def main_menu_animation():
            for i in range(169):
                j = 13-int((168-i)**(1/2))
                if j-3>=0:
                    stdscr.addstr(j-3, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ⢰⣶⠒⡖⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
                    stdscr.addstr(j-3, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ", curses.color_pair(1))
                    stdscr.addstr(j-3, 27, "⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀  ")
                    stdscr.addstr(j-3, 4, " ⠉⠉⣿⡏⠉⠁ ⢸⣿    ⣿⡇   ⣿⡇⠀⠀", curses.color_pair(1))
                if j-2>=0:
                    stdscr.addstr(j-2, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ⢸⣿⠀⡇⣿⡇⢠⡖⠒⠒⣦⠀⣶⠤⠒⢲⡄⢠⣶⠒⠒⠦⠄⢺⣿⠒⠂⠀⢠⣴⣒⣒⣦⡄⣶⡦⠒⢲⣦")
                    stdscr.addstr(j-2, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ", curses.color_pair(1))
                    stdscr.addstr(j-2, 27, "⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀     ")
                    stdscr.addstr(j-2, 4, " ⣠⡴⠛⠳⣤⡈⠉⢹⣿  ⣀⡴⠛⠳⢦⡀ ⣿⡏⠉⠁", curses.color_pair(1))
                if j-1>=0:
                    stdscr.addstr(j-1, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ⢸⣿⠀⡇⣿⡇⢸⡇⠀⠀⣿⠀⣿⠀⠀⢸⡇⢈⣛⠒⠒⣦⡄⢸⣿⠀⢀⣀⢸⣿⠉⠉⣉⡁⣿⡇⠀⠈⠉")
                    stdscr.addstr(j-1, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ", curses.color_pair(1))
                    stdscr.addstr(j-1, 27, "⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀    ")
                    stdscr.addstr(j-1, 4, " ⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀", curses.color_pair(1))
                if j>=0:
                    stdscr.addstr(j, 5, "⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀⠀⠀⠻⣇⠤⠤⠤⠤⠤⠤⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ⠘⠛⠀⠃⠛⠃⠀⠛⠛⠛⠃⠀⠛⠀⠀⠘⠃⠀⠛⠛⠛⠃⠀⠀⠘⠛⠛⠀⠀⠘⠛⠛⠃⠀⠛⠃⠀⠀⠀")
                    stdscr.addstr(j, 5, "⠸⠧⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⢿⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⢿⣇⣀⣀⣀⣀⣀⣀⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ", curses.color_pair(1))
                    stdscr.addstr(j, 27, "⠀⠻⠧⠤⠤⠤⠤⠤⠤⠄⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⠿⠇⠀     ")
                    stdscr.addstr(j, 4, " ⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀", curses.color_pair(1))
                stdscr.refresh()
                time.sleep(0.001)
                stdscr.clear()
            #흰색 화면으로 0.1초간 반짝하는 효과
            time.sleep(0.05)
            game_started()
        # Main menu loop
        current_index = 0
        curses.flushinp()  # Clear input buffer
        while True:
            if main_menu_reload:
                main_menu_animation()
                main_menu_reload = False
                time.sleep(2.5)
                curses.flushinp()  # Clear input buffer
            if musicOnOff:
                if pygame.mixer.music.get_busy() == 0:
                    play_music("../music/menu.wav")
            else:
                stop_music()
                if pygame.mixer.music.get_busy() == 1:
                    pygame.mixer.music.stop()
            stdscr.clear()
            stdscr.addstr(10, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ⢰⣶⠒⡖⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
            stdscr.addstr(11, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ⢸⣿⠀⡇⣿⡇⢠⡖⠒⠒⣦⠀⣶⠤⠒⢲⡄⢠⣶⠒⠒⠦⠄⢺⣿⠒⠂⠀⢠⣴⣒⣒⣦⡄⣶⡦⠒⢲⣦")
            stdscr.addstr(12, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ⢸⣿⠀⡇⣿⡇⢸⡇⠀⠀⣿⠀⣿⠀⠀⢸⡇⢈⣛⠒⠒⣦⡄⢸⣿⠀⢀⣀⢸⣿⠉⠉⣉⡁⣿⡇⠀⠈⠉")
            stdscr.addstr(13, 5, "⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀⠀⠀⠻⣇⠤⠤⠤⠤⠤⠤⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ⠘⠛⠀⠃⠛⠃⠀⠛⠛⠛⠃⠀⠛⠀⠀⠘⠃⠀⠛⠛⠛⠃⠀⠀⠘⠛⠛⠀⠀⠘⠛⠛⠃⠀⠛⠃⠀⠀⠀")
            stdscr.addstr(10, 5, "⠉⠉⣿⡏⠉⠁⠀⢸⣿⠀⠀⠀⠀⣿⡇⠀⠀⠀⣿⡇⠀⠀⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⢠⣴⠒⠒⣦⡄⣤⡖⠒⢲⣦ ", curses.color_pair(1))
            stdscr.addstr(11, 5, "⣠⡴⠛⠳⣤⡈⠉⢹⣿⠀⠀⣀⡴⠛⠳⢦⡀⠀⣿⡏⠉⠁⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠛⠧⠤⢤⣄ ", curses.color_pair(1))
            stdscr.addstr(12, 5, "⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣀⡀⣀⡀⠀⢸⣿ ", curses.color_pair(1))
            stdscr.addstr(13, 5, "⠸⠧⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⢿⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⢿⣇⣀⣀⣀⣀⣀⣀⡀⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠛⠛⠛⠃ ", curses.color_pair(1))
            stdscr.addstr(10, 27, "⠀⣿⡏⠉⠉⠉⠉⠉⣿⡇⠀⠀⠀⠀⠀⢰⣶⠀⠀⠀⠀⠀⢰⣶⠒⠒⠒⠂⠀⠀⣿⡇⠀⠀⠀⠀  ")
            stdscr.addstr(11, 27, "⢀⣙⣓⣒⣲⣶⣒⣒⣋⣁⠀⠀⣀⣀⣤⠞⠛⢦⣄⣀⡀⠀⢸⣿⠤⠤⠤⠄⣀⣀⣿⡇⠀     ")
            stdscr.addstr(12, 27, "⠈⣭⡍⠉⠉⠉⠉⠉⠉⠉⠀⠀⠉⠉⠉⠀⠀⠈⠉⠉⠁⠀⢸⣿⠀⠀⠀⠀⠉⠉⣿⡇⠀⠀    ")
            stdscr.addstr(13, 27, "⠀⠻⠧⠤⠤⠤⠤⠤⠤⠄⠀⠠⠤⠤⠤⠤⠤⠤⠤⠤⠤⠀⠘⠻⠤⠤⠟⠃⠀⠀⠿⠇⠀     ")
            stdscr.addstr(10, 4, " ⠉⠉⣿⡏⠉⠁ ⢸⣿    ⣿⡇   ⣿⡇⠀⠀", curses.color_pair(1))
            stdscr.addstr(11, 4, " ⣠⡴⠛⠳⣤⡈⠉⢹⣿  ⣀⡴⠛⠳⢦⡀ ⣿⡏⠉⠁", curses.color_pair(1))
            stdscr.addstr(12, 4, " ⢩⣥⠀⠀⠉⠁⠀⠈⠉⠀⠀⠉⣥⠀⠀⠈⠁⠀⠉⠁⠀⠀", curses.color_pair(1))
            stdscr.addstr(13, 4, " ⠘⠻⠤⠤⠤⠤⠤⠤⠤⠀⠀⠀⠻⠤⠤⠤⠤⠤⠤⠄⠀", curses.color_pair(1))
            options = ["졸업 모드", "기록 보기", "모험 모드", " 제작자  ", "환경 설정", " 도움말  "]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, 18 + int(i // 2) * 2, 20 * (i % 2) + 44, f"  {option}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 18 + int(i // 2) * 2, 20 * (i % 2) + 44, f"> {option}", curses.A_REVERSE)

            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('\n'):  # Enter 키를 누르면 선택 완료
                option_select_sound()
                main_menu_reload = True
                return options[current_index]
            elif key == ord('\b') or key == 27 or key == ord("q"):  # 'q' 키를 누르면 종료
                option_escape_sound()
                return False
            elif key == curses.KEY_UP and (current_index > 1 and current_index < len(options)):
                option_change_sound()
                current_index -= 2
            elif key == curses.KEY_DOWN and (current_index >= 0 and current_index < len(options) - 2):
                option_change_sound()
                current_index += 2
            elif key == curses.KEY_LEFT and (current_index % 2 == 1 and current_index < len(options) and current_index >= 0):
                option_change_sound()
                current_index -= 1
            elif key == curses.KEY_RIGHT and (current_index % 2 == 0 and current_index < len(options) and current_index >= 0 and current_index != len(options) - 1):
                option_change_sound()
                current_index += 1

    return curses.wrapper(menu_logic)
