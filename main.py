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

def wild_monster():
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(list(monsters.values())))

Me = player([copy.deepcopy(monsters["데이타구조"]), None, None, None, None, None], [copy.deepcopy(items["아메리카노"]), None, None, None, None, None])

# 전투 시작
now_CSmon = Me.csMons[0]
while Me.csMons.count(None) > 0:
    met_monster = wild_monster()
    
    now_CSmon = battle(Me, met_monster, now_CSmon)  # 첫 번째 몬스터와 전투 시작
    for mymon in Me.csMons:
        if mymon is not None:
            mymon.level += 1  # 레벨업
            mymon.update()
            mymon.nowhp = mymon.Maxhp

print(f"\n\n잡은 몬스터들: {[m.name for m in Me.csMons if m is not None]}")

input("\n아무 키나 눌러 종료")
clear_screen()

