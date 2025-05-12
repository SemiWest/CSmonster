import random
difficulty = 1  # 난이도 조정 (0: 쉬움, 1: 보통, 2: 어려움)
def set_difficulty(difficulty_level):
    global difficulty
    difficulty = difficulty_level

# type list: 데이터 과학 / 시스템-네트워크 / 전산이론 / 소프트웨어디자인 / 시큐어컴퓨팅 / 비주얼컴퓨팅 / 인공지능-정보서비스 / 소셜컴퓨팅 / 인터랙티브컴퓨팅
# 몬스터 타입 상성
type_chart = {
        "데이터 과학":          {"데이터 과학": 4, "시스템-네트워크": 1, "전산이론": 4,"소프트웨어디자인": 2, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 4, "소셜컴퓨팅": 4, "인터랙티브컴퓨팅": 2},
        "시스템-네트워크":      {"데이터 과학": 1, "시스템-네트워크": 2, "전산이론": 4,"소프트웨어디자인": 2, "시큐어컴퓨팅": 2, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 4, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 1},
        "전산이론":             {"데이터 과학": 4, "시스템-네트워크": 4, "전산이론": 2,"소프트웨어디자인": 1, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 1, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 2},
        "소프트웨어디자인":     {"데이터 과학": 1, "시스템-네트워크": 1, "전산이론": 1,"소프트웨어디자인": 2, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 4,"인공지능-정보서비스": 2, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 4},
        "시큐어컴퓨팅":         {"데이터 과학": 2, "시스템-네트워크": 4, "전산이론": 2,"소프트웨어디자인": 2, "시큐어컴퓨팅": 4, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 2, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 2},
        "비주얼컴퓨팅":         {"데이터 과학": 1, "시스템-네트워크": 2, "전산이론": 0,"소프트웨어디자인": 1, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 4, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 2},
        "인공지능-정보서비스":  {"데이터 과학": 4, "시스템-네트워크": 1, "전산이론": 2,"소프트웨어디자인": 2, "시큐어컴퓨팅": 2, "비주얼컴퓨팅": 4,"인공지능-정보서비스": 2, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 4},
        "소셜컴퓨팅":           {"데이터 과학": 2, "시스템-네트워크": 4, "전산이론": 2,"소프트웨어디자인": 2, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 1, "소셜컴퓨팅": 2, "인터랙티브컴퓨팅": 4},
        "인터랙티브컴퓨팅":     {"데이터 과학": 2, "시스템-네트워크": 1, "전산이론": 2,"소프트웨어디자인": 4, "시큐어컴퓨팅": 1, "비주얼컴퓨팅": 2,"인공지능-정보서비스": 4, "소셜컴퓨팅": 1, "인터랙티브컴퓨팅": 2},
    }

# 타입 코드
type_dict = {
    "데이터 과학": "DTS",
    "시스템-네트워크": "SYS",
    "전산이론": "CST",
    "소프트웨어디자인": "SWD",
    "시큐어컴퓨팅": "SEC",
    "비주얼컴퓨팅": "VSC",
    "인공지능-정보서비스": "AIS",
    "소셜컴퓨팅": "SOC",
    "인터랙티브컴퓨팅": "INT"
    }

def comp(atskilltype, tgtype):
    """
    공격 타입(atskilltype)과 방어 타입(tgtype)을 입력받아 상성 배율을 반환.
    상성 배율:
    - 4: 효과가 굉장히 좋다.
    - 1: 효과가 별로다.
    - 0: 효과가 없다.
    - 2: 일반적인 효과.
    """
    return type_chart[atskilltype][tgtype]/2

