import copy
from monster import *
from items import *

class player:
        def __init__(
                self, name = "Unknown", 
                csMons = [
                        copy.deepcopy(monsters["프밍기"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"])
                        ], 
                items = [
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"]), 
                        copy.deepcopy(monsters["빈 슬롯"])
                        ]
        ):
                self.name = name
                self.csMons = csMons
                self.items = items
                self.nowCSmon = csMons[0]
                self.gpa = "0.0"
        def gameover(self):
                # 게임 오버 조건: 
                if any(csmon.is_alive() and csmon.name != "빈 슬롯" for csmon in self.csMons):
                        return False
                return True
