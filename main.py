import pygame
import keyboard
import random

pygame.init()

font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 50)
screen = pygame.display.set_mode((500, 600))

clock = pygame.time.Clock()
FPS = 60


# ============ PLAYER & BULLET CLASS ============
class Player:
    """Represents the player character"""

    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 300  # Pixels PER SECOND instead of per frame

    def move_left(self, delta_time):
        """Move player left"""
        self.x -= self.speed * delta_time

    def move_right(self, delta_time):
        """Move player right"""
        self.x += self.speed * delta_time

    def draw(self, surface):
        """Draw the player on screen"""
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

    def update(self, delta_time):  # NOW accepts delta_time
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

    def update(self, delta_time):  # NOW accepts delta_time
        self.y += self.speed * delta_time

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > 600

    def get_rect(self):
        """Check get_rect in Class Bullet"""
        return self.image.get_rect(topleft=(self.x, self.y))


# ============ GAME CLASS ============
class GameState:
    """Manages the overall game state and logic"""

    def __init__(self):
        self.player = Player(250, 560, "Textures/Player.png")
        self.bullets = []
        self.enemies = []

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
        self.enemies_killed = 0
        self.wave_cooldown = 2.0  # Time between waves in seconds
        self.wave_cooldown_start = 0
        self.waiting_next_wave = False
        self.wave_text_timer = 0
        self.wave_text_duration = 2.0  # Show wave text for 2 seconds
        self.show_wave_text = True

    def shoot_bullet(self, current_time):  # NOW accepts current_time
        """Create a bullet if cooldown is ready"""
        if current_time - self.last_bullet_time > self.bullet_cooldown:
            player_x, player_y = self.player.get_position()
            bullet = Bullet(player_x + 7, player_y - 15, "Textures/Bullet.png")
            self.bullets.append(bullet)
            self.last_bullet_time = current_time
            self.bullets_shot += 1

    def spawn_enemy(self, current_time):  # NOW accepts current_time
        """Create a new enemy if it's time"""
        if self.enemies_spawned < self.enemies_per_wave:
            if current_time - self.last_enemy_spawn > self.enemy_spawn_delay:
                x = random.randint(0, screen.get_width() - 24)
                enemy = Enemy(x, 70, "Textures/EnemyTEMP.png")
                self.enemies.append(enemy)
                self.last_enemy_spawn = current_time
                self.enemies_spawned += 1

    def check_collisions(self):
        bullets_to_remove = []
        enemies_to_remove = []

        # Check each bullet against each enemy
        for bullet in self.bullets:
            bullet_rect = bullet.get_rect()

            for enemy in self.enemies:
                enemy_rect = enemy.get_rect()

                # Check if rectangles overlap
                if bullet_rect.colliderect(enemy_rect):
                    # Collision detected!
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    self.enemies_killed += 1
                    break

        # Remove collided bullets and enemies
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)

    def check_wave_complete(self, current_time):
        """Check if wave is complete and start next wave"""
        # Wave is complete if all enemies have been spawned AND all are gone
        if (self.enemies_spawned >= self.enemies_per_wave and
                len(self.enemies) == 0 and
                not self.waiting_next_wave):
            self.waiting_next_wave = True
            self.wave_cooldown_start = current_time
            self.show_wave_text = True
            self.wave_text_timer = current_time

        # Start next wave after cooldown
        if self.waiting_next_wave:
            if current_time - self.wave_cooldown_start > self.wave_cooldown:
                self.wave += 1
                self.enemies_per_wave += 2  # Make each wave harder
                self.enemies_spawned = 0
                self.enemy_spawn_delay = max(0.5, self.enemy_spawn_delay - 0.1)  # Faster spawns
                self.waiting_next_wave = False
                self.show_wave_text = True
                self.wave_text_timer = current_time

    def update(self, delta_time):
        """Update game state - called each frame"""
        # Get current time in seconds
        current_time = pygame.time.get_ticks() / 1000.0

        # Handle player movement (only if not waiting for next wave)
        if not self.waiting_next_wave:
            if keyboard.is_pressed("d"):
                self.player.move_right(delta_time)
            if keyboard.is_pressed("a"):
                self.player.move_left(delta_time)
            if keyboard.is_pressed("s"):
                self.shoot_bullet(current_time)  # NOW passes current_time

        # Update bullets and remove off-screen ones
        for bullet in self.bullets:
            bullet.update(delta_time)  # NOW passes delta_time
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]

        # Update enemies
        for enemy in self.enemies:
            enemy.update(delta_time)  # NOW passes delta_time
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

        # Spawn new enemies (only during active wave)
        if not self.waiting_next_wave:
            self.spawn_enemy(current_time)  # NOW passes current_time

        # Check collisions
        self.check_collisions()

        # Check if wave is complete
        self.check_wave_complete(current_time)

        # Update wave text timer
        if self.show_wave_text:
            if current_time - self.wave_text_timer > self.wave_text_duration:
                self.show_wave_text = False

    def draw(self, surface):
        """Draw all game elements"""
        surface.fill((0, 0, 0))

        self.player.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)

        # Display score and bullets shot
        score_text = font.render(f"Enemies Killed: {self.enemies_killed}", True, (255, 255, 255))
        bullets_text = font.render(f"Bullets Shot: {self.bullets_shot}", True, (255, 255, 255))
        wave_text = font.render(f"Wave: {self.wave}", True, (255, 255, 255))

        surface.blit(score_text, (10, 10))
        surface.blit(bullets_text, (10, 35))
        surface.blit(wave_text, (10, 60))

        # Display wave notification
        if self.show_wave_text:
            wave_notification = big_font.render(f"WAVE {self.wave}", True, (255, 0, 0))
            surface.blit(wave_notification, (
                screen.get_width() // 2 - wave_notification.get_width() // 2,
                screen.get_height() // 2 - wave_notification.get_height() // 2
            ))


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
    game = GameState()  # Create a game instance

    while True:
        # Gets delta_time from clock
        delta_time = clock.tick(FPS) / 1000  # Converts Milliseconds to Seconds

        game.update(delta_time)  # Update all game logic
        game.draw(screen)  # Draw everything

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