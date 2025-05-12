try:
    import pygame
except ImportError:
    os.system(f"{sys.executable} -m pip install pygame")
    import pygame
try:
    import curses
except ImportError:    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "windows-curses"])
    import curses
import subprocess
import sys
import os
import time
import threading
import unicodedata

import pygame

# 전역 변수
musicOnOff = True
musicVolume = 50  # 배경음악 볼륨 기본값 (0 ~ 100)
effectsound = True  # 효과음 기본값
ESVolume = 90  # 효과음 볼륨 기본값 (0 ~ 100)
music_channel = None  # 음악 채널
effect_channel = None  # 효과음 채널
music_thread_running = False  # 음악 스레드 상태

def change_options(BGM, BGMV, ES, ESV, eChannel, mChannel):
    """효과음 옵션 변경"""
    global musicOnOff, musicVolume, effectsound, ESVolume, effect_channel, music_channel
    musicOnOff = BGM
    musicVolume = BGMV
    effectsound = ES
    ESVolume = ESV
    effect_channel = eChannel
    music_channel = mChannel

def play_alternating_music(file_list):
    """두 개 이상의 배경음악을 끊김 없이 번갈아가며 재생"""
    global music_thread_running
    music_thread_running = True

    def music_loop():
        nowfile = 0
        try:
            # 첫 번째 음악 로드 및 재생
            pygame.mixer.music.load(file_list[nowfile])
            pygame.mixer.music.play()
            pygame.mixer.music.queue(file_list[(nowfile+1)%2])
            nowfile = (nowfile + 1) % 2
            #우선 3초 대기
            time.sleep(3)
            i=0
            while music_thread_running:    
                # 이후 초당 10번씩 총 32초, 320번 대기
                time.sleep(0.1)
                i+=1
                if i % 320 == 0:
                    pygame.mixer.music.queue(file_list[(nowfile+1)%2])
                    nowfile = (nowfile + 1) % 2

        except Exception as e:
            print(f"음악 재생 중 오류 발생: {e}")

    # 스레드로 실행
    music_thread = threading.Thread(target=music_loop, daemon=True)
    music_thread.start()

def play_single_music(file_path):
    """단일 배경음악 재생"""
    global music_thread_running
    music_thread_running = True
    def music_loop():
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1)  # 무한 반복 재생
        except Exception as e:
            print(f"음악 재생 중 오류 발생: {e}")
    
    music_thread = threading.Thread(target=music_loop, daemon=True)
    music_thread.start()

def stop_music():
    if musicOnOff and pygame.mixer.music.get_busy():
        """배경음악 정지"""
        global music_thread_running
        music_thread_running = False
        pygame.mixer.music.stop()
    else:
        return

def play_music(file_path):
    if musicOnOff:
        if isinstance(file_path, list):
            # 리스트가 주어지면 번갈아 재생
            play_alternating_music(file_path)
        else:
            # 단일 파일 재생
            play_single_music(file_path)
    else: 
        return

def play_effect(file_path, esp_volume = 100):
    """효과음 재생"""
    global effect_channel, effectsound, ESVolume
    if effectsound:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(ESVolume / esp_volume)  # 볼륨 설정
        effect_channel.play(sound)  # 효과음 재생

def get_ch_with_sound(stdscr):
    stdscr.refresh()
    curses.flushinp()
    stdscr.getch()
    play_effect("../sound/Conv_end.mp3")

def option_select_sound():
    play_effect("../sound/Option_select.mp3")

def option_escape_sound():
    play_effect("../sound/Option_escape.mp3")

def option_change_sound():
    play_effect("../sound/Option_change.mp3")

def catching():

    play_effect("../sound/Catch.mp3", 33)

def caught():
    play_effect("../sound/Catched.mp3")

def Critical():
    play_effect("../sound/Critical.mp3")

def Damage_strong():
    play_effect("../sound/Damage_strong.mp3")

def Damage_weak():
    play_effect("../sound/Damage_weak.mp3")

def HP_low():
    play_effect("../sound/HP_low.mp3", 150)

def Level_up():
    play_effect("../sound/Level_up.mp3")

def Heal():
    play_effect("../sound/Heal.mp3")

def Battle_win():
    play_effect("../sound/Battle_win.mp3")

def game_started():
    play_effect("../sound/Game_start.mp3")

def Lose():
    play_effect("../sound/Lose.mp3")