class Items:
    def __init__(self, name, description, effect, grade="노말", fixed=0, varied=0, buffto="", canuse_on_fainted=False):
        self.name = name            # 이름
        self.description = description  # 설명
        self.effect = effect        # 효과: heal, damage, buff, debuff 등
        self.grade = grade          # 노말, 레어, 에픽, 레전더리
        self.fixed = fixed
        self.varied = varied
        self.buffto = buffto        # 버프 대상 (예: speed, defense 등)
        self.canuse_on_fainted = canuse_on_fainted 

# 플레이어와 적 전산몬스터 생성
Noneitem = Items(
    name="빈 슬롯", 
    description="", 
    grade="아이템아님",
    effect=None,
)

# 레전더리
MonsterZero = Items(
    name="몬스터 제로",
    description="농축된 카페인의 힘으로 체력을 회복한다. 체력을 전부 회복한다.", 
    effect="heal",
    grade="레전더리",
    varied=1
)

GPT = Items(
    name="GPT",
    description="AI를 사용해서 싸운다. 상대의 체력을 1로 만든다.",
    effect="damage",
    grade="레전더리",
    fixed=-1   # (-1로 데미지)
)

# 에픽
Americano = Items(
    name="아메리카노", 
    description="카페인의 힘으로 체력을 회복한다. 50 또는 최대 체력의 50% 중 큰 값을 회복한다.", 
    effect="heal",
    varied=0.5,
    grade="에픽",
    fixed=50
)

LectureNote = Items(
    name="렉쳐노트",
    description="렉쳐노트를 정독한다. 상대의 체력을 현재 체력의 50%로 만든다.",
    effect="damage",
    grade="에픽",
    varied=0.5
)

# 레어 (새로 2개 추가)
AirPods = Items(
    name="에어팟",
    description="에어팟을 주고 노동요를 틀어준다. 흥이 올라 속도가 50% 오른다.", 
    effect="buff",
    grade="레어",
    varied=0.5,
    buffto="speed"
)

Ransomware = Items(
    name="랜섬웨어",
    description="상대에게 랜섬웨어를 건다. 상대의 방어력을 50% 감소시킨다.", 
    effect="debuff",
    grade="레어",
    buffto="defense",
    varied=0.5,
)

# 노말 (새로 2개 추가)
SnackBar = Items(
    name="에너지바",
    description="에너지바를 먹는다. 10 또는 최대 체력의 10% 중 큰 값을 회복한다.", 
    effect="heal",
    grade="노말",
    fixed=10,
    varied=0.1
)

Virus = Items(
    name="바이러스",
    description="상대에게 바이러스를 건다. 상대의 이동속도를 10% 감소시킨다.", 
    effect="debuff",
    grade="노말",
    varied=0.1,
    buffto="speed"
)

# 아이템 목록
items = {
    "빈 슬롯": Noneitem,
    "몬스터 제로": MonsterZero,
    "GPT": GPT,
    "아메리카노": Americano,
    "렉쳐노트": LectureNote,
    "에어팟": AirPods,
    "랜섬웨어": Ransomware,
    "에너지바": SnackBar,
    "바이러스": Virus
<<<<<<< HEAD
}

item_list = [
    MonsterZero,
    GPT,
    Americano,
    LectureNote,
    AirPods,
    Ransomware,
    SnackBar,
    Virus
]
=======
}
>>>>>>> 0395e80a64eb60298a08bc8da8f7835b895b0719
