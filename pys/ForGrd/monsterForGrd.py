import random

difficulty = 1  # 난이도 조정 (0: 쉬움, 1: 보통, 2: 어려움)
def set_difficulty(difficulty_level):
    global difficulty
    difficulty = difficulty_level

# 몬스터 타입 상성
# 타입별 상성표 (공격타입 -> 방어타입 -> 배율)
# CT: 격투 (체급이 높음) / DS: 불꽃 (무상성) / PS: 노말 / SN: 강철 (방어) / AI: 드래곤에서 모티브
TYPE_EFFECTIVENESS = {
    "*" : {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SYS": 1.0, "AI": 1.0, "*": 1.0},
    "CT": {"CT": 1.0, "DS": 0.0, "PS": 2.0, "SYS": 0.5, "AI": 1.0, "*": 1.0},
    "DS": {"CT": 1.0, "DS": 1.0, "PS": 1.0, "SYS": 2.0, "AI": 0.5, "*": 1.0},
    "PS": {"CT": 1.0, "DS": 0.5, "PS": 2.0, "SYS": 1.0, "AI": 0.0, "*": 1.0},
    "SYS": {"CT": 1.0, "DS": 1.0, "PS": 0.0, "SYS": 1.0, "AI": 1.0, "*": 1.0},
    "AI": {"CT": 2.0, "DS": 0.5, "PS": 1.0, "SYS": 0.5, "AI": 1.0, "*": 1.0},
}

# 타입 코드
type_dict = {
    "*": "기타",
    "CT": "전산이론",
    "DS": "데이터과학",
    "PS": "문제해결",
    "SYS": "시스템 네트워크",
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
    return TYPE_EFFECTIVENESS[atskilltype][tgtype]
def NumToName(mon_num):
        for value in monsters.values():
            if value.Num == mon_num:
                return value.name
        return "error"

class Monster:
    def __init__(self, Num, name, credit, HP, ATK, DEF, SPD, type=["CT"], SeonSu = [], image="../img/monsters/데이타구조.png", description=""):
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

        self.grade = "100번대"
        self.description = description
        self.stage="기억할 수 없는 곳"  # 등장한 스테이지
        self.skills = {}  # 스킬 저장
        self.participated = False  # 전투에 참여했는지 여부
        self.hpShield = False
        self.usedskill = None

        self.reflect_active = 0.0  # 0이면 반사 없음, 0<r<=1 반사율
        self.vatk = 1.0           # 공격 배율 (버프 누적)
        self.vdef = 1.0           # 방어 배율 (버프 누적)
        self.vspd = 1.0           # 속도 배율 (버프 누적)

        self.update_fullreset()

    def update_battle(self, Vatk, Vdef, Vspd):
        # 외부에서 배율을 바꿀 때도 호출 가능
        self.vatk = Vatk
        self.vdef = Vdef
        self.vspd = Vspd
        self.CATK = int(self.ATK * self.vatk)  # 공격력
        self.CDEF = int(self.DEF * self.vdef)  # 방어력
        self.CSPD = int(self.SPD * self.vspd)

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
        
        self.drop_exp = int(self.level * (30-10*difficulty))  # 드랍 경험치

        self.update_battle(self.vatk, self.vdef, self.vspd)
        
    def update_fullreset(self):
        self.update()
        self.nowhp = self.HP  # 현재 체력 회복

    def is_alive(self):
        return self.nowhp > 0

    def use_skill(self, player, skill):
        """스킬 사용"""
        damage, effectiveness = 0, 1.0 # 기본값 (모든 스킬 공통 반환용)

        # 데미지형 스킬
        if skill.effect_type == "Sdamage" or skill.effect_type == "Pdamage":
            # 데미지 계산
            damage, effectiveness = skill.damage(player, self)
            
            # 몬스터에게 데미지 적용
            reflect_ratio = getattr(player, "reflect_active", 0.0)
            if reflect_ratio and reflect_ratio > 0:
                # 0<r<=1: r 비율만큼 반사, 방어자는 (1-r)만큼만 실제 피해
                r = max(0.0, min(1.0, reflect_ratio))
                reflected = int(damage * r)
                actual = int(damage * (1.0 - r))

                # 방어자 피해 적용
                if hasattr(player, 'nowhp'):
                    player.nowhp -= actual
                    if player.nowhp < 0:
                        player.nowhp = 0
                
                # 공격자(=self)에게 반사 피해
                self.nowhp -= reflected
                if self.nowhp < 0:
                    self.nowhp = 0

                # 반사막은 1회 소모
                player.reflect_active = 0.0
            
                return {
                    "damage": actual,
                    "reflected": reflected,
                    "effectiveness": effectiveness,
                    "skill": skill,
                    "note": "reflect applied",
                }, "성공"
            
            # 평상시 데미지 적용
            if hasattr(player, 'nowhp'):
                player.nowhp -= damage
                if player.nowhp < 0:
                    player.nowhp = 0

            return {
                "damage": damage,
                "effectiveness": effectiveness,
                "skill": skill,
            }, "성공"

        # --- 비(非)데미지형 스킬들 구현 ---
        elif skill.effect_type == "heal":
            # skW가 (0,1] 이면 비율회복, 아니면 절대치 회복
            if isinstance(skill.skW, (int, float)) and 0 < skill.skW <= 1:
                heal_amount = int(self.HP * skill.skW)
            else:
                heal_amount = int(skill.skW) if isinstance(skill.skW, (int, float)) else 0

            pre = self.nowhp
            self.nowhp = min(self.HP, self.nowhp + heal_amount)
            return {
                "damage": damage,
                "effectiveness": effectiveness,
                "heal": self.nowhp - pre,
                "skill": skill
            }, "성공"
        
        elif skill.effect_type == "halve_hp":
            # 대상의 현재 HP를 절반으로(내림)
            if hasattr(player, 'nowhp'):
                before = player.nowhp
                player.nowhp = player.nowhp // 2
                return {
                    "damage": damage,
                    "effectiveness": effectiveness,
                    "halve_from": before,
                    "halve_to": player.nowhp,
                    "skill": skill
                }, "성공"
            else:
                return None, "대상 없음"
            
        elif skill.effect_type == "reflect":
            # skW > 0: 그 비율만큼 반사, skW<=0: 완전반사
            if isinstance(skill.skW, (int, float)):
                ratio = float(skill.skW)
                self.reflect_active = 1.0 if ratio <= 0 else min(1.0, ratio)
            else:
                self.reflect_active = 1.0
            return {
                "damage": damage,
                "effectiveness": effectiveness,
                "reflect_ratio": self.reflect_active,
                "skill": skill
            }, "성공"
        
        elif skill.effect_type == "buff":
            # 기본 규칙:
            # - skW 가 숫자: ATK에 +skW% (예: 9 -> +9%)
            # - skW 가 (a,b): DEF에 +a%, SPD에 +b%
            # - 음수도 허용(디버프)
            if isinstance(skill.skW, (int, float)):
                delta = float(skill.skW) / 100.0
                self.vatk = max(0.1, self.vatk * (1.0 + delta))
            elif isinstance(skill.skW, tuple) and len(skill.skW) == 2:
                a, b = skill.skW
                # 만약 둘 중 하나가 음수면 해당 능력치 감소
                self.vdef = max(0.1, self.vdef * (1.0 + float(a) / 100.0))
                self.vspd = max(0.1, self.vspd * (1.0 + float(b) / 100.0))
            else:
                # 우주방사선 같은 랜덤/커스텀 케이스는 여기서도 처리 가능
                pass
        
            # 버프 적용 후 전투스탯 재계산
            self.update_battle(self.vatk, self.vdef, self.vspd)
            return {
                "damage": damage,
                "effectiveness": effectiveness,
                "vatk": round(self.vatk, 3),
                "vdef": round(self.vdef, 3),
                "vspd": round(self.vspd, 3),
                "skill": skill
            }, "성공"
        
        else:
            return None, "미구현임"

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
            return int(multiplier * (basedmg*self.skW+2) * random.uniform(0.85, 1.00)), multiplier

        def Comp(self, target):
            multiplier = 1
            multiplier *= comp(self.skill_type, target.type)
            return multiplier

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
    HP = 30, ATK = 56, DEF = 35, SPD = 72, 
    type=["CT"], SeonSu=[206, 204, 230], 
    image="../img/monsters/프밍기2.png", 
    description="카이스트 입학 후 가장 먼저 듣게 되는 전산과 기필 과목이다. 시간표 브레이커로 유명하다."
)
cs101.skills = {
    'Hello, World!': Monster.Skill(
        name='Hello, World!', 
        effect_type="Pdamage",
        type="CT",
        skW=30, 
        priority=1, 
        description="근본중의 근본인 Hello, World!를 출력해 상대에게 데미지를 준다. 반드시 선제공격한다."),
    '휴보는 내 친구': Monster.Skill(
        name='휴보는 내 친구', 
        effect_type="buff",
        type="CT",
        skW=9, 
        description="휴보에게서 에너지가 가득 담긴 비퍼를 받는다. 공격력을 크게 올린다."),
    'CSV 접근': Monster.Skill(
        name='CSV 접근', 
        effect_type="Sdamage", 
        type="DS",
        skW=50,
        description="CSV 파일에 접근하여 상대의 구조를 파헤친다."),
    
}

# 이산	전산이론	이상해씨
cs204 = Monster(
    Num = 204, name="이산구조", credit = 3,
    HP = 57, ATK = 24, DEF = 86, SPD = 23, 
    type=["CT"], SeonSu=[300, 320],
    image="../img/monsters/이산.png",
    description="이산구조설명"
)
cs204.skills = {
    'Modus Pones': Monster.Skill(
        name='Modus Pones', 
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
        description="아리스토텔레스의 현명함을 빌려 상대를 공격한다."),
    '이산화': Monster.Skill(
        name='이산화', 
        effect_type="halve_hp",
        type="PS",
        skW=0,
        description="상대를 이산화시켜 HP를 반으로 줄인다."),
    '무한루프그래프': Monster.Skill(
        name='무한루프그래프', 
        effect_type="reflect", 
        type = "CT",
        skW=0,
        priority=4, 
        description="무한 루프 그래프를 만들어 상대의 공격을 흘려보낸다."),
}

# 데구	데이터 과학	파이리
cs206 = Monster(
    Num = 206, name="데이타구조", credit = 3,
    HP = 39, ATK = 52, DEF = 43, SPD = 65, 
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
        description="스택 오버플로우를 일으켜 공격한다."),
    'FIFO': Monster.Skill(
        name='FIFO', 
        effect_type="reflect", 
        type="DS",
        skW=0.5,
        priority=4, 
        description="큐를 U자로 만들어 상대를 향하게 한다. 상대의 공격을 절반의 피해로 상대에게 출력한다."),
    '트리 구축': Monster.Skill(
        name='트리 구축', 
        effect_type="Sdamage",
        type="DS",
        skW=50,
        description="거대한 트리를 상대에게 쓰러뜨린다. 반드시 명중한다."),
    'HashMap': Monster.Skill(
        name='HashMap', 
        effect_type="buff",
        type="DS",
        skW=3,
        description="해시맵을 사용하여 최적의 공격 방법을 찾는다. 특수공격을 올린다."),
}

