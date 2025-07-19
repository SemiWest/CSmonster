from adventure import *
import ForGrd.graduationmode as graduationmode
import option
import csv
import sys

music_volume = 50
music_on = True
ESVolume = 90
effectsound = True
difficulty = 1

def initialize_channels():
    """음악과 효과음을 위한 채널 초기화"""
    global music_channel, effect_channel
    pygame.mixer.init()
    music_channel = pygame.mixer.Channel(0)  # 채널 0: 음악
    effect_channel = pygame.mixer.Channel(1)  # 채널 1: 효과음

# 현재 작업 디렉터리를 Python 파일이 위치한 디렉터리로 설정
os.chdir(os.path.dirname(os.path.abspath(__file__)))
 
def clear_screen():
    # 화면 지우기
    os.system('cls' if os.name == 'nt' else 'clear')

def wild_monster(lists):
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(lists))

def Adventure_mode(endturn = 100):
    return game_start(endturn)

def graduation_mode():
    return graduationmode.game_start()
    
initialize_channels()
change_options(music_on, music_volume, effectsound, ESVolume, effect_channel, music_channel)
set_difficulty(difficulty)
pygame.mixer.music.set_volume(music_volume / 100)  # 음악 볼륨 설정
pygame.mixer.Channel(1).set_volume(ESVolume / 100)  # 효과음 볼륨 설정

while True:   
    clear_screen()
    sys.stdin.flush()
    start = main_menu()
    if   start == "졸업 모드":
        stop_music()
        Me = graduation_mode()

    elif start == "기록 보기":
        from game_menu import show_records
        show_records()
        clear_screen()
    elif start == "모험 모드":
        stop_music()
        Me = Adventure_mode(50)
    elif start == "환경 설정":
        music_volume, music_on, effectsound, ESVolume, difficulty = option.set(music_volume, music_on, effectsound, ESVolume, difficulty)
        change_options(music_on, music_volume, effectsound, ESVolume, effect_channel, music_channel)
        set_difficulty(difficulty)
        pygame.mixer.music.set_volume(music_volume / 100)
        pygame.mixer.Channel(1).set_volume(ESVolume / 100)
        clear_screen()
        if music_on == False and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()            
    elif start == "스태프 롤":
        from game_menu import show_credits
        show_credits()
    elif start == " *도움말 ":
        from game_menu import show_help
        show_help()
    else:
        break



