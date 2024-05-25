import pygame
import random
import os

FPS = 60
WIDTH = 700
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game Initialization and Create Window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceShip")
clock = pygame.time.Clock()

# Load images
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.ico")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
enemy_img = pygame.image.load(os.path.join("img", "enemy.ico")).convert()
enemy_img.set_colorkey(BLACK)
enemy_bullet_img = pygame.image.load(os.path.join("img", "enemy-bullet.png")).convert()
enemy_bullet_img.set_colorkey(BLACK)
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
expl_anim = {'lg': [], 'sm': [], 'player': []}
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {
    'shield': pygame.image.load(os.path.join("img", "shield.png")).convert(),
    'gun': pygame.image.load(os.path.join("img", "gun.png")).convert()
}

# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.4)

font_name = os.path.join("font.ttf")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_health(surf, hp, x, y, color):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y, scale=1):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + (img_rect.width * scale + 5) * i  # 5 像素的间距
        img_rect.y = y
        img_resized = pygame.transform.scale(img, (int(img_rect.width * scale), int(img_rect.height * scale)))
        surf.blit(img_resized, img_rect)

def get_highscores():
    try:
        with open("HighScore.txt", "r") as file:
            highscores = [int(line.strip()) for line in file.readlines()]
            return highscores
    except FileNotFoundError:
        return []
    except Exception as e:
        print("Failed to read highscore:", e)
        return []

def update_highscore(score):
    highscores = get_highscores()
    highscores.append(score)
    highscores.sort(reverse=True)
    with open("HighScore.txt", "w") as file:
        for score in highscores:
            file.write(f"{score}\n")

def get_highest_score():
    highscores = get_highscores()
    if highscores:
        return highscores[0]
    return 0

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, 'SpaceShip!', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '← → to move, Press "Space" to fire bullet', 22, WIDTH / 2, HEIGHT / 2)
    
    # 读取最高分数并显示在屏幕上
    highscore = get_highest_score()
    draw_text(screen, f'HighScore: {highscore}', 22, WIDTH / 2, HEIGHT * 3 / 4)
    
    draw_text(screen, 'Press SPACE key to start the game!', 18, WIDTH / 2, HEIGHT * 3 / 4 + 30)
    draw_text(screen, 'Press Esc key to quit game', 18, WIDTH / 2, HEIGHT * 3 / 4 + 60)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        # Get Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return False

def save_highscore(score):
    try:
        with open("HighScore.txt", "a") as f:
            f.write(f"{score}\n")
    except Exception as e:
        print("Failed to save highscore:", e)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not self.hidden:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(rock_imgs)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_orig, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (10, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(enemy_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH // 2  # 初始位置设置为屏幕中央
        self.rect.bottom = 100  # 确保敌机在屏幕范围内
        self.health = 100
        self.lives = 3

    def update(self):
        # 敌人不移动
        pass

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(enemy_bullet_img, (10, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = expl_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

def main():
    global all_sprites, bullets, enemy_bullets
    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)
    enemy = Enemy()
    all_sprites.add(enemy)

    for i in range(8):
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)

    enemy_shoot_event = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_shoot_event, 1000)  # 每1000毫秒（1秒）触发一次

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
            elif event.type == enemy_shoot_event:
                enemy.shoot()

        all_sprites.update()

        # Check for collision between player bullets and enemy
        hits = pygame.sprite.groupcollide(bullets, [enemy], True, False)
        for hit in hits:
            enemy.health -= 10

        # Check for collision between enemy bullets and player
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.health -= 10
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
                player.hide()

        # Check if the player collides with rocks
        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.health -= 10
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
                player.hide()
            rock = Rock()
            all_sprites.add(rock)
            rocks.add(rock)

        if enemy.health <= 0:
            enemy.lives -= 1
            enemy.health = 100
            enemy.rect.centerx = random.randrange(WIDTH)
            enemy.rect.bottom = 100  # 确保敌机重生在屏幕范围内

        if enemy.lives <= 0:
            running = False

        if player.lives <= 0:
            running = False

        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_health(screen, player.health, 5, 5, GREEN)
        draw_health(screen, enemy.health, 5, 25, RED)
        draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
        draw_lives(screen, enemy.lives, enemy_img, WIDTH - 100, 45, scale=0.5)
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    while True:
        show_go_screen = draw_init()
        if show_go_screen:
            break
        main()
