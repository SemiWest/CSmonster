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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return music_volume, music_on, effectsound, ESVolume, difficulty
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Enter 키를 누르면 선택 완료
                        option_select_sound() 
                        if current_index == 4:  # 난이도 설정
                            setting_mode = True
                            while setting_mode:
                                # 화면 다시 그리기
                                screen.fill(WHITE)
                                draw_text(screen, "환경 설정", SCREEN_WIDTH // 2 - 100, 100, BLACK)
                                
                                for i, option in enumerate(options):
                                    y_pos = 300 + i * 60
                                    x_pos1 = SCREEN_WIDTH // 2 - 200
                                    x_pos2 = SCREEN_WIDTH // 2
                                    
                                    if i == current_index:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, WHITE, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, WHITE, BLACK)  # 설정 중인 값도 하이라이트
                                    else:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
                                
                                pygame.display.flip()
                                
                                # 난이도 설정 이벤트 처리
                                for sub_event in pygame.event.get():
                                    if sub_event.type == pygame.QUIT:
                                        running = False
                                        setting_mode = False
                                        return music_volume, music_on, effectsound, ESVolume, difficulty
                                    elif sub_event.type == pygame.KEYDOWN:
                                        if sub_event.key == pygame.K_RETURN:
                                            option_select_sound()
                                            setting_mode = False
                                        elif sub_event.key == pygame.K_LEFT and difficulty > 0:
                                            option_change_sound()
                                            difficulty -= 1
                                            options[4][1] = f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"
                                        elif sub_event.key == pygame.K_RIGHT and difficulty < 2:
                                            option_change_sound()
                                            difficulty += 1
                                            options[4][1] = f"{' 이지 ' if difficulty == 0 else ' 노말 ' if difficulty == 1 else ' 하드 '}"
                                clock.tick(60)
                                
                        elif current_index % 2 == 0:  # 음악/효과음 ON/OFF 설정
                            setting_mode = True
                            if current_index == 0:
                                onoff = music_on
                            elif current_index == 2:
                                onoff = effectsound
                            
                            while setting_mode:
                                # 화면 다시 그리기
                                screen.fill(WHITE)
                                draw_text(screen, "환경 설정", SCREEN_WIDTH // 2 - 100, 100, BLACK)
                                
                                # 현재 설정값 업데이트
                                if current_index == 0:
                                    options[0][1] = f"{' 켜기 ' if onoff else ' 끄기 '}"
                                elif current_index == 2:
                                    options[2][1] = f"{' 켜기 ' if onoff else ' 끄기 '}"
                                
                                for i, option in enumerate(options):
                                    y_pos = 300 + i * 60
                                    x_pos1 = SCREEN_WIDTH // 2 - 200
                                    x_pos2 = SCREEN_WIDTH // 2
                                    
                                    if i == current_index:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, WHITE, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, WHITE, BLACK)  # 설정 중인 값도 하이라이트
                                    else:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
                                
                                pygame.display.flip()
                                
                                # ON/OFF 설정 이벤트 처리
                                for sub_event in pygame.event.get():
                                    if sub_event.type == pygame.QUIT:
                                        running = False
                                        setting_mode = False
                                        return music_volume, music_on, effectsound, ESVolume, difficulty
                                    elif sub_event.type == pygame.KEYDOWN:
                                        if sub_event.key == pygame.K_RETURN:
                                            option_select_sound()
                                            setting_mode = False
                                        elif sub_event.key == pygame.K_LEFT:
                                            option_change_sound()
                                            onoff = False
                                        elif sub_event.key == pygame.K_RIGHT:
                                            option_change_sound()
                                            onoff = True
                                
                                clock.tick(60)
                            
                            # 설정값 저장
                            if current_index == 0:
                                music_on = onoff
                            elif current_index == 2:
                                effectsound = onoff
                                
                        elif current_index % 2 == 1:  # 볼륨 설정
                            setting_mode = True
                            if current_index == 1:
                                volume = music_volume
                            elif current_index == 3:
                                volume = ESVolume

                            while setting_mode:
                                # 화면 다시 그리기
                                screen.fill(WHITE)
                                draw_text(screen, "환경 설정", SCREEN_WIDTH // 2 - 100, 100, BLACK)
                                
                                # 현재 설정값 업데이트
                                if current_index == 1:
                                    options[1][1] = f"{volume}".center(6)
                                elif current_index == 3:
                                    options[3][1] = f"{volume}".center(6)
                                
                                for i, option in enumerate(options):
                                    y_pos = 300 + i * 60
                                    x_pos1 = SCREEN_WIDTH // 2 - 200
                                    x_pos2 = SCREEN_WIDTH // 2
                                    
                                    if i == current_index:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, WHITE, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, WHITE, BLACK)  # 설정 중인 값도 하이라이트
                                    else:
                                        draw_text(screen, f"{option[0]}", x_pos1, y_pos, BLACK)
                                        draw_text(screen, f"{option[1]}", x_pos2, y_pos, BLACK)
                                
                                pygame.display.flip()
                                
                                # 볼륨 설정 이벤트 처리
                                for sub_event in pygame.event.get():
                                    if sub_event.type == pygame.QUIT:
                                        running = False
                                        setting_mode = False
                                        return music_volume, music_on, effectsound, ESVolume, difficulty
                                    elif sub_event.type == pygame.KEYDOWN:
                                        if sub_event.key == pygame.K_RETURN:
                                            option_select_sound()
                                            setting_mode = False
                                        elif sub_event.key == pygame.K_LEFT and volume > 0:
                                            option_change_sound()
                                            volume -= 1
                                        elif sub_event.key == pygame.K_RIGHT and volume < 100:
                                            option_change_sound()
                                            volume += 1
                                        elif sub_event.key == pygame.K_UP and volume < 91:
                                            option_change_sound()
                                            volume += 10
                                        elif sub_event.key == pygame.K_DOWN and volume > 9:
                                            option_change_sound()
                                            volume -= 10
                                
                                clock.tick(60)
                            
                            # 설정값 저장
                            if current_index == 1:
                                music_volume = volume
                            elif current_index == 3:
                                ESVolume = volume

                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE or event.key == pygame.K_q:  # 'q' 키를 누르면 종료
                        option_escape_sound()
                        return music_volume, music_on, effectsound, ESVolume, difficulty
                    elif event.key == pygame.K_UP and (current_index >= 1 and current_index < len(options)):
                        option_change_sound()
                        current_index -= 1
                    elif event.key == pygame.K_DOWN and (current_index >= 0 and current_index < len(options) - 1):
                        option_change_sound()
                        current_index += 1
            
            clock.tick(60)

    return option_menu(music_volume, music_on, effectsound, ESVolume, difficulty)