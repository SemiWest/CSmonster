@echo off
:: 배치 파일 시작

:: 현재 디렉터리를 배치 파일이 위치한 디렉터리로 설정
cd /d "%~dp0"

:: Python 설치 여부 확인
echo Python 설치 여부를 확인 중입니다...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python이 설치되어 있지 않습니다. 설치를 진행합니다...
    start https://www.python.org/downloads/
    echo Python 설치 후 다시 실행해주세요.
    pause
    exit
)

:: Git 설치 여부 확인
echo Git 설치 여부를 확인 중입니다...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git이 설치되어 있지 않습니다. 설치를 진행합니다...
    start https://git-scm.com/download/win
    echo Git 설치 후 다시 실행해주세요.
    pause
    exit
)

:: GitHub에서 최신 파일 가져오기
echo 최신 파일을 GitHub에서 가져오는 중입니다...
git pull origin main
if %errorlevel% neq 0 (
    echo GitHub에서 파일을 가져오는 데 실패했습니다. 저장소가 올바르게 설정되었는지 확인하세요.
    pause
    exit
)

:: Python 패키지 설치
echo 필요한 Python 패키지를 설치 중입니다...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Python 패키지 설치에 실패했습니다. pip가 올바르게 설정되었는지 확인하세요.
    pause
    exit
)

:: 게임 실행
echo 게임을 실행합니다...
python main.py

:: 종료 대기
pause