import random

difficulty = 1  # 난이도 조정 (0: 쉬움, 1: 보통, 2: 어려움)
def set_difficulty(difficulty_level):
    global difficulty
    difficulty = difficulty_level

# 몬스터 타입 상성
# 타입별 상성표 (공격타입 -> 방어타입 -> 배율)
TYPE_EFFECTIVENESS = {
    "CT": {"CT": 1.0, "DS": 0.0, "PS": 2.0, "SN": 0.5, "AI": 1.0},
    "DS": {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SN": 2.0, "AI": 0.5},
    "PS": {"CT": 1.0, "DS": 0.5, "PS": 2.0, "SN": 1.0, "AI": 0.0},
    "SN": {"CT": 1.0, "DS": 1.0, "PS": 0.0, "SN": 1.0, "AI": 1.0},
    "AI": {"CT": 2.0, "DS": 0.5, "PS": 1.0, "SN": 0.5, "AI": 1.0},
}

# 타입 코드
type_dict = {
    "CT": "전산이론",
    "DS": "데이터과학",
    "PS": "문제해결",
    "SN": "시스템 네트워크",
    "AI": "인공지능",
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
    return TYPE_EFFECTIVENESS[atskilltype][tgtype]/2

class Monster:
    def __init__(self, Num, name, HP, ATK, DEF, SPD, type=["CT"], SeonSu = [], image="../img/monsters/데이타구조.png", description=""):
        self.Num = Num  # 몬스터 번호
        self.name = name
        self.level = 5
        self.exp = 0
        self.type = type  # 타입 (데이터 과학, 시스템-네트워크, 전산이론, 소프트웨어디자인, 시큐어컴퓨팅, 비주얼컴퓨팅, 인공지능-정보서비스, 소셜컴퓨팅, 인터랙티브컴퓨팅)
        self.SeonSu = SeonSu  # 이 과목을 선수과목으로 하는 과목들
        self.image = image
        self.IV = []
        for i in range(4):
            self.IV.append(random.randint(0, 31))  # IV는 0~31 사이의 랜덤 값

        self.H = HP
        self.A = ATK
        self.D = DEF
        self.SP = SPD

        self.grade = "100번대"
        self.description = description
        self.stage="기억할 수 없는 곳"  # 등장한 스테이지
        self.skills = {}  # 스킬 저장
        self.participated = False  # 전투에 참여했는지 여부
        self.hpShield = False
        self.usedskill = None
        self.update_fullreset()

    def update_battle(self, Vatk, Vdef, Vspd):
        self.CATK = int(self.ATK * Vatk)  # 공격력
        self.CDEF = int(self.DEF * Vdef)  # 방어력
        self.CSPD = int(self.SPD * Vspd)
        
    def update(self):
        # HP = [ { (종족값 x 2) + 개체값 + 100 } x 레벨/100 ] + 10
        self.HP = int((self.H * 2 + self.IV[0] + 100) * (self.level / 100)) + 10

        # E = [ { (종족값 x 2) + 개체값} x 레벨/100 + 5 ]
        self.ATK = int((self.A * 2 + self.IV[1]) * (self.level / 100)) + 5
        self.DEF = int((self.D * 2 + self.IV[2]) * (self.level / 100)) + 5
        self.SPD = int((self.SP * 2 + self.IV[3]) * (self.level / 100)) + 5
        
        self.max_exp = int((self.level ** 3))  # 경험치 필요량
        self.drop_exp = int(self.level * (30-10*difficulty))  # 드랍 경험치

        self.update_battle(1 ,1 ,1)
        
    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복

    def level_up(self):
        while self.exp >= self.max_exp:
            current_hp = self.HP
            self.level += 1
            self.update()
            if self.is_alive():
                self.nowhp += (self.HP-current_hp)
            self.exp -= self.max_exp  # 레벨업 시 경험치 차감

    def is_alive(self):
        return self.nowhp > 0

    class Skill:
        def __init__(self, name, effect_type, type, skW, priority=0, description=""):
            self.description = description
            self.name = name
            self.effect_type = effect_type  # 스킬 효과 타입 (Pdamage, Sdamage, heal, buff, reflect, halve_hp 등)
            self.skill_type = type 
            self.skW = skW # 위력
            self.priority = priority # 우선도
            self.consecutive_uses = 0  # 연속 사용 횟수 (리플렉트 계열 스킬에 사용)

        def damage(self, target, attacker):
            # 데미지 계산
            basedmg = ((2*attacker.level + 10)/250)*attacker.CATK/(target.CDEF) 
            
            # 상성
            multiplier = self.Comp(target)
            
            return multiplier * (basedmg*self.skW+2) * random.uniform(0.85, 1.00)

        def Comp(self, target):
            multiplier = 1
            for typ in target.type:
                multiplier *= comp(self.skill_type, typ)
            return multiplier

# 플레이어와 적 전산몬스터 생성
Nonemonster = Monster(
    Num = -1, name="빈 슬롯", 
    HP = 0, ATK = 0, DEF = 0, SPD = 0,
    type=["CT"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="빈 슬롯입니다. 몬스터를 선택하세요.")

# 프밍기	전산이론	팽도리
cs101 = Monster(
    Num = 101, name="프밍기", 
    HP = 30, ATK = 56, DEF = 35, SPD = 72, 
    type=["CT"], SeonSu=[206, 204, 230], 
    image="../img/monsters/데이타구조.png", 
    description="카이스트 입학 후 가장 먼저 듣게 되는 전산과 기필 과목이다. 시간표 브레이커로 유명하다."
)
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="Pdamage",
        type="전산이론",
        skW=30, 
        priority=1, 
        description="근본중의 근본인 Hello, World!를 출력해 상대에게 데미지를 준다. 반드시 선제공격한다."),
    '휴보는 내 친구': Monster.Skill(
        name='휴보는 내 친구', 
        effect_type="buff",
        type="전산이론",
        skW=9, 
        description="휴보에게서 에너지가 가득 담긴 비퍼를 받는다. 공격력을 크게 올린다."),
    'CSV 접근': Monster.Skill(
        name='CSV 접근', 
        effect_type="Sdamage", 
        type="데이터 과학",
        skW=50,
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다."),
    
}

# 이산	전산이론	이상해씨
cs204 = Monster(
    Num = 204, name="이산구조", 
    HP = 57, ATK = 24, DEF = 86, SPD = 23, 
    type=["CT"], SeonSu=[300, 320],
    image="../img/monsters/데이타구조.png",
    description="이산구조설명"
)
cs204.skills = {
    'Modus Pones': Monster.Skill(
        name='Modus Pones', 
        effect_type="Sdamage",
        type="비주얼컴퓨팅",
        skW=40,
        priority=-1, 
        description="만약 내가 나중에 공격한다면, 공격은 명중한다. 반드시 나중에 공격한다. 반드시 명중한다."),
    '삼단논법': Monster.Skill(
        name='삼단논법', 
        effect_type="Pdamage",
        type="전산이론",
        skW=60, 
        description="아리스토텔레스의 현명함을 빌려 상대를 공격한다."),
    '이산화': Monster.Skill(
        name='이산화', 
        effect_type="halve_hp",
        type="시큐어컴퓨팅",
        skW=0,
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        type = "전산이론",
        skW=0,
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

# 데구	데이터 과학	파이리
cs206 = Monster(
    Num = 206, name="데이타구조", 
    HP = 39, ATK = 52, DEF = 43, SPD = 65, 
    type=["DS"], SeonSu=[360],
    image="../img/monsters/데이타구조.png",
    description="데이타구조설명"
)
cs206.skills = {
    'StackOverflow': Monster.Skill(
        name='StackOverflow', 
        effect_type="Sdamage",
        type="전산이론",
        skW=100,
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        type="데이터 과학",
        skW=0.5,
        priority=4, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격을 절반의 피해로 상대에게 출력한다."),
    '트리 구축': Monster.Skill(
        name='트리 구축', 
        effect_type="Sdamage",
        type="데이터 과학",
        skW=50,
        description="거대한 트리를 상대에게 쓰러뜨린다. 반드시 명중한다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff",
        type="데이터 과학",
        skW=3,
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 특수공격을 올린다."),
}

# 시프	시 넽	레츠고이브이
cs230 = Monster(
    Num = 230, name="시프", 
    HP = 65, ATK = 60, DEF = 50, SPD = 85, 
    type=["SN"], SeonSu=[311, 341],
    image="../img/monsters/데이타구조.png",
    description="시프설명"
)
cs230.skills = {
    'BufferOverflow': Monster.Skill(
        name='BufferOverflow', 
        effect_type="Sdamage",
        type="시스템-네트워크",
        skW=100,
        description="버퍼 오버플로우를 일으켜 공격한다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="Sdamage", 
        type="시큐어컴퓨팅",
        skW=70,
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다."),
    '시프 스킬 3': Monster.Skill(
        name='미정', 
        effect_type="Sdamage", 
        type="시큐어컴퓨팅",
        skW=50,
        priority=1,
        description="어떻게 해서 공격한다. 선제공격한다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="시스템-네트워크",
        skW=0.5,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# OS	시 넽	거북왕
cs330 = Monster(
    Num = 330, name="OS", 
    HP =65, ATK = 65, DEF = 60, SPD = 130, 
    type = ["SN"], SeonSu=[],
    image="../img/monsters/데이타구조.png",  
    description="전산과 과목 중 가장 악명이 높다. 자전거를 손을 놓고 타게 만드는 과목이다.")
cs330.skills = {
    '우주방사선': Monster.Skill(
        name='우주방사선', 
        effect_type="buff", 
        type="시스템-네트워크",
        skW=(random.randint(8, 15), random.randint(-16, -9)),
        description="무작위로 능력치 하나를 크게 올리고 대신 능력치 하나를 낮춘다."),
    'System32 삭제': Monster.Skill(
        name='System32 삭제', 
        effect_type="Sdamage", 
        type="시큐어컴퓨팅",
        skW=130,
        description="상대의 운영체제 폴더를 삭제한다. 명중률이 낮다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="Sdamage", 
        type="시큐어컴퓨팅",
        skW=70,
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="시스템-네트워크",
        skW=0.5,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# 알고개	PS	피카츄
cs300 = Monster(
    Num = 300, name = "알고개", 
    HP = 67, ATK = 89, DEF = 116, SPD = 33, 
    type = ["PS"], SeonSu=[202],
    image="../img/monsters/알고개.png",
    description="알고리즘과 문제해결 능력을 기르는 과목이다. 알고리즘의 기초를 다진다.")
cs300.skills = {
    '퀵소트': Monster.Skill(
        name='퀵소트', 
        effect_type="buff",
        type="전산이론",
        skW=(10,12),
        priority=1, 
        description="빠르게 정렬해 방어와 특수 방어를 모두 크게 올린다."),
    '빅O': Monster.Skill(
        name='빅O', 
        effect_type="Pdamage",
        type="전산이론",
        skW=60, 
        description="총 방어 수치가 높은 만큼 더 강하게 공격한다."),
    '이산화2': Monster.Skill(
        name='이산화2', 
        effect_type="halve_hp",
        type="시큐어컴퓨팅",
        skW=0,
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        type = "전산이론",
        skW=0,
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

# 아키	시 넽	꼬부기
cs311 = Monster(
    Num = 301, name="전산기조직", 
    HP = 70, ATK = 80, DEF = 90, SPD = 60, 
    type=["SN"], SeonSu=[330],
    image="../img/monsters/전산기조직.png",
    description="전산기조직설명"
)
cs311.skills = {
    '프로그래밍 언어': Monster.Skill(
        name='프로그래밍 언어', 
        effect_type="Pdamage",
        type="전산이론",
        skW=70, 
        description="프로그래밍 언어를 사용해 상대에게 강력한 공격을 한다."),
}

# PL	전산이론	메타몽
cs320 = Monster(
    Num = 302, name="프로그래밍언어", 
    HP = 80, ATK = 70, DEF = 90, SPD = 60, 
    type=["CT"], SeonSu=[220],
    image="../img/monsters/데이타구조.png",
    description="프로그래밍 언어설명"
)
cs320.skills = {
    '프로그래밍 언어': Monster.Skill(
        name='프로그래밍 언어', 
        effect_type="Pdamage",
        type="전산이론",
        skW=70, 
        description="프로그래밍 언어를 사용해 상대에게 강력한 공격을 한다."),
}

# 네떡	시 넽	잠만보
cs341 = Monster(
    Num = 303, name="전산망개론", 
    HP = 90, ATK = 80, DEF = 70, SPD = 60, 
    type=["SN"], SeonSu=[330],
    image="../img/monsters/데이타구조.png",
    description="네트워크설명"
)
cs341.skills = {
    '네트워크 공격': Monster.Skill(
        name='네트워크 공격', 
        effect_type="Pdamage",
        type="시스템-네트워크",
        skW=70,
        description="네트워크를 통해 상대에게 강력한 공격을 한다."),
}

# 디비개	데이터 과학	리자몽
cs360 = Monster(
    Num = 360, name="데이터베이스개론", 
    HP = 100, ATK = 90, DEF = 80, SPD = 70, 
    type=["DS"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="데이터베이스개론설명"
)
cs360.skills = {
    '데이터베이스 공격': Monster.Skill(
        name='데이터베이스 공격', 
        effect_type="Pdamage",
        type="데이터 과학",
        skW=70, 
        description="데이터베이스를 통해 상대에게 강력한 공격을 한다."),
}

# 문해기	PS	마자용
cs202 = Monster(
    Num = 202, name="문제해결기법", 
    HP = 80, ATK = 70, DEF = 90, SPD = 60, 
    type=["PS"], SeonSu=[300],
    image="../img/monsters/데이타구조.png",
    description="문제해결기법"
)
cs202.skills = {
    '문제해결 공격': Monster.Skill(
        name='문제해결 공격', 
        effect_type="Pdamage",
        type="문제해결",
        skW=70, 
        description="문제해결 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 딥러개	인공지능	망나뇽
cs371 = Monster(
    Num = 371, name="딥러닝개론", 
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["AI"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="딥러닝개론설명"
)
cs371.skills = {
    '딥러닝 공격': Monster.Skill(
        name='딥러닝 공격', 
        effect_type="Pdamage",
        type="인공지능",
        skW=70,
        description="딥러닝 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 기계학습	인공지능	라티오스
# 프밍이	전산이론	치코리타
# 코옵	(이벤트)	야도란
# 몰캠	(이벤트)	고라파덕
# 개별연구	(이벤트)	폴리곤

monsters = {
    "프밍기": cs101,
    "이산구조": cs204,
    "데이타구조": cs206,
    "시프": cs230,
    "OS": cs330,
    "알고개": cs300,
}

def monsterget():
    pass