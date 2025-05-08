from battle import *
from player import *
from game_menu import *
import option
import csv

Me = player()
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

def save_game_log_csv(filename, player, turn, totalhap):
    """플레이 기록을 CSV 형식으로 저장"""
    # 절대 경로 생성
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 디렉터리
    filepath = os.path.join(base_dir, filename)  # 절대 경로로 파일 생성

    file_exists = os.path.isfile(filepath)  # 파일 존재 여부 확인

    with open(filepath, 'a', newline='', encoding='utf-8') as file:  # filepath 사용
        writer = csv.writer(file)
        
        # 파일이 없을 경우 헤더 작성
        if not file_exists:
            header = ["플레이어 이름", "클리어 여부", "졸업 GPA/최종 스테이지", "총 전투 횟수"]
            for i in range(len(player.csMons)):
                header.append(f"전산몬{i+1}")
                header.append(f"전산몬{i+1} 레벨")
                header.append(f"전산몬{i+1} 스테이지")
            writer.writerow(header)
        
        # 플레이어 데이터 작성
        clear_status = "클리어" if turn > 30 else "제적"
        gpa_or_stage = player.gpa if turn > 30 else turn
        row = [player.name, clear_status, gpa_or_stage, totalhap]
        
        for mymon in player.csMons:
            if mymon.name != "빈 슬롯":
                row.append(mymon.name)
                row.append(mymon.level)
                row.append(mymon.stage)
            else:
                row.append("빈 슬롯")
                row.append("")
                row.append("")
        
        writer.writerow(row)

def limited_turn_mode(turn, totalhap, Me, music_volume=50, music_on=True, endturn = 100):
    # 배경음악 재생 시작
    play_music(["../music/Im_a_kaist_nonmelody.wav", "../music/Im_a_kaist_melody.wav"])
    while turn <= endturn:
        if turn == endturn:
            # 졸업 연구
            met_monster = copy.deepcopy(graudation)
        elif turn <= 10:
            # 1~10 스테이지
            meetable_monsters = []
            for i in range(100):
                if i<40: meetable_monsters.append(monsters["프밍기"])
                elif i<70: meetable_monsters.append(monsters["데이타구조"])
                elif i<100: meetable_monsters.append(monsters["이산구조"])
                
            met_monster = wild_monster(meetable_monsters)
            met_monster.level = random.randint(met_monster.get_monster_max_level(turn)-8, 
                                               (met_monster.get_monster_max_level(turn) + max(-8, (turn%10-11))))
            met_monster.stage = turn
            if turn % 10 == 0:
                met_monster.level = met_monster.get_monster_max_level(turn)
                met_monster.grade = "중간 보스"
                met_monster.hpShield = True
            met_monster.update_fullhp()
        else:
            meetable_monsters = []
            for i in range(100):
                if i<40: meetable_monsters.append(monsters["프밍기"])
                elif i<65: meetable_monsters.append(monsters["데이타구조"])
                elif i<90: meetable_monsters.append(monsters["이산구조"])
                elif i<100: meetable_monsters.append(monsters["시프"])
                
            met_monster = wild_monster(meetable_monsters)
            met_monster.level = random.randint(met_monster.get_monster_max_level(turn)-8, 
                                               (met_monster.get_monster_max_level(turn) + max(-8, (turn%10-11))))
            met_monster.stage = turn
            if turn % 10 == 0:
                met_monster.level = met_monster.get_monster_max_level(turn)
                met_monster.grade = "중간 보스"
                met_monster.hpShield = True
            met_monster.update_fullhp()
            
        battlehap = battle(Me, met_monster, turn, endturn)
        if battlehap == 0:
            turn = 1
            totalhap = 0
            continue
        totalhap += battlehap
        # 전투 종료 후 몬스터 상태 업데이트
        # 몬스터가 쓰러진 상태라면 게임오바
        if Me.gameover():
            break
        turn += 1
    stop_music()
    clear_screen()
    sys.stdin.flush()    
    print("게임 결과\n")
    if turn >= endturn:
        print("클리어")
        print("\n졸업 GPA: ", Me.gpa, "졸업 성적: ", Me.grade)
    else:
        print("제적당하고 말았다...")           
        print("\n최종 스테이지:", turn)
    print("총 전투 횟수:", totalhap)

    print("\n나의 전산몬스터: ")
    for mymon in Me.csMons:
        if mymon.name != "빈 슬롯":
            print(f"{mymon.name} lv{mymon.level} 잡은 스테이지: {mymon.stage}")

    save_game_log_csv("game_log.csv", Me, turn, totalhap)
    sys.stdin.flush()
    input("\n아무 키나 눌러 종료")

