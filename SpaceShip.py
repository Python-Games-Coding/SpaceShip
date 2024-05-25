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

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surf.blit(img, img_rect)

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
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
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

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedx = random.randrange(-3, 3)
        self.health = 3
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
        shoot_sound.play()

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.health = 3

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

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

def main():
    global all_sprites, bullets, mobs, enemy_bullets, powers, enemies

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    powers = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    for i in range(8):
        m = Rock()
        all_sprites.add(m)
        mobs.add(m)

    for i in range(3):
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)

    score = 0
    pygame.mixer.music.play(loops=-1)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()

        # Check to see if a bullet hit a mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 50 - hit.radius
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Power(hit.rect.center)
                all_sprites.add(pow)
                powers.add(pow)
            m = Rock()
            all_sprites.add(m)
            mobs.add(m)

        # Check to see if a mob hit the player
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.health -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            m = Rock()
            all_sprites.add(m)
            mobs.add(m)
            if player.health <= 0:
                die_sound.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.health = 100

        # Check to see if player hit a power
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

        # Check to see if an enemy bullet hit the player
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player.health -= 10
            if player.health <= 0:
                die_sound.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.health = 100

        # if the player died and the explosion has finished playing
        if player.lives == 0 and not death_explosion.alive():
            running = False
            update_highscore(score)
            save_highscore(score)

        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_health(screen, player.health, 5, 15, GREEN)
        draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)
        pygame.display.flip()

    pygame.mixer.music.stop()

if __name__ == '__main__':
    while True:
        show_go_screen = draw_init()
        if show_go_screen:
            break
        main()
    pygame.quit()

if __name__ == '__main__':
    while True:
        show_go_screen = draw_init()
        if show_go_screen:
            break
        main()
    pygame.quit()
