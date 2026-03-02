import pygame
import keyboard
import random

pygame.init()

font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 50)

screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()
FPS = 60


# ============ PLAYER & BULLET CLASS ============
class Player:

    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 300  # Pixels PER SECOND instead of per frame

    def move_left(self, delta_time):
        self.x -= self.speed * delta_time
        if self.x <= 0:
            self.x = 0

    def move_right(self, delta_time):
        self.x += self.speed * delta_time
        if self.x + self.width > screen.get_width():
            self.x = screen_width - self.width

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def get_position(self):
        """Return player's current position"""
        return self.x, self.y


class Bullet:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.speed = 400  # Pixels PER SECOND

    def update(self, delta_time):
        self.y -= self.speed * delta_time

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y < -50

    def get_rect(self):
        """Creates a rectangle of the size of the bullet
            Even if in the future I'll change the image,
            the collision will work"""
        return self.image.get_rect(topleft=(self.x, self.y))

# ============ ENEMIES CLASS ============
class Enemy:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.speed = 150  # You've got it now, Lobster, Right?

    def update(self, delta_time):
        self.y += self.speed * delta_time

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > screen_height

    def get_rect(self):
        """Check get_rect in Class Bullet"""
        return self.image.get_rect(topleft=(self.x, self.y))

# ============ GAME CLASS ============
    """Manages game state and logic
    Such as updating shi, spawning enemies and text"""
class GameState:

    def __init__(self):
        self.player = Player((screen_width / 2), (screen_height - 200), "Textures/Player.png")
        self.bullets = []
        self.enemies = []
        self.screen_x = screen.get_width()

        # Shooting
        self.last_bullet_time = 0
        self.bullet_cooldown = 0.2  # Seconds
        self.bullets_shot = 0

        # Enemies
        self.last_enemy_spawn = 0
        self.enemy_spawn_delay = 1  # One Second

        # Waves
        self.wave = 1
        self.enemies_per_wave = 5
        self.enemies_spawned = 0
        self.wave_in_progress = True
        self.wave_cooldown = 2.0  # Time between waves in seconds
        self.wave_cooldown_start = 0
        self.waiting_next_wave = False
        self.wave_text_timer = 0
        self.wave_text_duration = 2.0  # Show wave text for 2 seconds
        self.show_wave_text = True

        self.enemies_killed = 0
        self.enemy_attacks = 0

    def shoot_bullet(self, current_time):  # NOW accepts current_time
        """Create a bullet if cooldown is ready"""
        if current_time - self.last_bullet_time > self.bullet_cooldown:
            player_x, player_y = self.player.get_position()
            bullet = Bullet(player_x + 7, player_y - 15, "Textures/Bullet.png")
            self.bullets.append(bullet)
            self.last_bullet_time = current_time
            self.bullets_shot += 1

    def spawn_enemy(self, current_time):
        """Create a new enemy if it's time"""
        if self.enemies_spawned < self.enemies_per_wave:
            if current_time - self.last_enemy_spawn > self.enemy_spawn_delay:
                x = random.randint(0, screen_width - 24)
                enemy = Enemy(x, 70, "Textures/EnemyTEMP.png")
                self.enemies.append(enemy)
                self.last_enemy_spawn = current_time
                self.enemies_spawned += 1

    def check_collisions(self):
        bullets_to_remove = []
        enemies_to_remove = []

        for bullet in self.bullets:
            bullet_rect = bullet.get_rect()

            for enemy in self.enemies:
                enemy_rect = enemy.get_rect()
                if bullet_rect.colliderect(enemy_rect):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    self.enemies_killed += 1
                    break

        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

    def check_wave_complete(self, current_time):
        """Check if wave is complete and start next wave"""
        if (self.enemies_spawned >= self.enemies_per_wave and
                len(self.enemies) == 0 and
                not self.waiting_next_wave):
            self.waiting_next_wave = True
            self.wave_cooldown_start = current_time
            self.show_wave_text = True
            self.wave_text_timer = current_time

        if self.waiting_next_wave:
            if current_time - self.wave_cooldown_start > self.wave_cooldown:
                self.wave += 1
                self.enemies_per_wave += 2
                self.enemies_spawned = 0
                self.enemy_spawn_delay = max(0.5, self.enemy_spawn_delay - 0.1)
                self.waiting_next_wave = False
                self.show_wave_text = True
                self.wave_text_timer = current_time

    def update(self, delta_time):
        # Get current time in seconds
        current_time = pygame.time.get_ticks() / 1000.0

        if keyboard.is_pressed("d"):
            self.player.move_right(delta_time)
        if keyboard.is_pressed("a"):
            self.player.move_left(delta_time)
        if keyboard.is_pressed("s"):
            self.shoot_bullet(current_time)

        for bullet in self.bullets:
            bullet.update(delta_time)
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)
        for enemy in self.enemies:
            if enemy.is_off_screen():
                self.enemy_attacks += 1

        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

        # Spawn new enemies
        if not self.waiting_next_wave:
            self.spawn_enemy(current_time)

        self.check_collisions()

        self.check_wave_complete(current_time)

        if self.show_wave_text:
            if current_time - self.wave_text_timer > self.wave_text_duration:
                self.show_wave_text = False

    def draw(self, surface):
        surface.fill((0, 0, 0))

        self.player.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

        #Text shi
        enemy_hits = font.render(f"Enemy Hits: {self.enemy_attacks}", True, (255, 0, 0))
        score_text = font.render(f"Enemies Killed: {self.enemies_killed}", True, (255, 255, 255))
        bullets_text = font.render(f"Bullets Shot: {self.bullets_shot}", True, (255, 255, 255))
        wave_text = font.render(f"Wave: {self.wave}", True, (255, 255, 255))

        surface.blit(enemy_hits, (10, 10))
        surface.blit(score_text, (10, 35))
        surface.blit(bullets_text, (10, 60))
        surface.blit(wave_text, (10, 85))

        if self.show_wave_text:
            wave_notification = big_font.render(f"WAVE {self.wave}", True, (255, 0, 0))
            surface.blit(wave_notification, (
                screen_width // 2 - wave_notification.get_width() // 2,
                screen_height // 2 - wave_notification.get_height() // 2
            ))

def main_menu():
    button_rect = pygame.Rect((screen_width / 2 - 50), (screen_height // 2- 25), 100, 50)

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
    game = GameState()

    while True:
        # Gets delta_time from clock
        delta_time = clock.tick(FPS) / 1000  # Converts Milliseconds to Seconds

        game.update(delta_time)
        game.draw(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

def main():
    while True:
        result = main_menu()
        if result == "quit":
            break
        if result == "game":
            result = main_game_loop()
        if result == "quit":
            break


if __name__ == "__main__":
    main()
    pygame.quit()