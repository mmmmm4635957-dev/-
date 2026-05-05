# entities.py
# 게임 엔티티 클래스들

import json
import random
from constants import MAX_BULLETS

# ----------------------
# 탄 풀
# ----------------------
class Bullet:
    __slots__ = ("x","y","dx","dy","speed","active","enemy","width","height","grazed")

    def __init__(self):
        self.active = False
        self.grazed = False

pool = [Bullet() for _ in range(MAX_BULLETS)]

def get_bullet():
    for b in pool:
        if not b.active:
            b.active = True
            return b
    return None

# ----------------------
# 플레이어
# ----------------------
player = {
    "x": 300,  # WIDTH//2
    "y": 700,  # HEIGHT-100
    "width": 24,
    "height": 24,
    "hitbox_radius": 12,
    "collision_radius": 4,
    "bullet_offsets": (-3, 3),
    "cool": 0,
    "invincible": 0,
    "life": 3,
    "score": 0,
    "graze": 0
}

# ----------------------
# 적 관리
# ----------------------
enemies = []

# JSON에서 적 데이터 로드
enemy_data = {}
try:
    with open('enemy.json', 'r', encoding='utf-8') as f:
        enemy_data = json.load(f)
except FileNotFoundError:
    print("enemy.json 파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    print("enemy.json 파일 형식이 잘못되었습니다.")

# 스폰된 적 추적
spawned_enemies = set()

def spawn_enemies_from_json(t, pattern_spiral, WIDTH):
    """JSON 데이터에 따라 적을 스폰"""
    if '000001' not in enemy_data:
        return
    
    for enemy_info in enemy_data['000001']:
        boss_flag = enemy_info.get('boss', False)
        is_boss = boss_flag is True
        is_mid = boss_flag == "mid"
        enemy_id = f"{enemy_info['Time']}_{enemy_info['enemy']}_{boss_flag}"
        
        # 이미 스폰되었는지 확인
        if enemy_id in spawned_enemies:
            continue
            
        # 시간 체크
        if t >= enemy_info['Time']:
            # X 좌표 계산 (ratio를 0-1 사이의 비율로 사용)
            x_pos = int(WIDTH * enemy_info['ratio'])

            # 보스 등장 시 기존 일반 몹은 점수 없이 제거
            if is_boss:
                for existing in enemies[:]:
                    if existing["active"] and not existing.get("is_boss", False):
                        enemies.remove(existing)

            # 적 생성
            if is_boss:
                hp = 400
            elif is_mid:
                hp = 80
            else:
                hp = 10

            enemy_draw_at_position(enemy_info['Time'], 0, [pattern_spiral], hp, None, is_boss, is_mid, x_pos)
            spawned_enemies.add(enemy_id)

def enemy_draw_at_position(phase, delay, patterns, hp, image, is_boss, is_mid, x_pos):
    # 적 등장 함수 (지정된 X 좌표에서)
    width = 40 if is_boss else (32 if is_mid else 24)
    height = 40 if is_boss else (32 if is_mid else 24)
    target_y = 150 if is_boss else (130 if is_mid else 100)
    hit_radius = max(width, height) / 2
    enemy = {
        "x": x_pos,
        "y": -50,  # 위쪽에서 시작
        "target_y": target_y,
        "spawn_speed": 300,  # 초기 속도
        "life": hp,
        "max_life": hp,
        "patterns": patterns,  # 탄막 패턴 함수 리스트
        "image": image,  # 이미지 (None이면 기본 사각형)
        "is_boss": is_boss,
        "is_mid": is_mid,
        "width": width,
        "height": height,
        "hit_radius": hit_radius,
        "active": False,
        "spawn_time": phase + delay,
        "phase": phase
    }
    enemies.append(enemy)

def enemy_draw(phase, delay, patterns, hp, image, is_boss):
    # 적 등장 함수
    width = 40 if is_boss else 24
    height = 40 if is_boss else 24
    enemy = {
        "x": 300,  # WIDTH // 2
        "y": -50,  # 위쪽에서 시작
        "target_y": 150 if is_boss else 100,
        "spawn_speed": 300,  # 초기 속도
        "life": hp,
        "max_life": hp,
        "patterns": patterns,  # 탄막 패턴 함수 리스트
        "image": image,  # 이미지 (None이면 기본 사각형)
        "is_boss": is_boss,
        "is_mid": False,
        "width": width,
        "height": height,
        "hit_radius": max(width, height) / 2,
        "active": False,
        "spawn_time": phase + delay,
        "phase": phase
    }
    enemies.append(enemy)