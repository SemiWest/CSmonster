from battle import *
from monster import monsters
import random
import copy

clear_screen()

player_csMons = [copy.deepcopy(monsters["이산구조"]), None, None, None, None, None]
wild_monster = copy.deepcopy(random.choice(list(monsters.values())))

# 전투 시작
battle(player_csMons, wild_monster)

input("\n아무 키나 눌러 종료")
clear_screen()

