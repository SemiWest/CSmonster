import copy
from ForGrd.monsterForGrd import *
from ForGrd.itemForGrd import *
import random

DIFFICULTY_MULTIPLIER = 1.15

# 플레이어 스킬 정의
""" 코파일럿이 만들어놓은거임 수정하면 될듯? -이준서"""
GPASCORE = {
    "A+": 4.3,
    "A0": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B0": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C0": 2.0,
    "C-": 1.7,
    "F": 0.0,
    "W": 0.0,  # 수강 취소
    "P": 4.3,  # Pass
    "NR": 0.0  # None Record
}

GPACOLOR = {
    "A+": (255, 215, 0),    # Gold
    "A0": (255, 215, 0),    # Gold
    "A-": (255, 215, 0),    # Gold
    "B+": (192, 192, 192),  # Silver
    "B0": (192, 192, 192), # Silver
    "B-": (192, 192, 192), # Silver
    "C+": (205, 127, 50),  # Bronze
    "C0": (205, 127, 50),  # Bronze
    "C-": (205, 127, 50), # Bronze
    "F": (255, 0, 0),       # Red
    "W": (128, 128, 128),   # Gray
    "-": (0, 0, 0),         # Black
    "P": (0, 255, 0),       # Green
    "NR": (0, 0, 0)          # Black
}

PLAYER_SKILLS = {
    "*": [
        {"name": "타자치기", "effect_type": "Sdamage", "skW": round(30*DIFFICULTY_MULTIPLIER/5)*5, "type": "*", "description": "한글은 100타, 영어는 독수리타법", "level": 1, "priority": 0},
        {"name": "Python", "effect_type": "Sdamage", "skW": round(40*DIFFICULTY_MULTIPLIER/5)*5, "type": "*", "description": "프밍기를 수강한 당신, 이제 파이썬을 다룰 줄 안다", "level": 2, "priority": 0}
    ],
    "PS": [
        {"name": "논리왕", "effect_type": "Sdamage", "skW": round(50*DIFFICULTY_MULTIPLIER/5)*5, "type": "PS", "description": "상대를 논리로 누른다", "level": 1, "priority": 0},
        {"name": "Master Theorem", "effect_type": "reflect", "skW": 0.5, "type": "PS", "description": "상대의 복잡도를 분석하여 공격을 반사한다", "level": 2, "priority": 3},
        {"name": "PNP", "effect_type": "Sdamage", "skW": round(65*DIFFICULTY_MULTIPLIER/5)*5, "type": "PS", "description": "PNP문제를 해결했다. 전 세계 수학자들은 당신의 편이다", "level": 3, "priority": 3},
    ],
    "CT": [
        {"name": "증명", "effect_type": "reflect", "skW": 0, "type": "CT", "description": "상대의 공격을 무력화한다.", "level": 1, "priority": 4},
        {"name": "이산화", "effect_type": "Sdamage", "skW": round(55*DIFFICULTY_MULTIPLIER/5)*5, "type": "CT", "description": "상대를 이산화해 분해해버린다", "level": 2, "priority": 1},
        {"name": "RUST", "effect_type": "Sdamage", "skW": round(60*DIFFICULTY_MULTIPLIER/5)*5, "type": "CT", "description": "순수 함수를 배웠다. 어렵다.", "level": 3, "priority": 3},
        {"name": "팬파인애플애플팬", "effect_type": "Sdamage", "skW": round(70*DIFFICULTY_MULTIPLIER/5)*5, "type": "CT", "description": "학부장을 호출한다", "level": 4, "priority": 4}
    ],
    "SYS": [
        {"name": "스택오버플로우", "effect_type": "buff", "skW": 3, "type": "SYS", "description": "일정 턴 동안 방어력을 증가시킨다.", "level": 1, "priority": 1},
        {"name": "CTRL^C", "effect_type": "Sdamage", "skW": round(5*DIFFICULTY_MULTIPLIER/5)*5, "type": "SYS", "description": "상대 쉘을 다운시키는 나만의 시그널", "level": 2, "priority": 5},
        {"name": "DDOS", "effect_type": "halve_hp", "skW": 0, "type": "SYS", "description": "상대에게 무한한 공격 요청을 보내 체력을 절반으로 만든다.", "level": 3, "priority": 2},
        {"name": "핀토스", "effect_type": "heal", "skW": 0.5, "type": "SYS", "description": "핀토스를 끝낸 자. 자신의 체력을 크게 회복한다.", "level": 4, "priority": 4},
    ],
    "DS": [
        {"name": "OOP", "effect_type": "Sdamage", "skW": round(50*DIFFICULTY_MULTIPLIER/5)*5, "type": "DS", "description": "상대를 객체화시켜 약점을 찾아 파괴한다", "level": 1, "priority": 1},
        {"name": "SQL 인젝션", "effect_type": "Sdamage", "skW": round(65*DIFFICULTY_MULTIPLIER/5)*5, "type": "DS", "description": "상대에게 SQL 인젝션 공격을 가한다", "level": 2, "priority": 3}
    ],
    "AI": [
        {"name": "오버피팅", "effect_type": "halve_hp", "skW": 0, "type": "AI", "description": "상대를 과적합 학습 완벽하게 공격한다", "level": 1, "priority": 3},
        {"name": "샘 올트먼", "effect_type": "Sdamage", "skW": round(75*DIFFICULTY_MULTIPLIER/5)*5, "type": "AI", "description": "상대에게 특화된 GPT를 만든다", "level": 2, "priority": 4}
    ]
}

