from battle import *
from player import *
from monster import *
from items import *
import random
import copy
import os

def clear_screen():
    # 화면 지우기
    os.system('cls' if os.name == 'nt' else 'clear')

def wild_monster(lists):
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(lists))

# 전투 시작
player_name = input("이름을 입력하세요: ")
Me = player(
    name = player_name,
    csMons = [
        copy.deepcopy(monsters["프밍기"]), 
        copy.deepcopy(monsters["빈 슬롯"]), 
        copy.deepcopy(monsters["빈 슬롯"]), 
        copy.deepcopy(monsters["빈 슬롯"]), 
        copy.deepcopy(monsters["빈 슬롯"]), 
        copy.deepcopy(monsters["빈 슬롯"])
        ], 
    items = [
        copy.deepcopy(items["아메리카노"]),
        copy.deepcopy(items["빈 슬롯"]),
        copy.deepcopy(items["빈 슬롯"]),
        copy.deepcopy(items["빈 슬롯"]),
        copy.deepcopy(items["빈 슬롯"]),
        copy.deepcopy(items["빈 슬롯"])
        ]
    )

now_CSmon = Me.csMons[0]
turn = 1
while turn <=30:
    for mymon in Me.csMons:
        if mymon is not None:
            mymon.update()

    if turn == 30:
        met_monster = copy.deepcopy(monsters["졸업 GPA"])
        gpa = battle(Me, met_monster, now_CSmon, turn)
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
        if turn % 10 == 0:
            met_monster.level = turn
        met_monster.update()
        
    now_CSmon = battle(Me, met_monster, now_CSmon, turn)

    # 전투 종료 후 몬스터 상태 업데이트
    # 몬스터가 쓰러진 상태라면 게임오바
    if now_CSmon.nowhp == 0:
        break
    # 아니면 레벨업
    for mymon in Me.csMons:
        if mymon is not None:
            mymon.level += 1 
    turn += 1
    
print("결과")
if turn >30:
    print("클리어")
    print("졸업 GPA:", gpa)
else:           print("최종 스테이지: ", turn)
print("나의 전산몬스터: ")
for mymon in Me.csMons:
    if mymon.name != "빈 슬롯":
        print(f"{mymon.name} lv{mymon.level}")

input("\n아무 키나 눌러 종료")

