from game_menu import *

def set(music_volume, music_on):
    def option_menu(stdscr, music_volume, music_on):
        curses.flushinp()  # Clear input buffer
        curses.noecho()  # Disable automatic echoing of typed characters
        curses.curs_set(0)
        stdscr.keypad(True)
        current_index = 0
        while True:
            stdscr.clear()
            options = [[f"음악", f"{'켜기' if music_on else '끄기'}"], [f"볼륨", f"{music_volume}".center(4)]]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, 12 + i, 54, f"{option[0]}")
                addstr_with_korean_support(stdscr, 12 + i, 62, f"{option[1]}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 12 + i, 54, f"{option[0]}", curses.A_REVERSE)
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('\n'):  # Enter 키를 누르면 선택 완료
                if current_index == 0:
                    while True:
                        addstr_with_korean_support(stdscr, 12, 62, f"{'켜기' if music_on else '끄기'}", curses.A_REVERSE)
                        stdscr.refresh()
                        key = stdscr.getch()
                        if key == ord('\n'):
                            break
                        elif key == curses.KEY_LEFT:
                            music_on = False
                        elif key == curses.KEY_RIGHT:
                            music_on = True
                if current_index == 1:
                    while True:
                        addstr_with_korean_support(stdscr, 13, 62, f"{music_volume}".center(4), curses.A_REVERSE)
                        stdscr.refresh()
                        key = stdscr.getch()
                        if key == ord('\n'):
                            break
                        elif key == curses.KEY_LEFT and music_volume > 0:
                            music_volume -= 1
                        elif key == curses.KEY_RIGHT and music_volume < 100:
                            music_volume += 1
                        elif key == curses.KEY_UP and music_volume < 91:
                            music_volume += 10
                        elif key == curses.KEY_DOWN and music_volume > 9:
                            music_volume -= 10
            elif key == ord('\b'):  # 'q' 키를 누르면 종료
                return music_volume, music_on
            elif key == curses.KEY_UP and (current_index >= 1 and current_index < len(options)):
                current_index -= 1
            elif key == curses.KEY_DOWN and (current_index >= 0 and current_index < len(options) - 1):
                current_index += 1

    return curses.wrapper(option_menu, music_volume, music_on)