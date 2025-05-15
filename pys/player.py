import copy
from monster import *
from items import *

battleScript = {
        "선배": "나한테 덤빈다고? 내가 너보다 수업 몇개를 더 들었는데!",
        "대학원생": "교수님...? 아, 아니구나...",
        "후배": "선배님, 저랑 한판 붙으실래요??",
        "동기": "너, 나랑 한판 붙어보자!",
        }

LoseScript = {
        "선배": "...말도 안돼. 후배한테 지다니!",
        "대학원생": "너 우리 랩으로 들어올래...?",
        "후배": "선배 강하네요!",
        "동기": "너 잘한다~",
        }

class Player:
        def __init__(
                self, name = "Unknown", Etype = "학생", 
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
                self.Etype = Etype
                self.csMons = csMons
                self.items = items
                self.nowCSmon = csMons[0]
                self.gpa = "0.0"
                self.knowhow = 100
                self.concentration = 50
                self.grade = "A+"

        def gameover(self):
                # 게임 오버 조건: 
                if any(csmon.is_alive() and csmon.dictNo != -1 for csmon in self.csMons):
                        return False
                return True
        
Hanjin = Player(
        name = "한진", 
        Etype = "동기", 
        csMons = [
                copy.deepcopy(monsters["프밍기"]),
                copy.deepcopy(monsters["데이타구조"]),
                copy.deepcopy(monsters["이산구조"]),
                copy.deepcopy(monsters["빈 슬롯"]),
                copy.deepcopy(monsters["빈 슬롯"]),
                copy.deepcopy(monsters["빈 슬롯"])
                ],
)
for m in Hanjin.csMons:
        m.level = 4
        m.update_fullreset()
