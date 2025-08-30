class Items:
    def __init__(self, name, description, effect, grade="노말", fixed=0, varied=0, buffto="", canuse_on_fainted=False, special = False):
        self.name = name            # 이름
        self.description = description  # 설명
        self.effect = effect        # 효과: heal, damage, buff, debuff 등
        self.grade = grade          # 노말, 레어, 에픽, 레전더리
        self.fixed = fixed
        self.varied = varied
        self.buffto = buffto        # 버프 대상 (예: speed, defense 등)
        self.canuse_on_fainted = canuse_on_fainted 
        self.special = special  # 특수 아이템 여부 (예: GPT)
        self.gradeSymbol = {
            "레전더리": "◈",
            "에픽": "◆",
            "레어": "▼",
            "노말": "●",
            "아이템아님": ""
        }.get(grade, "")

def get_item_color_by_grade(grade):
    """아이템 등급에 따라 색상 반환"""
    if grade == "레전더리":
        return (255, 215, 0)      # 노란색
    elif grade == "에픽":
        return (180, 140, 255)    # 연한 보라색
    elif grade == "레어":
        return (80, 220, 120)     # 연한 초록색
    elif grade == "노말":
        return (255, 255, 255)    # 흰색
    else:
        return (180, 180, 180)    # 기타(회색)

# 플레이어와 적 전산몬스터 생성
Noneitem = Items(
    name="빈 슬롯", 
    description="", 
    grade="아이템아님",
    effect=None,
)

# 레전더리
MonsterZero = Items(
    name="몬스터제로",
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
    fixed=1,   # (-1로 데미지)
    special=True
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
    description="에너지바를 먹는다. 체력을 10만큼 회복한다.", 
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

Alcohol = Items(
    name="알코올",
    description="기분이 좋아지는 미지의 초록 병. 스피드를 30% 올린다.",
    effect="buff",
    grade="노말",
    varied=0.3,
    buffto="speed",
    canuse_on_fainted=False,
    special=False
)

Google = Items(
    name="구글신",
    description="구글신에게 나를 치료할 수 있는 방법을 검색한다. 체력을 5만큼 회복한다. ",
    effect="heal",
    grade="노말",
    fixed=5
)

# 아이템 목록
items = {
    "빈 슬롯": Noneitem,
    "몬스터제로": MonsterZero,
    "GPT": GPT,
    "아메리카노": Americano,
    "렉쳐노트": LectureNote,
    "에어팟": AirPods,
    "랜섬웨어": Ransomware,
    "에너지바": SnackBar,
    "바이러스": Virus,
    "알코올": Alcohol,
    "구글신": Google
}

item_list = [
    MonsterZero,
    GPT,
    Americano,
    LectureNote,
    AirPods,
    Ransomware,
    SnackBar,
    Virus,
    Alcohol
]

