import copy
from monster import *
from items import *

class player:
    def __init__(
            self, name = "Unknown", 
            csMons = [copy.deepcopy(monsters["프밍기"]), 
                    copy.deepcopy(monsters["빈 슬롯"]), 
                    copy.deepcopy(monsters["빈 슬롯"]), 
                    copy.deepcopy(monsters["빈 슬롯"]), 
                    copy.deepcopy(monsters["빈 슬롯"]), 
                    copy.deepcopy(monsters["빈 슬롯"])], 
            items = [copy.deepcopy(items["빈 슬롯"]),
                    copy.deepcopy(items["빈 슬롯"]),
                    copy.deepcopy(items["빈 슬롯"]),
                    copy.deepcopy(items["빈 슬롯"]),
                    copy.deepcopy(items["빈 슬롯"]),
                    copy.deepcopy(items["빈 슬롯"])]
    ):
        self.name = name
        self.csMons = csMons
        self.items = items
        self.nowCSmon = csMons[0]
        self.gpa = "0.0"