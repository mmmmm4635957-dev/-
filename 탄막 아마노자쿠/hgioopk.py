import pygame
import math
import sys
import os

# ----------------------
# 설정
# ----------------------
WIDTH, HEIGHT = 600, 800
FPS = 60

MAX_BULLETS = 8000

PLAYER_SPEED = 280
FOCUS_SPEED = 120

# 게임창 오프셋
GAME_X_OFFSET = 200
GAME_Y_OFFSET = 50
PANEL_MARGIN = 20
PANEL_WIDTH = 300
PANEL_HEIGHT = HEIGHT

# 게임 상태
STATE_MENU = "menu"
STATE_GAME = "game"
STATE_PAUSE = "pause"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"

# ----------------------
# 초기화
# ----------------------
# 듀얼 모니터에서 첫 번째 모니터에 고정하고 해상도 변경을 피하기 위해
# 전체화면 대신 현재 데스크톱 해상도 크기의 무테 창을 사용합니다.
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()
info = pygame.display.Info()
FULL_WIDTH, FULL_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((FULL_WIDTH, FULL_HEIGHT), pygame.NOFRAME)
game_surface = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 폰트
font = pygame.font.SysFont(['Malgun Gothic', 'Arial', 'sans-serif'], 48)
small_font = pygame.font.SysFont(['Malgun Gothic', 'Arial', 'sans-serif'], 36)

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
    "x": WIDTH//2,
    "y": HEIGHT-100,
    "width": 24,
    "height": 24,
    "hitbox_radius": 6,
    "cool": 0,
    "invincible": 0,
    "hp": 3,
    "score": 0,
    "graze": 0
}

# ----------------------
# 플레이어 샷
# ----------------------
def fire_player():
    for offset in (-8, 8):
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
SPIRAL_FIRE_RATE = 3
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
# 적 관리
# ----------------------
enemies = []

def enemy_draw(phase, delay, patterns, hp, image, is_boss):
    # 적 등장 함수
    enemy = {
        "x": WIDTH // 2,
        "y": -50,  # 위쪽에서 시작
        "target_y": 150 if is_boss else 100,
        "spawn_speed": 300,  # 초기 속도
        "hp": hp,
        "patterns": patterns,  # 탄막 패턴 함수 리스트
        "image": image,  # 이미지 (None이면 기본 사각형)
        "is_boss": is_boss,
        "width": 40 if is_boss else 24,
        "height": 40 if is_boss else 24,
        "hit_radius": 14 if is_boss else 9,
        "active": False,
        "spawn_time": phase + delay,
        "phase": phase
    }
    enemies.append(enemy)

# 예시 적 추가 (나중에 호출)
# enemy_draw(0, 0, [pattern_spiral], 200, None, True)

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
# 메인
# ----------------------
INVINCIBLE_FLASH_INTERVAL = 0.12
TAB_COOLDOWN_TIME = 0.3

t = 0
game_state = STATE_MENU
tab_cooldown = 0.0

# 메뉴 시스템
menu_options = ["Start Game", "Quit"]
current_menu_index = 0
menu_cooldown = 0.0
MENU_COOLDOWN_TIME = 0.15

# 일시정지 메뉴 옵션
pause_menu_options = ["Resume", "Main Menu"]
current_pause_menu_index = 0
pause_menu_cooldown = 0.0