def gpaColor(gpa):
    if len(gpa) >= 3:
        gpa = float(gpa)
        if gpa >= 4.3:
            return GPACOLOR["A+"]
        elif gpa >= 4.0:
            return GPACOLOR["A0"]
        elif gpa >= 3.7:
            return GPACOLOR["A-"]
        elif gpa >= 3.3:
            return GPACOLOR["B+"]
        elif gpa >= 3.0:
            return GPACOLOR["B0"]
        elif gpa >= 2.7:
            return GPACOLOR["B-"]
        elif gpa >= 2.3:
            return GPACOLOR["C+"]
        elif gpa >= 2.0:
            return GPACOLOR["C0"]
        elif gpa >= 1.7:
            return GPACOLOR["C-"]
        else:
            return GPACOLOR["F"]
    else: return GPACOLOR[gpa]

class Player:
    def __init__(self, name="Unknown"):
        self.name = name
        self.level = 5
        self.exp = 0

        self.H = 70

        self.A = 110
        self.D = 70
        self.SP = 90
        self.skills = {}  # 스킬 저장
        self.usedskill = None
        self.starting = "CT"
        
        # 학기 진행 시스템
        self.current_semester = "새터"
        self.semester_order = ["새터", "1-1", "1-2", "2-1", "2-2", "3-1", "3-여름방학", "3-2", "4-1", "4-여름방학", "4-2"]
        self.semester_progress = 0
        self.canBeMetMonsters = ["프밍기"]
        self.thisSemesterMonsters = []
        self.thisSemesterGpas = []
        self.clearedMonsters = []
        self.clearedSemesters = []
        self.gpas = []
        self.completed_semesters = []
        self.Rank = [0]*3
        self.mylevelup = 0
        self.skilllevelup = [False, False, False, False, False, False]  # CT, DS, SYS, PS, AI
        
        # PNR 시스템
        self.pnr_available = True
        self.pnr_used = False
        
        # 성적 및 상태 관리
        self.jangzal_count = 0
        self.warning_count = 0
        self.deans_count = 0
        self.titles = []
        
        #학기 수 관리 시스템
        self.all_monster_count = len(monsters) - 3 # 졸업연구, 몰입캠프, 코옵, 개별연구 등 이벤트성 제외
        self.ending_type = "정상" # 초기값은 '정상'
        
        # 스킬 시스템 (플레이어가 직접 배우는 스킬들)
        self.learned_skills = {
            "*": 1,  # 기본 스킬
            "CT": 0,  # 각 타입별 스킬 레벨
            "DS": 0,
            "SYS": 0,
            "PS": 0,  # 기본적으로 코딩은 할 수 있음
            "AI": 0
        }

        # 현재 내가 들고 있는 스킬
        self.current_skills = {
            "*": 1,
            "CT": 0,
            "DS": 0,
            "SYS": 0,
            "PS": 0,
            "AI": 0
        }
        
        # 아이템 인벤토리
        self.items = [
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem)
        ]
        self.update_fullreset()  # 초기화 시 스탯 업데이트

        # 치트 모드 (개발자용)
        self.cheatmode = False  # 치트모드 기본값 추가
    
    def playertype(self):
        """플레이어의 주력 스킬 타입 반환"""
        if self.current_semester == "새터":
            return "*"
        else:
            newdict = {k: v for k, v in self.learned_skills.items() if k != "*"}
            max = 0
            maxkeys = []
            for k in newdict.keys():
                if newdict[k] > max:
                    max = newdict[k]
                    maxkeys = [k]
                if newdict[k] == max and newdict[k] != 0:
                    maxkeys.append(k)
            if len(maxkeys) == 0:
                return ["*"]
            if self.starting in maxkeys:
                return [self.starting]
            return [random.choice(maxkeys)]

    def get_available_skills(self):
        """사용 가능한 스킬 목록 반환"""
        available = []
        for skill_type, level in self.current_skills.items():
            if level > 0:
                skilllist = PLAYER_SKILLS.get(skill_type, [])
                available.append(skilllist[level-1])
        return available
    
    def update_battle(self):        
        self.CATK = int(self.ATK * (2+max(0, self.Rank[0]))/(2-min(0, self.Rank[0]))) # 공격력
        self.CDEF = int(self.DEF * (2+max(0, self.Rank[1]))/(2-min(0, self.Rank[1]))) # 방어력
        self.CSPD = int(self.SPD * (2+max(0, self.Rank[2]))/(2-min(0, self.Rank[2]))) # 스피드

    def update(self):
        self.type = self.playertype()  # 플레이어 타입 설정
        # HP = [ { (종족값 x 2) + 개체값 + 100 } x 레벨/100 ] + 10
        self.HP = int((self.H * 2 + 16 + 100) * (self.level / 100)) + 10

        # E = [ { (종족값 x 2) + 개체값} x 레벨/100 + 5 ]
        self.ATK = int((self.A * 2 + 16) * (self.level / 100)) + 5
        self.DEF = int((self.D * 2 + 16) * (self.level / 100)) + 5
        self.SPD = int((self.SP * 2 + 16) * (self.level / 100)) + 5
        
        self.max_exp = int((self.level ** 3))  # 경험치 필요량

        self.update_battle()
        
    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복
    
    def take_damage(self, damage):
        if self.cheatmode:
            damage = 0

        self.nowhp -= damage
        if self.nowhp < 0:
            self.nowhp = 0

    def can_use_pnr(self):
        """PNR 사용 가능 여부"""
        return (self.pnr_available and 
                self.current_semester in ["1-1", "1-2"] and 
                not self.pnr_used)
    
    def calcGPA(self, Option):
        sum1, sum2 = 0, 0
        src = self.thisSemesterGpas if Option == 1 else self.gpas

        for credit, grade in src:
            # P나 NR 학점은 GPA 산정에서 제외
            if grade in ["P", "NR", "-"]:
                continue
            
            sum1 += GPASCORE[grade] * credit
            sum2 += credit

        if sum2 == 0:
            return "-"
        return f"{(sum1 / sum2):.2f}"

    def complete_monster(self, monster_name):
        """몬스터(과목) 처치 완료"""
        self.semester_progress += 1
        self.mylevelup = 0
        self.skilllevelup = [False, False, False, False, False, False]

        if monster_name == "몰입캠프":
            self.level += 3
            self.update_fullreset()
            print("Debug: 몰입캠프 클리어! 레벨이 3 상승하고 체력이 완전히 회복되었습니다.")
        if monster_name == "코옵":
            self.update_fullreset()
            self.titles.append("회사원")
            print("Debug: 코옵 클리어! 체력이 완전히 회복되고 취업 루트가 해금되었습니다.")
        if monster_name == "개별연구":
            self.update_fullreset()
            self.titles.append("대학원생")
            print("Debug: 개별연구 클리어! 체력이 완전히 회복되고 대학원 진학 루트가 해금되었습니다.")
        
        # 경험치 획득
        self.mylevelup = self.gain_exp(monsters[monster_name].drop_exp)
        
        # 과목별 스킬 성장
        self.skilllevelup, need_skill_change  = self.grow_skill_from_monster(monster_name)

        return need_skill_change

    def grow_skill_from_monster(self, monster_name):
        """몬스터 처치에 따른 스킬 성장"""

        need_skill_change = False

        typearray = [False, False, False, False, False, False]

        if monsters[monster_name].type[0] == "EVENT":
            return typearray, need_skill_change
    
        skill_type = monsters[monster_name].type[0]
        
        if monster_name == "프밍기":
            self.learned_skills['*'] += 1
            self.current_skills['*'] = self.learned_skills['*']
            print(f"Debug: {'*'} 스킬이 {self.learned_skills['*']} 레벨로 상승!")
            typearray[0] = True

            # 프밍기 처치 시 CT 스킬을 추가로 획득하는 로직
            if self.learned_skills['CT'] < 5:
                self.learned_skills['CT'] += 1
                self.current_skills['CT'] = self.learned_skills['CT']
                print(f"Debug: {'CT'} 스킬이 {self.learned_skills['CT']} 레벨로 상승!")
                typearray[1] = True


        else:     
            if self.learned_skills[skill_type] < 5:
                self.learned_skills[skill_type] += 1
                self.current_skills[skill_type] = self.learned_skills[skill_type]
                print(f"Debug: {skill_type} 스킬이 {self.learned_skills[skill_type]} 레벨로 상승!")
                if skill_type == "CT":
                    typearray[1] = True
                elif skill_type == "DS":
                    typearray[2] = True
                elif skill_type == "SYS":
                    typearray[3] = True
                elif skill_type == "PS":
                    typearray[4] = True
                elif skill_type == "AI":
                    typearray[5] = True
        
        # 현재 가지고 있는 스킬이 4개면 바꾸기
        num_current_skills = sum(1 for level in self.current_skills.values() if level > 0)
        if num_current_skills > 4:
            need_skill_change = True

        print(f"Debug: self.current_skills: {self.current_skills}")
        print(f"Debug: num_current_skills: {num_current_skills}")
        print(f"Debug: need_skill_change: {need_skill_change}")

        return typearray, need_skill_change

    def advance_semester(self):
        """다음 학기로 진행"""        
        # 학기 초기화
        self.completed_semesters.append(self.current_semester)
        old_progress = self.semester_progress
        self.semester_progress = 0
        
        # 다음 학기 결정
        current_index = self.semester_order.index(self.current_semester)
        print(f"Debug: 학기 진행 - {self.current_semester}({old_progress}) -> ", end="")
        
        if current_index < len(self.semester_order) - 1:
            self.current_semester = self.semester_order[current_index + 1]
            print(f"{self.current_semester}")
            return True
        else:
            print("졸업!")
            return False        
    
    def gain_exp(self, amount):
        """경험치 획득 및 레벨업"""
        self.exp += amount
        return self.level if self.level_up() == True else None
        
    
    def level_up(self):
        levelHasUpped = False
        while self.exp >= self.max_exp:
            levelHasUpped = True
            current_hp = self.HP
            self.level += 1
            self.update()
            if self.is_alive():
                self.nowhp += (self.HP-current_hp)
            self.exp -= self.max_exp  # 레벨업 시 경험치 차감
            print(f"Debug: 레벨업! 현재 레벨: {self.level}")
        return levelHasUpped
    
    def is_alive(self):
        """생존 여부"""
        return self.nowhp > 0
    
    def gameover(self):
        """게임 오버 조건"""
        # 1-1은 학사경고 없음 (부활 가능)
        if self.current_semester == "1-1" and not self.is_alive():
            self.nowhp = self.HP  # 자동 부활
            return False
        
        # 학사 경고 3회
        return self.warning_count >= 3
    
    def get_final_ending(self):
        """최종 엔딩 결정"""
        if "회사원" in self.titles:
            return "당신은 코옵에서의 경험을 살려 프로그래머로 취업하였습니다!"
        elif "대학원생" in self.titles:
            if self.deans_count >= 3:
                return "당신은 우수한 성적을 기반으로 대학원에 진학했고 훗날 교수로 임명되었습니다!"
            return "당신은 개별연구로 쌓은 경험을 바탕으로 대학원에 진학하였습니다!"
        else:
            return "당신은 졸업 후 꿈을 향해 나아갔습니다!"
        
    def heal(self, amount: int, allow_revive: bool = False) -> int:
        """체력을 회복하고 실제 회복량을 반환한다.
        nowhp==0일 때 부활을 허용하려면 allow_revive=True로 호출."""
        if amount <= 0:
            return 0
        if self.nowhp <= 0 and not allow_revive:
            return 0
        before = max(0, self.nowhp)
        self.nowhp = min(self.HP, before + amount)
        return self.nowhp - before
