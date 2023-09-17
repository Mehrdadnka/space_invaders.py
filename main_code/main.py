import pygame, sys
from player import Player
import obstacles
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
    def __init__(self):
        # player setup
        player_sprite = Player((SCREEN_WIDTH / 2, SCREEN_HEIGHT),SCREEN_WIDTH, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # health and score setup
        self.lives = 3
        self.live_surface = pygame.image.load('graphics/player.png').convert_alpha()
        self.live_x_start_pos = SCREEN_WIDTH - (self.live_surface.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)

        # obstacle setup
        self.shape = obstacles.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        # positioning obstacles by x position
        self.obstacles_x_positions = [num * (SCREEN_WIDTH / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacles_x_positions, x_start = SCREEN_WIDTH / 15, y_start = 480)

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1

        # Extra alien setup
        self.extra =pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(40, 80)

        # import music files
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.2)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound('audio/laser.wav')
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    # create the position inside the game
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacles.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset
				
                if row_index == 0: alien_sprite = Alien('yellow',x,y)
                elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
                else: alien_sprite = Alien('red',x,y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= SCREEN_WIDTH:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

        #moving down aliens mothod
    def alien_move_down(self, distance):
        all_aliens = self.aliens.sprites()
        if self.aliens:
            for alien in all_aliens:
                alien.rect.y += distance

        # aliens laser shooting method
    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, SCREEN_HEIGHT)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
            self.extra_spawn_time -= 1
            if self.extra_spawn_time <= 0:
                self.extra.add(Extra(choice(['right', 'left']), SCREEN_WIDTH))
                self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    laser.kill()
                    for alien in aliens_hit:
                        self.score += alien.value
                    self.explosion_sound.play()

                # extra alien collisions
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()

        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # player collisions
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1

                    # losing the game 
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                # losing the game 
                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surface.get_size()[0] + 10))
            screen.blit(self.live_surface, (x, 8))

    def display_score(self):
        score_surface = self.font.render(f'score: {self.score}', False, 'white')
        score_rect = score_surface.get_rect(topleft = (10, -10))
        screen.blit(score_surface, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surface = self.font.render('You won!', False, 'white')
            victory_rect = victory_surface.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(victory_surface, victory_rect)

    def run(self):
        # update all sprite groups
        self.player.update() # update the player
        self.aliens.update(self.alien_direction) # animate the direction of aliens
        self.alien_position_checker() # check the position of aliens
        self.alien_lasers.update()
        self.extra_alien_timer()
        self.extra.update()
        self.collision_checks()

        # draw all sprite groups
        self.player.sprite.lasers.draw(screen) # draw the laser
        self.player.draw(screen) # draw the player
        self.blocks.draw(screen) # draw blocks
        self.aliens.draw(screen) # draw aliens
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()

# creating the modern style for displaying the game
class CRT:
    def __init__(self):
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def create_crt_lines(self):
        line_height = 3
        line_amount = int(SCREEN_HEIGHT / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            # same opacity for lines and tv
            pygame.draw.line(self.tv, 'black', (0, y_pos), (SCREEN_WIDTH, y_pos), 1)

    def draw(self):
        self.tv.set_alpha(randint(75, 90))
        self.create_crt_lines()
        screen.blit(self.tv, (0, 0))

# general settings
if __name__ == '__main__':
    pygame.init()
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()

        screen.fill((30, 30, 30)) # screen color
        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)