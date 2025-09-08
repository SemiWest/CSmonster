from adventure import *
import ForGrd.graduationmode as graduationmode
import option
import argparse
from logging_setup import init_logging
from typing import NamedTuple

# 명령줄 인수 파서 생성
parser = argparse.ArgumentParser(description="게임 실행 옵션")
parser.add_argument('--debug', action='store_true', help="디버그 모드 활성화")
parser.add_argument('--cheat', action='store_true', help="게임 시작 시 치트 모드 활성화")
parser.add_argument('--damage', type=str, default='True', help="디버그 모드에서 데미지 적용 여부 (True/False)")
parser.add_argument('--skip', action='store_true', help="Tab키로 현재 전투 스킵 활성화")
parser.add_argument('--log', action='store_true', default=True, help="로깅 활성화 (기본값: True)")
parser.add_argument('--log-level', type=str, default='DEBUG', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="로깅 레벨 설정 (기본값: DEBUG)")
parser.add_argument('--log-file', type=str, default='logs/game.log', help="로그 파일 경로 (기본값: logs/game.log)")
parser.add_argument('--log-stdout', action='store_true', help="표준 출력으로 로그 출력")
parser.add_argument('--no-log', action='store_true', help="로깅 완전히 비활성화")


# 인수 파싱
args = parser.parse_args()

# 로깅 시스템 초기화 (--no-log가 있으면 비활성화)
enable_logging = args.log and not args.no_log
init_logging(
    enable_logging=enable_logging,
    log_level=args.log_level,
    log_file=args.log_file if enable_logging else None,
    log_stdout=args.log_stdout
)
logger = logging.getLogger(__name__)

# DebugConfig 데이터 클래스
class DebugConfig(NamedTuple):
    debug: bool
    damage: bool
    skip: bool

# 파싱된 값으로 변수 설정
debug_mode = args.debug
cheat_mode_on_start = args.cheat # 게임 시작 시 치트 모드 활성화 여부
damage_str = args.damage.lower() if args.damage else 'true'
damage_bool = damage_str == 'true'

# 디버그 설정 생성
debug_config = DebugConfig(debug=debug_mode, damage=damage_bool, skip=args.skip)

music_volume = 50
music_on = True
ESVolume = 90
effectsound = True
difficulty = 1

def initialize_channels():
    """음악과 효과음을 위한 채널 초기화"""
    global music_channel, effect_channel, effect_channel_alt
    pygame.mixer.init()
    music_channel = pygame.mixer.Channel(0)  # 채널 0: 음악
    effect_channel = pygame.mixer.Channel(1)  # 채널 1: 효과음
    effect_channel_alt = pygame.mixer.Channel(2)  # 채널 2: 효과음 대체

# 현재 작업 디렉터리를 Python 파일이 위치한 디렉터리로 설정
os.chdir(os.path.dirname(os.path.abspath(__file__)))
 
def clear_screen():
    # 화면 지우기
    os.system('cls' if os.name == 'nt' else 'clear')

def wild_monster(lists):
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(lists))

initialize_channels()
change_options(music_on, music_volume, effectsound, ESVolume, effect_channel, music_channel, effect_channel_alt)
set_difficulty(difficulty)
pygame.mixer.music.set_volume(music_volume / 100)  # 음악 볼륨 설정
pygame.mixer.Channel(1).set_volume(ESVolume / 100)  # 효과음 볼륨 설정
pygame.mixer.Channel(2).set_volume(ESVolume / 100)  # 효과음 대체 볼륨 설정

if logger.isEnabledFor(logging.INFO):
    logger.info("게임 시작")

while True:   
    clear_screen()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("메인 메뉴 표시")
    result = main_menu()
    if result == False:
        if logger.isEnabledFor(logging.INFO):
            logger.info("게임 종료")
        break
    start, screen = result
    if logger.isEnabledFor(logging.INFO):
        logger.info(f"모드 선택: {start}")
    if   start == "졸업 모드":
        stop_music()
        if logger.isEnabledFor(logging.INFO):
            logger.info("졸업 모드 시작")
        Me = graduationmode.game_start(screen, debug_config=debug_config)

    elif start == "기록 보기":
        if logger.isEnabledFor(logging.INFO):
            logger.info("기록 보기 화면 진입")
        from game_menu import show_deans_list_from_notion
        show_deans_list_from_notion(player=None)  # 플레이어 객체 있으면 넘기기
        clear_screen()
    
    # elif start == "모험 모드":
    #     stop_music()
    #     if logger.isEnabledFor(logging.INFO):
    #         logger.info("모험 모드 시작")
    #     Me = game_start(screen, 50)
    
    elif start == "환경 설정":
        if logger.isEnabledFor(logging.INFO):
            logger.info("환경 설정 진입")
        music_volume, music_on, effectsound, ESVolume, difficulty = option.set(music_volume, music_on, effectsound, ESVolume, difficulty)
        change_options(music_on, music_volume, effectsound, ESVolume, effect_channel, music_channel, effect_channel_alt)
        set_difficulty(difficulty)
        pygame.mixer.music.set_volume(music_volume / 100)
        pygame.mixer.Channel(1).set_volume(ESVolume / 100)
        clear_screen()
        if music_on == False and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()            
    
    elif start == "스태프 롤":
        if logger.isEnabledFor(logging.INFO):
            logger.info("스태프 롤 화면 진입")
        from game_menu import show_credits
        show_credits()

    # elif start == " *도움말 ":
    #     if logger.isEnabledFor(logging.INFO):
    #         logger.info("도움말 화면 진입")
    #     from game_menu import show_help
    #     show_help()

    else:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("알 수 없는 메뉴 선택으로 게임 종료")
        break



