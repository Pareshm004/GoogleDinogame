import os
import sys
import math
import random
import pygame

WIDTH = 623
HEIGHT = 150 

pygame.init()
pygame.mixer.init() #for sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('DINO')


class BG:
    def __init__(self,x):
        self.width = WIDTH
        self.height = HEIGHT
        self.x = x
        self.y = 0
        self.set_texture()
        self.show()

    def update(self, dx):
        self.x += dx
        if self.x <= -WIDTH:
            self.x = WIDTH


    def show(self):
        screen.blit(self.texture, (self.x, self.y))    
    def set_texture(self):
        path = os.path.join('assets/images/bg.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Dino:
    def __init__(self):
        self.width = 44
        self.height = 44
        self.x = 10
        self.y = 80
        self.texture_num = 0
        self.dy = 3
        self.gravity = 1.2
        self.onground = True
        self.jumping = False
        self.jump_stop = 10
        self.falling = False
        self.fall_stop = 80
        self.set_texture()
        self.set_sound()
        self.show()

    def update(self, loops):
        #jumping
        if self.jumping:
            self.y -= self.dy
            if self.y <= self.jump_stop:
                self.fall()
        #falling
        elif self.falling:
            self.y += self.gravity*self.dy
            if self.y >= self.fall_stop:
                self.stop()

        #walking
        elif self.onground and loops % 5 == 0:
            self.texture_num = (self.texture_num + 1) % 3 #returns either dino0 or dino1 or dino2, which is what we want to do for updating our dino picture
            self.set_texture()
    def show(self):  
        screen.blit(self.texture, (self.x, self.y)) 
    def set_texture(self):
        path = os.path.join(f'assets/images/dino{self.texture_num}.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

    def set_sound(self):
        path = os.path.join('assets/sounds/jump.wav')
        self.jump_sound = pygame.mixer.Sound(path)

    def jump(self):
        self.jump_sound.play()
        self.jumping = True
        self.onground = False
    
    def fall(self):
        self.jumping = False
        self.falling = True
    
    def stop(self):
        self.falling = False
        self.onground = True

class Cactus:
    def __init__ (self, x):
        self.width = 34
        self.height = 44
        self.x = x
        self.y = 80
        self.set_texture()
        self.show()

    def update(self, dx):
        self.x += dx

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join('assets/images/cactus.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Collision:
    def between(self, obj1, obj2):
        distance = math.sqrt((obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2)
        return distance < 35 #if both objects have distance less than 35, consider it as a collision 

class Score:
    def __init__(self, hs):
        self.hs = hs
        self.act = 0
        self.font = pygame.font.SysFont('monospace', 18)
        self.color = (0, 0, 0)
        self.set_sound()
        self.show()
    
    def update(self, loops):
        self.act = loops // 10
        self.check_hs()
        self.check_sound()

    def show(self):
        self.lbl = self.font.render(f'HI {self.hs} {self.act}', 1, self.color)
        lbl_width = self.lbl.get_rect().width
        screen.blit(self.lbl, (WIDTH - lbl_width - 10, 10)) #score label is dynamic, i.e., when the width is increasing the label re-adjusts its position on screen 
    
    def set_sound(self):
        path = os.path.join('assets/sounds/point.wav')
        self.point_sound = pygame.mixer.Sound(path)        

    def check_hs(self):
        if self.act > self.hs:
            self.hs = self.act
    
    def check_sound(self):
        if self.act % 100 == 0 and self.act != 0:
            self.point_sound.play()

class Game:
    def __init__(self, hs = 0):
        self.bg = [BG(x=0), BG(x=WIDTH)]
        self.dino = Dino()
        self.obstacles = []
        self.collision = Collision()
        self.score = Score(hs)
        self.speed = 4
        self.playing = False
        self.set_sound() 
        self.set_labels()
        self.spawn_cactus()
    
    def set_labels(self):
        big_font = pygame.font.SysFont('monospace', 24, bold =True)
        small_font = pygame.font.SysFont('monospace', 18)
        self.big_lbl = big_font.render('G A M E  O V E R!!!!', 1, (0, 0, 0))
        self.small_lbl = small_font.render('Press r to restart the game', 1, (0, 0, 0))

    def set_sound(self):
        path = os.path.join('assets/sounds/die.wav')
        self.die_sound = pygame.mixer.Sound(path)

    def start(self):
        self.playing = True

    def over(self):
        self.die_sound.play()
        screen.blit(self.big_lbl, (WIDTH // 2 - self.big_lbl.get_width() // 2, HEIGHT // 4))
        screen.blit(self.small_lbl, (WIDTH // 2 - self.small_lbl.get_width() //2, HEIGHT // 2)) #bracket code is to basically center the big and the small label 
        self.playing = False

    def tospawn(self, loops):
        return loops % 100 == 0 #reset after loop runs 100 times

    def spawn_cactus(self):
        # list with cactus
        if len(self.obstacles) > 0:
            prev_cactus = self.obstacles[-1]
            x = random.randint(prev_cactus.x + self.dino.width + 84, WIDTH + prev_cactus.x + self.dino.width + 84) #this makes sure that in between two cactus, the dino fits, 84 is a random value to put some space between two cactus. 

        # empty list  
        else:
            x = random.randint(WIDTH + 100, 1000) #Return random integer in range [a, b], including both end points.
        #create new cactus 
        cactus = Cactus(x)
        self.obstacles.append(cactus)
    
    def restart(self):
        self.__init__(hs = self.score.hs) #saves previous high score and overrides it if necessary

def main():
    #objects    
    game = Game()
    dino = game.dino

    #variables
    clock = pygame.time.Clock()
    loops = 0
    over = False


    while True:

        if game.playing:

            loops += 1

            #--BG--
            for bg in game.bg:
                bg.update(-game.speed)
                bg.show()

            #--Dino--
            dino.update(loops)
            dino.show()

            #--Cactus--
            if game.tospawn(loops):
                game.spawn_cactus()

            for cactus in game.obstacles:
                cactus.update(-game.speed)
                cactus.show()
            #collisions
                if game.collision.between(dino, cactus):
                    over = True
            
            if over:
                game.over()
            
            #--Score--
            game.score.update(loops)
            game.score.show()

        
        #events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: #if we press spacebar key
                    if not over: 
                        if dino.onground:  #we can jump only if dino is on ground
                            dino.jump()

                        if not game.playing:
                            game.start()
                if event.key == pygame.K_r:
                    game.restart()
                    dino = game.dino
                    loops = 0
                    over = False

        clock.tick(90)
        pygame.display.update()
    
main()