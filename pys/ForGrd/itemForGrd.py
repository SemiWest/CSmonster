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

ProfSoul = Items(
    name="교수의영혼",
    description="교수님의 영혼이 강림했다. 공격력을 최대로 올린다.",
    effect="buff",
    grade="레전더리",
    fixed=15,
)

PGSSoul = Items(
    name="원생의영혼",
    description="대학원생?의 영혼을 깃들게 해 방어력을 최대로 올린다.",
    effect="buff",
    grade="레전더리",
    fixed=16,
)

# 에픽
Americano = Items(
    name="아메리카노", 
    description="카페인의 힘으로 체력을 회복한다. 25 또는 최대 체력의 50% 중 큰 값을 회복한다.", 
    effect="heal",
    varied=0.5,
    grade="에픽",
    fixed=25
)

LectureNote = Items(
    name="렉쳐노트",
    description="렉쳐노트를 정독한다. 상대의 체력을 현재 체력의 50%로 만든다.",
    effect="damage",
    grade="에픽",
    varied=0.5
)

Jokbo = Items(
    name="족보",
    description="족보를 통해 상대의 약점을 파악한다. 상대의 방어력과 속도를 3랭크 감소시킨다.",
    effect="debuff",
    grade="에픽",
    fixed=(-11,-10)
)

Subway = Items(
    name="서브웨이",
    description="서브웨이를 먹고 힘을 낸다. 모든 스탯을 각 2랭크 상승시킨다.",
    effect="buff",
    grade="에픽",
    fixed=(3,4,5),
)

# 레어 (새로 2개 추가)
Pokari = Items(
    name="포카리",
    description="포카리를 마신다. 15 또는 최대 체력의 30% 중 큰 값만큼 회복한다.", 
    effect="heal",
    grade="레어",
    fixed=15,
    varied=0.3
)

AirPods = Items(
    name="에어팟",
    description="에어팟을 주고 노동요를 틀어준다. 흥이 올라 속도가 2랭크 오른다.", 
    effect="buff",
    grade="레어",
    fixed=5,
)

Ransomware = Items(
    name="랜섬웨어",
    description="상대에게 랜섬웨어를 건다. 상대의 방어력을 2랭크 감소시킨다.", 
    effect="debuff",
    grade="레어",
    fixed=-8,
)

Protein = Items(
    name="프로틴",
    description="벌크업을 시도한다. 공격력과 방어력이 각 1랭크 상승한다.",
    effect="buff",
    grade="레어",
    fixed=(0, 1),
)

# 노말 (새로 2개 추가)
SnackBar = Items(
    name="에너지바",
    description="에너지바를 먹는다. 5 또는 최대 체력의 10% 중 큰 값을 회복한다.", 
    effect="heal",
    grade="노말",
    fixed=5,
    varied=0.1
)

Virus = Items(
    name="바이러스",
    description="상대에게 바이러스를 건다. 상대의 공격력를 1랭크 감소시킨다.", 
    effect="debuff",
    grade="노말",
    fixed= -6,
    buffto="speed"
)

Alcohol = Items(
    name="알코올",
    description="기분이 좋아지는 미지의 초록 병. 속도를 1랭크 올린다.",
    effect="buff",
    grade="노말",
    fixed = 2,
    canuse_on_fainted=False,
    special=False
)

Google = Items(
    name="구글링",
    description="구글링을 통해 한글 자료를 찾는다. 공격력을 1랭크 올린다.",
    effect="buff",
    grade="노말",
    fixed=0,
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
    "구글링": Google,
    "교수의영혼": ProfSoul,
    "원생의영혼": PGSSoul,
    "프로틴": Protein,
    "포카리": Pokari,
    "족보": Jokbo,
    "서브웨이": Subway
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
    Alcohol,
    Google,
    ProfSoul,
    PGSSoul,
    Protein,
    Pokari,
    Jokbo,
    Subway
]

