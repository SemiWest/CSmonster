import pygame
import sys
import os
import time
import threading
import unicodedata

# 전역 변수
musicOnOff = True
musicVolume = 50  # 배경음악 볼륨 기본값 (0 ~ 100)
effectsound = True  # 효과음 기본값
ESVolume = 90  # 효과음 볼륨 기본값 (0 ~ 100)
music_channel = None  # 음악 채널
effect_channel = None  # 효과음 채널
effect_channel_alt = None  # 효과음 채널2
music_thread_running = False  # 음악 스레드 상태

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
LIGHTGRAY = (178, 178, 178)
ORANGE = (255, 165, 0)
LIGHTBLUE = (173, 216, 230)
VIOLET = (238, 130, 238)
PURPLE = (128, 0, 128)
MYMINT = (33, 221, 159)
EWERED = (150, 40, 35)
SOCBLUE = (54, 176, 230)
WONJUN = (230, 214, 41)
JIMIN = (235, 131, 21)
YUNJEONG = (146, 68, 230)
MINBEOM = (86, 173, 41)
SEUNGMIN = (209, 12, 12)
MINHO = (0, 5, 153)
TAK = (204, 86, 204)
KMC = (156, 186, 186)
AIC = (189, 215, 238)
SYSC = (57, 36, 214)
PSC = (152, 235, 96)
DSC = (252, 98, 4)
CTC = (165, 165, 165)
EVENTC = (255, 255, 15)
STARC = (100, 100, 100)
DARKGRAY = (64, 64, 64)

def change_options(BGM, BGMV, ES, ESV, eChannel, mChannel, eChannelAlt):
    """효과음 옵션 변경"""
    global musicOnOff, musicVolume, effectsound, ESVolume, effect_channel, music_channel, effect_channel_alt
    musicOnOff = BGM
    musicVolume = BGMV
    effectsound = ES
    ESVolume = ESV
    effect_channel = eChannel
    effect_channel_alt = eChannelAlt
    music_channel = mChannel

def mute_music(num=0):
    pygame.mixer.music.set_volume(musicVolume * num / 100)
def unmute_music():
    pygame.mixer.music.set_volume(musicVolume / 100)

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

def play_effect_alt(file_path, esp_volume = 100):
    """효과음 재생"""
    global effect_channel_alt, effectsound, ESVolume
    if effectsound:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(ESVolume / esp_volume)  # 볼륨 설정
        effect_channel_alt.play(sound)  # 효과음 재생

def wait_for_key(sound = True, Noescape=False):
    """키 입력 대기 (pygame)"""
    pygame.event.clear()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE:
                    if sound:
                        option_select_sound()
                    return 'enter'
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q or event.key == pygame.K_BACKSPACE:
                    if Noescape:
                        continue
                    return 'escape'
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    return 'up'
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    return 'down'
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    return 'left'
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    return 'right'
                elif event.key == pygame.K_TAB:
                    return 'tab'
        pygame.time.wait(10)

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

def Effective():
    play_effect("../sound/Hit Super Effective.mp3")

def NotEffective():
    play_effect("../sound/Hit Weak Not Very Effective.mp3")

def NormalDamage():
    play_effect("../sound/Hit Normal Damage.mp3")

def HP_low():
    play_effect_alt("../sound/HP_low.mp3", 150)

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

def Report():
    play_effect("../sound/report.mp3", 150)

def RankUp():
    play_effect("../sound/Stat Rise Up.mp3")

def RankDown():
    play_effect("../sound/Stat Fall.mp3")