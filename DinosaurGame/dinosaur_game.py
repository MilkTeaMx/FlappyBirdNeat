from ftplib import MAXLINE
from tokenize import Triple
import pygame 
import neat
import random
import sys
import os
import math

pygame.init()

#CONSTANT

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))
FONT = pygame.font.Font("freesansbold.ttf", 20)


#DINOSAUR
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]

JUMPING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]


#OBSTACLES
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5
    
    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.step_index = 0
        
        #visualization
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
    def update(self):
        if self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0
        
    def jump(self):
        
        self.image = JUMPING[self.step_index // 5]
        self.step_index += 1
        
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
            
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL
            
        
    def run(self):
        
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1
        
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2)
        
        
class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        
    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()
    
    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)
    
class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325
        
class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300

def remove(index):
    dinosaurs.pop(index)
    ge.pop(index)
    nets.pop(index)
        
def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx**2 + dy**2)


#This function must assign python float to the fitness of each genome
def eval_genomes(genomes, config_file):
    
        
    global game_speed, y_pos_bg, x_pos_bg, points, obstacles, dinosaurs, ge, nets
    
    game_speed = 20
    y_pos_bg = 380
    x_pos_bg = 0
    points = 0
    dinosaurs = []
    obstacles = []
    
    ge = []      #Each object contains connections, nodes and fitness level
    nets = []    #Stores nueral networks of each dinosaur
    
    for genome_id, genome in genomes:
        
        dinosaurs.append(Dinosaur())
        ge.append(genome)
        genome.fitness = 0
        
        net = neat.nn.FeedForwardNetwork.create(genome, config_file)
        nets.append(net)

    def score():
        global points, game_speed
        points += 1
        
        #Increasing speed of game as score increases
        if points % 100 == 0:
            game_speed += 1
            
        text = FONT.render(f'Points: {str(points)}', True, (0,0,0))
        SCREEN.blit(text, (950, 50))
    
    def background():
        
        global x_pos_bg, y_pos_bg
        
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        
        x_pos_bg -= game_speed
    
    def statistics():
        global dinosaurs, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive: {len(dinosaurs)}', True, (0,0,0))
        text_2 = FONT.render(f'Generation: {pop.generation+1}', True, (0,0,0))
        text_3 = FONT.render(f'Game Speed: {str(game_speed)}', True, (0,0,0))
        
        SCREEN.blit(text_1, (50, 450))
        SCREEN.blit(text_2, (50, 480))
        SCREEN.blit(text_3, (50, 510))
        
   
     
    clock = pygame.time.Clock()
    run = True
    
    #Loop
    while run:
                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dinosaur.dino_jump = True
                    dinosaur.dino_run = False
                
                
        SCREEN.fill((255, 255, 255))
        
        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)
        
        if len(dinosaurs) == 0:
            break
        
        #Generating Obstacles
        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))
                
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            
            for i, dinosaur in enumerate(dinosaurs):
                ge[i].fitness += 1
                if dinosaur.rect.colliderect(obstacle.rect):
                   
                    remove(i)
              
                    #later change this
                
        for i, dinosaur in enumerate(dinosaurs):
            output = nets[i].activate((dinosaur.rect.y, distance((dinosaur.rect.x, dinosaur.rect.y), obstacle.rect.midtop)))
          
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False

        
        background()
        score()
        statistics()
    
        clock.tick(30)
        pygame.display.update()
        



#Main Run Function
def run(config_file):
    
    global pop
    
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )
    
    pop = neat.Population(config)
    pop.run(eval_genomes, 50) #eval genoms is the evolution / fitness function, 50times
    
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir, 'config.txt')
    run(config_file)