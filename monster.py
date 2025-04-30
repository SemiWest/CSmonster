class Monster:
    def __init__(self, name, level=5, hpD=0, hpW=1, adD=0, adW=1, spD=0, spW=1):
        self.name = name
        self.level = level
        self.hpD = hpD
        self.hpW = hpW
        self.adD = adD
        self.adW = adW
        self.spD = spD
        self.spW = spW
        self.skills = {}  # 스킬 저장
        self.update()
        self.nowhp = self.Maxhp  # 현재 체력 초기화

    def update(self):
        self.Maxhp = int(self.hpD + self.level * self.hpW)
        self.ad = int(self.adD + self.level * self.adW)
        self.sp = int(self.spD + self.level * self.spW)

    def is_alive(self):
        return self.nowhp > 0

    class Skill:
        def __init__(self, name, effect_type, dom="", mp=1, skD=0, skW=1, priority=0, description=""):
            self.description = description
            self.name = name
            self.effect_type = effect_type  # 스킬 효과 타입 (damage, heal, buff, reflect, halve_hp 등)
            self.skD = skD
            self.skW = skW
            self.dom = dom
            self.mp = mp
            self.priority = priority

        def damage(self, target, attacker):
            # 데미지 계산
            multiplier = self.Comp(target, self.mp)  # 상성에 따라 데미지 배율 조정
            return int(multiplier * (self.skD + self.skW * attacker.ad))

        def Comp(self, target, mp):
            # 상성 계산
            if target.name == self.dom:
                return mp  # 상성에 따라 데미지 배율 조정
            return 1  # 기본 상성은 1
        

# 플레이어와 적 전산몬스터 생성
cs101 = Monster(name="프밍기", level=5, hpD=5, hpW=1, adD=2, adW=1, spD=2, spW=2)
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="damage", 
        skD=0, skW=0.3, 
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
        skD=4, skW=0, 
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다. 데이타구조에게 두 배의 데미지를 준다."),
    
}

cs206 = Monster(name="데이타구조", level=5, hpD=7, hpW=0.8, adD=3, adW=0.8, spD=5, spW=1)
cs206.skills = {
    'StackOverflow': Monster.Skill(
        name='StackOverflow', 
        effect_type="damage", 
        skD=0, skW=1, 
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        skD=0, skW=1, 
        priority=4, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격이 입력되면 그 공격을 다시 상대에게 출력한다."),
    '트리 구축': Monster.Skill(
        name='트리 구축', 
        effect_type="damage", 
        skD=3, skW=0.2, 
        description="거대한 트리를 상대에게 쓰러뜨린다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff", 
        skD=0, skW=1.5, 
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 내 공격력이 1.5배가 된다."),
}

cs204 = Monster(name="이산구조", level=5, hpD=9, hpW=1.3, adD=0, adW=0.4, spD=3, spW=1.2)
cs204.skills = {
    'Modus Pones': Monster.Skill(
        name='Modus Pones', 
        effect_type="damage", 
        skD=0, skW=1, 
        priority=-1, 
        description="만약 내가 나중에 공격한다면, 공격은 명중한다. 반드시 나중에 공격한다."),
    '삼단논법': Monster.Skill(
        name='삼단논법', 
        effect_type="damage", 
        skD=2, skW=0.5, 
        description="아리스토텔레스의 현명함을 빌려 상대를 공격한다."),
    '이산화': Monster.Skill(
        name='이산화', 
        effect_type="halve_hp", 
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        skD=0, skW=0, 
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

monsters = {
    "프밍기": cs101,
    "이산구조": cs204,
    "데이타구조": cs206
}
