from turtle import window_width
import pygame
import neat
import time
import os
import random
import sys

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        
    def jump(self):
        self.vel = -10.5 #0, 0 is top right. -10 y goes up
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        
        
        """displacemnt is used in conjunction with time / tick_count in order to 
        gradually slow down jump and then reverse velocity after enough time."""
        displacement = self.vel * self.tick_count + 1.5*self.tick_count**2
        
        if displacement >= 16:
            displacement = 16
            
        if displacement < 0:
            displacement -= 2 #all this does is make the jump a little higher if its jumping
            
        self.y = self.y + displacement
        
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        self.img_count += 1
        
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
            
        if self.tilt <= -80:
            self.img = self.IMGS[1] #if nosediving, no flap
            self.img_count = self.ANIMATION_TIME*2 #Sets bird into animation time for nuetral state
            
        
            
        rotated_image = pygame.transform.rotate(self.img, self.tilt) #rotates along top left #x, y is top left
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center) #idk but makes rotate along center
        win.blit(rotated_image, new_rect.topleft)
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    


class Pipe: 
    GAP = 200 #Space in between pipes
    VEL = 5
    
    def __init__(self, x):
        self.x = x 
        self.height = 0
        self.gap = 100
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False #False is pipe is still in front of bird
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height() #negative is above screen
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
    
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
        #masks are array of all pixes inside pygame box for more precise collision
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        #offset is how far masks away from each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #Returns None is no collision
        t_point = bird_mask.overlap(top_mask, top_offset)
        
        if t_point or b_point:
            return True
        
        return False
        


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
    
def intro_screen():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    intro = True
    clock = pygame.time.Clock()
    win.blit(BG_IMG, (0,0))
    
    
    while intro:
        clock.tick(30) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro = False
        
            
        win.blit(BG_IMG, (0,0)) 
    
        text = STAT_FONT.render("Flappy Bird", 1, (255, 255, 255))
        win.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, 100))
        
        pygame.draw.rect(win, (220, 80, 0), (WIN_WIDTH / 2 - 150, 300, 300, 150))
        text2 = STAT_FONT.render("Press Space to Start", 1, (255, 255, 255))
        win.blit(text2, (WIN_WIDTH / 2 - text2.get_width() / 2, 350))
        
        pygame.display.update()
    
    
    
def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))

    
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    
    bird.draw(win)
    base.draw(win)
    
    pygame.display.update()
    
def main():
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    
    run = True
    score = 0
 
    while run:
        clock.tick(30) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()
        base.move()
        

        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                pygame.quit()
                
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #if pipe is offscreen
                rem.append(pipe) #adding to list to later remove
            
            if not pipe.passed and pipe.x < bird.x: #bird passes pipe
                pipe.passed = True
                add_pipe = True
            
            pipe.move()
            
        if add_pipe:
            score += 1
            pipes.append(Pipe(550))
            
        for i in rem:
            pipes.remove(i)
            
        if bird.y + bird.img.get_height() >= 730:
            pygame.quit()
            
            
        draw_window(win, bird, pipes, base, score)
   
        
        
    pygame.quit()

intro_screen()           
main()
    
