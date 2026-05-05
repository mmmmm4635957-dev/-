# constants.py
# 게임 설정 상수들

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

# 타이머 설정
INVINCIBLE_FLASH_INTERVAL = 0.12
TAB_COOLDOWN_TIME = 0.3
MENU_COOLDOWN_TIME = 0.15

# 탄막 패턴 설정
SPIRAL_FIRE_RATE = 3

# 초기화 관련 (main.py에서 사용)
# 듀얼 모니터에서 첫 번째 모니터에 고정하고 해상도 변경을 피하기 위해
# 전체화면 대신 현재 데스크톱 해상도 크기의 무테 창을 사용합니다.
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()
info = pygame.display.Info()
FULL_WIDTH, FULL_HEIGHT = info.current_w, info.current_h