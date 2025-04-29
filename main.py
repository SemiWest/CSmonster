from battle import *
from monster import *
import random
import copy

clear_screen()

player_csMons = [copy.deepcopy(monsters["이산구조"]), None, None, None, None, None]

def wild_monster():
    # 랜덤으로 야생 몬스터 선택
    return copy.deepcopy(random.choice(list(monsters.values())))

# 전투 시작
fmon = wild_monster()
battle(player_csMons, fmon)
player_csMons[1] = player_csMons[0]
player_csMons[0] = copy.deepcopy(fmon)
for mymon in player_csMons:
    if mymon is not None:
        mymon.level += 1  # 레벨업
        mymon.update()
        mymon.nowhp = mymon.Maxhp
smon = wild_monster()
battle(player_csMons, smon)
player_csMons[2] = copy.deepcopy(smon)

print(f"\n\n잡은 몬스터들: {[m.name for m in player_csMons if m is not None]}")

input("\n아무 키나 눌러 종료")
clear_screen()

