from game_menu import *

def set(music_volume, music_on, effectsound, ESVolume, difficulty):
    def option_menu(music_volume, music_on, effectsound, ESVolume, difficulty):
        # pygame 초기화 및 화면 설정
        init_pygame_screen()  # screen이 None이어도 강제로 초기화
        
        # 이제 screen을 가져와서 사용
        from game_menu import screen
        
        clock = pygame.time.Clock()
        current_index = 0
        running = True
        
        while running:
            # 화면 지우기 (흰색 배경)
            screen.fill(WHITE)
            if music_on:
                if pygame.mixer.music.get_busy() == 0:
                    play_music("../music/menu.wav")
            else:
                stop_music()
                if pygame.mixer.music.get_busy() == 1:
                    pygame.mixer.music.stop()
            
            # 타이틀 그리기
            draw_text(screen, "환경 설정", SCREEN_WIDTH // 2 - 72, 180, BLACK)
            
            options = [[f" 음악 ", f"{' 켜기 ' if music_on else ' 끄기 '}"], 
                       [f" 볼륨 ", f"{music_volume}".center(6)], 
                       [f"효과음", f"{' 켜기 ' if effectsound else ' 끄기 '}"], 
                       [f" 볼륨 ", f"{ESVolume}".center(6)],
                       [f"난이도", f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"]]
            
            # 옵션들 그리기
            for i, option in enumerate(options):
                y_pos = 404 + i * 60
                x_pos1 = SCREEN_WIDTH // 2 - 200
                x_pos2 = SCREEN_WIDTH // 2 + 120
                
                if i == current_index:
                    draw_text(screen, f"{option[0]}", x_pos1, y_pos, WHITE, BLACK)  # 하이라이트
                    draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
                else:
                    draw_text(screen, f"{option[0]}", x_pos1, y_pos, BLACK)
                    draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
            
            pygame.display.flip()
            
            # 이벤트 처리
            select = wait_for_key()
            if select == None:
                return music_volume, music_on, effectsound, ESVolume, difficulty
            elif select == 'escape':
                option_escape_sound()
                return music_volume, music_on, effectsound, ESVolume, difficulty
            elif select == 'up' and (current_index > 0 and current_index < len(options)):
                option_change_sound()
                current_index -= 1
            elif select == 'down' and (current_index >= 0 and current_index < len(options) - 1): 
                option_change_sound()
                current_index += 1
            elif select == 'enter':  # Enter 키를 누르면 선택 완료
                setting_mode = True
                while setting_mode:
                    # 화면 다시 그리기
                    draw_text(screen, "환경 설정", SCREEN_WIDTH // 2 - 72, 180, BLACK)
                    
                    options = [[f" 음악 ", f"{' 켜기 ' if music_on else ' 끄기 '}"], 
                            [f" 볼륨 ", f"{music_volume}".center(6)], 
                            [f"효과음", f"{' 켜기 ' if effectsound else ' 끄기 '}"], 
                            [f" 볼륨 ", f"{ESVolume}".center(6)],
                            [f"난이도", f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"]]
                    
                    # 옵션들 그리기
                    for i, option in enumerate(options):
                        y_pos = 404 + i * 60
                        x_pos1 = SCREEN_WIDTH // 2 - 200
                        x_pos2 = SCREEN_WIDTH // 2 + 120
                        
                        if i == current_index:
                            draw_text(screen, f"{option[0]}", x_pos1, y_pos, WHITE, BLACK)  # 하이라이트
                            draw_text(screen, f"{option[1]}", x_pos2, y_pos, WHITE, BLACK)
                        else:
                            draw_text(screen, f"{option[0]}", x_pos1, y_pos, BLACK)
                            draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
                    
                    pygame.display.flip()
                    sub_event = wait_for_key()
                    if sub_event == None:
                        running = False
                        setting_mode = False
                        return music_volume, music_on, effectsound, ESVolume, difficulty  
                    elif sub_event == 'escape' or sub_event == 'enter':
                        option_select_sound()
                        setting_mode = False
                    else: 
                        val = 1
                        if sub_event == 'left':
                            if   current_index == 0: music_on = False
                            elif current_index == 1: music_volume = max(0, music_volume - 1)
                            elif current_index == 2: effectsound = False
                            elif current_index == 3: ESVolume = max(0, ESVolume - 1)
                            elif current_index == 4:
                                if difficulty <= 0:
                                    val = 0
                                    continue
                                difficulty -= 1
                                options[4][1] = f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"
                        elif sub_event == 'right':
                            if   current_index == 0: music_on = True
                            elif current_index == 1: music_volume = min(100, music_volume + 1)
                            elif current_index == 2: effectsound = True
                            elif current_index == 3: ESVolume = min(100, ESVolume + 1) 
                            elif current_index == 4:
                                if difficulty >= 2:
                                    val = 0
                                    continue
                                difficulty += 1
                                options[4][1] = f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"
                        elif sub_event == 'up':
                            if    current_index == 1: music_volume = min(100, music_volume + 10)
                            elif  current_index == 3: ESVolume = min(100, ESVolume + 10)
                            else: val = 0
                        elif sub_event == 'down':
                            if    current_index == 1: music_volume = max(0, music_volume - 10)
                            elif  current_index == 3: ESVolume = max(0, ESVolume - 10)
                            else: val = 0
                        if val: option_change_sound()
                        
    return option_menu(music_volume, music_on, effectsound, ESVolume, difficulty)