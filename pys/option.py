from game_menu import *

def set(music_volume, music_on, effectsound, ESVolume, difficulty):
    def option_menu(stdscr, music_volume, music_on, effectsound, ESVolume, difficulty):
        curses.flushinp()  # Clear input buffer
        curses.noecho()  # Disable automatic echoing of typed characters
        curses.curs_set(0)
        stdscr.keypad(True)
        current_index = 0
        while True:
            stdscr.clear()
            options = [[f"음악", f"{' 켜기 ' if music_on else ' 끄기 '}"], 
                       [f"볼륨", f"{music_volume}".center(6)], 
                       [f"효과음", f"{' 켜기 ' if effectsound else ' 끄기 '}"], 
                       [f"볼륨", f"{ESVolume}".center(6)],
                       ["난이도", f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"]]
            for i, option in enumerate(options):
                addstr_with_korean_support(stdscr, 11 + 3*(i//2)+i%2, 53, f"{option[0]}")
                addstr_with_korean_support(stdscr, 11 + 3*(i//2)+i%2, 61, f"{option[1]}")
                if i == current_index:
                    addstr_with_korean_support(stdscr, 11 + 3*(i//2)+i%2, 53, f"{option[0]}", curses.A_REVERSE)
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('\n'):  # Enter 키를 누르면 선택 완료
                option_select_sound() 
                if current_index == 4:
                    while True:
                        addstr_with_korean_support(stdscr, 11+(current_index//2)*3+current_index%2, 61, f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}", curses.A_REVERSE)
                        stdscr.refresh()
                        key = stdscr.getch()
                        if key == ord('\n'):
                            option_select_sound()
                            break
                        elif key == curses.KEY_LEFT and difficulty > 0:
                            option_change_sound()
                            difficulty -= 1
                        elif key == curses.KEY_RIGHT and difficulty < 3:
                            option_change_sound()
                            difficulty += 1
                elif current_index % 2 == 0:
                    while True:
                        if current_index == 0:
                            onoff = music_on
                        elif current_index == 2:
                            onoff = effectsound
                        
                        addstr_with_korean_support(stdscr, 11+(current_index//2)*3+current_index%2, 61, f"{' 켜기 ' if onoff else ' 끄기 '}", curses.A_REVERSE)
                        stdscr.refresh()
                        key = stdscr.getch()
                        if key == ord('\n'):
                            option_select_sound()
                            break
                        elif key == curses.KEY_LEFT:
                            option_change_sound()
                            onoff = False
                        elif key == curses.KEY_RIGHT:
                            option_change_sound()
                            onoff = True
                        
                        if current_index == 0:
                            music_on = onoff
                        elif current_index == 2:
                            effectsound = onoff
                elif current_index % 2 == 1:
                    while True:
                        if current_index == 1:
                            volume = music_volume
                        elif current_index == 3:
                            volume = ESVolume

                        addstr_with_korean_support(stdscr, 11+(current_index//2)*3+current_index%2, 61, f"{volume}".center(6), curses.A_REVERSE)
                        stdscr.refresh()
                        key = stdscr.getch()
                        if key == ord('\n'):
                            option_select_sound()
                            break
                        elif key == curses.KEY_LEFT and music_volume > 0:
                            option_change_sound()
                            volume -= 1
                        elif key == curses.KEY_RIGHT and music_volume < 100:
                            option_change_sound()
                            volume += 1
                        elif key == curses.KEY_UP and music_volume < 91:
                            option_change_sound()
                            volume += 10
                        elif key == curses.KEY_DOWN and music_volume > 9:
                            option_change_sound()
                            volume -= 10
                        
                        if current_index == 1:
                            music_volume = volume
                        elif current_index == 3:
                            ESVolume = volume

            elif key == ord('\b') or key == 27 or key == ord("q")   :  # 'q' 키를 누르면 종료
                option_escape_sound()
                return music_volume, music_on, effectsound, ESVolume, difficulty
            elif key == curses.KEY_UP and (current_index >= 1 and current_index < len(options)):
                option_change_sound()
                current_index -= 1
            elif key == curses.KEY_DOWN and (current_index >= 0 and current_index < len(options) - 1):
                option_change_sound()
                current_index += 1

    return curses.wrapper(option_menu, music_volume, music_on, effectsound, ESVolume, difficulty)