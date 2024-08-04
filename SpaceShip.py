import pygame
import random
import os
import pickle
from tkinter import Tk, simpledialog
import AI_code

# Game Initialization and Create Window
FPS = 60
WIDTH = 800
HEIGHT = 600
# TESTING
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

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
global easy_bg, hard_bg, hardcore_bg, normal_bg
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
normal_bg = pygame.mixer.Sound(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(1.4)

easy_bg = pygame.mixer.Sound(os.path.join('sound', 'easy_background.ogg'))
hard_bg = pygame.mixer.Sound(os.path.join('sound', 'hard_background.ogg'))
hardcore_bg = pygame.mixer.Sound(os.path.join('sound', 'hardcore_background.ogg'))

font_name = os.path.join(".spaceship/font", "font.ttf")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health(surf, hp, x, y, color):
    if hp < 0:
        hp = 0
    if hp > 100:
        hp = 100
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if hp <= 50:  # 在血量低于等于50时显示为红色
        pygame.draw.rect(surf, RED, fill_rect)
    else:
        pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def get_highscores():
    try:
        with open("4869676853636F7265.dat", "rb") as file:
            highscores = pickle.load(file)
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
    with open("4869676853636F7265.dat", "wb") as file:
        pickle.dump(highscores, file)

def get_highest_score():
    highscores = get_highscores()
    if highscores:
        return highscores[0]
    return 0

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, 'SpaceShip!', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '← → to move, Press "Space" to fire bullet', 22, WIDTH / 2, HEIGHT / 2)
    highscore = get_highest_score()
    draw_text(screen, f'HighScore: {highscore}', 22, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text(screen, 'Press SPACE key to start the game!', 18, WIDTH / 2, HEIGHT * 3 / 4 + 30)
    draw_text(screen, 'Press Esc key to quit game', 18, WIDTH / 2, HEIGHT * 3 / 4 + 60)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return False
    return False

def draw_difficulty():
    screen.blit(background_img, (0, 0))
    draw_text(screen, 'Select Difficulty', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '1. Easy Mode', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, '2. Normal Mode', 22, WIDTH / 2, HEIGHT / 2 + 30)
    draw_text(screen, '3. Hard Mode', 22, WIDTH / 2, HEIGHT / 2 + 60)
    draw_text(screen, '4. HardCore Mode', 22, WIDTH / 2, HEIGHT / 2 + 90)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    easy_bg.play()
                    normal_bg.stop()
                    return 200  # Easy difficulty gives 150 health
                if event.key == pygame.K_2:
                    return 100  # Normal difficulty gives 100 health
                if event.key == pygame.K_3:
                    hard_bg.play()
                    normal_bg.stop()
                    return 50   # Hard difficulty gives 50 health
                if event.key == pygame.K_4:
                    hardcore_bg.play()
                    normal_bg.stop()
                    return 25   
    return 100  # Default to Normal difficulty

def save_username(username):
    with open(".spaceship/saves/save.dat", "wb") as f:
        pickle.dump(username, f)

def load_username():
    try:
        with open(".spaceship/saves/save.dat", "rb") as f:
            if os.path.getsize(".spaceship/saves/save.dat") == 0:
                return None
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return None

# Get or create username
username = load_username()
if not username:
    root = Tk()
    root.withdraw()
    username = simpledialog.askstring("Username", "Choose a username:")
    root.destroy()
    if username:
        save_username(username)

class Player(pygame.sprite.Sprite):
    def __init__(self, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = health
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
        if key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedx
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(enemy_img, (50, 38))  # Adjust size as necessary
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1500  # delay between shots in milliseconds

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 5)
            self.speedx = random.randrange(-3, 3)
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(rock_imgs)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
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
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 5

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

# Game Loop
normal_bg.play()

show_init = True
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False

        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player_health = draw_difficulty()
        player = Player(player_health)
        all_sprites.add(player)

        for i in range(8):
            new_rock = Rock()
            all_sprites.add(new_rock)
            rocks.add(new_rock)

        for i in range(5):
            new_enemy = Enemy()
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)

        score = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        score += hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock = Rock()
        all_sprites.add(new_rock)
        rocks.add(new_rock)

    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock = Rock()
        all_sprites.add(new_rock)
        rocks.add(new_rock)
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            die = Explosion(player.rect.center, 'player')
            all_sprites.add(die)
            die_sound.play()
            player.lives -= 1
            player.health = player_health
            player.hide()

    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits:
        enemy_bullets.remove(hit)  # 移除敌方子弹
        player.health -= 10
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            die = Explosion(player.rect.center, 'player')
            all_sprites.add(die)
            die_sound.play()
            player.lives -= 1
            player.health = player_health
            player.hide()



    hits = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_enemy = Enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)
        player.health -= hit.radius
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            die = Explosion(player.rect.center, 'player')
            all_sprites.add(die)
            die_sound.play()
            player.lives -= 1
            player.health = player_health
            player.hide()

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.health += 20
            if player.health > 100:
                player.health = 100
        if hit.type == 'gun':
            gun_sound.play()
            player.gunup()

    if player.lives == 0 and not any(isinstance(s, Explosion) for s in all_sprites):
        show_init = True
        hardcore_bg.stop()
        hard_bg.stop()
        easy_bg.stop()
        normal_bg.stop()
        normal_bg.play()
        update_highscore(score)

    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 5, 15, GREEN)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
    pygame.display.update()

pygame.quit()
