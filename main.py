import pygame, sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice , randint
from laser import Laser

class Intro:
    def __init__(self):
        self.font = pygame.font.Font("font/8bit.ttf", 40)
        self.text_surf = self.font.render("Space Invaders", True, "white")
        self.text_rect = self.text_surf.get_rect(center=(screen_width / 2, screen_height / 2))
        self.instruction_font = pygame.font.Font("font/8bit.ttf", 20)
        self.instruction_surf = self.instruction_font.render("Press SPACE to Start", True, "white")
        self.instruction_rect = self.instruction_surf.get_rect(center=(screen_width / 2, screen_height / 2 + 40))

    def show_intro(self):
        screen.fill((0, 0, 0))
        screen.blit(self.text_surf, self.text_rect)
        screen.blit(self.instruction_surf, self.instruction_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
                    
pygame.init()

class Game:
    def __init__(self):
        # player setup
        player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load("img/life.png").convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font("font/8bit.ttf",20)

        # obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

        # alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1

        # extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400,800)

        # audio
        music = pygame.mixer.Sound("audio/bgmusic.mp3")
        music.set_volume(0.1)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound("audio/laser.mp3")
        self.laser_sound.set_volume(0.3)
        self.explosion_sound = pygame.mixer.Sound("audio/explode.mp3")
        self.explosion_sound.set_volume(0.3)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index,col in enumerate(row):
                if col == "x":
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size,(25,140,155),x,y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self,*offset,x_start,y_start):
        for offset_x in offset:
            self.create_obstacle(x_start,y_start,offset_x)

    def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70,y_offset = 30):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0: alien_sprite = Alien("alien1",x,y)
                elif 1 <= row_index <= 2: alien_sprite = Alien("alien2",x,y)
                else : alien_sprite = Alien("alien3",x,y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self,distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center,6,screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(["right","left"],screen_width))
            self.extra_spawn_time = randint (400,800)

    def collision_checks(self):
        
        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()

                # alien collision
                aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                # extra collision
                if pygame.sprite.spritecollide(laser,self.extra,True):
                    self.score += 500
                    laser.kill()

        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()

                # player collision
                if pygame.sprite.spritecollide(laser,self.player,False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        game.game_over()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien,self.blocks,True)

                if pygame.sprite.spritecollide(alien,self.player,False):
                   pygame.quit()
                   sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1 ):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf,(x,8))

    def display_score(self):
        score_surf = self.font.render(f"score: {self.score}",False,"white")
        score_rect = score_surf.get_rect(topleft = (10,10))
        screen.blit(score_surf,score_rect)

    def victory_message(self): 
        if not self.aliens.sprites():
            victory_font = pygame.font.Font("font/8bit.ttf", 40)
            victory_surf = self.font.render("YOU WIN !",False,"white")
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf,victory_rect)
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.quit()

    def game_over(self):
        if self.lives <= 0:
            game_over_font = pygame.font.Font("font/8bit.ttf", 40)
            game_over_surf = game_over_font.render("GAME OVER !", False, "white")
            game_over_rect = game_over_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(game_over_surf, game_over_rect)
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.quit()

    def reset_game(self):
        self.lives = 3
        self.score = 0
        self.player.sprite.lasers.empty()
        self.blocks.empty()
        self.aliens.empty()
        self.alien_lasers.empty()
        self.extra.empty()
        self.alien_setup(rows=6, cols=8)

    def run(self):
        self.player.update()
        self.alien_lasers.update()  
        self.extra.update()        

        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()
        
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()
    
if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    game = Game()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER,800)
    
    background_image = pygame.image.load("img/space.png")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    intro = Intro()
    intro.show_intro()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
                
        screen.fill((30, 30, 30))
        screen.blit(background_image, (0, 0))
        game.game_over()
        game.run()

        pygame.display.flip()
        clock.tick(60)