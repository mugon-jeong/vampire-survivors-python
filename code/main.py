import os

import pygame
import random
import math
pygame.init()

WIDTH = 1280
HEIGHT = 720
WORLD_WIDTH = 2560
WORLD_HEIGHT = 1440

GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vampire Survivors")


# 이미지 로드 함수
def load_images(path):
    images = []
    for i in range(4):
        img = pygame.image.load(os.path.join(path, f"{i}.png")).convert_alpha()  # 투명배경 처리
        images.append(img)
    return images


player_images = {
    'up': load_images(os.path.join('../images', 'player', 'up')),
    'down': load_images(os.path.join('../images', 'player', 'down')),
    'left': load_images(os.path.join('../images', 'player', 'left')),
    'right': load_images(os.path.join('../images', 'player', 'right')),
}

obstacle_image = [
    pygame.image.load('../data/graphics/objects/grassrock1.png'),
    pygame.image.load('../data/graphics/objects/green_tree_small.png'),
]

enemy_images = {
    'bat': load_images(os.path.join('../images', 'enemies', 'bat')),
    'skeleton': load_images(os.path.join('../images', 'enemies', 'skeleton')),
    'blob': load_images(os.path.join('../images', 'enemies', 'blob')),
}

# 게임에서 이미지를 sprite라고 함
class Player(pygame.sprite.Sprite):
    # 플레이어의 초기 위치
    def __init__(self, x, y):
        super().__init__()  # 초기화

        self.image = player_images['down'][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.direction = pygame.Vector2()  # 2차원 vector 생성 (0,0) 초기화
        self.animation_index = 0
        self.animation_time = 0
        self.state = 'down'

        self.shoot_timer = 0
        self.shoot_delay = 1000

    def update(self, dt):
        # 플레이어의 움직임이 있으면 애니메이션 작동
        if self.direction.length():
            self.animation_time += dt

            # 0.2초 마다 업데이트
            if self.animation_time > 0.2:
                self.animation_time = 0
                self.animation_index += 1
                self.animation_index = self.animation_index % 4
                self.image = player_images[self.state][self.animation_index]
        else:
            self.animation_index = 0
            self.image = player_images[self.state][self.animation_index]

    def move(self, dx, dy):
        if dx > 0:
            self.state = 'right'
        elif dx < 0:
            self.state = 'left'
        elif dy > 0:
            self.state = 'down'
        elif dy < 0:
            self.state = 'up'

        self.direction.x = dx
        self.direction.y = dy

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()  # 어느방향으로 가든 1만큼 움직임
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def shoot(self):
        bullets = []
        for angle in range(0, 360, 45):
            state = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            bullet = Bullet(self.rect.centerx, self.rect.centery, state)
            bullets.append(bullet)
        return bullets

# 장애물
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(obstacle_image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# 사용자와 장애물의 상대적인 위치를 찾아서 플레이어 중심으로 모든 좌표 이동
class Camera:
    def __init__(self):
        self.camera = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, player):
        x = WIDTH // 2 - player.rect.centerx
        y = HEIGHT // 2 - player.rect.centery

        x = min(0, x)
        y = min(0, y)

        x = max(-WIDTH, x)
        y = max(-HEIGHT, y)

        self.camera = pygame.Rect(x, y, WORLD_WIDTH, WORLD_HEIGHT)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = direction
        self.lifetime = 0.5
        self.dtt = 0

    def update(self, dt):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        self.dtt += dt

        if self.dtt > self.lifetime:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = enemy_images[enemy_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = pygame.Vector2()

        self.animation_index = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        self.speed = 2

    def update(self, dt):
        self.move()
        if self.direction.length():
            self.animation_time += dt

            if self.animation_time > self.animation_speed:
                self.animation_time = 0
                self.animation_index += 1
                self.animation_index = self.animation_index % 4
                self.image = enemy_images[self.enemy_type][self.animation_index]
        else:
            self.animation_index = 0
            self.image = enemy_images[self.enemy_type][self.animation_index]

    def move(self):
        # 플레이어 방향으로 이동
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        self.direction.x = dx
        self.direction.y = dy

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        if pygame.sprite.spritecollide(self, obstacles, False):
            self.rect.x -= self.direction.x * self.speed
            self.rect.y -= self.direction.y * self.speed


player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)  # 플레이어 초기 위치
camera = Camera()

# sprite 그룹
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

all_sprites.add(player)

# 장애물 추가
for _ in range(20):
    x = random.randint(0, WORLD_WIDTH)
    y = random.randint(0, WORLD_HEIGHT)
    obstacle = Obstacle(x, y)
    all_sprites.add(obstacle)
    obstacles.add(obstacle)

# 적 추가
for _ in range(10):
    x = random.randint(0, WORLD_WIDTH)
    y = random.randint(0, WORLD_HEIGHT)
    enemy_type = random.choice(['bat', 'skeleton', 'blob'])
    enemy = Enemy(x, y, enemy_type)
    all_sprites.add(enemy)
    enemies.add(enemy)

# 게임 루프
running = True
clock = pygame.time.Clock()
enemy_timer = 0
# frame 당 갱신
while running:
    dt = clock.tick(60) / 1000  # 초당 60 프레임 고정
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_d] - keys[pygame.K_a]  # -이면 왼쪽으로 이동 +이면 오른쪽으로 이동
    dy = keys[pygame.K_s] - keys[pygame.K_w]  # -이면 아래로 이동 +이면 위로 이동

    player.update(dt)
    player.move(dx, dy)
    bullets.update(dt)
    enemies.update(dt)

    ## 충돌판정
    if pygame.sprite.spritecollide(player, obstacles, False):
        player.rect.x -= dx * player.speed
        player.rect.y -= dy * player.speed

    # 총알과 적의 충돌 체크
    for bullet in bullets:
       hit_enemies = pygame.sprite.spritecollide(bullet, enemies, True)
       if hit_enemies:
           bullet.kill()
           for enemy in hit_enemies:
               all_sprites.remove(enemy)

    # 총알 발사
    player.shoot_timer += dt * 1000
    if player.shoot_timer >= player.shoot_delay:
        player.shoot_timer = 0
        new_bullets = player.shoot()
        bullets.add(new_bullets)
        all_sprites.add(new_bullets)

    # 무작위 적 생성
    enemy_timer += dt
    if enemy_timer > 1:
        enemy_timer = 0
        enemy_type = random.choice(['bat', 'skeleton', 'blob'])
        x = random.randint(0, WORLD_WIDTH)
        y = random.randint(0, WORLD_HEIGHT)
        new_enemy = Enemy(x, y, enemy_type)
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)


    # 그리는 부분
    camera.update(player)
    screen.fill(GREEN)

    # all_sprites.draw(screen)
    for sprite in all_sprites:
        # 이미지를 떼어서 다시 붙인다.
        screen.blit(sprite.image, camera.apply(sprite))

    pygame.display.flip()  # 준비된 화면 실행

pygame.quit()
