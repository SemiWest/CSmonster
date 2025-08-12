class Items:
    def __init__(self, name, description, effect, grade="노말", fixed=0, varied=0, buffto="", canuse_on_fainted=False):
        self.name = name            # 이름
        self.description = description  # 설명
        self.effect = effect        # 효과: heal, damage, buff 등
        self.grade = grade          # 노말, 레어, 에픽, 레전더리
        self.fixed = fixed
        self.varied = varied
        self.buffto = buffto        # 버프 대상
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
    description="에어팟을 주고 노동요를 틀어준다. 흥이 올라 속도가 오른다.", 
    effect="buff",
    grade="레어",
    varied=5,
    buffto="speed"
)

VitaminWater = Items(
    name="비타민 워터",
    description="비타민 워터를 마신다. 30의 체력을 회복한다.", 
    effect="heal",
    grade="레어",
    fixed=30
)

# 노말 (새로 2개 추가)
SnackBar = Items(
    name="에너지바",
    description="에너지바를 먹는다. 15의 체력을 회복한다.", 
    effect="heal",
    grade="노말",
    fixed=15
)
# 아이디어가 필요해요
SmallRock = Items(
    name="작은 돌멩이",
    description="돌멩이를 던진다. 상대에게 10의 피해를 준다.", 
    effect="damage",
    grade="노말",
    fixed=10
)

# 아이템 목록
items = {
    "빈 슬롯": Noneitem,
    "몬스터 제로": MonsterZero,
    "GPT": GPT,
    "아메리카노": Americano,
    "렉쳐노트": LectureNote,
    "에어팟": AirPods,
    "비타민 워터": VitaminWater,
    "에너지바": SnackBar,
    "작은 돌멩이": SmallRock
}