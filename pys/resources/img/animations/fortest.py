# 애니메이션 테스트하는 소스코드, 아무 키나 누르면 애니메이션이 한 칸씩 넘어감
import pygame
import os
import sys
import time
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

BACKGROUND = load_image("../background.png")
STAT = load_image("../stat.png")
TEXT = load_image("../text.png")

CT = load_image("../CT.png")
DS = load_image("../DS.png")
AI = load_image("../AI.png")
PS = load_image("../PS.png")
SYS = load_image("../SYS.png")
EVENT = load_image("../EVENT.png")
STAR = load_image("../STAR.png")

ME = load_image("../monsters/ME.png")
SHIELD = load_image("items/shield.png")
MIRROR = load_image("items/mirror.png")
BUFF = []
DEBUFF = []
images = []

# 기존 좌표 및 이미지 로드는 그대로 유지
sX, sY = 32, 32
stX = sX+22
stY = sY+568
esX, esY = sX+20, sY+36
psX, psY = sX+582, sY+346

def load_images():
    # 기존 이미지들 그대로 유지
    global BACKGROUND, STAT, TEXT, CT, DS, AI, PS, SYS, EVENT, STAR, ME, SHIELD, MIRROR, BUFF, DEBUFF, images, current_image
    BACKGROUND = load_image("../background.png")
    STAT = load_image("../stat.png")
    TEXT = load_image("../text.png")

    CT = load_image("../CT.png")
    DS = load_image("../DS.png")
    AI = load_image("../AI.png")
    PS = load_image("../PS.png")
    SYS = load_image("../SYS.png")
    EVENT = load_image("../EVENT.png")
    STAR = load_image("../STAR.png")

    ME = load_image("../monsters/ME.png")

    BACKGROUND = pygame.transform.scale_by(BACKGROUND, 11)
    TEXT = pygame.transform.scale_by(TEXT, 5)
    ME = pygame.transform.scale_by(ME, 10)
    CT = pygame.transform.scale_by(CT, 4)
    DS = pygame.transform.scale_by(DS, 4)
    AI = pygame.transform.scale_by(AI, 4)
    PS = pygame.transform.scale_by(PS, 4)
    SYS = pygame.transform.scale_by(SYS, 4)
    EVENT = pygame.transform.scale_by(EVENT, 4)
    STAR = pygame.transform.scale_by(STAR, 4)

    SHIELD = load_image("items/shield.png")
    SHIELD = pygame.transform.scale_by(SHIELD, 8)
    MIRROR = load_image("items/mirror.png")
    MIRROR = pygame.transform.scale_by(MIRROR, 8)

    BUFF = []
    path = "../animations/buff"
    for i in range(len(os.listdir(path))):
        img = load_image(f"{path}/{i}.png")
        img = pygame.transform.scale_by(img, 10)
        BUFF.append(img)
    DEBUFF = []
    path = "../animations/debuff"
    for i in range(len(os.listdir(path))):
        img = load_image(f"{path}/{i}.png")
        img = pygame.transform.scale_by(img, 10)
        DEBUFF.append(img)
    path = "Python"
    images = []
    for i in range(len(os.listdir(path))):
        img = load_image(f"{path}/{i}.png")
        img = pygame.transform.scale_by(img, 11/3)
        # img = pygame.transform.scale_by(img, 10)
        images.append(img)

current_image = 0

def display_type(screen, y, x, type):
    """타입 표시 (pygame)"""
    if type == "CT":
        screen.blit(CT, (x, y))
    elif type == "DS":
        screen.blit(DS, (x, y))
    elif type == "SYS":
        screen.blit(SYS, (x, y))
    elif type == "PS":
        screen.blit(PS, (x, y))
    elif type == "*":
        screen.blit(STAR, (x, y))
    elif type == "AI":
        screen.blit(AI, (x, y))
    elif type == "EVENT":
        screen.blit(EVENT, (x, y))


load_images()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r:
                load_images()
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                for i in range(len(images)):
                    screen.fill((113,113,113))
                    screen.blit(BACKGROUND, (32, 32))
                    image = load_image("../monsters/데이타구조.png")
                    image = pygame.transform.scale_by(image, 10)
                    screen.blit(image, (esX+900-image.get_width()//2, esY+310-image.get_height()))
                    
                    defense_img = MIRROR
                    anchor_x, anchor_y = esX + 880, esY + 305
                    img_pos_x = anchor_x - defense_img.get_width()//2
                    img_pos_y = anchor_y - defense_img.get_height()
                    screen.blit(defense_img, (img_pos_x, img_pos_y))
                    current_image = i
                    screen.blit(images[current_image], (0, 0))
                    
                    screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
                    screen.blit(STAT, (esX, esY))
                    display_type(screen, esY, esX+470, "CT")
                    screen.blit(STAT, (psX, psY))
                    display_type(screen, psY, psX+470, "EVENT") 
                    screen.blit(TEXT, (sX+11, sY+536))

                    pygame.display.flip()
                    time.sleep(0.02)
            
            if event.key == pygame.K_RIGHT:
                current_image = (current_image + 1) % len(images)
            if event.key == pygame.K_LEFT:
                current_image = (current_image - 1) % len(images)
        screen.fill((113,113,113))
        screen.blit(BACKGROUND, (sX, sY))
        
        image = load_image("../monsters/데이타구조.png")
        image = pygame.transform.scale_by(image, 10)
        screen.blit(image, (esX+900-image.get_width()//2, esY+310-image.get_height()))
        defense_img = SHIELD
        anchor_x, anchor_y = esX + 880, esY + 305
        img_pos_x = anchor_x - defense_img.get_width()//2
        img_pos_y = anchor_y - defense_img.get_height()
        screen.blit(defense_img, (img_pos_x, img_pos_y))

        # 내 스프라이트
        screen.blit(ME, (sX+320-ME.get_width()//2, sY+536-ME.get_height()))
        
        # 적 상태
        screen.blit(STAT, (esX, esY))

        # 적 타입 표시
        display_type(screen, esY, esX+470, "CT")
                    
        # 플레이어 상태 (하단) - 직접 전투
        screen.blit(STAT, (psX, psY))

        # 플레이어 타입 표시
        display_type(screen, psY, psX+470, "EVENT")
        
        screen.blit(TEXT, (sX+11, sY+536))
    pygame.display.flip()
pygame.quit()   