# game_logic.py
# 게임 로직 함수들

import math
import pygame
from constants import SPIRAL_FIRE_RATE
from entities import get_bullet, player, enemies

# ----------------------
# 플레이어 샷
# ----------------------
def fire_player():
    for offset in player["bullet_offsets"]:
        b = get_bullet()
        if not b:
            return

        b.x = player["x"] + offset
        b.y = player["y"]
        b.dx = 0
        b.dy = -1
        b.speed = 500
        b.enemy = False
        b.width = 6
        b.height = 12
        b.grazed = False

# ----------------------
# 탄막 패턴
# ----------------------
spiral_timer = 0
def pattern_spiral(cx, cy, t, dt, ang):
    global spiral_timer

    spiral_timer -= dt
    if spiral_timer > 0:
        return

    spiral_timer = SPIRAL_FIRE_RATE / 60  # FPS에 맞춰 조정, 원래 3이었음

    trn = 0
    for i in range(4):
        b = get_bullet()
        if not b: return
        if trn == 0:
            angle = t * ang + i * 90
            trn = 1
        else:
            angle = t * -ang + i * 90
            trn = 0
        rad = math.radians(angle)

        b.x = cx
        b.y = cy
        b.dx = math.cos(rad)
        b.dy = math.sin(rad)
        b.speed = 200
        b.enemy = True
        b.width = 8
        b.height = 14
        b.grazed = False

straight_timer = 0
def pattern_straight(cx, cy, t, dt, ang):
    global straight_timer

    straight_timer -= dt
    if straight_timer > 0:
        return

    straight_timer = 0.5  # 0.5초마다

    for i in range(3):
        b = get_bullet()
        if not b: return
        angle = -90 + (i - 1) * 30  # 아래쪽으로 퍼짐
        rad = math.radians(angle)

        b.x = cx
        b.y = cy
        b.dx = math.cos(rad)
        b.dy = math.sin(rad)
        b.speed = 150
        b.enemy = True
        b.width = 8
        b.height = 14
        b.grazed = False

# ----------------------
# 충돌
# ----------------------
def hit(ax, ay, ar, bx, by, br):
    dx = ax - bx
    dy = ay - by
    return dx*dx + dy*dy < (ar+br)*(ar+br)

def draw_rotated_rect(surface, color, cx, cy, width, height, angle_deg):
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    hw = width / 2
    hh = height / 2
    corners = [
        (-hw, -hh),
        (hw, -hh),
        (hw, hh),
        (-hw, hh)
    ]
    points = []
    for x, y in corners:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        points.append((int(cx + rx), int(cy + ry)))
    pygame.draw.polygon(surface, color, points)

# ----------------------
# 게임 업데이트 로직
# ----------------------
def update_game(dt, t, keys, WIDTH, HEIGHT, PLAYER_SPEED, FOCUS_SPEED):
    # 입력
    speed = PLAYER_SPEED
    if keys[pygame.K_LSHIFT]:
        speed = FOCUS_SPEED

    if keys[pygame.K_LEFT]:
        player["x"] -= speed * dt
    if keys[pygame.K_RIGHT]:
        player["x"] += speed * dt
    if keys[pygame.K_UP]:
        player["y"] -= speed * dt
    if keys[pygame.K_DOWN]:
        player["y"] += speed * dt

    # 플레이어 위치 제한 (플레이어 형체가 화면 밖으로 나가지 않도록)
    player["x"] = max(player["width"] / 2, min(WIDTH - player["width"] / 2, player["x"]))
    player["y"] = max(player["height"] / 2, min(HEIGHT - player["height"] / 2, player["y"]))

    # 플레이어 공격
    player["cool"] -= dt
    if keys[pygame.K_z] and player["cool"] <= 0:
        fire_player()
        player["cool"] = 0.08

    # 적 등장 및 업데이트
    for e in enemies[:]:
        if not e["active"] and t >= e["spawn_time"]:
            e["active"] = True

        if e["active"]:
            # 등장 효과: 위에서 아래로 감속
            if e["y"] < e["target_y"]:
                e["spawn_speed"] -= 200 * dt  # 감속
                if e["spawn_speed"] < 50:
                    e["spawn_speed"] = 50
                e["y"] += e["spawn_speed"] * dt
                if e["y"] > e["target_y"]:
                    e["y"] = e["target_y"]
            elif not e["is_boss"] and not e.get("is_mid", False):
                # 일반 적만 목표 지점 이후에도 계속 아래로 이동
                e["y"] += 120 * dt
                if e["y"] > HEIGHT + 50:
                    enemies.remove(e)
                    continue

            # 탄막 발사
            for pattern in e["patterns"]:
                pattern(e["x"], e["y"], t, dt, 420)

    # 승리 체크 (보스 격파로 승리)
    boss_alive = any(e["active"] and e["is_boss"] for e in enemies)
    if not boss_alive and any(e["is_boss"] for e in enemies):  # 보스가 있었고 모두 죽었으면 승리
        return "win"

    # 무적 시간 감소
    if player["invincible"] > 0:
        player["invincible"] -= dt

    return None

def update_bullets(dt, WIDTH, HEIGHT, pool):
    for b in pool:
        if not b.active:
            continue

        b.x += b.dx * b.speed * dt
        b.y += b.dy * b.speed * dt

        # 화면 밖 제거
        if b.x < -10 or b.x > WIDTH+10 or b.y < -10 or b.y > HEIGHT+10:
            b.active = False
            continue

        # 충돌
        if b.enemy:
            graze_dist = player["hitbox_radius"] + 18
            dist2 = (b.x - player["x"])**2 + (b.y - player["y"])**2
            if dist2 < (player["collision_radius"] + b.width/2)**2:
                if player["invincible"] <= 0 and hit(b.x, b.y, b.width/2,
                                                    player["x"], player["y"], player["collision_radius"]):
                    player["life"] -= 1
                    player["invincible"] = 2
                    if player["life"] <= 0:
                        return "game_over"
            elif dist2 < graze_dist**2 and not b.grazed:
                b.grazed = True
                player["graze"] += 1
                player["score"] += 5
        else:
            # 플레이어 탄 → 적
            for e in enemies[:]:  # 복사본으로 순회
                if e["active"] and hit(b.x, b.y, 4, e["x"], e["y"], e["hit_radius"]):
                    e["life"] -= 1
                    b.active = False
                    if e["life"] <= 0:
                        player["score"] += 10 if not e["is_boss"] else 50  # 보스는 더 높은 점수
                        enemies.remove(e)
                    break

    return None