import copy
from ForGrd.monsterForGrd import *
from ForGrd.itemForGrd import *
import random

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
    "P": (0, 255, 0),       # Green
    "NR": (0, 0, 0)          # Black
}

PLAYER_SKILLS = {
    "*": [
        {"name": "타자치기", "damage": 30, "type": "*", "description": "한글은 100타, 영어는 독수리타법", "level": 1},
        {"name": "Python", "damage": 40, "type": "*", "description": "파이썬을 다룰 줄 안다", "level": 2}
    ],
    "PS": [
        {"name": "논리왕", "damage": 60, "type": "PS", "description": "상대를 논리로 누른다", "level": 1},
        {"name": "Master Theorem", "damage": 80, "type": "PS", "description": "상대의 복잡도를 분석한다", "level": 2},
        {"name": "PNP", "damage": 90, "type": "PS", "description": "PNP문제를 해결했다. 전 세계 수학자들은 당신의 편이다", "level": 3},
    ],
    "CT": [
        {"name": "이산화", "damage": 60, "type": "CT", "description": "상대를 이산화해 분해해버린다", "level": 1},
        {"name": "RUST", "damage": 80, "type": "CT", "description": "메모리 관리를 더 이상 하지 않아도 된다. 이제 공격에 집중해보자", "level": 2},
        {"name": "팬파인애플애플팬", "damage": 90, "type": "CT", "description": "학부장을 호출한다", "level": 3}
    ],
    "SYS": [
        {"name": "스택오버플로우", "damage": 60, "type": "SYS", "description": "상대의 머리를 과부화시킨다", "level": 1},
        {"name": "CTRL^C", "damage": 65, "type": "SYS", "description": "상대 쉘을 다운시키는 나만의 시그널", "level": 2},
        {"name": "DDOS", "damage": 70, "type": "SYS", "description": "상대에게 무한한 공격 요청을 보낸다", "level": 3},
        {"name": "핀토스", "damage": 85, "type": "SYS", "description": "핀토스를 끝낸 자. 어떤 과제가 와도 이겨낼 수 있다.", "level": 4},
    ],
    "DS": [
        {"name": "OOP", "damage": 65, "type": "DS", "description": "상대를 객채화시킨다", "level": 1},
        {"name": "SQL 인젝션", "damage": 75, "type": "DS", "description": "상대에게 SQL 인젝션 공격을 가한다", "level": 2}
    ],
    "AI": [
        {"name": "오버피팅", "damage": 90, "type": "AI", "description": "상대를 과적합 학습 완벽하게 공격한다", "level": 1},
        {"name": "샘 올트먼", "damage": 100, "type": "AI", "description": "상대에게 특화된 GPT를 만든다", "level": 2}
    ]
}
def Comp(skill, target):
    multiplier = 1
    for typ in target.type:
        multiplier *= comp(skill["type"], typ)
    return multiplier

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

        self.H = 30

        self.A = 56
        self.D = 60
        self.SP = 90
        self.skills = {}  # 스킬 저장
        self.usedskill = None
        
        # 학기 진행 시스템
        self.current_semester = "새터"
        self.semester_order = ["새터", "1-1", "1-2", "2-1", "2-2", "3-1", "3-여름방학", "3-2", "4-1", "4-여름방학", "4-2"]
        self.semester_progress = 0
        self.canBeMetMonsters = ["프밍기"]
        self.thisSemesterMonsters = []
        self.thisSemesterGpas = []
        self.clearedMonsters = []
        self.gpas = []
        self.completed_semesters = []
        
        # PNR 시스템
        self.pnr_available = True
        self.pnr_used = False
        
        # 성적 및 상태 관리
        self.jangzal_count = 0
        self.warning_count = 0
        self.deans_count = 0
        self.titles = []
        
        # 스킬 시스템 (플레이어가 직접 배우는 스킬들)
        self.learned_skills = {
            "*": 1,  # 기본 스킬
            "CT": 0,  # 각 타입별 스킬 레벨
            "DS": 0,
            "SYS": 0,
            "PS": 0,  # 기본적으로 코딩은 할 수 있음
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
        return max(self.learned_skills, key=lambda k: self.learned_skills[k])

    def get_available_skills(self):
        """사용 가능한 스킬 목록 반환"""
        available = []
        for skill_type, level in self.learned_skills.items():
            if level > 0:
                skilllist = PLAYER_SKILLS.get(skill_type, [])
                available.append(skilllist[level-1])
        return available
    
    def update_battle(self, Vatk, Vdef, Vspd):
        self.CATK = int(self.ATK * Vatk)  # 공격력
        self.CDEF = int(self.DEF * Vdef)  # 방어력
        self.CSPD = int(self.SPD * Vspd)

    def take_damage(self, damage):
        if self.cheatmode:
            damage = 0

        self.nowhp -= damage
        if self.nowhp < 0:
            self.nowhp = 0
        
    def update(self):
        self.type = self.playertype()  # 플레이어 타입 설정
        # HP = [ { (종족값 x 2) + 개체값 + 100 } x 레벨/100 ] + 10
        self.HP = int((self.H * 2 + 31 + 100) * (self.level / 100)) + 10

        # E = [ { (종족값 x 2) + 개체값} x 레벨/100 + 5 ]
        self.ATK = int((self.A * 2 + 31) * (self.level / 100)) + 5
        self.DEF = int((self.D * 2 + 31) * (self.level / 100)) + 5
        self.SPD = int((self.SP * 2 + 31) * (self.level / 100)) + 5
        
        self.max_exp = int((self.level ** 3))  # 경험치 필요량

        self.update_battle(1 ,1 ,1)
        
    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복

    def use_skill(self, skill_name, target_monster):
        """스킬 사용"""
        # 스킬 찾기
        available_skills = self.get_available_skills()
        skill = None
        
        for available_skill in available_skills:
            if available_skill["name"] == skill_name:
                skill = available_skill
                break
        
        if not skill:
            return None, "스킬을 찾을 수 없습니다"
        
        # 데미지 계산
        damage, effectiveness = self.damage(skill, target_monster)
        
        # 몬스터에게 데미지 적용
        if hasattr(target_monster, 'nowhp'):
            target_monster.nowhp -= damage
            if target_monster.nowhp < 0:
                target_monster.nowhp = 0
        
        return {
            "damage": damage,
            "effectiveness": effectiveness,
            "skill": skill,
        }, "성공"
    
    def damage(self, skill, target):
        basedmg = ((2*self.level + 10)/250) * self.CATK / max(1, target.CDEF)  # ✅ max(1, ...)
        multiplier = Comp(skill, target)
        return int(multiplier * (basedmg*skill["damage"] + 2) * random.uniform(0.85, 1.00)), multiplier

    def can_use_pnr(self):
        """PNR 사용 가능 여부"""
        return (self.pnr_available and 
                self.current_semester in ["1-1", "1-2"] and 
                not self.pnr_used)
    
    def calcGPA(self, Option):
        sum1, sum2 = 0, 0
        src = self.thisSemesterGpas if Option == 1 else self.gpas

        onlyP = True  # 이번 학기에 P 과목만 있었는지 확인용

        for credit, grade in src:
            # P/NR은 GPA에서 제외
            if grade in ("P", "NR"):
                continue
            onlyP = False
            sum1 += GPASCORE[grade] * credit
            sum2 += credit

        # 이번 학기 전부 P인 경우 → GPA를 "P"로 반환
        if Option == 1 and onlyP and src:
            return "P"

        if sum2 == 0:
            return "0.00"
        return f"{(sum1 / sum2):.2f}"

    def complete_monster(self, monster_name):
        """몬스터(과목) 처치 완료"""
        self.semester_progress += 1
        
        # 경험치 획득
        self.gain_exp(monsters[monster_name].drop_exp)
        
        # 과목별 스킬 성장
        self.grow_skill_from_monster(monster_name)
    
    def grow_skill_from_monster(self, monster_name):
        """몬스터 처치에 따른 스킬 성장"""
        skill_type = monsters[monster_name].type[0]
        if self.learned_skills[skill_type] < 5:
            self.learned_skills[skill_type] += 1
            print(f"Debug: {skill_type} 스킬이 {self.learned_skills[skill_type]} 레벨로 상승!")
    
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
        while self.exp >= self.max_exp:
            self.level_up()
    
    def level_up(self):
        while self.exp >= self.max_exp:
            current_hp = self.HP
            self.level += 1
            self.update()
            if self.is_alive():
                self.nowhp += (self.HP-current_hp)
            self.exp -= self.max_exp  # 레벨업 시 경험치 차감
    
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
            return "취업 엔딩"
        elif "대학원생" in self.titles:
            return "대학원 엔딩" 
        elif self.deans_count >= 3:
            return "딘즈 엔딩"
        else:
            return "일반 졸업 엔딩"
        
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
