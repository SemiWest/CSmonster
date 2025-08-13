import copy
from ForGrd.monsterForGrd import *
from ForGrd.itemForGrd import *
import random

# 플레이어 스킬 정의
""" 코파일럿이 만들어놓은거임 수정하면 될듯? -이준서"""
GPASCORE = {
    "A+": 4.3,
    "A0": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B0": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C0": 2.0,
    "C-": 1.7,
    "F": 0.0,
    "W": 0.0,  # 수강 취소
    "P": 4.3,  # Pass
    "NR": 0.0  # None Record
}

PLAYER_SKILLS = {
    "*": [
        {"name": "타자치기", "damage": 10, "type": "*", "description": "한글은 100타, 영어는 독수리타법", "level": 1},
        {"name": "Python", "damage": 15, "type": "*", "description": "파이썬을 다룰 줄 안다", "level": 2}
    ],
    "PS": [
        {"name": "논리왕", "damage": 20, "type": "PS", "description": "상대를 논리로 누른다", "level": 1},
        {"name": "Master Theorem", "damage": 30, "type": "PS", "description": "상대의 복잡도를 분석한다", "level": 2},
        {"name": "그리디", "damage": 50, "type": "PS", "description": "나에게 항상 이익이 되는 선택을 한다", "level": 3},
        {"name": "PNP", "damage": 70, "type": "PS", "description": "PNP문제를 해결했다. 전 세계 수학자들은 당신의 편이다", "level": 4},
        {"name": "리트코드", "damage": 80, "type": "PS", "description": "리트코드에 상대를 이기는 방법을 검색한다", "level": 5}
    ],
    "CS": [
        {"name": "이산화", "damage": 25, "type": "CS", "description": "상대를 이산화해 분해해버린다", "level": 1},
        {"name": "순수 함수", "damage": 50, "type": "CS", "description": "순수 함수를 호출해 공격한다", "level": 2},
        {"name": "RUST", "damage": 50, "type": "CS", "description": "메모리 관리를 더 이상 하지 않아도 된다. 이제 공격에 집중해보자", "level": 3},
        {"name": "팬파인애플애플팬", "damage": 90, "type": "CS", "description": "학부장을 호출한다", "level": 4}
    ],
    "SYS": [
        {"name": "스택오버플로우", "damage": 25, "type": "SYS", "description": "상대의 머리를 과부화시킨다", "level": 1},
        {"name": "DDOS", "damage": 55, "type": "SYS", "description": "상대에게 무한한 공격 요청을 보낸다", "level": 3},
        {"name": "CTRL^C", "damage": 45, "type": "SYS", "description": "상대 쉘을 다운시키는 나만의 시그널", "level": 2},
        {"name": "핀토스", "damage": 85, "type": "SYS", "description": "핀토스를 끝낸 자. 어떤 과제가 와도 이겨낼 수 있다.", "level": 4},
        {"name": "구글 검색", "damage": 95, "type": "SYS", "description": "구글에 상대를 이기는 방법을 검색한다", "level": 5}
    ],
    "DS": [
        {"name": "Q", "damage": 30, "type": "DS", "description": "Queue를 만들어 때린다", "level": 1},
        {"name": "OOP", "damage": 55, "type": "DS", "description": "상대를 객채화시킨다", "level": 2},
        {"name": "RDBMS", "damage": 65, "type": "DS", "description": "상대와 나의 관계를 정의한다", "level": 3},
        {"name": "SQL 인젝션", "damage": 75, "type": "DS", "description": "상대에게 SQL 인젝션 공격을 가한다", "level": 4},
        {"name": "빅데이터 분석", "damage": 85, "type": "DS", "description": "지금까지 진행된 모든 사용자의 플레이 기록을 분석해 공격을 가한다.", "level": 5}
    ],
    "AI": [
        {"name": "'회귀'분석", "damage": 80, "type": "AI", "description": "'과거로 회귀'해 상대를 분석하고 다시 돌아와 공격한다", "level": 5},
        {"name": "오버피팅", "damage": 90, "type": "AI", "description": "상대를 과적합 학습 완벽하게 공격한다", "level": 6},
        {"name": "GPT 호출", "damage": 100, "type": "AI", "description": "GPT에게 공격해달라고 한다", "level": 9}
    ]
}

