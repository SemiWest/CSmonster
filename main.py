from battle import *
from monster import *
from items import *
import random
import copy
import os

def clear_screen():
    # 화면 지우기
    os.system('cls' if os.name == 'nt' else 'clear')

class player:
    def __init__(self, csMons, items):
        self.csMons = csMons
        self.items = items  # 아이템 슬롯

def wild_monster(lists):
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(lists))

Me = player([copy.deepcopy(monsters["데이타구조"]), 
             copy.deepcopy(monsters["빈 슬롯"]), 
             copy.deepcopy(monsters["빈 슬롯"]), 
             copy.deepcopy(monsters["빈 슬롯"]), 
             copy.deepcopy(monsters["빈 슬롯"]), 
             copy.deepcopy(monsters["빈 슬롯"])], 
            
            [copy.deepcopy(items["아메리카노"]),
             copy.deepcopy(items["빈 슬롯"]),
             copy.deepcopy(items["빈 슬롯"]),
             copy.deepcopy(items["빈 슬롯"]),
             copy.deepcopy(items["빈 슬롯"]),
             copy.deepcopy(items["빈 슬롯"])
            ])

# 전투 시작
now_CSmon = Me.csMons[0]
turn = 1
while turn <=30:
    for mymon in Me.csMons:
        if mymon is not None:
            mymon.update()

    if now_CSmon is False:
        break

    meetable_monsters = []
    
    for i in range(100):
        if i%5 == 0: meetable_monsters.append(copy.deepcopy(monsters["데이타구조"]))
        elif i%5 == 1: meetable_monsters.append(copy.deepcopy(monsters["프밍기"]))
        elif i%5 == 2: meetable_monsters.append(copy.deepcopy(monsters["이산구조"]))
        elif i%5 == 3: meetable_monsters.append(copy.deepcopy(monsters["시프"]))
        elif i%5 == 4: meetable_monsters.append(copy.deepcopy(monsters["프밍기"]))
        
    met_monster = wild_monster(meetable_monsters)
    met_monster.level = turn//3 + 5
    if turn % 10 == 0:
        met_monster.level = turn
    met_monster.update()

    now_CSmon = battle(Me, met_monster, now_CSmon, turn)
    for mymon in Me.csMons:
        if mymon is not None:
            mymon.level += 1 
    turn += 1
    

print(f"\n\n잡은 몬스터들: {[m.name for m in Me.csMons if m is not None]}")

input("\n아무 키나 눌러 종료")
clear_screen()

