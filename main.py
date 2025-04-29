from battle import *
from monster import monsters

clear_screen()

player_csMons = [monsters["프밍기"], None, None, None, None, None]
# 전투 시작
battle(player_csMons, monsters["이산구조"])

input("\n아무 키나 눌러 종료")
clear_screen()

