import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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

    def take_damage(self, enemy, skill, reflected=None):
        # FIFO 스킬 처리
        if skill.name == "FIFO":
            print(f"{enemy.name}가 {self.name}의 {reflected.name} 스킬을 반사했습니다!")
            damage = reflected.damage(self, enemy)  # 적의 스킬 데미지를 계산
            self.nowhp -= damage  # 적에게 데미지를 반사
            if self.nowhp < 0:
                self.nowhp = 0
            print(f"{self.name}가 {enemy.name}의 반사로 {damage}의 데미지를 받았습니다! 현재 체력: {self.nowhp}/{self.Maxhp}")
            return  # 자신은 피해를 입지 않음

        # 일반 스킬 처리
        damage = skill.damage(self, enemy)
        self.nowhp -= damage
        if self.nowhp < 0:
            self.nowhp = 0
        print(f"{self.name}가 {enemy.name}의 {skill.name} 스킬로 {damage}의 데미지를 받았습니다! 현재 체력: {self.nowhp}/{self.Maxhp}")

    def is_alive(self):
        return self.nowhp > 0

    class Skill:
        def __init__(self, name, dom="", mp=1, dmgD=0, dmgW=1, priority=0):
            self.name = name
            self.dmgD = dmgD
            self.dmgW = dmgW
            self.dom = dom
            self.mp = mp
            self.priority = priority

        def damage(self, target, attacker):
            # 데미지 계산
            multiplier = self.Comp(target, self.mp)  # 상성에 따라 데미지 배율 조정
            return int(multiplier * (self.dmgD + self.dmgW * attacker.ad))

        def Comp(self, target, mp):
            # 상성 계산
            if target.name == self.dom:
                return mp  # 상성에 따라 데미지 배율 조정
            return 1  # 기본 상성은 1

def display_status(player, enemy):
    """플레이어와 적의 상태를 출력"""
    def health_bar(monster):
        bar_length = 10
        filled_length = int(bar_length * monster.nowhp / monster.Maxhp)
        return f"{'■' * monster.nowhp}{'□' * (monster.Maxhp-monster.nowhp)} ({monster.nowhp}/{monster.Maxhp})"

    print(f"\n{enemy.name}(lv {enemy.level})")
    print(health_bar(enemy))
    print("\n")
    print(health_bar(player))
    print(f"{player.name}(lv {player.level})\n")

def display_skills(player):
    """플레이어의 스킬 목록 출력 (가로 정렬, 위력은 아래로 출력, 순서 유지)"""
    print(f"{player.name}의 스킬:")

    # 스킬 이름 출력 (가로 정렬, 순서 유지)
    for skill_name, _ in player.skills.items():
        print(f"{skill_name}\t", end="")  # 탭으로 간격 조정
    print()

    # 위력 출력 (가로 정렬, 순서 유지)
    for _, skill in player.skills.items():
        power = int(skill.dmgD + skill.dmgW * player.ad) * 10  # 위력 계산
        print(f"위력 {power}\t\t", end="")  # 탭으로 간격 조정
    print("\n")

def battle(player, enemy):
    print(f"야생의 {enemy.name}가 나타났다!")

    while player.is_alive() and enemy.is_alive():

        # 전투 상태 출력
        display_status(player, enemy)

        # 플레이어 스킬 선택
        display_skills(player)
        player_skill_name = input(f"{player.name}가 사용할 스킬을 선택하세요: ")
        if player_skill_name not in player.skills:
            print("잘못된 스킬 이름입니다. 다시 선택하세요.")
            continue
        player_skill = player.skills[player_skill_name]

        # 화면 클리어
        clear_screen()

        # 적 스킬 랜덤 선택
        enemy_skill_name = random.choice(list(enemy.skills.keys()))
        enemy_skill = enemy.skills[enemy_skill_name]

        # 우선순위 비교
        if player_skill.priority > enemy_skill.priority or (player_skill.priority == enemy_skill.priority and player.sp > enemy.sp):
            # 플레이어 스킬 먼저 발동
            print(f"\n{player.name}는 {player_skill.name}를 사용했다!")
            if player_skill.name == "FIFO":
                enemy.take_damage(player, player_skill, enemy_skill)
            else:
                enemy.take_damage(player, player_skill)

                # 적이 살아있으면 반격
                if enemy.is_alive():
                    print(f"{enemy.name}는 {enemy_skill.name}를 사용했다!")
                    player.take_damage(enemy, enemy_skill)
        else:
            # 적 스킬 먼저 발동
            print(f"{enemy.name}는 {enemy_skill.name}를 사용했다!")
            if enemy_skill.name == "FIFO":
                player.take_damage(enemy, enemy_skill, player_skill)
            else:
                player.take_damage(enemy, enemy_skill)

                # 플레이어가 살아있으면 반격
                if player.is_alive():
                    print(f"\n{player.name}는 {player_skill.name}를 사용했다!")
                    enemy.take_damage(player, player_skill)
        

    # 전투 결과 출력
    display_status(player, enemy)
    if not player.is_alive():
        print(f"\n{player.name}가 쓰러졌다!")
    elif not enemy.is_alive():
        print(f"\n{enemy.name}가 쓰러졌다!")

# 플레이어와 적 전산몬스터 생성
cs101 = Monster(name="프밍기", level=5, hpD=5, hpW=1, adD=2, adW=1, spD=2, spW=2)
cs101.skills = {
    'Hello, World!': Monster.Skill(name='Hello, World!', dmgD=0, dmgW=0.3, priority=1),
    '휴보는 내 친구': Monster.Skill(name='휴보는 내 친구', dmgD=2, dmgW=0.2),
    'CSV 접근': Monster.Skill(name='CSV 접근', dom="데이타구조", mp=2, dmgD=4, dmgW=0)
}

cs206 = Monster(name="데이타구조", level=5, hpD=7, hpW=0.8, adD=3, adW=0.8, spD=5, spW=1)
cs206.skills = {
    'StackOverflow': Monster.Skill(name='StackOverflow', dmgD=0, dmgW=1),
    'FIFO': Monster.Skill(name='FIFO', dmgD=0, dmgW=0, priority=4),  # 반사 스킬
    '트리 구축': Monster.Skill(name='트리 구축', dmgD=3, dmgW=0.2)
}

# 전투 시작
battle(cs101, cs206)