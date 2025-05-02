class Items:
    def __init__(self, name, description, effect, fixed=0, varied=0, buffto="", canuse_on_fainted=False):
        self.name = name
        self.description = description
        self.effect = effect
        self.fixed = fixed
        self.varied = varied
        self.buffto = buffto
        self.canuse_on_fainted = canuse_on_fainted

# 플레이어와 적 전산몬스터 생성
Noneitem = Items(name="빈 슬롯", 
                  description="", 
                  effect=None,)

americano = Items(name="아이스아메리카노", 
                  description="카페인의 힘으로 체력을 회복한다. 5 또는 최대 체력의 10% 중 큰 값을 회복한다.", 
                  effect="heal",
                  fixed=5,
                  varied=0.1,
                  )

MonsterZero = Items(name="몬스터 제로",
                    description="농축된 카페인의 힘으로 체력을 회복한다. 10 또는 최대 체력의 25% 중 큰 값을 회복한다.", 
                    effect="heal",
                    fixed=10,
                    varied=0.25,
                    )

AirPods = Items(name="에어팟",
                    description="에어팟을 주고 노동요를 틀어준다. 흥이 올라 속도가 2배로 상승한다.", 
                    effect="buff",
                    varied=2,
                    buffto="sp",
                    )

clever_soup = Items(name="총명탕",
                    description="총명탕을 먹인다. 두뇌 능력이 상승해 공격력이 1.5배로 증가한다.", 
                    effect="buff",
                    varied=1.5,
                    buffto="ad",
                    )

zokbo = Items(name="족보",
                    description="족보를 보고 상대의 취약점을 파악한다. 공격력이 2배로 증가한다.", 
                    effect="buff",
                    varied=2,
                    buffto="ad",
                    )

# grace_of_TA = Items(name="조교님의 은총",
#                     description="조교님의 은총을 받아 상대를 완전히 이해한다. 상대를 반드시 포획한다.", 
#                     effect="capture",
#                     )

Linger = Items(name="링거",
                    description="링거를 맞아 풀 컨디션으로 돌아온다. 체력을 모두 회복한다. 쓰러진 전산몬스터에게도 사용 가능하다.", 
                    effect="heal",
                    varied=1,
                    canuse_on_fainted=True,
                    )


items = {
    "빈 슬롯": Noneitem,
    "아메리카노": americano,
    "몬스터 제로": MonsterZero,
    "에어팟": AirPods,
    "총명탕": clever_soup,
    "족보": zokbo,
    "링거": Linger,
}