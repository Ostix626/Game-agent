# -*- coding: utf-8 -*-
"""
Created on Tue April  13 12:35:34 2021

@author: filip
"""
import pickle
import numpy as np
import pygame
import sys
import neat
import os
import random
import matplotlib.pyplot as plt

pygame.font.init()
chicken0 = pygame.image.load(os.path.join("imgs", "little legs0.png"))
chicken1 = pygame.image.load(os.path.join("imgs", "little legs1.png"))
CHICKEN_IMGS = [chicken0, chicken1]
OBSTACLE_IMG = pygame.image.load(os.path.join("imgs", "vele vile.png"))
GROUND_IMG = pygame.image.load(os.path.join("imgs", "grass.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "skyBG.png"))
STAT_FONT = pygame.font.Font('fonts/04B_30__.TTF', 50)

WIN_WIDTH = 1024
WIN_HEIGHT = 1024
GROUND_HEIGHT = 920
BG_WIDTH = BG_IMG.get_width()
GROUND_WIDTH = GROUND_IMG.get_width()
SPEED = 6
GAP = 250
x_os = 0
chicken_img_index = 0

GENERATION = 0
ALIVE = 0
best_genome = 0
fitness_per_generation = []
pygame.init()
WINGFLAP = pygame.USEREVENT
pygame.time.set_timer(WINGFLAP, 250)  # brzina animacije krila kokosi

def raise_difficulty(passed):
    global GAP, SPEED
    
    if(GAP > 200 and (passed / 5) % 2 == 1): GAP -= 10
    elif SPEED < 10: SPEED += 1
    
def calculate_height(top_height):
    height = random.randrange(80, 580)
    top = height - top_height
    bottom = height + GAP
    
    return height, top, bottom

def collide_check(obstacle, chicken, win):
    bottom_obstacle, top_obstacle = obstacle.get_rect()
    chicken_rect = chicken.get_rect()
    
    if chicken_rect.colliderect(bottom_obstacle) or chicken_rect.colliderect(top_obstacle): 
        return True
    return False
    
class Chicken:
    global chicken_img_index, CHICKEN_IMGS

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = 0
        self.gravity = 0.5
        self.flying = 0
        self.img = CHICKEN_IMGS[chicken_img_index]

    def jump(self):
        self.flying = -10.5

    def move(self):
        self.flying += self.gravity
        if (self.flying > 15): self.flying = 15

        self.rotation = -self.flying
        self.y += self.flying

    def draw(self, win):
        self.img = CHICKEN_IMGS[chicken_img_index]
        win.blit(pygame.transform.rotozoom(self.img, self.rotation * 4, 1), self.get_rect())

    def get_rect(self):
        return self.img.get_rect(center = (self.x, self.y))


class Obstacle:
    global SPEED, GAP

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.OBSTACLE_TOP = pygame.transform.flip(OBSTACLE_IMG, False, True)
        self.OBSTACLE_BOTTOM = OBSTACLE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height, self.top, self.bottom = calculate_height(self.OBSTACLE_TOP.get_height())

    def move(self):
        self.x -= SPEED

    def draw(self, win):
        win.blit(self.OBSTACLE_TOP, (self.x, self.top))
        win.blit(self.OBSTACLE_BOTTOM, (self.x, self.bottom))
        
    def get_rect(self):
        return self.OBSTACLE_BOTTOM.get_rect(midtop=(self.x, self.bottom)), self.OBSTACLE_TOP.get_rect(midbottom=(self.x, self.height))
        

def moveBG(win):
    global SPEED, BG_IMG, BG_WIDTH, x_os
    x_os -= SPEED
    if (x_os < -BG_WIDTH): x_os = 0
    win.blit(BG_IMG, (x_os, 0))
    win.blit(BG_IMG, (x_os + BG_WIDTH, 0))


def moveGound(win):
    global SPEED, GROUND_HEIGHT, GROUND_IMG, GROUND_WIDTH, x_os
    win.blit(GROUND_IMG, (x_os, GROUND_HEIGHT))
    win.blit(GROUND_IMG, (x_os + GROUND_WIDTH, GROUND_HEIGHT))


def draw_window(win, chickens, obstacles, score, GENERATION):
    moveBG(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    text = STAT_FONT.render("Generation: " + str(GENERATION), 1, (235, 247, 247))
    win.blit(text, (10, 10))

    text = STAT_FONT.render("Gap: " + str(GAP), 1, (235, 247, 247))
    win.blit(text, (10, 675))

    text = STAT_FONT.render("Speed: " + str(SPEED), 1, (235, 247, 247))
    win.blit(text, (10, 735))

    text = STAT_FONT.render("Alive: " + str(ALIVE), 1, (235, 247, 247))
    win.blit(text, (10, 795))

    text = STAT_FONT.render("Score: " + str(score), 1, (235, 247, 247))
    win.blit(text, (10, 855))


    moveGound(win)
    drawNet(win, best_genome)

    for chicken in chickens:
        chicken.draw(win)
    pygame.display.update()


def drawNet(win, genome):
    y_graph = 800
    x_graph = 850
    input_nodes = 3
    output_nodes = 1
    circle_radius = 10
    y_offset = (circle_radius * 2 + circle_radius)
    x_offset = y_offset * 2
    max_offset = y_offset * max([input_nodes, output_nodes])
    offset_pos = 0

    if genome != 0:
        node_layers = []
        layer = []
        for node in range(input_nodes):
            layer.append(-node - 1)
        node_layers.append(layer)
        layer = []
        for node in genome.nodes:
            if node not in range(output_nodes):
                if len(layer) >= 4:
                    node_layers.append(layer)
                    layer = []
                layer.append(node)
        if len(layer) > 0:
            node_layers.append(layer)
        layer = []
        for node in range(output_nodes):
            layer.append(node)
        node_layers.append(layer)

        if len(node_layers) > 2:
            x_graph -= (len(node_layers) - 2) * x_offset

        for con in genome.connections:
            node_one_y = 0
            node_one_x = 0
            node_two_y = 0
            node_two_x = 0
            for layer_id in range(len(node_layers)):
                for node_id in range(len(node_layers[layer_id])):
                    temp = node_layers[layer_id]
                    if node_id % 2 > 0:
                        offset_pos += 1
                    if con[0] == temp[node_id]:
                        node_one_y = offset_pos
                        node_one_x = layer_id
                    if con[1] == temp[node_id]:
                        node_two_y = offset_pos
                        node_two_x = layer_id
                    offset_pos = -offset_pos
                offset_pos = 0
            pygame.draw.line(win, (0, 0, 0), (
            round(x_graph + x_offset * node_one_x), round(y_graph + max_offset / 2 + y_offset * node_one_y)), (
                             round(x_graph + x_offset * node_two_x),
                             round(y_graph + max_offset / 2 + y_offset * node_two_y)), 2)

            for layer_id in range(len(node_layers)):
                for node_id in range(len(node_layers[layer_id])):
                    if node_id % 2 > 0:
                        offset_pos += 1
                    pygame.draw.circle(win, (235, 247, 247), (
                        round(x_graph + x_offset * layer_id), round(y_graph + max_offset / 2 + y_offset * offset_pos)),
                                       circle_radius)
                    offset_pos = -offset_pos
                offset_pos = 0


def main(genomes, config):
    global GENERATION, ALIVE, SPEED, GAP, chicken_img_index, best_genome
    # SPEED = 5
    # GAP = 270
    GENERATION += 1
    nets = []
    ge = []
    chickens = []
    current_best = 0

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        chickens.append(Chicken(300, 550))
        g.fitness = 0
        ge.append(g)

    obstacles = [Obstacle(1100)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0

    while run:
        # clock.tick(30)
        for event in pygame.event.get():
            if event.type == WINGFLAP:
                chicken_img_index = abs(1 - chicken_img_index)
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        obstacle_ind = 0

        if len(chickens) > 0:
            ALIVE = len(chickens)
            if len(obstacles) > 1 and chickens[0].x > obstacles[0].x + obstacles[0].OBSTACLE_TOP.get_width():
                obstacle_ind = 1
        else:
            ALIVE = 0
            run = False
            break

        for x, chicken in enumerate(chickens):
            chicken.move()
            ge[x].fitness += 0.01

            output = nets[x].activate(
                (chicken.y, abs(obstacles[obstacle_ind].height), abs(obstacles[obstacle_ind].bottom)))
                # (chicken.y, abs(chicken.y - obstacles[obstacle_ind].height), abs(chicken.y - obstacles[obstacle_ind].bottom)))

            if output[0] > 0.2:
                chicken.jump()

        add_obstacle = False
        deleted_obstacles = []

        for obstacle in obstacles:
            for x, chicken in enumerate(chickens):
                if collide_check(obstacle, chicken, win):
                    chickens.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not obstacle.passed and obstacle.x < chicken.x:
                    obstacle.passed = True
                    add_obstacle = True

            if obstacle.x + obstacle.OBSTACLE_TOP.get_width() < 0:
                deleted_obstacles.append(obstacle)

            obstacle.move()

        if add_obstacle:
            score += 1
            # if(score % 10 == 0 and score <= 100): raise_difficulty(score)
            if (score % 5 == 0 and (GAP > 200 or SPEED < 10)): raise_difficulty(score)
            for g in ge:
                g.fitness += 1
            obstacles.append(Obstacle(1100))

        for obstacle in deleted_obstacles:
            obstacles.remove(obstacle)

        for x, chicken in enumerate(chickens):
            if chicken.y + chicken.img.get_height() >= 920 or chicken.y < -10:
                chickens.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, chickens, obstacles, score, GENERATION)
        clock.tick(60)

        # if genomes[0].fitness > 20:
        #     flag = True
        # for _, genome in genomes:
        #     flag = False
        #     if genome.fitness >= current_best:
        #         current_best = genome.fitness
        #     print(current_best)
        #     if current_best > 100:
        #         flag = True
        # if flag:
        #     break
        if len(ge) > 0:
            fitness = ge[0].fitness
            print(fitness)
            # if fitness >= current_best:
            #     current_best = fitness
            if fitness > 100:
                break

    best_fitness = 0
    for _, genome in genomes:
        if genome.fitness >= current_best:
            current_best = genome.fitness
        if genome.fitness >= best_fitness:
            best_fitness = genome.fitness
            best_genome = genome
            
    fitness_per_generation.append(current_best)
    
    if np.max(fitness_per_generation) > 100:
        generation_array = [(i+1) for i in range(GENERATION)]
        print(generation_array)
        plt.plot(generation_array, fitness_per_generation)
        plt.xlabel("Generation")
        plt.ylabel("Best chicken's fitness value")
        plt.xticks(generation_array)
        plt.show()
        pygame.quit()
        sys.exit()
            


def run():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    best_chicken = pop.run(main, 50)
    with open('best chicken', 'wb') as f:
        pickle.dump(best_chicken, f)
    print(best_chicken)

if __name__ == "__main__":
    # with open('best chicken', 'rb') as f:
    #     best_chicken = pickle.load(f)
    run()