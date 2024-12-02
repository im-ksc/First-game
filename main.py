# Welcome to my game!
#
# Instructions are simple
# Use Arrow keys or WASD for movement and spacebar for jumping
#
# Your task is to survive as long and collect as many coins as possible, while avoiding monsters.
# As time passes, more monsters will spawn, increasing the difficulty of your task
#
# Would further improve this with collision knockback, and probably better collision indications
#
# Thank you and hope you enjoy!

import pygame
import random
from datetime import datetime, timedelta


# global variables
window_width = 640
window_height = 480
fps = 60

class Player:
    def __init__(self, x, y):
        self.robot = pygame.image.load("robot.png").convert_alpha()
        self.x = x - self.robot.get_width() / 2
        self.y = min(window_height - self.robot.get_height(), y)
        self.velocity = 5
        self.left = False
        self.right = False
        self.jump = False
        self.jump_velocity = 12
        self.jump_height = 12
        self.gravity = 0.6
        self.invul = 0
        self.hitbox = ''

    def on_ground(self):
        if self.y == window_height - self.robot.get_height():
            return True

    def move(self):
        if self.left == True:
            self.x -= self.velocity
            self.x = max(0, self.x)

        if self.right == True:
            self.x += self.velocity
            self.x = min(window_width - self.robot.get_width(), self.x)

        if self.jump:
            self.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            if self.jump_velocity < -self.jump_height:
                self.jump = False
                self.jump_velocity = self.jump_height
        else:
            self.jump = False
            self.y += self.gravity
            self.jump_count = 10

        self.y = min(window_height - self.robot.get_height(), self.y)
        self.hitbox = pygame.Rect(self.x + 6, self.y, self.robot.get_width() - 12, self.robot.get_height())

    def draw(self, window):
        self.move()
        if self.invul > 0:
            self.robot.set_alpha(100)
        else:
            self.robot.set_alpha(255)
        window.blit(self.robot, (self.x, self.y))

class Coin:
    def __init__(self, x, y):
        self.coin = pygame.image.load("coin.png")
        self.x = min(window_width - self.coin.get_width(), x)
        self.y = y - self.coin.get_height()
        self.drop_velocity = 2
        self.hitbox = ''

    def on_ground(self):
        if self.y == window_height - self.coin.get_height():
            return True

    def move(self):
        self.y += self.drop_velocity
        self.y = min(window_height - self.coin.get_height(), self.y)
        self.hitbox = pygame.Rect(self.x, self.y, self.coin.get_width(), self.coin.get_height())

    def draw(self, window):
        self.move()
        window.blit(self.coin, (self.x, self.y))


class Monster:
    def __init__(self, x):
        self.monster = pygame.image.load("monster.png")
        self.monster = pygame.transform.scale(self.monster, (self.monster.get_width() * 0.8, self.monster.get_height() * 0.8))
        self.x = min(window_width - self.monster.get_width(), x)
        self.y = window_height - self.monster.get_height()
        self.directions = ["left", "centre", "right"]
        self.direction = ''
        self.direction_count = 0
        self.velocity = 1
        self.hitbox = ""

    def move(self):
        if self.direction_count == 0:
            self.direction = self.directions[random.randint(0,2)]
            self.direction_count = 90

        if self.direction == "left":
            self.x -= self.velocity
            self.x = max(0, self.x)

        if self.direction == "right":
            self.x += self.velocity
            self.x = min(window_width - self.monster.get_width(), self.x)
        self.direction_count -= 1
        self.hitbox = pygame.Rect(self.x + 4, self.y + 4, self.monster.get_width() - 5, self.monster.get_height() - 4)

    def draw(self, window):
        self.move()
        window.blit(self.monster, (self.x, self.y))