# 시프	시 넽	레츠고이브이
cs230 = Monster(
    Num = 230, name="시프", credit = 3,
    HP = 65, ATK = 60, DEF = 50, SPD = 85, 
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
        description="버퍼 오버플로우를 일으켜 공격한다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="Sdamage", 
        type="PS",
        skW=70,
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다."),
    '시프 스킬 3': Monster.Skill(
        name='미정', 
        effect_type="Sdamage", 
        type="PS",
        skW=50,
        priority=1,
        description="어떻게 해서 공격한다. 선제공격한다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="SYS",
        skW=0.5,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# OS	시 넽	거북왕
cs330 = Monster(
    Num = 330, name="OS", credit = 4,
    HP =65, ATK = 65, DEF = 60, SPD = 130, 
    type = ["SYS"], SeonSu=[],
    image="../img/monsters/OS.png",  
    description="전산과 과목 중 가장 악명이 높다. 자전거를 손을 놓고 타게 만드는 과목이다.")
cs330.skills = {
    '우주방사선': Monster.Skill(
        name='우주방사선', 
        effect_type="buff", 
        type="SYS",
        skW=(random.randint(8, 15), random.randint(-16, -9)),
        description="무작위로 능력치 하나를 크게 올리고 대신 능력치 하나를 낮춘다."),
    'System32 삭제': Monster.Skill(
        name='System32 삭제', 
        effect_type="Sdamage", 
        type="PS",
        skW=130,
        description="상대의 운영체제 폴더를 삭제한다. 명중률이 낮다."),
    '페이지 폴트': Monster.Skill(
        name='페이지 폴트', 
        effect_type="Sdamage", 
        type="PS",
        skW=70,
        description="상대가 사용중인 페이지를 페이징 파일로 옮겨버린다."),
    '셀프 디버그': Monster.Skill(
        name='셀프 디버그', 
        effect_type="heal", 
        type="SYS",
        skW=0.5,
        description="자기 자신을 디버깅해 에러를 고친다. 체력을 최대 체력의 절반만큼 회복한다."),
}

# 알고개	PS	피카츄
cs300 = Monster(
    Num = 300, name = "알고개", credit = 3,
    HP = 67, ATK = 89, DEF = 116, SPD = 33, 
    type = ["PS"], SeonSu=[202],
    image="../img/monsters/알고개.png",
    description="알고리즘과 문제해결 능력을 기르는 과목이다. 알고리즘의 기초를 다진다.")
cs300.skills = {
    '퀵소트': Monster.Skill(
        name='퀵소트', 
        effect_type="buff",
        type="CT",
        skW=(10,12),
        priority=1, 
        description="빠르게 정렬해 방어와 특수 방어를 모두 크게 올린다."),
    '빅O': Monster.Skill(
        name='빅O', 
        effect_type="Pdamage",
        type="CT",
        skW=60, 
        description="총 방어 수치가 높은 만큼 더 강하게 공격한다."),
    '이산화2': Monster.Skill(
        name='이산화2', 
        effect_type="halve_hp",
        type="PS",
        skW=0,
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
    HP = 70, ATK = 80, DEF = 90, SPD = 60, 
    type=["SYS"], SeonSu=[330],
    image="../img/monsters/아키.png",
    description="전산기조직설명"
)
cs311.skills = {
    '파이프라인': Monster.Skill(
        name='파이프라인', 
        effect_type="buff",
        type="CT",
        skW=20, 
        description="CPU 파이프라인을 최적화해 방어력과 속도를 상승시킨다"),
    'MultiThread': Monster.Skill(
        name='MultiThread', 
        effect_type="Pdamage",
        type="CT",
        skW=70, 
        description="한 턴에 여러 차례의 연속 공격을 한다."), # TODO: 연속 공격 구현 가능한지 확인
    'XOR': Monster.Skill(
        name='XOR',
        effect_type="reflect",
        type="CT",
        skW=0,
        description="XOR 게이트로 상대 공격을 반전시켜 무효화시킨다."),
}

# PL	전산이론	메타몽
cs320 = Monster(
    Num = 320, name="프로그래밍언어", credit = 3,
    HP = 80, ATK = 70, DEF = 90, SPD = 60, 
    type=["CT"], SeonSu=[220],
    image="../img/monsters/PL.png",
    description="프로그래밍 언어의 설계와 구현 원리를 심도 있게 이해하는 과목이다. 펜파인애플애플팬이라는 비유로 유명하다."
)
cs320.skills = {
    'PPAP': Monster.Skill(
        name='PPAP', 
        effect_type="Pdamage",
        type="CT",
        skW=100,
        description="함수 안에 함수를 넣은 밀도있는 공격을 한다"),
    'Garbage Collection': Monster.Skill(
        name='Garbage Collection',
        effect_type="heal",
        type="CT",
        skW=20,
        description="필요 없는 메모리를 정리하여 체력을 회복한다."),
    'Type Error': Monster.Skill(
        name='Type Error', 
        effect_type="disable",
        type="CT",
        skW=0, 
        description="타입 에러를 일으켜 상대의 행동을 취소한다."), #TODO: 구현 가능한지 확인해야함
}

# 네떡	시 넽	잠만보
cs341 = Monster(
    Num = 341, name="전산망개론", credit = 3,
    HP = 90, ATK = 80, DEF = 70, SPD = 60,
    type=["SYS"], SeonSu=[330],
    image="../img/monsters/네떡.png",
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
    HP = 100, ATK = 90, DEF = 80, SPD = 70, 
    type=["DS"], SeonSu=[],
    image="../img/monsters/디비개.png",
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
        skW=50,
        description="데이터 손상을 복구하여 체력을 회복한다."
    ),
    '인덱스 재구성': Monster.Skill(
        name='인덱스 재구성',
        effect_type="buff",
        type="DS",
        skW=20,
        description="시스템 최적화를 통해 능력치를 증가시킨다."
    ),
}

# 문해기	PS	마자용
cs202 = Monster(
    Num = 202, name="문제해결기법", credit = 3,
    HP = 80, ATK = 70, DEF = 90, SPD = 60, 
    type=["PS"], SeonSu=[],
    image="../img/monsters/문해기.png",
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
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["AI"], SeonSu=[],
    image="../img/monsters/딥러개.png",
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
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["AI"], SeonSu=[],
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
    HP = 110, ATK = 100, DEF = 90, SPD = 80, 
    type=["PS"], SeonSu=[],
    image="../img/monsters/프밍이.png",
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
    type=["*"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="코옵설명"
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
    type=["*"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="몰입캠프설명"
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
    type=["*"], SeonSu=[],
    image="../img/monsters/데이타구조.png",
    description="개별연구설명"
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