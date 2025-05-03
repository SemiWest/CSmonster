from battle import *
from player import *
from monster import *
from items import *
from game_menu import *
import random
import copy
import os
import sys
import csv

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

    with open(filename, 'a', newline='', encoding='utf-8') as file:
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

def thirty_turn_mode(turn, totalhap, Me):
    while turn <=30:
        if turn == 30:
            pass
        # 졸업 연구 몬스터와 전투   
        #     met_monster = copy.deepcopy(monsters["졸업 연구"])
        #     Me.gpa = battle(Me, met_monster, turn)
        else:
            meetable_monsters = []
            for i in range(100):
                if i%5 == 0: meetable_monsters.append(copy.deepcopy(monsters["데이타구조"]))
                elif i%5 == 1: meetable_monsters.append(copy.deepcopy(monsters["프밍기"]))
                elif i%5 == 2: meetable_monsters.append(copy.deepcopy(monsters["이산구조"]))
                elif i%5 == 3: meetable_monsters.append(copy.deepcopy(monsters["시프"]))
                elif i%5 == 4: meetable_monsters.append(copy.deepcopy(monsters["프밍기"]))
                
            met_monster = wild_monster(meetable_monsters)
            met_monster.level = turn//3 + 2
            met_monster.stage = turn
            if turn % 10 == 0:
                met_monster.level = turn
            met_monster.update()
            
        battlehap = battle(Me, met_monster, turn)
        if battlehap == 0:
            turn = 1
            totalhap = 0
            continue
        totalhap += battlehap
        # 전투 종료 후 몬스터 상태 업데이트
        # 몬스터가 쓰러진 상태라면 게임오바
        if Me.nowCSmon.nowhp == 0:
            break

        # 아니면 레벨업
        for mymon in Me.csMons:
            if mymon != monsters["빈 슬롯"]:
                mymon.level += 1
                if mymon.level > turn+5:
                    mymon.level = turn+5
                mymon.update()
        turn += 1

    clear_screen()    
    print("결과\n")
    if turn >30:
        print("클리어")
        print("\n졸업 GPA: ", Me.gpa)
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


Me = player()

os.system(f'mode con: cols={120} lines={30}')
input("게임을 시작하기 전, 전체 화면으로 전환해주세요.\n\n아무 키나 눌러 계속")

while True:
    clear_screen()
    start = main_menu()
    if start == "30턴 모드":
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
        thirty_turn_mode(turn, totalhap, Me)
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
        pass
    elif start == " 제작자  ":
        clear_screen()
        print("\n\n\n\n\n\n\n\n\n\n")
        print("\t\t\t\t\t               제작자           ")
        print("\t\t\t\t\t         이준서 == SemiWest     \n")
        print("\t\t\t\t\t               감사링           ")
        getch = input("아무 키나 눌러 종료")
        clear_screen()
    else:
        clear_screen()
        input("플레이 해주셔서 감삼당\n\n아무 키나 눌러 종료")
        clear_screen()
        break



