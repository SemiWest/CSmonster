import random

difficulty = 1  # 난이도 조정 (0: 쉬움, 1: 보통, 2: 어려움)
def set_difficulty(difficulty_level):
    global difficulty
    difficulty = difficulty_level

# 몬스터 타입 상성
# 타입별 상성표 (공격타입 -> 방어타입 -> 배율)
# CT: 격투 (체급이 높음) / DS: 불꽃 (무상성) / PS: 노말 / SN: 강철 (방어) / AI: 드래곤에서 모티브
TYPE_EFFECTIVENESS = {
    "*"     : {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SYS": 1.0, "AI": 1.0, "*": 1.0, "EVENT": 1.0},
    "EVENT" : {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SYS": 1.0, "AI": 1.0, "*": 1.0, "EVENT": 1.0},
    "CT"    : {"CT": 1.0, "DS": 0.0, "PS": 2.0, "SYS": 0.5, "AI": 1.0, "*": 1.0, "EVENT": 1.0},
    "DS"    : {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SYS": 2.0, "AI": 0.5, "*": 1.0, "EVENT": 1.0},
    "PS"    : {"CT": 1.0, "DS": 0.5, "PS": 2.0, "SYS": 1.0, "AI": 0.0, "*": 1.0, "EVENT": 1.0},
    "SYS"   : {"CT": 1.0, "DS": 1.0, "PS": 0.0, "SYS": 1.0, "AI": 1.0, "*": 1.0, "EVENT": 1.0},
    "AI"    : {"CT": 2.0, "DS": 0.5, "PS": 1.0, "SYS": 0.5, "AI": 1.0, "*": 1.0, "EVENT": 1.0},
}

typecolor_dict = {
    "AI" : (189, 215, 238),
    "SYS" : (57, 36, 214),
    "PS" : (152, 235, 96),
    "DS" : (252, 98, 4),
    "CT" : (165, 165, 165),
    "EVENT" : (255, 255, 15),
    "*" : (100, 100, 100),
}

# 타입 코드
type_dict = {
    "*": "*",
    "EVENT": "이벤트",
    "CT": "전산이론",
    "DS": "데이터과학",
    "PS": "문제해결",
    "SYS": "시스템 네트워크",
    "AI": "인공지능",
}
    
def NumToName(mon_num):
        for value in monsters.values():
            if value.Num == mon_num:
                return value.name
        return "error"

class Monster:
    def __init__(self, Num, name, credit, HP, ATK, DEF, SPD, type=["CT"], SeonSu = [], image="../img/monsters/데이타구조.png", description="", reward="", special = False, re = False):
        self.reward = reward
        self.Num = Num  # 몬스터 번호
        self.name = name
        self.credit = credit
        self.level = 5
        self.type = type  # 타입 (데이터 과학, 시스템-네트워크, 전산이론, 시큐어컴퓨팅, 인공지능)
        self.SeonSu = SeonSu  # 이 과목을 선수과목으로 하는 과목들
        self.image = image
        self.IV = []
        for i in range(4):
            self.IV.append(random.randint(0, 31))  # IV는 0~31 사이의 랜덤 값

        self.H = HP
        self.A = ATK
        self.D = DEF
        self.SP = SPD

        self.Rank = [0]*3

        self.special = special  # 특수 몬스터 여부 (예: 코옵, 몰입캠프, 개별연구)
        self.re = re # 재수강 여부

        self.grade = "100번대"
        self.description = description
        self.stage="기억할 수 없는 곳"  # 등장한 스테이지
        self.skills = {}  # 스킬 저장
        self.participated = False  # 전투에 참여했는지 여부
        self.hpShield = False
        self.usedskill = None
        self.update_fullreset()

    def update_battle(self):        
        self.CATK = int(self.ATK * (2+max(0, self.Rank[0]))/(2-min(0, self.Rank[0]))) # 공격력
        self.CDEF = int(self.DEF * (2+max(0, self.Rank[1]))/(2-min(0, self.Rank[1]))) # 방어력
        self.CSPD = int(self.SPD * (2+max(0, self.Rank[2]))/(2-min(0, self.Rank[2]))) # 스피드

    def take_damage(self, damage):
        """ 몬스터가 데미지를 받았을 때 호출되는 메서드 """
        self.nowhp -= damage
        if self.nowhp < 0:
            self.nowhp = 0
        
    def update(self):
        # HP = [ { (종족값 x 2) + 개체값 + 100 } x 레벨/100 ] + 10
        self.HP = int((self.H * 2 + self.IV[0] + 100) * (self.level / 100)) + 10

        # E = [ { (종족값 x 2) + 개체값} x 레벨/100 + 5 ]
        self.ATK = int((self.A * 2 + self.IV[1]) * (self.level / 100)) + 5
        self.DEF = int((self.D * 2 + self.IV[2]) * (self.level / 100)) + 5
        self.SPD = int((self.SP * 2 + self.IV[3]) * (self.level / 100)) + 5
        
        self.drop_exp = int((self.level ** 2) * (30-10*difficulty))  # 드랍 경험치
        self.Rank = [0]*3  # 버프/디버프 랭크 초기화

        # 교체: update 마지막 줄 근처
        self.update_battle()
        
    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복

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
            self.animation = "none" # 애니메이션 파일명 (없으면 "none")

# 플레이어와 적 전산몬스터 생성
Nonemonster = Monster(
    Num = -1, name="빈 슬롯", credit = 3,
    HP = 0, ATK = 0, DEF = 0, SPD = 0,
    type=["CT"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="빈 슬롯입니다. 몬스터를 선택하세요.")

# 프밍기	전산이론	팽도리
cs101 = Monster(
    Num = 101, name="프밍기", credit= 3,
    HP = 53, ATK = 55, DEF = 54, SPD = 40, 
    type=["CT"], SeonSu=[206, 204, 230], 
    image="../img/monsters/프밍기.png", 
    description="카이스트 입학 후 가장 먼저 듣게 되는 전산과 기필 과목이다. 시간표 브레이커로 유명하다."
)
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="Pdamage",
        type="CT",
        skW=30, 
        priority=0, 
        description="근본중의 근본인 Hello, World!를 출력해 상대에게 데미지를 준다. 반드시 선제공격한다."),
    '휴보는 내 친구': Monster.Skill(
        name='휴보는 내 친구', 
        effect_type="buff",
        type="CT",
        skW=3, 
        priority=0, 
        description="휴보에게서 에너지가 가득 담긴 비퍼를 받는다. 공격력을 크게 올린다."),
    'CSV 접근': Monster.Skill(
        name='CSV 접근', 
        effect_type="Sdamage", 
        type="DS",
        skW=50,
        priority=1, 
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다."),
    '나는야 시간표 브레이커': Monster.Skill(
        name='나는야 시간표 브레이커', 
        effect_type="Sdamage", 
        type="DS",
        skW=30,
        priority=1, 
        description="새내기의 시간표를 혼란스럽게 만든다.")
    
}

# 이산	전산이론	이상해씨
cs204 = Monster(
    Num = 204, name="이산구조", credit = 3,
    HP = 45, ATK = 57, DEF = 57, SPD = 45, 
    type=["CT"], SeonSu=[300, 320],
    image="../img/monsters/이산구조.png",
    description="이산구조설명"
)
cs204.skills = {
    'Modus Ponens': Monster.Skill(
        name='Modus Ponens', 
        effect_type="Sdamage",
        type="DS",
        skW=40,
        priority=-1, 
        description="만약 내가 나중에 공격한다면, 공격은 명중한다. 반드시 나중에 공격한다. 반드시 명중한다."),
    '삼단논법': Monster.Skill(
        name='삼단논법', 
        effect_type="Pdamage",
        type="CT",
        skW=60, 
        priority=0,
        description="아리스토텔레스의 현명함을 빌려 상대를 공격한다."),
    '이산화': Monster.Skill(
        name='이산화', 
        effect_type="halve_hp",
        type="PS",
        skW=0,
        priority=2,
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        type = "CT",
        skW=0,
        priority=1, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

# 데구	데이터 과학	파이리
cs206 = Monster(
    Num = 206, name="데이타구조", credit = 3,
    HP = 39, ATK = 58, DEF = 47, SPD = 65, 
    type=["DS"], SeonSu=[360],
    image="../img/monsters/데이타구조.png",
    description="데이타구조설명"
)
cs206.skills = {
    'StackOverflow': Monster.Skill(
        name='StackOverflow', 
        effect_type="Sdamage",
        type="CT",
        skW=100,
        priority=1,
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        type="DS",
        skW=0.5,
        priority=3, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격을 절반의 피해로 상대에게 출력한다."),
    '트리 파괴': Monster.Skill(
        name='트리 파괴', 
        effect_type="Sdamage",
        type="DS",
        skW=50,
        priority=2,
        description="거대한 트리를 상대에게 쓰러뜨린다. 반드시 명중한다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff",
        type="DS",
        skW=0,
        priority=0,
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 공격을 올린다."),
}

# 시프	시 넽	레츠고이브이
cs230 = Monster(
    Num = 230, name="시프", credit = 3,
    HP = 65, ATK = 70, DEF = 77, SPD = 75, 
    type=["SYS"], SeonSu=[311, 341],
    image="../img/monsters/시프.png",
    description="시프설명"
)
cs230.skills = {
    'BufferOverflow': Monster.Skill(
        name='BufferOverflow', 
        effect_type="Sdamage",
        type="SYS",
        skW=100,
        priority=2,
        description="버퍼 오버플로우를 일으켜 공격한다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="Sdamage", 
        type="PS",
        skW=70,
        priority=2,
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다."),
    'Disassemble': Monster.Skill(
        name='Disassemble', 
        effect_type="Sdamage", 
        type="PS",
        skW=50,
        priority=3,
        description="상대의 코드를 역공학하여 공격한다. 반드시 선제공격한다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="SYS",
        skW=0.5,
        priority=0,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# OS	시 넽	거북왕
cs330 = Monster(
    Num = 330, name="OS", credit = 4,
    HP =79, ATK = 119, DEF = 117, SPD = 78, 
    type = ["SYS"], SeonSu=[],
    image="../img/monsters/OS.png",  
    description="전산과 과목 중 가장 악명이 높다. 자전거를 손을 놓고 타게 만드는 과목이다.")
cs330.skills = {
    '메모리 누수 해결': Monster.Skill(
        name='메모리 누수 해결', 
        effect_type="buff", 
        type="SYS",
        skW=(random.randint(3, 6), random.randint(-7, -4)),
        priority=0,
        description="내 아까운 메모리...해결했다."),
    '과제': Monster.Skill(
        name='과제', 
        effect_type="Sdamage", 
        type="PS",
        skW=130,
        priority=3,
        description="과제가 나왔다. 큰일났다;; 명중률이 낮다."),
    '커널 패닉': Monster.Skill(
        name='커널 패닉', 
        effect_type="Sdamage", 
        type="PS",
        skW=70,
        priority=4,
        description="OS 망했다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="SYS",
        skW=0.5,
        priority=0,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# 알고개	PS	피카츄
cs300 = Monster(
    Num = 300, name = "알고개", credit = 3,
    HP = 45, ATK = 77, DEF = 55, SPD = 120, 
    type = ["PS"], SeonSu=[202],
    image="../img/monsters/알고개.png",
    description="알고리즘과 문제해결 능력을 기르는 과목이다. 알고리즘의 기초를 다진다.")
cs300.skills = {
    '퀵소트': Monster.Skill(
        name='퀵소트', 
        effect_type="buff",
        type="CT",
        skW=4,
        priority=1, 
        description="빠르게 정렬해 방어를 크게 올린다."),
    '빅O': Monster.Skill(
        name='빅O', 
        effect_type="Pdamage",
        type="CT",
        skW=60, 
        priority=2,
        description="총 방어 수치가 높은 만큼 더 강하게 공격한다."),
    '이산화2': Monster.Skill(
        name='이산화2', 
        effect_type="halve_hp",
        type="PS",
        skW=0,
        priority=3,
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        type = "CT",
        skW=0,
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

# 아키	시 넽	꼬부기
cs311 = Monster(
    Num = 311, name="전산기조직", credit = 3,
    HP = 79, ATK = 84, DEF = 103, SPD = 78, 
    type=["SYS"], SeonSu=[330],
    image="../img/monsters/전산기조직.png",
    description="전산기조직설명"
)
cs311.skills = {
    '파이프라인': Monster.Skill(
        name='파이프라인', 
        effect_type="buff",
        type="CT",
        skW=(1,2), 
        priority=0,
        description="CPU 파이프라인을 최적화해 방어력과 속도를 상승시킨다"),
    'MultiThread': Monster.Skill(
        name='MultiThread', 
        effect_type="Pdamage",
        type="CT",
        skW=70, 
        priority=2,
        description="한 턴에 여러 차례의 연속 공격을 한다."), # TODO: 연속 공격 구현 가능한지 확인
    'XOR': Monster.Skill(
        name='XOR',
        effect_type="reflect",
        type="CT",
        skW=0,
        priority=3,
        description="XOR 게이트로 상대 공격을 반전시켜 무효화시킨다."),
}

# PL	전산이론	메타몽
cs320 = Monster(
    Num = 320, name="프로그래밍언어", credit = 3,
    HP = 85, ATK = 85, DEF = 85, SPD = 85, 
    type=["CT"], SeonSu=[220],
    image="../img/monsters/프로그래밍언어.png",
    description="프로그래밍 언어설명"
)
cs320.skills = {
    'PPAP': Monster.Skill(
        name='PPAP', 
        effect_type="Pdamage",
        type="CT",
        skW=60,
        priority=2,
        description="함수 안에 함수를 넣은 밀도있는 공격을 한다"),
    'Garbage Collection': Monster.Skill(
        name='Garbage Collection',
        effect_type="heal",
        type="CT",
        skW=0.5,
        priority=0,
        description="필요 없는 메모리를 정리하여 체력을 회복한다."),
    'Functional Programming': Monster.Skill(
        name='Functional Programming',
        effect_type="reflect",
        type="CT",
        skW=1,
        priority=4,
        description="함수형 프로그래밍이 나를 거부한다. "),
    'Type Error': Monster.Skill(
        name='Type Error', 
        effect_type="disable",
        type="CT",
        skW=0, 
        priority=3,
        description="타입 에러를 일으켜 상대의 행동을 취소한다."), #TODO: 구현 가능한지 확인해야함
}


# 네떡	시 넽	잠만보
cs341 = Monster(
    Num = 341, name="전산망개론", credit = 3,
    HP = 160, ATK = 87, DEF = 87, SPD = 30, 
    type=["SYS"], SeonSu=[],
    image="../img/monsters/전산망개론.png",
    description="네트워크설명"
)
cs341.skills = {
    'DDoS': Monster.Skill(
        name='DDOS', 
        effect_type="Pdamage", 
        type="SYS", 
        skW=70, 
        description="다수의 공격을 여러 차례 퍼붓는다."),
}
# 디비개	데이터 과학	리자몽
cs360 = Monster(
    Num = 360, name="데이터베이스개론", credit = 3,
    HP = 78, ATK = 96, DEF = 81, SPD = 100, 
    type=["DS"], SeonSu=[],
    image="../img/monsters/데이터베이스개론.png",
    description="데이터베이스개론설명"
)
cs360.skills = {
    'SQL Injection': Monster.Skill(
        name='SQL Injection',
        effect_type="Pdamage",
        type="DS",
        skW=85,
        description="데이터베이스에 강력한 공격을 가한다."
    ),
    '트랜잭션 복구': Monster.Skill(
        name='트랜잭션 복구',
        effect_type="heal",
        type="DS",
        skW=0.5,
        description="데이터 손상을 복구하여 체력을 회복한다."
    ),
    '인덱스 재구성': Monster.Skill(
        name='인덱스 재구성',
        effect_type="buff",
        type="DS",
        skW=0,
        description="시스템 최적화를 통해 능력치를 증가시킨다."
    ),
}


# 문해기	PS	마자용
cs202 = Monster(
    Num = 202, name="문제해결기법", credit = 3,
    HP = 190, ATK = 33, DEF = 58, SPD = 33, 
    type=["PS"], SeonSu=[],
    image="../img/monsters/문제해결기법.png",
    description="문제해결기법"
)
cs202.skills = {
    '문제해결 공격': Monster.Skill(
        name='문제해결 공격', 
        effect_type="Pdamage",
        type="PS",
        skW=70, 
        description="문제해결 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 딥러개	인공지능	망나뇽
cs371 = Monster(
    Num = 371, name="딥러닝개론", credit = 3,
    HP = 91, ATK = 117, DEF = 97, SPD = 80, 
    type=["AI"], SeonSu=[],
    image="../img/monsters/딥러닝개론.png",
    description="딥러닝개론설명"
)
cs371.skills = {
    'Backpropagation': Monster.Skill(
        name='Backpropagation', 
        effect_type="Pdamage",
        type="AI",
        skW=70,
        description="지속적으로 학습하며 강력한 공격을 가한다."),
    'Overfitting': Monster.Skill(
        name='Backpropagation', 
        effect_type="Pdamage",
        type="AI",
        skW=100,
        description="한 차례 강력한 공격을 가하지만 이후 가하는 공격이 크게 약해진다."), # TODO: 추가적인 구현 필요
    
}

# 기계학습	인공지능	라티오스
cs376 = Monster(
    Num = 376, name="기계학습", credit = 3,
    HP = 80, ATK = 110, DEF = 95, SPD = 110, 
    type=["AI"], SeonSu=[371],
    image="../img/monsters/기계학습.png",
    description="기계학습설명"
)
cs376.skills = {
    '기계 공격': Monster.Skill(
        name='기계 공격', 
        effect_type="Pdamage",
        type="AI",
        skW=70,
        description="기계학습 기법을 사용해 상대에게 강력한 공격을 한다."),
    '기계 공격': Monster.Skill(
        name='기계 공격', 
        effect_type="Pdamage",
        type="AI",
        skW=70,
        description="기계학습 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 프밍이	전산이론	치코리타
cs220 = Monster(
    Num = 220, name="프로그래밍의 이해", credit = 3,
    HP = 80, ATK = 82, DEF = 100, SPD = 80, 
    type=["PS"], SeonSu=[],
    image="../img/monsters/프로그래밍의이해.png",
    description="프로그래밍의 이해 설명"
)
cs220.skills = {
    '이해의 공격': Monster.Skill(
        name='이해의 공격', 
        effect_type="Pdamage",
        type="PS",
        skW=70,
        description="이해한다."),
}

# 코옵	(이벤트)	야도란
coop = Monster(
    Num = 888, name="코옵", credit = 123123,
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["EVENT"], SeonSu=[],
    image="../img/monsters/코옵.png",
    description="코옵설명",
    reward = "기업인의 길 해금",
    special=True
)
coop.skills = {
    '코옵 공격': Monster.Skill(
        name='코옵 공격', 
        effect_type="Pdamage",
        type="*",
        skW=70,
        description="코옵 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 몰캠	(이벤트)	고라파덕
madcamp = Monster(
    Num = 777, name="몰입캠프", credit = 234234,
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["EVENT"], SeonSu=[],
    image="../img/monsters/몰입캠프.png",
    description="몰입캠프설명",
    reward = "멘트 변동 예정",
    special=True
)
madcamp.skills = {
    '딥러닝 공격': Monster.Skill(
        name='딥러닝 공격', 
        effect_type="Pdamage",
        type="AI",
        skW=70,
        description="딥러닝 기법을 사용해 상대에게 강력한 공격을 한다."),
}

# 개별연구	(이벤트)	폴리곤
study = Monster(
    Num = 999, name="개별연구", credit = 345345,
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["EVENT"], SeonSu=[],
    image="../img/monsters/개별연구.png",
    description="개별연구설명",
    reward = "연구자의 길 해금",
    special=True
)
study.skills = {
    '연구 공격': Monster.Skill(
        name='연구 공격', 
        effect_type="Pdamage",
        type="*",
        skW=70,
        description="개별연구 기법을 사용해 상대에게 강력한 공격을 한다."),
}

monsters = {
    "프밍기": cs101,
    "이산구조": cs204,
    "데이타구조": cs206,
    "시프": cs230,
    "OS": cs330,
    "알고개": cs300,
    "전산기조직": cs311,
    "프로그래밍언어": cs320,
    "전산망개론": cs341,
    "데이터베이스개론": cs360,
    "문제해결기법": cs202,
    "딥러닝개론": cs371,
    "기계학습": cs376,
    "프로그래밍의 이해": cs220,
    "코옵": coop,
    "몰입캠프": madcamp,
    "개별연구": study,
}