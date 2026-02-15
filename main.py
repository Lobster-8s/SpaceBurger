import pygame, keyboard, random

pygame.init()

playerX = 250
playerY = 560

#LOAD IMAGES
player = pygame.image.load("Textures/Player.png")
bullet_img = pygame.image.load("Textures/Bullet.png")
enemy_img = pygame.image.load("Textures/EnemyTEMP.png")
screen = pygame.display.set_mode((500, 600))

#BULLETS
bullets = []
last_bullet_time = 0
bullet_cooldown = 200

#ENEMIES
enemies = []
enemy_spawn_delay = 1000 # Millisecondi
last_enemy_spawn = 0


def shoot_bullet(player_x, player_y):
    global last_bullet_time
    current_time_for_bullets = pygame.time.get_ticks()
    if current_time_for_bullets - last_bullet_time > bullet_cooldown:
        bullets.append([player_x + 7, player_y -15])
        last_bullet_time = current_time_for_bullets

def spawn_enemies():
    global last_enemy_spawn
    x = random.randint(0, screen.get_width()-24)
    y = -50
    enemies.append([x, y])


running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(player, (playerX, playerY))

    if keyboard.is_pressed("d"):
        playerX += 0.1
    if keyboard.is_pressed("a"):
        playerX -= 0.1
    if keyboard.is_pressed("s"):
        shoot_bullet(playerX, playerY)
    for bullet_pos in bullets:
        bullet_pos[1] -= 0.3
        screen.blit(bullet_img,bullet_pos)

    bullets = [b for b in bullets if b[1] > -50] #Update Bullets

    #UPDATE ENEMIES
    current_time_for_enemies = pygame.time.get_ticks()
    if current_time_for_enemies - last_enemy_spawn > enemy_spawn_delay:
        spawn_enemies()
        last_enemy_spawn = current_time_for_enemies
    for enemy in enemies:
        enemy[1] += 0.05
        screen.blit(enemy_img, enemy)
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if pygame.Rect(enemy[0], enemy[1], 22, 24).colliderect(
                    pygame.Rect(bullet[0], bullet[1], 8, 20)):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break
    enemies = [e for e in enemies if e[1] < 650]
    #END OF UPDATING ENEMIES

    pygame.display.update()
    for  event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()