# 애니메이션 테스트하는 소스코드, 아무 키나 누르면 애니메이션이 한 칸씩 넘어감
import pygame
import os
import sys
import time
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
# 기존 이미지들 그대로 유지
BACKGROUND = pygame.image.load("../background.png")
path = "Python"
images = []
for i in range(len(os.listdir(path))):
    img = pygame.image.load(f"{path}/{i}.png")
    # img = pygame.transform.scale_by(img, 10)
    images.append(img)
current_image = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                for i in range(len(images)):
                    current_image = i
                    screen.fill((113,113,113))
                    screen.blit(BACKGROUND, (32, 32))
                    screen.blit(images[current_image], (0, 0))
                    pygame.display.flip()
                    time.sleep(1/len(images))
            if event.key == pygame.K_RIGHT:
                current_image = (current_image + 1) % len(images)
            if event.key == pygame.K_LEFT:
                current_image = (current_image - 1) % len(images)
    screen.fill((113,113,113))
    screen.blit(BACKGROUND, (32, 32))
    pygame.display.flip()
pygame.quit()   