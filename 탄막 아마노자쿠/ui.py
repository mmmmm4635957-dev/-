# ui.py
# UI 렌더링 함수들

import pygame
import math
from constants import WIDTH, HEIGHT, GAME_X_OFFSET, GAME_Y_OFFSET, PANEL_MARGIN, FULL_WIDTH, FULL_HEIGHT
from entities import player, enemies, pool
from game_logic import draw_rotated_rect

def render_menu(screen, font, small_font, menu_options, current_menu_index):
    # 메뉴 전체화면 렌더링
    title = font.render("南方南作戰", True, (255,255,255))
    screen.blit(title, (FULL_WIDTH//2 - title.get_width()//2, FULL_HEIGHT//2 - 200))
    for i, option in enumerate(menu_options):
        color = (255,255,0) if i == current_menu_index else (255,255,255)
        text = small_font.render(option, True, color)
        # 오른쪽 아래에 배치
        x = FULL_WIDTH - text.get_width() - 50 - 200
        y = FULL_HEIGHT - 100 + i * 50 - 200
        screen.blit(text, (x, y))

def render_game(game_surface, small_font, INVINCIBLE_FLASH_INTERVAL, player, enemies, pool, draw_rotated_rect):
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
    if player["invincible"] <= 0 or int(player["invincible"] / INVINCIBLE_FLASH_INTERVAL) % 2 == 0:
        pygame.draw.rect(game_surface, (100,255,100), player_rect)
    else:
        pygame.draw.rect(game_surface, (80,150,80), player_rect)

    # 히트박스 (항상 표시)
    pygame.draw.circle(game_surface, (255,255,255), (int(player["x"]), int(player["y"])), player["hitbox_radius"], 1)

    # HP 표시 (보스만)
    for e in enemies:
        if e["active"] and e["is_boss"]:
            bar_x = 20
            bar_y = 20
            bar_width = 200
            bar_height = 10
            ratio = max(0.0, min(1.0, e["life"] / e.get("max_life", 1)))
            pygame.draw.rect(game_surface, (80,80,80), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(game_surface, (255,50,50), (bar_x, bar_y, int(bar_width * ratio), bar_height))
            pygame.draw.rect(game_surface, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 2)

def render_pause_menu(game_surface, small_font, pause_menu_options, current_pause_menu_index, WIDTH, HEIGHT):
    # TAB 메뉴가 떠있으면 게임 위에 반투명 배경 추가
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    game_surface.blit(overlay, (0, 0))
    
    menu_box = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 130, 400, 220)
    pygame.draw.rect(game_surface, (20, 20, 30), menu_box)
    pygame.draw.rect(game_surface, (255, 255, 255), menu_box, 2)
    
    paused_title = small_font.render("PAUSED", True, (255,255,255))
    game_surface.blit(paused_title, (WIDTH//2 - paused_title.get_width()//2, HEIGHT//2 - 100))
    for i, option in enumerate(pause_menu_options):
        color = (255,255,0) if i == current_pause_menu_index else (255,255,255)
        text = small_font.render(option, True, color)
        x = WIDTH//2 - text.get_width()//2
        y = HEIGHT//2 - 40 + i * 50
        game_surface.blit(text, (x, y))
    
    hint_text = small_font.render("Z: 선택   ESC: 메인메뉴", True, (180,180,180))
    game_surface.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 80))

def render_panel(screen, small_font, player, enemies, GAME_X_OFFSET, WIDTH, PANEL_MARGIN, GAME_Y_OFFSET):
    # 오른쪽 패널 배경
    panel_x = GAME_X_OFFSET + WIDTH + PANEL_MARGIN
    panel_y = GAME_Y_OFFSET

    # 오른쪽 패널 내용
    if small_font:
        title = small_font.render("GAME INFO", True, (255,255,255))
        screen.blit(title, (panel_x + 20, panel_y + 20))
        score_text = small_font.render(f"Score: {player['score']}", True, (255,255,0))
        screen.blit(score_text, (panel_x + 20, panel_y + 60))
        life_label = small_font.render("Life", True, (255,100,100))
        screen.blit(life_label, (panel_x + 20, panel_y + 100))
        for i in range(player["life"]):
            pygame.draw.circle(screen, (255,100,100), (panel_x + 20 + i * 28, panel_y + 144), 10)
        graze_text = small_font.render(f"Graze: {player['graze']}", True, (180,255,180))
        screen.blit(graze_text, (panel_x + 20, panel_y + 180))
        enemies_text = small_font.render(f"Enemies: {len([e for e in enemies if e['active']])}", True, (180,180,255))
        screen.blit(enemies_text, (panel_x + 20, panel_y + 220))
        if not any(e['active'] for e in enemies):
            status_text = small_font.render("Waiting spawn...", True, (180,180,180))
            screen.blit(status_text, (panel_x + 20, panel_y + 260))

def render_game_over(screen, game_surface, font, small_font, GAME_X_OFFSET, GAME_Y_OFFSET, FULL_WIDTH, FULL_HEIGHT):
    # 게임 surface 렌더링
    screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))
    text = font.render("GAME OVER", True, (255,0,0))
    screen.blit(text, (FULL_WIDTH//2 - text.get_width()//2, FULL_HEIGHT//2 - 50))
    text2 = small_font.render("R: Restart  Q: Main Menu", True, (255,255,255))
    screen.blit(text2, (FULL_WIDTH//2 - text2.get_width()//2, FULL_HEIGHT//2))

def render_win(screen, game_surface, font, small_font, GAME_X_OFFSET, GAME_Y_OFFSET, FULL_WIDTH, FULL_HEIGHT):
    # 게임 surface 렌더링
    screen.blit(game_surface, (GAME_X_OFFSET, GAME_Y_OFFSET))
    text = font.render("YOU WIN!", True, (0,255,0))
    screen.blit(text, (FULL_WIDTH//2 - text.get_width()//2, FULL_HEIGHT//2 - 50))
    text2 = small_font.render("R: Restart  Q: Main Menu", True, (255,255,255))
    screen.blit(text2, (FULL_WIDTH//2 - text2.get_width()//2, FULL_HEIGHT//2))