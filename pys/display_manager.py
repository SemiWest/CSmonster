"""
Display Manager for Window Resizing & Fullscreen

논리적 해상도 1920x1080을 유지하면서 실제 윈도우 크기를 자유롭게 조절할 수 있게 하는 디스플레이 관리자
"""
import pygame
import math
import logging

logger = logging.getLogger(__name__)

LOGICAL_W, LOGICAL_H = 1920, 1080

class DisplayManager:
    def __init__(self, init_size=(1920, 1080)):
        """
        Args:
            init_size (tuple): 초기 윈도우 크기 (width, height)
        """
        self.windowed_size = init_size
        self.fullscreen = False
        self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        self.canvas = pygame.Surface((LOGICAL_W, LOGICAL_H)).convert_alpha()
        
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"DisplayManager 초기화: 윈도우 크기={init_size}, 논리 해상도={LOGICAL_W}x{LOGICAL_H}")

    def handle_event(self, ev):
        """
        윈도우 관련 이벤트 처리 (리사이즈, 풀스크린 토글)
        
        Args:
            ev: pygame event 객체
            
        Returns:
            bool: 이벤트가 처리되었으면 True, 아니면 False
        """
        if ev.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
            if not self.fullscreen:
                # 이벤트에서 크기 정보 추출 (안전한 방식)
                try:
                    new_w = ev.w if hasattr(ev, 'w') else ev.dict.get('w', 800)
                    new_h = ev.h if hasattr(ev, 'h') else ev.dict.get('h', 600)
                except AttributeError:
                    new_w, new_h = 800, 600  # 기본값
                
                # 최소 크기 보장 (1x1 이상)
                new_w, new_h = max(new_w, 1), max(new_h, 1)
                self.windowed_size = (new_w, new_h)
                self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                
                if logger.isEnabledFor(logging.INFO):
                    scale_exact = min(new_w / LOGICAL_W, new_h / LOGICAL_H)
                    use_integer = scale_exact >= 1.0
                    mode = "integer" if use_integer else "fractional"
                    bars = "on" if new_w/new_h != LOGICAL_W/LOGICAL_H else "off"
                    logger.info(f"window resized to {new_w}x{new_h}, scale_exact={scale_exact:.3f}, mode={mode}, bars={bars}")
                
            return True
            
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            self.toggle_fullscreen()
            return True
            
        return False

    def toggle_fullscreen(self):
        """풀스크린 모드 토글"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            if logger.isEnabledFor(logging.INFO):
                logger.info("fullscreen toggled: on")
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f"fullscreen toggled: off, restoring to {self.windowed_size}")
            self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    def begin_frame(self):
        """
        프레임 시작 - 게임 코드가 그릴 논리적 캔버스 반환
        
        Returns:
            pygame.Surface: 1920x1080 논리적 캔버스
        """
        self.canvas.fill((0, 0, 0, 0))  # 투명하게 초기화
        return self.canvas

    def end_frame(self):
        """
        프레임 종료 - 논리적 캔버스를 실제 윈도우에 스케일링하여 표시
        """
        ww, wh = self.window.get_size()
        scale_exact = min(ww / LOGICAL_W, wh / LOGICAL_H)
        
        # 스케일이 너무 작으면 경고
        if scale_exact < 0.1:
            if logger.isEnabledFor(logging.WARNING):
                logger.warning(f"computed scale yields very small display: scale={scale_exact:.3f}")
        
        # 정수 스케일링 우선 (선명한 픽셀 유지)
        use_integer = scale_exact >= 1.0
        if use_integer:
            scale_int = max(1, int(math.floor(scale_exact)))
            sw, sh = LOGICAL_W * scale_int, LOGICAL_H * scale_int
            ox, oy = (ww - sw) // 2, (wh - sh) // 2
            
            # 검은색 레터박스
            self.window.fill((0, 0, 0))
            
            # 정수 배수일 때는 nearest-neighbor로 선명하게
            scaled = pygame.transform.scale(self.canvas, (sw, sh))
            self.window.blit(scaled, (ox, oy))
            
        else:
            # 소수 스케일링: 부드럽게 스케일링 (모아레 방지)
            sw, sh = int(LOGICAL_W * scale_exact), int(LOGICAL_H * scale_exact)
            # 최소 크기 보장
            sw, sh = max(1, sw), max(1, sh)
            ox, oy = (ww - sw) // 2, (wh - sh) // 2
            
            # 검은색 레터박스
            self.window.fill((0, 0, 0))
            
            # 소수 스케일링일 때는 smoothscale로 부드럽게
            scaled = pygame.transform.smoothscale(self.canvas, (sw, sh))
            self.window.blit(scaled, (ox, oy))

        pygame.display.flip()

    def get_logical_size(self):
        """논리적 화면 크기 반환"""
        return (LOGICAL_W, LOGICAL_H)
        
    def get_window_size(self):
        """실제 윈도우 크기 반환"""
        return self.window.get_size()
        
    def is_fullscreen(self):
        """풀스크린 모드 여부 반환"""
        return self.fullscreen