os.system(f'mode con: cols={120} lines={30}')
os.system(f"title 전산몬스터")

print("\n\n\n\n\n\n\n\n\n\nF11키를 눌러 전체화면으로 전환해주세요.")
print("폰트 설정: D2coding, 폰트 크기: 36")
print("조작키 정보: 방향키로 조작, enter키로 선택, esc키/q키/backspace키로 종료 및 취소")
print("스크립트 넘기기: 아무 키나 누르기")
input("\n\n아무 키나 눌러 시작")

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
        turn = 0
        totalhap = 0
        Me.name = "Unknown"
        Me.csMons = [
            copy.deepcopy(monsters["프밍기"]), 
            copy.deepcopy(monsters["빈 슬롯"]), 
            copy.deepcopy(monsters["빈 슬롯"]), 
            copy.deepcopy(monsters["빈 슬롯"]), 
            copy.deepcopy(monsters["빈 슬롯"]), 
            copy.deepcopy(monsters["빈 슬롯"])
            ]
        Me.items = [
            copy.deepcopy(items["빈 슬롯"]),
            copy.deepcopy(items["빈 슬롯"]),
            copy.deepcopy(items["빈 슬롯"]),
            copy.deepcopy(items["빈 슬롯"]),
            copy.deepcopy(items["빈 슬롯"]),
            copy.deepcopy(items["빈 슬롯"])
            ]
        while True:
            newname = input("이름을 입력하세요: ")
            if len(newname) > 10:
                print("이름은 10자 이내로 입력해주세요.")
            elif len(newname) < 1:
                print("이름을 입력해주세요.")
            else:
                Me.name = newname
                break
        
        Me.nowCSmon = Me.csMons[0]
        clear_screen()
        limited_turn_mode(turn, totalhap, Me, music_volume, music_on, 2)
    elif start == "기록 보기":
        clear_screen()
        # 절대 경로 생성
        base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 디렉터리
        filepath = os.path.join(base_dir, "game_log.csv")  # 절대 경로로 파일 생성
        file_exists = os.path.isfile(filepath)  # 파일 존재 여부 확인
        if not file_exists:
            print("기록이 없습니다.")
            input("\n아무 키나 눌러 종료")
            clear_screen()
            continue

        print("클리어 기록")
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            clear_count = 1
            for row in reader:
                if row[1] == "클리어":
                    print(f"{clear_count}. {row[0]}\n    졸업 GPA {row[2]}")
                    print("    잡은 전산몬스터")
                    for i in range(4, len(row), 3):
                        if row[i] != "빈 슬롯":
                            print(f"       {row[i].ljust(13-len(row[i]))}lv {row[i+1].ljust(3)}  잡은 스테이지: {row[i+2]}")
                    print()
                    clear_count += 1
        
        input("\n아무 키나 눌러 종료")
        clear_screen()    
    elif start == "무한 모드":
        print("개발중입니당")
        input("아무 키나 눌러 종료")
        clear_screen()
        stop_music()
    elif start == "환경 설정":
        music_volume, music_on, effectsound, ESVolume, difficulty = option.set(music_volume, music_on, effectsound, ESVolume, difficulty)
        change_options(music_on, music_volume, effectsound, ESVolume, effect_channel, music_channel)
        set_difficulty(difficulty)
        pygame.mixer.music.set_volume(music_volume / 100)
        pygame.mixer.Channel(1).set_volume(ESVolume / 100)
        clear_screen()
        if music_on == False and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()            
    elif start == " 제작자  ":
        clear_screen()
        print("\n\n\n\n\n\n\n\n")
        print("\t\t\t\t\t               제작자             ")
        print("\t\t\t\t\t              SemiWest            \n")
        print("\t\t\t\t\t          special thank to        ")
        print("\t\t\t\t\t               eweRim             \n")
        print("\t\t\t\t\t               감사링             ")
        getch = input("아무 키나 눌러 종료")
        clear_screen()
    else:
        clear_screen()
        input("플레이 해주셔서 감삼당\n\n아무 키나 눌러 종료")
        clear_screen()
        break



