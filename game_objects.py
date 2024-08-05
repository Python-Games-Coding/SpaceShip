import pygame
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, health):
        super().__init__()
        self.image = pygame.Surface((50, 38))
        self.image.fill((0, 255, 0))  # 绿色表示玩家
        self.rect = self.image.get_rect()
        self.rect.centerx = 400
        self.rect.bottom = 600 - 10
        self.health = health

    def update(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += 5
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= 5
        if self.rect.right > 800:
            self.rect.right = 800
        if self.rect.left < 0:
            self.rect.left = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 38))
        self.image.fill((255, 0, 0))  # 红色表示敌人
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, 800 - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0 or self.rect.left > 800:
            self.rect.x = random.randrange(0, 800 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3, 3)