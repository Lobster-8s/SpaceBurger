import pygame, keyboard, random

pygame.init()

font = pygame.font.SysFont("Arial", 20)
screen = pygame.display.set_mode((500, 600))

def main_menu():
    button_rect = pygame.Rect(200, 250, 100, 50)

    while True:
        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (0, 200, 0), button_rect)
        text = font.render("START", True, (0, 0, 0))
        screen.blit(text, (
            button_rect.centerx - text.get_width() // 2,
            button_rect.centery - text.get_height() // 2
        ))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        return "game"

        pygame.display.update()


def main_game_loop():
    player_x = 250
    player_y = 560
    enemies_killed = 0
    bullets_shot = 0


    # LOAD IMAGES
    player = pygame.image.load("Textures/Player.png")
    bullet_img = pygame.image.load("Textures/Bullet.png")
    enemy_img = pygame.image.load("Textures/EnemyTEMP.png")


    # BULLETS
    bullets = []
    last_bullet_time = 0
    bullet_cooldown = 200

    # ENEMIES
    enemies = []
    enemy_spawn_delay = 1000  # Millisecondi
    last_enemy_spawn = 0

    # WAVE THINGS
    wave = 1
    enemies_per_wave = 5
    enemies_spawned = 0
    wave_in_progress = True

    wave_cooldown = 2000
    wave_cooldown_start = 0
    waiting_next_wave = False

    wave_text_timer = 0
    wave_text_duration = 2000  # 2 seconds
    show_wave_text = True

    def shoot_bullet(x, y):
        nonlocal last_bullet_time, bullets_shot
        current_time_for_bullets = pygame.time.get_ticks()
        if current_time_for_bullets - last_bullet_time > bullet_cooldown:
            bullets.append([x + 7, y - 15])
            last_bullet_time = current_time_for_bullets
            bullets_shot += 1

    def spawn_enemies():
        nonlocal last_enemy_spawn
        x = random.randint(0, screen.get_width()-24)
        y = 70
        enemies.append([x, y])



    while True:
        screen.fill((0, 0, 0))
        screen.blit(player, (player_x, player_y))

        if keyboard.is_pressed("d"):
            player_x += 0.1
        if keyboard.is_pressed("a"):
            player_x -= 0.1
        if keyboard.is_pressed("s"):
            shoot_bullet(player_x, player_y)
        for bullet_pos in bullets:
            bullet_pos[1] -= 0.3
            screen.blit(bullet_img,bullet_pos)

        bullets = [b for b in bullets if b[1] > -50] #Update Bullets

        #UPDATE ENEMIES
        current_time_for_enemies = pygame.time.get_ticks()
        if enemies_spawned < enemies_per_wave:
            if current_time_for_enemies - last_enemy_spawn > enemy_spawn_delay:
                spawn_enemies()
                last_enemy_spawn = current_time_for_enemies
                enemies_spawned += 1

        for enemy in enemies:
            enemy_speed = 0.05 + (wave * 0.01)
            enemy[1] += enemy_speed
            screen.blit(enemy_img, enemy)
        enemies = [e for e in enemies if e[1] < 650]
        #END OF UPDATING ENEMIES

        #Check if Enemies have been hit
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if pygame.Rect(enemy[0], enemy[1], 22, 24).colliderect(
                        pygame.Rect(bullet[0], bullet[1], 8, 20)):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    enemies_killed += 1
                    break

        #Check if Wave ended
        if wave_in_progress and enemies_spawned == enemies_per_wave and len(enemies) == 0:
            wave_in_progress = False
            waiting_next_wave = True
            wave_cooldown_start = pygame.time.get_ticks()
        #Cooldown between Waves
        if waiting_next_wave:
            if pygame.time.get_ticks() - wave_cooldown_start > wave_cooldown:
                wave += 1
                enemies_per_wave += 3
                enemies_spawned = 0
                waiting_next_wave = False
                wave_in_progress = True
                show_wave_text = True
                wave_text_timer = pygame.time.get_ticks()

        #Wave Text
        if show_wave_text:
            if pygame.time.get_ticks() - wave_text_timer < wave_text_duration:
                wave_surface = font.render(f"Wave {wave}", True, (255, 255, 255))
                screen.blit(wave_surface,(
                    screen.get_width() // 2 - wave_surface.get_width() // 2,
                    screen.get_height() // 2 - wave_surface.get_height() // 2,))
            else:
                show_wave_text = False

        #Update Text
        kills_text = font.render(f"Nemici Uccisi: {enemies_killed}", True, (255, 255, 255))
        shots_text = font.render(f"Proiettili Sparati: {bullets_shot}", True, (255, 255, 255))
        screen.blit(kills_text, (500 - kills_text.get_width() - 10, 10))
        screen.blit(shots_text, (500 - shots_text.get_width() - 10, 40))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
        if keyboard.is_pressed("enter"):
            return "menu"

MENU = "menu"
GAME = "game"
QUIT = "quit"

state = MENU

while state != QUIT:
    if state == MENU:
        state = main_menu()
    elif state == GAME:
        state = main_game_loop()

pygame.quit()
