from playsound import *
from player import *

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

# 전역 변수로 screen을 선언하되 초기화는 하지 않음
screen = None
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
font = None

def init_pygame_screen():
    """pygame 화면을 초기화하는 함수"""
    global screen, font
    if screen is None:
        # pygame 초기화 (playsound에서 이미 초기화되었는지 확인)
        if not pygame.get_init():
            pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("전산몬스터")
        
        # 폰트 설정
        font = pygame.font.Font("../neodgm.ttf", 32)

def load_title_image():
    """타이틀 이미지를 로드하는 함수"""
    # 상대경로로 이미지 로드
    image = pygame.image.load("../img/전산몬스터.PNG")
    # 이미지 크기 조정 (화면 크기에 맞게)
    image_width = SCREEN_WIDTH # 화면 너비의 절반 또는 600px 중 작은 값
    image_height = int(image.get_height() * (image_width / image.get_width()))
    image = pygame.transform.scale(image, (image_width, image_height))
    return image

def create_flash_effect(surface, intensity):
    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flash_surface.fill(BLACK)
    flash_surface.set_alpha(intensity)
    surface.blit(flash_surface, (0, 0))

def draw_text(surface, text, x, y, color=BLACK, highlight=False):
    """pygame 화면에 텍스트를 그리는 함수""" 
    font_obj = font
    
    if highlight:
        # 하이라이트된 텍스트는 배경색을 추가
        text_surface = font_obj.render(text, True, color, highlight)
    else:
        text_surface = font_obj.render(text, True, color)
    
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(topleft=(x, y))


def main_menu():
    def menu_logic():
        init_pygame_screen()
        main_menu_reload = True
        clock = pygame.time.Clock()
        
        def main_menu_animation():
            """메인 메뉴 애니메이션 - 타이틀 이미지가 떨어지고 플래시 효과"""
            title_image = load_title_image()
            # 애니메이션 파라미터
            image_rect = title_image.get_rect()
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            start_y = -image_rect.height  # 화면 위쪽에서 시작
            end_y = center_y - image_rect.height * 0.7 # 화면 중앙보다 조금 위
            
            # 총 애니메이션 프레임 수 (일정한 속도로 떨어짐)
            total_frames = 61
            for frame in range(total_frames):
                # 화면 지우기 (흰색 배경)
                screen.fill(WHITE)
                # 일정한 속도로 떨어지는 애니메이션
                current_y = start_y + frame**2 * (end_y - start_y)/3600
                image_x = center_x - image_rect.width // 2
                # 이미지 그리기
                screen.blit(title_image, (image_x, current_y))
                
                pygame.display.flip()
                clock.tick(60)  # 60 FPS
                
                # 이벤트 처리 (애니메이션 중 종료 가능)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
            
            # 중앙 도달 시 플래시 효과와 게임 시작 사운드
            create_flash_effect(screen, 255)  # 플래시 효과
            game_started()  # 게임 시작 사운드 재생
            
            # 2초 정적 (이미지만 표시)
            pygame.time.wait(3000)
                    
        # Main menu loop
        current_index = 0
        running = True
        
        while running:
            if main_menu_reload:
                main_menu_animation()
                main_menu_reload = False
            
            if musicOnOff:
                if pygame.mixer.music.get_busy() == 0:
                    play_music("../music/menu.wav")
            else:
                stop_music()
                if pygame.mixer.music.get_busy() == 1:
                    pygame.mixer.music.stop()
            
            # 화면 지우기 (흰색 배경)
            screen.fill(WHITE)
            
            # 타이틀 이미지를 배경으로 그리기
            title_image = load_title_image()
            image_rect = title_image.get_rect()
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            image_x = center_x - image_rect.width // 2
            image_y = center_y - image_rect.height * 0.7  # 조금 위쪽에 배치
            screen.blit(title_image, (image_x, image_y))
            
            # 메뉴 옵션들
            options = ["졸업 모드", "기록 보기", "모험 모드", " 제작자  ", "환경 설정", " 도움말  "]
            
            # 메뉴 옵션들을 2x3 격자로 배치
            for i, option in enumerate(options):
                x = 516 * (i % 2) + center_x - 376  # 2열 배치
                y = int(i // 2) * 60 + SCREEN_HEIGHT * 0.6  # 이미지 아래쪽에 배치
                
                if i == current_index:
                    draw_text(screen, f"> {option}", x, y, WHITE, BLACK)  # 하이라이트는 노란색 배경
                else:
                    draw_text(screen, f"  {option}", x, y, BLACK)  # 일반 텍스트는 검은색
            
            pygame.display.flip()
            
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Enter 키
                        option_select_sound()
                        main_menu_reload = True
                        return options[current_index]
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q or event.key == pygame.K_BACKSPACE:
                        option_escape_sound()
                        return False
                    elif event.key == pygame.K_UP and current_index > 1:
                        option_change_sound()
                        current_index -= 2
                    elif event.key == pygame.K_DOWN and current_index < len(options) - 2:
                        option_change_sound()
                        current_index += 2
                    elif event.key == pygame.K_LEFT and current_index % 2 == 1:
                        option_change_sound()
                        current_index -= 1
                    elif event.key == pygame.K_RIGHT and current_index % 2 == 0 and current_index != len(options) - 1:
                        option_change_sound()
                        current_index += 1
            
            clock.tick(60)  # 60 FPS
    
    return menu_logic()
