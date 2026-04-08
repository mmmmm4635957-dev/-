import pygame
import math
import sys

# ----------------------
# 설정
# ----------------------
WIDTH, HEIGHT = 600, 800
FPS = 60

MAX_BULLETS = 8000

PLAYER_SPEED = 280
FOCUS_SPEED = 120

# ----------------------
# 초기화
# ----------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ----------------------
# 탄 풀
# ----------------------
class Bullet:
    __slots__ = ("x","y","dx","dy","speed","active","enemy")

    def __init__(self):
        self.active = False

pool = [Bullet() for _ in range(MAX_BULLETS)]

def get_bullet():
    for b in pool:
        if not b.active:
            b.active = True
            return b
    return None

def clear_all_bullets():
    for b in pool:
        b.active = False

# ----------------------
# 플레이어
# ----------------------
player = {
    "x": WIDTH//2,
    "y": HEIGHT-100,
    "radius": 3,
    "cool": 0,
    "invincible": 0
}

# ----------------------
# 플레이어 샷
# ----------------------
def fire_player():
    for offset in (-8, 8):
        b = get_bullet()
        if not b: return

        b.x = player["x"] + offset
        b.y = player["y"]
        b.dx = 0
        b.dy = -1
        b.speed = 500
        b.enemy = False

# ----------------------
# 탄막 패턴
# ----------------------
SPIRAL_FIRE_RATE = 3
spiral_timer = 0
def pattern_spiral(cx, cy, t, dt, ang):
    global spiral_timer

    spiral_timer -= dt
    trn = 0
    if spiral_timer > 0:
        return

    spiral_timer = SPIRAL_FIRE_RATE

    for i in range(4):
        b = get_bullet()5
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

# ----------------------
# 적 (간단 보스)
# ----------------------
enemy = {
    "x": WIDTH//2,
    "y": 150,
    "hp": 200
}

# ----------------------
# 충돌
# ----------------------
def hit(ax, ay, ar, bx, by, br):
    dx = ax - bx
    dy = ay - by
    return dx*dx + dy*dy < (ar+br)*(ar+br)

# ----------------------
# 메인
# ----------------------
t = 0

running = True
while running:
    dt = clock.tick(FPS)/1000
    t += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----------------------
    # 입력
    # ----------------------
    keys = pygame.key.get_pressed()

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

    # ----------------------
    # 플레이어 공격
    # ----------------------
    player["cool"] -= dt
    if keys[pygame.K_z] and player["cool"] <= 0:
        fire_player()
        player["cool"] = 0.08

    # ----------------------
    # 적 탄막
    # ----------------------
    pattern_spiral(enemy["x"], enemy["y"], t, 1, 420)

    # ----------------------
    # 무적 시간 감소
    # ----------------------
    if player["invincible"] > 0:
        player["invincible"] -= dt

    # ----------------------
    # 탄 업데이트
    # ----------------------
    for b in pool:
        if not b.active:
            continue

        b.x += b.dx * b.speed * dt
        b.y += b.dy * b.speed * dt

        # 화면 밖 제거
        if b.x < -10 or b.x > WIDTH+10 or b.y < -10 or b.y > HEIGHT+10:
            b.active = False
            continue

        # ----------------------
        # 충돌
        # ----------------------
        if b.enemy:
            if player["invincible"] <= 0 and hit(b.x, b.y, 3,
                                                player["x"], player["y"], player["radius"]):
                print("HIT!")

                # 💥 탄막 전체 제거
                clear_all_bullets()

                # 무적 시간
                player["invincible"] = 2
        else:
            # 플레이어 탄 → 적
            if hit(b.x, b.y, 4, enemy["x"], enemy["y"], 20):
                enemy["hp"] -= 1
                b.active = False

    # ----------------------
    # 렌더링
    # ----------------------
    screen.fill((10,10,25))

    # 적
    pygame.draw.circle(screen, (255,100,100),
                       (int(enemy["x"]), int(enemy["y"])), 20)

    # 탄
    for b in pool:
        if b.active:
            color = (255,120,120) if b.enemy else (120,200,255)
            pygame.draw.circle(screen, color,
                               (int(b.x), int(b.y)), 3)

    # 플레이어 (무적 깜빡임)
    if int(t*10) % 2 == 0 or player["invincible"] <= 0:
        pygame.draw.circle(screen, (100,255,100),
                           (int(player["x"]), int(player["y"])), 6)

    # 히트박스
    pygame.draw.circle(screen, (255,255,255),
                       (int(player["x"]), int(player["y"])),
                       player["radius"],1)

    # HP 표시
    pygame.draw.rect(screen, (255,50,50),
                     (20,20, enemy["hp"]*2, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()