class Monster:
    def __init__(self, name, HP, ATK, DEF, SP_ATK, SP_DEF, SPD, type=["전산이론"], evlev=1, evbefore=None, description=""):
        self.name = name
        self.level = 5
        self.exp = 0
        self.type = type  # 타입 (데이터 과학, 시스템-네트워크, 전산이론, 소프트웨어디자인, 시큐어컴퓨팅, 비주얼컴퓨팅, 인공지능-정보서비스, 소셜컴퓨팅, 인터랙티브컴퓨팅)

        self.IV = []
        for i in range(6):
            self.IV.append(random.randint(0, 31))  # IV는 0~31 사이의 랜덤 값
        self.EV = [0]*6

        self.H = HP

        self.A = ATK
        self.D = DEF
        self.SA = SP_ATK
        self.SD = SP_DEF
        self.SP = SPD
        
        self.Rank = [0]*8  # 랭크
        self.giving_EV = []

        self.grade = "일반"
        self.evlev = evlev  # 진화
        self.evbefore = evbefore  # 진화 전 몬스터
        self.description = description
        self.stage="기억할 수 없는 곳"  # 등장한 스테이지
        self.skills = {}  # 스킬 저장
        self.participated = False  # 전투에 참여했는지 여부
        self.nowhp = self.HP  # 현재 체력
        self.hpShield = False
        self.update_fullreset()

    def update_battle(self):        
        self.critChance = sorted([2,3*2**(2*self.Rank[0]-1),48])[1]/48  # 크리티컬 확률 
        self.CATK = int(self.ATK * (2+max(0, self.Rank[1]))/(3-min(0, self.Rank[1]))) # 공격력
        self.CDEF = int(self.DEF * (2+max(0, self.Rank[2]))/(3-min(0, self.Rank[2]))) # 방어력
        self.CSP_ATK = int(self.SP_ATK * (2+max(0, self.Rank[3]))/(3-min(0, self.Rank[3]))) # 특수 공격력
        self.CSP_DEF = int(self.SP_DEF * (2+max(0, self.Rank[4]))/(3-min(0, self.Rank[4]))) # 특수 방어력
        self.CSPD = int(self.SPD * (2+max(0, self.Rank[5]))/(3-min(0, self.Rank[5]))) # 스피드
        self.evasion = self.Rank[6]  # 회피율
        self.accuracy = self.Rank[7]  # 명중률
        
    def update(self):
        self.update_battle()

        # HP = [ { (종족값 x 2) + 개체값 + (노력치/4) + 100 } x 레벨/100 ] + 10
        self.HP = int((self.H * 2 + self.IV[0] + self.EV[0] / 4 + 100) * (self.level / 100)) + 10

        # E = [ { (종족값 x 2) + 개체값 + (노력치/4) } x 레벨/100 + 5 ]
        self.ATK = int((self.A * 2 + self.IV[1] + self.EV[1] / 4) * (self.level / 100)) + 5
        self.DEF = int((self.D * 2 + self.IV[2] + self.EV[2] / 4) * (self.level / 100)) + 5
        self.SP_ATK = int((self.SA * 2 + self.IV[3] + self.EV[3] / 4) * (self.level / 100)) + 5
        self.SP_DEF = int((self.SD * 2 + self.IV[4] + self.EV[4] / 4) * (self.level / 100)) + 5
        self.SPD = int((self.SP * 2 + self.IV[5] + self.EV[5] / 4) * (self.level / 100)) + 5
        
        self.max_exp = int((self.level ** 3))  # 경험치 필요량
        self.drop_exp = int(self.level * (30-10*difficulty))  # 드랍 경험치

    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복
        self.Rank = [0]*6

    def level_up(self, turn):
        while self.exp >= self.max_exp:
            current_hp = self.HP
            self.level += 1
            self.update()
            if self.is_alive():
                self.nowhp += (self.HP-current_hp)
            self.exp -= self.max_exp  # 레벨업 시 경험치 차감
            if self.level >= self.get_monster_max_level(turn):
                self.exp = 0
                break

    def is_alive(self):
        return self.nowhp > 0

    def get_monster_max_level(self,turn):
        """스테이지에 따른 몬스터 레벨 계산"""
        if turn <= 10:
            return 10
        elif turn <= 20:
            return 16
        elif turn <= 30:
            return 24
        elif turn <= 40:
            return 32
        elif turn <= 50:
            return 38
        elif turn <= 60:
            return 48
        elif turn <= 70:
            return 56
        elif turn <= 80:
            return 64
        elif turn <= 90:
            return 74
        elif turn <= 100:
            return 84
        elif turn <= 110:
            return 94
        elif turn <= 120:
            return 104
        elif turn <= 130:
            return 114
        elif turn <= 140:
            return 126
        elif turn <= 150:
            return 138
        elif turn <= 160:
            return 150
        elif turn <= 170:
            return 162
        elif turn <= 180:
            return 174
        elif turn <= 190:
            return 188
        elif turn <= 200:
            return 200
        else:
            return 200  # 200 이상의 스테이지는 최대 레벨 200

    class Skill:
        def __init__(self, name, effect_type, type, cp, skW, acc=100, priority=0, description=""):
            self.description = description
            self.name = name
            self.effect_type = effect_type  # 스킬 효과 타입 (Pdamage, Sdamage, heal, buff, reflect, halve_hp 등)
            self.skill_type = type # 스킬 타입 (데이터 과학, 시스템-네트워크, 전산이론, 소프트웨어디자인, 시큐어컴퓨팅, 비주얼컴퓨팅, 인공지능-정보서비스, 소셜컴퓨팅, 인터랙티브컴퓨팅)
            self.cp = cp # 사용 가능 횟수
            self.skW = skW # 위력
            self.acc = acc  # 명중률
            self.priority = priority # 우선도

        def damage(self, target, attacker):
            # 데미지 계산
            # 크리티컬
            crit = random.random() < attacker.critChance
            if self.effect_type == "Pdamage": 
                basedmg = ((2*attacker.level + 10)/250)*attacker.CATK/(target.DEF if crit else target.CDEF)
            else: 
                basedmg = ((2*attacker.level + 10)/250)*attacker.CSP_ATK/(target.SP_DEF if crit else target.CSP_DEF) 
            
            # 상성
            multiplier = self.Comp(attacker, target)
            
            # 자속 보정
            if any(type==self.skill_type for type in attacker.type):
                multiplier *= 1.5
            
            # 명중률
            if hitChance == -1:  # 명중률이 -1이면 무조건 명중
                hit = True
            else:
                hitChance = self.acc(3+max*(0,attacker.accuracy-target.evasion))/(3-min(0,attacker.accuracy-target.evasion))/100  # 명중 확률
                hit = random.random() < hitChance
            
            # 최종 데미지 출력
            if not hit:
                return False, False
            elif crit:
                return multiplier * (basedmg*self.skW+2) * random.uniform(0.85, 1.00) * 1.5, crit
            return multiplier * (basedmg*self.skW+2) * random.uniform(0.85, 1.00), crit

        def Comp(self, target):
            multiplier = 1
            for type in target.type:
                multiplier *= comp(self.skill_type, type)
            return multiplier

