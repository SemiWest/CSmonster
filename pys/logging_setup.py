"""
중앙 집중식 로깅 설정 모듈

이 모듈은 게임 전체의 로깅을 설정하고 관리합니다.
"""
import logging
import logging.handlers
import sys
import os
from pathlib import Path


def init_logging(enable_logging=False, log_level='INFO', log_file=None, log_stdout=False):
    """
    로깅 시스템 초기화
    
    Args:
        enable_logging (bool): 로깅 활성화 여부
        log_level (str): 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): 로그 파일 경로 (None이면 파일 로깅 비활성화)
        log_stdout (bool): 표준 출력으로 로그 출력 여부
    """
    if not enable_logging:
        # 로깅이 비활성화된 경우 NullHandler만 설정
        logging.getLogger().addHandler(logging.NullHandler())
        return
    
    # 로그 레벨 설정
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 로그 포매터 설정
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 표준 출력 핸들러 설정
    if log_stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 파일 핸들러 설정
    if log_file:
        # 로그 디렉터리 생성
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 회전 파일 핸들러 사용 (최대 10MB, 최대 5개 파일)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 로깅 시스템 초기화 완료 로그
    logger = logging.getLogger(__name__)
    if logger.isEnabledFor(logging.INFO):
        logger.info(f"로깅 시스템 초기화 완료: 레벨={log_level}, 파일={'활성화' if log_file else '비활성화'}, 표준출력={'활성화' if log_stdout else '비활성화'}")


def get_logger(name):
    """
    모듈별 로거 생성 헬퍼 함수
    
    Args:
        name (str): 로거 이름 (보통 __name__ 사용)
    
    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    return logging.getLogger(name)