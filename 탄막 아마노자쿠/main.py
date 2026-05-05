# main.py
# 메인 게임 루프

import pygame
import os
from constants import *
from entities import player, enemies, pool, enemy_draw, spawn_enemies_from_json, spawned_enemies
from game_logic import update_game, update_bullets, pattern_spiral, draw_rotated_rect
from ui import render_menu, render_game, render_pause_menu, render_panel, render_game_over, render_win

# ----------------------
# 초기화
# ----------------------
# 듀얼 모니터에서 첫 번째 모니터에 고정하고 해상도 변경을 피하기 위해
# 전체화면 대신 현재 데스크톱 해상도 크기의 무테 창을 사용합니다.
screen = pygame.display.set_mode((FULL_WIDTH, FULL_HEIGHT), pygame.NOFRAME)
game_surface = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 폰트
font = pygame.font.SysFont(['Malgun Gothic', 'Arial', 'sans-serif'], 48)
small_font = pygame.font.SysFont(['Malgun Gothic', 'Arial', 'sans-serif'], 36)

# ----------------------
# 메인
# ----------------------

def reset_game_state():
    global t, tab_cooldown, menu_cooldown, pause_menu_cooldown, current_pause_menu_index, current_menu_index
    t = 0
    tab_cooldown = 0.0
    menu_cooldown = 0.0
    pause_menu_cooldown = 0.0
    current_pause_menu_index = 0
    current_menu_index = 0
    player["x"] = WIDTH // 2
    player["y"] = HEIGHT - 100
    player["life"] = 3
    player["invincible"] = 0
    player["cool"] = 0
    player["score"] = 0
    player["graze"] = 0
    player["hitbox_radius"] = player["width"] // 2
    player["collision_radius"] = 4
    player["bullet_offsets"] = (-3, 3)
    enemies.clear()
    spawned_enemies.clear()
    for b in pool:
        b.active = False


t = 0
game_state = STATE_MENU
tab_cooldown = 0.0

# 메뉴 시스템
menu_options = ["Start Game", "Quit"]
current_menu_index = 0
menu_cooldown = 0.0

# 일시정지 메뉴 옵션
pause_menu_options = ["계속하기", "다시하기", "메인메뉴"]
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
                    reset_game_state()
                    game_state = STATE_GAME
                    # 초기 적 추가는 JSON에서 자동으로 처리됨
                    menu_cooldown = MENU_COOLDOWN_TIME
                elif current_menu_index == 1:  # Quit
                    running = False
            elif keys[pygame.K_ESCAPE]:
                running = False  # ESC로 바로 나가기
                menu_cooldown = MENU_COOLDOWN_TIME

        if menu_cooldown > 0:
            menu_cooldown -= dt

    elif game_state == STATE_GAME:
        # 게임 로직
        keys = pygame.key.get_pressed()
        
        # JSON 데이터에 따라 적 스폰
        spawn_enemies_from_json(t, pattern_spiral, WIDTH)
        
        result = update_game(dt, t, keys, WIDTH, HEIGHT, PLAYER_SPEED, FOCUS_SPEED)
        if result:
            game_state = result

        if tab_cooldown > 0:
            tab_cooldown -= dt

        # 탄 업데이트
        result = update_bullets(dt, WIDTH, HEIGHT, pool)
        if result:
            game_state = result

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
                if current_pause_menu_index == 0:  # 계속하기
                    game_state = STATE_GAME
                    pause_menu_cooldown = MENU_COOLDOWN_TIME
                elif current_pause_menu_index == 1:  # 다시하기
                    reset_game_state()
                    game_state = STATE_GAME
                    enemy_draw(0, 0, [pattern_spiral], 200, None, True)
                    pause_menu_cooldown = MENU_COOLDOWN_TIME
                elif current_pause_menu_index == 2:  # 메인메뉴
                    game_state = STATE_MENU
                    # 메인메뉴로 갈 때 적 초기화
                    enemies.clear()
                    for b in pool:
                        b.active = False
                    pause_menu_cooldown = MENU_COOLDOWN_TIME
            elif keys[pygame.K_ESCAPE]:
                current_pause_menu_index = 2  # ESC로 메인메뉴 선택
                pause_menu_cooldown = MENU_COOLDOWN_TIME

        if pause_menu_cooldown > 0:
            pause_menu_cooldown -= dt

    elif game_state == STATE_GAME_OVER:
        # 게임 오버 메뉴
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game_state()
            game_state = STATE_GAME
            enemy_draw(0, 0, [pattern_spiral], 200, None, True)
        if keys[pygame.K_q]:
            reset_game_state()
            game_state = STATE_MENU

    elif game_state == STATE_WIN:
        # 승리 메뉴
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game_state()
            game_state = STATE_GAME
            enemy_draw(0, 0, [pattern_spiral], 200, None, True)
        if keys[pygame.K_q]:
            reset_game_state()
            game_state = STATE_MENU

    # 렌더링
    screen.fill((0,0,0))
    game_surface.fill((10,10,25))

    if game_state == STATE_MENU:
        render_menu(screen, font, small_font, menu_options, current_menu_index)

    if game_state in [STATE_GAME, STATE_PAUSE]:
        render_game(game_surface, small_font, INVINCIBLE_FLASH_INTERVAL, player, enemies, pool, draw_rotated_rect)

        if game_state == STATE_PAUSE:
            render_pause_menu(game_surface, small_font, pause_menu_options, current_pause_menu_index, WIDTH, HEIGHT)

        # 게임 surface를 화면에 오프셋 위치로 blit
        screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))

        render_panel(screen, small_font, player, enemies, GAME_X_OFFSET, WIDTH, PANEL_MARGIN, GAME_Y_OFFSET)

    elif game_state == STATE_GAME_OVER:
        render_game_over(screen, game_surface, font, small_font, GAME_X_OFFSET, GAME_Y_OFFSET, FULL_WIDTH, FULL_HEIGHT)

    elif game_state == STATE_WIN:
        render_win(screen, game_surface, font, small_font, GAME_X_OFFSET, GAME_Y_OFFSET, FULL_WIDTH, FULL_HEIGHT)

    pygame.display.flip()

pygame.quit()