class Player:
    def __init__(self, name="Unknown", Etype="학생"):
        self.name = name
        self.Etype = Etype
        
        # 플레이어 기본 스탯
        self.level = 1
        self.maxHp = 100
        self.currentHp = 100
        self.attack = 20
        self.defense = 15
        self.speed = 10
        self.exp = 0
        self.expToNext = 100
        
        # 학기 진행 시스템
        self.current_semester = "새터"
        self.semester_order = ["새터", "1-1", "1-2", "2-1", "2-2", "3-1", "3-여름방학", "3-2", "4-1", "4-여름방학", "4-2"]
        self.semester_progress = 0
        self.canBeMetMonsters = ["프밍기"]
        self.thisSemesterMonsters = []
        self.thisSemesterGpas = []
        self.clearedMonsters = []
        self.gpas = []
        self.completed_semesters = []
        
        # PNR 시스템
        self.pnr_available = True
        self.pnr_used = False
        
        # 성적 및 상태 관리
        self.jangzal_count = 0
        self.warning_count = 0
        self.deans_count = 0
        self.titles = []
        
        # 스킬 시스템 (플레이어가 직접 배우는 스킬들)
        self.learned_skills = {
            "CT": 1,  # 각 타입별 스킬 레벨
            "DS": 0,
            "SN": 0,
            "PS": 0,  # 기본적으로 코딩은 할 수 있음
            "AI": 0
        }
        
        # 아이템 인벤토리
        self.items = [
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem), 
            copy.deepcopy(Noneitem)
        ]
    
    def get_available_skills(self):
        """사용 가능한 스킬 목록 반환"""
        available = []
        for skill_type, level in self.learned_skills.items():
            if level > 0:
                skills = PLAYER_SKILLS.get(skill_type, [])
                for skill in skills:
                    required_level = skill.get("level", 1)
                    if level >= required_level:
                        available.append(skill)
        return available
    
    def calculate_damage(self, skill, target_monster):
        """데미지 계산"""
        base_damage = skill["damage"]
        skill_type = skill["type"]
        
        # 몬스터의 타입 가져오기
        target_types = getattr(target_monster, 'type', ['CT'])
        if isinstance(target_types, str):
            target_types = [target_types]
        
        # 상성 계산 (여러 타입에 대해 최대 효과 선택)
        effectiveness = 1.0
        for target_type in target_types:
            type_effectiveness = TYPE_EFFECTIVENESS.get(skill_type, {}).get(target_type, 1.0)
            effectiveness = max(effectiveness, type_effectiveness)
        
        # 플레이어 공격력 적용
        attack_multiplier = (100 + self.attack) / 100
        
        # 몬스터 방어력 적용
        target_defense = getattr(target_monster, 'DEF', 10)
        defense_reduction = 100 / (100 + target_defense)
        
        # 난수 (0.9 ~ 1.1)
        random_factor = random.uniform(0.9, 1.1)
        
        final_damage = int(base_damage * attack_multiplier * effectiveness * defense_reduction * random_factor)
        
        return max(1, final_damage), effectiveness
    
    def use_skill(self, skill_name, target_monster):
        """스킬 사용"""
        # 스킬 찾기
        available_skills = self.get_available_skills()
        skill = None
        
        for available_skill in available_skills:
            if available_skill["name"] == skill_name:
                skill = available_skill
                break
        
        if not skill:
            return None, "스킬을 찾을 수 없습니다"
        
        # 데미지 계산
        damage, effectiveness = self.calculate_damage(skill, target_monster)
        
        # 몬스터에게 데미지 적용
        if hasattr(target_monster, 'nowhp'):
            target_monster.nowhp -= damage
            if target_monster.nowhp < 0:
                target_monster.nowhp = 0
        
        return {
            "damage": damage,
            "effectiveness": effectiveness,
            "skill": skill,
        }, "성공"
    
    def can_use_pnr(self):
        """PNR 사용 가능 여부"""
        return (self.pnr_available and 
                self.current_semester in ["1-1", "1-2"] and 
                not self.pnr_used)
    
    def use_pnr_in_battle(self):
        """전투 중 PNR 사용"""
        if not self.can_use_pnr():
            return False, "PNR 사용 불가"
        
        # 95% 확률로 성공
        if random.random() < 0.95:
            self.pnr_used = True
            self.pnr_available = False
            return True, "PNR 성공! 과목을 패스했습니다!"
        else:
            self.pnr_used = True
            self.pnr_available = False
            return False, "PNR 실패... 5% 확률로 실패했습니다."
    
    def calcGPA(self, Option):
        sum1, sum2 = 0, 0
        if Option == 1:    
            for credit, gpa in self.thisSemesterGpas:
                sum1 += GPASCORE[gpa]*credit
                sum2 += credit
        elif Option == 2:
            for credit, gpa in self.gpas:
                sum1 += GPASCORE[gpa]*credit
                sum2 += credit
        if sum2 == 0:
            return "0.00"
        return f"{(sum1 / sum2):.2f}"

    def complete_monster(self, monster_name):
        """몬스터(과목) 처치 완료"""
        self.semester_progress += 1
        
        # 경험치 획득
        self.gain_exp(50)
        
        # 체력 회복
        heal_amount = int(self.maxHp * 0.1)
        self.heal(heal_amount)
        
        # 과목별 스킬 성장
        self.grow_skill_from_monster(monster_name)
    
    def grow_skill_from_monster(self, monster_name):
        """몬스터 처치에 따른 스킬 성장"""
        skill_growth_map = {
            "프밍기": "PS",
            "이산구조": "CT",
            "데이타구조": "PS", 
            "논리회로": "CT",
            "시프": "SN",
            "시스템": "SN",
            "네트워크": "SN",
            "운영체제": "SN",
            "데이터베이스": "DS",
            "컴구조": "SN",
            "알고리즘": "PS",
            "소공": "PS",
            "캡스톤": "PS",
            "졸업연구": "DS",
            "개별연구": "DS",
            "인턴": "PS"
        }
        
        skill_type = skill_growth_map.get(monster_name)
        if skill_type and self.learned_skills[skill_type] < 5:
            self.learned_skills[skill_type] += 1
            print(f"Debug: {skill_type} 스킬이 {self.learned_skills[skill_type]} 레벨로 상승!")
    
    def advance_semester(self):
        """다음 학기로 진행"""        
        # 학기 초기화
        self.completed_semesters.append(self.current_semester)
        old_progress = self.semester_progress
        self.semester_progress = 0
        
        # 다음 학기 결정
        current_index = self.semester_order.index(self.current_semester)
        print(f"Debug: 학기 진행 - {self.current_semester}({old_progress}) -> ", end="")
        
        if current_index < len(self.semester_order) - 1:
            self.current_semester = self.semester_order[current_index + 1]
            print(f"{self.current_semester}")
            return True
        else:
            print("졸업!")
            return False        
    
    def gain_exp(self, amount):
        """경험치 획득 및 레벨업"""
        self.exp += amount
        while self.exp >= self.expToNext:
            self.level_up()
    
    def level_up(self):
        """레벨업"""
        self.exp -= self.expToNext
        self.level += 1
        
        # 스탯 증가
        old_max_hp = self.maxHp
        
        self.maxHp += 20
        self.attack += 3
        self.defense += 2
        self.speed += 1
        
        # 체력과 MP 완전 회복
        self.currentHp = self.maxHp
        
        # 다음 레벨 필요 경험치
        self.expToNext = int(self.expToNext * 1.2)

    def heal(self, amount):
        """체력 회복"""
        self.currentHp = min(self.maxHp, self.currentHp + amount)
    
    def take_damage(self, damage):
        """데미지 받기"""
        actual_damage = max(1, damage - self.defense)
        self.currentHp -= actual_damage
        self.battle_stats["damage_taken"] += actual_damage
        if self.currentHp < 0:
            self.currentHp = 0
        return actual_damage
    
    def is_alive(self):
        """생존 여부"""
        return self.currentHp > 0
    
    def gameover(self):
        """게임 오버 조건"""
        # 1-1은 학사경고 없음 (부활 가능)
        if self.current_semester == "1-1" and not self.is_alive():
            self.currentHp = self.maxHp  # 자동 부활
            return False
        
        # 학사 경고 3회
        return self.warning_count >= 3
    
    def get_final_ending(self):
        """최종 엔딩 결정"""
        if "회사원" in self.titles:
            return "취업 엔딩"
        elif "대학원생" in self.titles:
            return "대학원 엔딩" 
        elif self.deans_count >= 3:
            return "딘즈 엔딩"
        else:
            return "일반 졸업 엔딩"