class Door:
    def __init__(self, x):
        self.door = pygame.image.load("door.png").convert_alpha()
        self.door = pygame.transform.scale(self.door, (self.door.get_width() * 0.9, self.door.get_height() * 0.9))
        self.x = min(window_width - self.door.get_width(), x)
        self.y = window_height - self.door.get_height()
        self.alpha = 255
        self.spawn_timer = datetime.now()
        self.spawned = False

    def draw(self, window):
        if self.spawned:
            self.alpha -= 3
        self.door.set_alpha(self.alpha)
        window.blit(self.door, (self.x, self.y))


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((window_width, window_height))
        self.game_font = pygame.font.SysFont("Arial", 24)
        self.game_font2 = pygame.font.SysFont("Arial", 16)
        pygame.display.set_caption("Game")

        self.player = Player(window_width / 2, window_height)
        self.lifes = 3
        self.points = 0
        self.gameover = False
        self.start_time = datetime.now()

        self.coins: list[Coin] = []
        self.coin_time = datetime.now()

        self.door = Door(random.randint(0, window_width))
        self.monsters: list[Monster] = []

        self.clock = pygame.time.Clock()

        self.check_events()
        self.main_loop()

    def main_loop(self):
        while True:
            self.check_events()
            self.new_coin()
            self.new_door()
            self.new_monster()
            if self.gameover:
                self.draw_gameover()
            else:
                self.draw_window()
            self.clock.tick(fps)

    def reset(self):
        self.player = Player(window_width / 2, window_height)
        self.lifes = 3
        self.points = 0
        self.gameover = False
        self.start_time = datetime.now()

        self.coins: list[Coin] = []
        self.coin_time = datetime.now()

        self.door = Door(random.randint(0, window_width))
        self.monsters: list[Monster] = []

    def new_coin(self):
        if datetime.now() - self.coin_time >= timedelta(seconds = 3):
            self.coins.append(Coin(random.randint(0, window_width), 0))
            self.coin_time = datetime.now()

    def new_door(self):
        if datetime.now() - self.door.spawn_timer >= timedelta(seconds = 15):
            self.door = Door(random.randint(0, window_width))

    def new_monster(self):
        if datetime.now() - self.door.spawn_timer >= timedelta(seconds = 2) and self.door.spawned == False and self.door.alpha == 255:
            self.monsters.append(Monster(self.door.x))
            self.door.spawned = True

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.left = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.right = True
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    if self.player.on_ground():
                        self.player.jump = True
                if event.key == pygame.K_r and self.gameover:
                    self.reset()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.left = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.right = False

            if event.type == pygame.QUIT:
                print("Quitting pygame")
                exit()

        for coin in list(self.coins):
            if coin.on_ground() and len(self.coins) > 5:
                self.coins.remove(coin)
            try:
                if coin.hitbox.colliderect(self.player.hitbox):
                    self.points += 1
                    self.coins.remove(coin)
            except:
                pass

        for monster in self.monsters:
            try:
                if monster.hitbox.colliderect(self.player.hitbox) and self.player.invul <= 0:
                    self.lifes -= 1
                    self.player.invul = 120
                else:
                    self.player.invul -= 1
            except:
                pass
        if self.gameover == False:
            self.time_passed = datetime.now() - self.start_time
        self.life_text = self.game_font.render(f"Life: {self.lifes}", True, (255, 0, 0))
        self.points_text = self.game_font.render(f"Points: {self.points}", True, (255, 0, 0))
        self.time_text = self.game_font2.render(f"Time(seconds): {self.time_passed.total_seconds():.0f}", True, (255, 0, 0))
        if self.lifes <= 0:
            self.gameover = True

    def draw_window(self):
        self.window.fill((255, 255, 255))
        instructions_text = self.game_font2.render("Arrow keys or WASD for movement", True, (255, 0, 0))
        task_text = self.game_font2.render("Collect as many coins while avoiding monsters! Difficulty increases as time passes", True, (255, 0, 0))
        self.window.blit(instructions_text, (10, 45))
        self.window.blit(task_text, (10, 65))
        self.window.blit(self.life_text, (10, 10))
        self.window.blit(self.points_text, (window_width - 100, 10))
        self.window.blit(self.time_text, (window_width - 130, 40))
        self.player.draw(self.window)
        for coin in self.coins:
            coin.draw(self.window)
        self.door.draw(self.window)
        for monster in self.monsters:
            monster.draw(self.window)

        pygame.display.flip()

    def draw_gameover(self):
        self.window.fill((255, 255, 255))
        gameover_text = self.game_font.render("Gameover! Press 'R' to restart!", True, (255, 0, 0))
        self.window.blit(self.points_text, (window_width / 2 - self.points_text.get_width() / 2, window_height / 2))
        self.window.blit(self.time_text, (window_width / 2 - self.time_text.get_width() / 2, window_height / 2 + 30))
        self.window.blit(gameover_text, (window_width / 2 - gameover_text.get_width() / 2, window_height / 2 - 30))
        pygame.display.flip()

if __name__ == "__main__":
    Game()
