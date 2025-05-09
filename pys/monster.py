difficulty = 1  # 난이도 조정 (0: 쉬움, 1: 보통, 2: 어려움)
def set_difficulty(difficulty_level):
    global difficulty
    difficulty = difficulty_level

class Monster:
    def __init__(self, name, level=5, hpD=0, hpW=1, adD=0, adW=1, spD=0, spW=1, grade = "일반", description="", stage="기억할 수 없는 곳"):
        self.name = name
        self.level = level
        self.hpD = hpD
        self.hpW = hpW
        self.adD = adD
        self.adW = adW
        self.spD = spD
        self.spW = spW
        self.grade = grade
        self.description = description
        self.stage = stage  # 등장한 스테이지
        self.skills = {}  # 스킬 저장
        self.participated = False  # 전투에 참여했는지 여부
        self.Maxhp = int(self.hpD + self.level * self.hpW)  # 최대 체력
        self.nowhp = self.Maxhp  # 현재 체력
        self.exp = 0
        self.hpShield = False
        self.update_fullhp()

    def update(self):
        self.Maxhp = int(self.hpD + self.level * self.hpW)
        self.nowhp = self.Maxhp  if self.nowhp > self.Maxhp else int(self.nowhp)
        self.max_exp = int((self.level ** 3))  # 경험치 필요량
        self.drop_exp = int(self.level * (30-10*difficulty))  # 드랍 경험치
        self.ad = int(self.adD + self.level * self.adW)
        self.normad = self.ad
        self.sp = int(self.spD + self.level * self.spW)
        self.normsp = self.sp

    def update_fullhp(self):
        self.update()
        self.nowhp = self.Maxhp  # 현재 체력 회복

    def level_up(self, turn):
        while self.exp >= self.max_exp:
            if self.is_alive():
                self.nowhp += self.hpW  # 레벨업 시 체력 회복
            self.level += 1
            self.exp -= self.max_exp  # 레벨업 시 경험치 차감
            if self.level >= self.get_monster_max_level(turn):
                self.exp = 0
                break
        self.update()

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
        def __init__(self, name, effect_type, dom="", mp=1, skW=1, priority=0, description=""):
            self.description = description
            self.name = name
            self.effect_type = effect_type  # 스킬 효과 타입 (damage, heal, buff, reflect, halve_hp 등)
            self.skW = skW
            self.dom = dom
            self.mp = mp
            self.priority = priority

        def damage(self, target, attacker):
            # 데미지 계산
            multiplier = self.Comp(target, self.mp)  # 상성에 따라 데미지 배율 조정
            return max(1, int(multiplier * ( self.skW * attacker.ad)))

        def Comp(self, target, mp):
            # 상성 계산
            if target.name == self.dom:
                return mp  # 상성에 따라 데미지 배율 조정
            return 1  # 기본 상성은 1
        

# 플레이어와 적 전산몬스터 생성
Nonemonster = Monster(name="빈 슬롯")

cs101 = Monster(name="프밍기", level=5, hpD=5, hpW=1, adD=2, adW=1, spD=2, spW=2,
                description="카이스트 입학 후 가장 먼저 듣게 되는 전산과 기필 과목이다. 시간표 브레이커로 유명하다.")
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="damage", 
        skW=0.3, 
        priority=1, 
        description="근본중의 근본인 Hello, World!를 출력해 상대에게 데미지를 준다."),
    '휴보는 내 친구': Monster.Skill(
        name='휴보는 내 친구', 
        effect_type="buff", 
        skW=2, 
        description="휴보에게서 에너지가 가득 담긴 비퍼를 받는다. 내 공격력이 두 배가 된다."),
    'CSV 접근': Monster.Skill(
        name='CSV 접근', 
        effect_type="damage", 
        dom="데이타구조", mp=2, 
        skW=0.2, 
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다. 데이타구조에게 두 배의 데미지를 준다."),
    
}

cs206 = Monster(name="데이타구조", level=5, hpD=7, hpW=0.8, adD=3, adW=0.8, spD=5, spW=1)
cs206.skills = {
    'StackOverflow': Monster.Skill(
        name='StackOverflow', 
        effect_type="damage", 
        skW=1, 
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        skW=1, 
        priority=4, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격이 입력되면 그 공격을 다시 상대에게 출력한다."),
    '트리 구축': Monster.Skill(
        name='트리 구축', 
        effect_type="damage",
        skW=0.4,
        description="거대한 트리를 상대에게 쓰러뜨린다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff", 
        skW=1.5, 
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 내 공격력이 1.5배가 된다."),
}

cs204 = Monster(name="이산구조", level=5, hpD=9, hpW=1.3, adD=0, adW=0.4, spD=3, spW=1.2)
cs204.skills = {
    'Modus Pones': Monster.Skill(
        name='Modus Pones', 
        effect_type="damage", 
        skW=1, 
        priority=-1, 
        description="만약 내가 나중에 공격한다면, 공격은 명중한다. 반드시 나중에 공격한다."),
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

cs230 = Monster(name="시프", level=5, hpD=7, hpW=0.6, adD=3, adW=1, spD=6, spW=1.8)
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
graudation = Monster(name="졸업 연구", level=99, hpD=9999, hpW=0, adD=0, adW=0, spD=9999, spW=0, grade="보스", description="졸업이 눈 앞이다. 그동안의 성과를 보이자.")
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