running = True
while running:
    dt = clock.tick(FPS)/1000
    t += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB and tab_cooldown <= 0:
                if game_state == STATE_GAME:
                    game_state = STATE_PAUSE
                    tab_cooldown = TAB_COOLDOWN_TIME
                elif game_state == STATE_PAUSE:
                    game_state = STATE_GAME
                    tab_cooldown = TAB_COOLDOWN_TIME

    if tab_cooldown > 0:
        tab_cooldown -= dt

    if game_state == STATE_MENU:
        # 메뉴 선택
        keys = pygame.key.get_pressed()
        if menu_cooldown <= 0:
            if keys[pygame.K_UP]:
                current_menu_index = (current_menu_index - 1) % len(menu_options)
                menu_cooldown = MENU_COOLDOWN_TIME
            elif keys[pygame.K_DOWN]:
                current_menu_index = (current_menu_index + 1) % len(menu_options)
                menu_cooldown = MENU_COOLDOWN_TIME
            elif keys[pygame.K_z]:
                if current_menu_index == 0:  # Start Game
                    game_state = STATE_GAME
                    # 초기 적 추가
                    enemy_draw(0, 0, [pattern_spiral], 200, None, True)
                elif current_menu_index == 1:  # Quit
                    running = False
            elif keys[pygame.K_ESCAPE]:
                running = False  # ESC로 바로 나가기

        if menu_cooldown > 0:
            menu_cooldown -= dt


    elif game_state == STATE_GAME:
        # 게임 로직
        # 입력
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

        # 플레이어 위치 제한
        player["x"] = max(0, min(WIDTH, player["x"]))
        player["y"] = max(0, min(HEIGHT, player["y"]))

        # 플레이어 공격
        player["cool"] -= dt
        if keys[pygame.K_z] and player["cool"] <= 0:
            fire_player()
            player["cool"] = 0.08

        # 적 등장 및 업데이트
        for e in enemies:
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

                # 탄막 발사
                for pattern in e["patterns"]:
                    pattern(e["x"], e["y"], t, dt, 420)

        # 승리 체크
        if not any(e["active"] for e in enemies):
            game_state = STATE_WIN

        # 무적 시간 감소
        if player["invincible"] > 0:
            player["invincible"] -= dt

        if tab_cooldown > 0:
            tab_cooldown -= dt

        # 탄 업데이트
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
                if dist2 < (player["hitbox_radius"] + b.width/2)**2:
                    if player["invincible"] <= 0 and hit(b.x, b.y, b.width/2,
                                                        player["x"], player["y"], player["hitbox_radius"]):
                        print("HIT!")
                        player["hp"] -= 1
                        player["invincible"] = 2
                        if player["hp"] <= 0:
                            game_state = STATE_GAME_OVER
                elif dist2 < graze_dist**2 and not b.grazed:
                    b.grazed = True
                    player["graze"] += 1
                    player["score"] += 5
            else:
                # 플레이어 탄 → 적
                for e in enemies[:]:  # 복사본으로 순회
                    if e["active"] and hit(b.x, b.y, 4, e["x"], e["y"], e["hit_radius"]):
                        e["hp"] -= 1
                        b.active = False
                        if e["hp"] <= 0:
                            player["score"] += 10 if not e["is_boss"] else 50  # 보스는 더 높은 점수
                            enemies.remove(e)
                        break

    elif game_state == STATE_PAUSE:
        # 부가 메뉴
        keys = pygame.key.get_pressed()
        if pause_menu_cooldown <= 0:
            if keys[pygame.K_UP]:
                current_pause_menu_index = (current_pause_menu_index - 1) % len(pause_menu_options)
                pause_menu_cooldown = MENU_COOLDOWN_TIME
            elif keys[pygame.K_DOWN]:
                current_pause_menu_index = (current_pause_menu_index + 1) % len(pause_menu_options)
                pause_menu_cooldown = MENU_COOLDOWN_TIME
            elif keys[pygame.K_z]:
                if current_pause_menu_index == 0:  # Resume
                    game_state = STATE_GAME
                elif current_pause_menu_index == 1:  # Main Menu
                    game_state = STATE_MENU
            elif keys[pygame.K_ESCAPE]:
                game_state = STATE_MENU  # ESC로 메인 메뉴

        if pause_menu_cooldown > 0:
            pause_menu_cooldown -= dt

    elif game_state == STATE_GAME_OVER:
        # 게임 오버 메뉴
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # 재시작
            game_state = STATE_GAME
            t = 0
            player["x"] = WIDTH//2
            player["y"] = HEIGHT-100
            player["hp"] = 3
            player["invincible"] = 0
            player["score"] = 0
            enemies.clear()
            # 탄 초기화
            for b in pool:
                b.active = False
            enemy_draw(0, 0, [pattern_spiral], 200, None, True)
        if keys[pygame.K_q]:
            game_state = STATE_MENU

    elif game_state == STATE_WIN:
        # 승리 메뉴
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # 재시작
            game_state = STATE_GAME
            t = 0
            player["x"] = WIDTH//2
            player["y"] = HEIGHT-100
            player["hp"] = 3
            player["invincible"] = 0
            player["score"] = 0
            enemies.clear()
            # 탄 초기화
            for b in pool:
                b.active = False
            enemy_draw(0, 0, [pattern_spiral], 200, None, True)
        if keys[pygame.K_q]:
            game_state = STATE_MENU

    # 렌더링
    screen.fill((0,0,0))
    game_surface.fill((10,10,25))

    if game_state == STATE_MENU:
        # 메뉴 전체화면 렌더링
        title = font.render("탄막 아마노자쿠", True, (255,255,255))
        screen.blit(title, (FULL_WIDTH//2 - title.get_width()//2, FULL_HEIGHT//2 - 200))
        for i, option in enumerate(menu_options):
            color = (255,255,0) if i == current_menu_index else (255,255,255)
            text = small_font.render(option, True, color)
            # 오른쪽 아래에 배치
            x = FULL_WIDTH - text.get_width() - 50 - 200
            y = FULL_HEIGHT - 100 + i * 50 - 200
            screen.blit(text, (x, y))
        # 폰트 없으면 그냥 검은 화면

    elif game_state == STATE_PAUSE:
        # 게임 surface 렌더링
        screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))
        # 패널 렌더링
        panel_x = GAME_X_OFFSET + WIDTH + PANEL_MARGIN
        panel_y = GAME_Y_OFFSET
        pygame.draw.rect(screen, (20,20,40), (panel_x, panel_y, PANEL_WIDTH, PANEL_HEIGHT))
        pygame.draw.rect(screen, (80,80,120), (panel_x, panel_y, PANEL_WIDTH, PANEL_HEIGHT), 2)
        if small_font:
            title = small_font.render("GAME INFO", True, (255,255,255))
            screen.blit(title, (panel_x + 20, panel_y + 20))
            score_text = small_font.render(f"Score: {player['score']}", True, (255,255,0))
            screen.blit(score_text, (panel_x + 20, panel_y + 60))
            hp_text = small_font.render(f"Life: {player['hp']}", True, (255,100,100))
            screen.blit(hp_text, (panel_x + 20, panel_y + 100))
            graze_text = small_font.render(f"Graze: {player['graze']}", True, (180,255,180))
            screen.blit(graze_text, (panel_x + 20, panel_y + 140))
            enemies_text = small_font.render(f"Enemies: {len([e for e in enemies if e['active']])}", True, (180,180,255))
            screen.blit(enemies_text, (panel_x + 20, panel_y + 180))
            if not any(e['active'] for e in enemies):
                status_text = small_font.render("Waiting spawn...", True, (180,180,180))
                screen.blit(status_text, (panel_x + 20, panel_y + 220))

        # 일시정지 메뉴 렌더링 (오른쪽 아래)
        for i, option in enumerate(pause_menu_options):
            color = (255,255,0) if i == current_pause_menu_index else (255,255,255)
            text = small_font.render(option, True, color)
            x = FULL_WIDTH - text.get_width() - 50
            y = FULL_HEIGHT - 100 + i * 50
            screen.blit(text, (x, y))

    elif game_state in [STATE_GAME]:
        # 적
        for e in enemies:
            if e["active"]:
                if e["image"]:
                    game_surface.blit(e["image"], (int(e["x"] - e["image"].get_width()//2), int(e["y"] - e["image"].get_height()//2)))
                else:
                    color = (255,100,100) if e["is_boss"] else (200,100,100)
                    border = (255,180,180) if e["is_boss"] else (220,160,160)
                    rect = pygame.Rect(int(e["x"] - e["width"]/2), int(e["y"] - e["height"]/2), e["width"], e["height"])
                    pygame.draw.rect(game_surface, color, rect)
                    pygame.draw.rect(game_surface, border, rect, 2)
                    inner = rect.inflate(-6, -6)
                    pygame.draw.rect(game_surface, (min(color[0]+20,255), min(color[1]+20,255), min(color[2]+20,255)), inner)
        # 탄
        for b in pool:
            if b.active:
                color = (255,120,120) if b.enemy else (120,200,255)
                angle = math.degrees(math.atan2(b.dy, b.dx)) - 90
                draw_rotated_rect(game_surface, color, b.x, b.y, b.width, b.height, angle)
                if not b.enemy:
                    draw_rotated_rect(game_surface, (180,230,255), b.x, b.y, b.width, b.height, angle)

        # 플레이어 (임시 사각형)
        player_rect = pygame.Rect(int(player["x"] - player["width"]/2), int(player["y"] - player["height"]/2), player["width"], player["height"])
        if player["invincible"] <= 0 or int(player["invincible"] / 0.12) % 2 == 0:
            pygame.draw.rect(game_surface, (100,255,100), player_rect)
        else:
            pygame.draw.rect(game_surface, (80,150,80), player_rect)

        # 히트박스 (항상 표시)
        pygame.draw.circle(game_surface, (255,255,255), (int(player["x"]), int(player["y"])), player["hitbox_radius"], 1)

        # HP 표시 (보스만)
        for e in enemies:
            if e["active"] and e["is_boss"]:
                pygame.draw.rect(game_surface, (255,50,50), (20,20, e["hp"]*2, 10))

        # 플레이어 HP 표시 (왼쪽)
        for i in range(player["hp"]):
            pygame.draw.circle(game_surface, (255,100,100), (30 + i*25, 30), 10)

        # 점수 표시 (오른쪽)
        if small_font:
            score_text = small_font.render(f"Score: {player['score']}", True, (255,255,255))
            game_surface.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

        # 게임 surface를 화면에 오프셋 위치로 blit
        screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))

        # 오른쪽 패널 배경
        panel_x = GAME_X_OFFSET + WIDTH + PANEL_MARGIN
        panel_y = GAME_Y_OFFSET
        pygame.draw.rect(screen, (20,20,40), (panel_x, panel_y, PANEL_WIDTH, PANEL_HEIGHT))
        pygame.draw.rect(screen, (80,80,120), (panel_x, panel_y, PANEL_WIDTH, PANEL_HEIGHT), 2)

        # 오른쪽 패널 내용
        if game_state in [STATE_GAME, STATE_PAUSE]:
            if small_font:
                title = small_font.render("GAME INFO", True, (255,255,255))
                screen.blit(title, (panel_x + 20, panel_y + 20))
                score_text = small_font.render(f"Score: {player['score']}", True, (255,255,0))
                screen.blit(score_text, (panel_x + 20, panel_y + 60))
                hp_text = small_font.render(f"Life: {player['hp']}", True, (255,100,100))
                screen.blit(hp_text, (panel_x + 20, panel_y + 100))
                graze_text = small_font.render(f"Graze: {player['graze']}", True, (180,255,180))
                screen.blit(graze_text, (panel_x + 20, panel_y + 140))
                enemies_text = small_font.render(f"Enemies: {len([e for e in enemies if e['active']])}", True, (180,180,255))
                screen.blit(enemies_text, (panel_x + 20, panel_y + 180))
                if not any(e['active'] for e in enemies):
                    status_text = small_font.render("Waiting spawn...", True, (180,180,180))
                    screen.blit(status_text, (panel_x + 20, panel_y + 220))

    elif game_state == STATE_GAME_OVER:
        # 게임 surface 렌더링
        screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))
        text = font.render("GAME OVER", True, (255,0,0))
        screen.blit(text, (FULL_WIDTH//2 - text.get_width()//2, FULL_HEIGHT//2 - 50))
        text2 = small_font.render("R: Restart  Q: Main Menu", True, (255,255,255))
        screen.blit(text2, (FULL_WIDTH//2 - text2.get_width()//2, FULL_HEIGHT//2))

    elif game_state == STATE_WIN:
        # 게임 surface 렌더링
        screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))
        text = font.render("YOU WIN!", True, (0,255,0))
        screen.blit(text, (FULL_WIDTH//2 - text.get_width()//2, FULL_HEIGHT//2 - 50))
        text2 = small_font.render("R: Restart  Q: Main Menu", True, (255,255,255))
        screen.blit(text2, (FULL_WIDTH//2 - text2.get_width()//2, FULL_HEIGHT//2))

    pygame.display.flip()