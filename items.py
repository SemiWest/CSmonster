class Items:
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect

# 플레이어와 적 전산몬스터 생성
Noneitem = Items(name="빈 슬롯", 
                  description="", 
                  effect=None)


americano = Items(name="아메리카노", 
                  description="카페인의 힘으로 체력을 회복한다. 5 또는 최대 체력의 20% 중 큰 값을 회복한다.", 
                  effect="heal")



items = {
    "빈 슬롯": Noneitem,
    "아메리카노": americano,
}