# 플레이어와 적 전산몬스터 생성
Nonemonster = Monster(name="빈 슬롯", HP = 0, ATK = 0, DEF = 0, SP_ATK = 0, SP_DEF = 0, SPD = 0, type=None, evlev=1, evbefore=None,)

cs101 = Monster(name="프밍기", HP = 30, ATK = 56, DEF = 35, SP_ATK = 25, SP_DEF = 35, SPD = 72, type=["전산이론"], evlev=1, evbefore=None,
                description="카이스트 입학 후 가장 먼저 듣게 되는 전산과 기필 과목이다. 시간표 브레이커로 유명하다.")
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="Pdamage",
        type="전산이론",
        cp = 40,
        skW=30, 
        priority=1, 
        description="근본중의 근본인 Hello, World!를 출력해 상대에게 데미지를 준다. 반드시 선제공격한다."),
    '휴보는 내 친구': Monster.Skill(
        name='휴보는 내 친구', 
        effect_type="buff",
        type="전산이론", 
        cp = 10,
        skW=9, 
        description="휴보에게서 에너지가 가득 담긴 비퍼를 받는다. 공격력을 크게 올린다."),
    'CSV 접근': Monster.Skill(
        name='CSV 접근', 
        effect_type="Sdamage", 
        type="데이터 과학",
        cp = 30,
        skW=50,
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다. 데이타구조에게 두 배의 데미지를 준다."),
    
}

cs206 = Monster(name="데이타구조", level=5, hpD=7, hpW=0.8, atkD=3, atkW=0.8, spD=5, spW=1)
cs206.skills = {
    'StackOverflow': Monster.Skill(
        name='StackOverflow', 
        effect_type="damage",
        type="전산이론",
        cp = 10,
        skW=100,
        acc=90, 
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        type="데이터 과학",
        cp = 5,
        skW=1, 
        priority=4, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격이 입력되면 그 공격을 다시 상대에게 출력한다."),
    '트리 구축': Monster.Skill(
        name='트리 구축', 
        effect_type="damage",
        type="데이터 과학",
        cp = 30,
        skW=50,
        acc=-1,
        description="거대한 트리를 상대에게 쓰러뜨린다. 반드시 명중한다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff",
        type="데이터 과학",
        cp = 20,
        skW=1,
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 공격력을 올린다."),
}

cs204 = Monster(name="이산구조", level=5, hpD=9, hpW=1.3, atkD=0, atkW=0.4, spD=3, spW=1.2)
cs204.skills = {
    'Modus Pones': Monster.Skill(
        name='Modus Pones', 
        effect_type="damage", 
        skW=40, 
        priority=-1, 
        description="만약 내가 나중에 공격한다면, 공격은 명중한다. 반드시 나중에 공격한다., 반드시 명중한다."),
    '삼단논법': Monster.Skill(
        name='삼단논법', 
        effect_type="damage", 
        skW=0.5, 
        description="아리스토텔레스의 현명함을 빌려 상대를 공격한다."),
    '이산화': Monster.Skill(
        name='이산화', 
        effect_type="halve_hp", 
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        skW=0, 
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

cs230 = Monster(name="시프", level=5, hpD=7, hpW=0.6, atkD=3, atkW=1, spD=6, spW=1.8)
cs230.skills = {
    'BufferOverflow': Monster.Skill(
        name='BufferOverflow', 
        effect_type="damage", 
        skW=1, 
        description="버퍼 오버플로우를 일으켜 공격한다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="damage", 
        skW=0.6,
        dom="아키", mp=2, 
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다. 아키에게 두 배의 데미지를 준다."),
    '시프 스킬 3': Monster.Skill(
        name='미정', 
        effect_type="damage", 
        skW=0.7, 
        description="어떻게 해서 공격한다. OS에게 두 배의 데미지를 준다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        skW=0.5, 
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# 졸업 연구
# 졸업 연구는 특별한 몬스터로, 레벨과 스킬이 다름
graudation = Monster(name="졸업 연구", level=99, hpD=9999, hpW=0, atkD=0, atkW=0, spD=9999, spW=0, grade="보스", description="졸업이 눈 앞이다. 그동안의 성과를 보이자.")
graudation.skills = {
    '시련': Monster.Skill(
        name='시련', 
        effect_type="halve_hp", 
        description="졸업 연구를 통과하기 위한 시련을 준다. 상대의 HP를 반으로 줄인다."),
}

monsters = {
    "빈 슬롯": Nonemonster,
    "프밍기": cs101,
    "이산구조": cs204,
    "데이타구조": cs206,
    "시프": cs230,
}
