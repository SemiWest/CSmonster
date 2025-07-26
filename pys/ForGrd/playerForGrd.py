import copy
from ForGrd.monsterForGrd import *
from ForGrd.itemForGrd import *
import random

# 플레이어 스킬 정의
""" 코파일럿이 만들어놓은거임 수정하면 될듯? -이준서"""
PLAYER_SKILLS = {
    "*": [
        {"name": "타자치기", "damage": 10, "type": "CT", "description": "한글은 500타, 영어는 독수리타법"}
    ],
    "CT": [
        {"name": "이론공격", "damage": 30, "type": "CT", "description": "기본적인 이론 공격"},
        {"name": "정리증명", "damage": 60, "type": "CT", "description": "강력한 증명 공격", "level": 3},
        {"name": "수학적귀납법", "damage": 80, "type": "CT", "description": "논리적 사고의 극한", "level": 5}
    ],
    "DS": [
        {"name": "데이터분석", "damage": 35, "type": "DS", "description": "데이터로 약점 파악"},
        {"name": "빅데이터", "damage": 70, "type": "DS", "description": "대량 데이터로 압박", "level": 3},
        {"name": "머신러닝", "damage": 90, "type": "DS", "description": "AI의 힘을 빌린 공격", "level": 5}
    ],
    "SN": [
        {"name": "시스템콜", "damage": 25, "type": "SN", "description": "시스템 명령으로 공격"},
        {"name": "네트워크공격", "damage": 55, "type": "SN", "description": "네트워크를 통한 침투", "level": 3},
        {"name": "커널해킹", "damage": 85, "type": "SN", "description": "시스템 핵심부 조작", "level": 5}
    ],
    "PS": [
        {"name": "코딩", "damage": 40, "type": "PS", "description": "기본 프로그래밍 실력"},
        {"name": "알고리즘", "damage": 65, "type": "PS", "description": "최적화된 알고리즘", "level": 3},
        {"name": "아키텍처설계", "damage": 95, "type": "PS", "description": "완벽한 시스템 설계", "level": 5}
    ],
    "AI": [
        {"name": "보안스캔", "damage": 20, "type": "AI", "description": "취약점을 찾아 공격"},
        {"name": "암호화공격", "damage": 50, "type": "AI", "description": "보안을 뚫고 침투", "level": 3},
        {"name": "해킹마스터", "damage": 75, "type": "AI", "description": "완벽한 해킹 기술", "level": 5}
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
        self.completed_semesters = []
        self.defeated_monsters = []
        
        # PNR 시스템
        self.pnr_available = True
        self.pnr_used = False
        
        # 성적 및 상태 관리
        self.semester_grades = {}
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
        
        # 전투 관련
        self.battle_stats = {
            "turns_used": 0,
            "items_used": 0,
            "damage_taken": 0
        }
        
        # 기존 호환성 유지 (일부 기능에서 필요할 수 있음)
        self.gpa = "0.0"
        self.knowhow = 100
        self.concentration = 50
        self.grade = "A+"
        self.totalhap = 0
    
    def get_current_semester_monsters(self):
        """현재 학기에서 싸워야 할 몬스터(과목) 목록"""
        if self.current_semester == "새터":
            return ["프밍기"]
        elif self.current_semester == "3-여름방학":
            return [777]
        elif self.current_semester == "4-여름방학":
            if random.random() < 0.5:
                return [888]
            else: return [999]
        else:
            return ["프밍기"]
    
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
    
    def complete_monster(self, monster_name):
        """몬스터(과목) 처치 완료"""
        self.semester_progress += 1
        self.defeated_monsters.append(monster_name)
        
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
        # 학기 성적 계산
        self.calculate_semester_grade()
        
        # 학기 초기화
        self.completed_semesters.append(self.current_semester)
        old_progress = self.semester_progress
        self.semester_progress = 0
        self.battle_stats = {"turns_used": 0, "items_used": 0, "damage_taken": 0}
        
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
    
    def calculate_semester_grade(self):
        """학기 성적 계산"""
        total_monsters = len(self.get_current_semester_monsters())
        passed_monsters = self.semester_progress
        
        if total_monsters == 0:
            return
        
        # 성적 계산
        success_rate = passed_monsters / total_monsters
        
        if success_rate >= 0.9:
            grade = "A+"
            gpa = 4.5
        elif success_rate >= 0.8:
            grade = "A"
            gpa = 4.0
        elif success_rate >= 0.7:
            grade = "B+"
            gpa = 3.5
        elif success_rate >= 0.6:
            grade = "B"
            gpa = 3.0
        elif success_rate >= 0.5:
            grade = "C"
            gpa = 2.0
        else:
            grade = "F"
            gpa = 0.0
        
        self.semester_grades[self.current_semester] = {"grade": grade, "gpa": gpa}
        
        # 장짤 체크
        if passed_monsters == 0 and total_monsters >= 2:
            self.jangzal_count += 1
            if self.jangzal_count >= 3:
                self.warning_count += 1
                self.jangzal_count = 0
        
        # 딘즈 체크
        hp_percentage = (self.currentHp / self.maxHp) * 100
        if gpa >= 4.2 or hp_percentage >= 90:
            self.deans_count += 1
            self.titles.append(f"{self.current_semester} 딘즈")
    
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
        
        # 체력이 0 이하이거나 학사 경고 3회
        return not self.is_alive() or self.warning_count >= 3
    
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