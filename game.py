import pygame, sys, random

def restart_game():
    global game_active, chicken_flying, score
    start_sound.play()
    game_active = 1
    obstacle_list.clear()
    chicken_rect.center = (100, 500)
    chicken_flying = -10
    score = 0

def grass_floor():
    floor_y = 920
    screen.blit(grass, (x_os, floor_y))
    screen.blit(grass, (x_os + 1024, floor_y))

def lava_floor():
    lava_y = 920
    screen.blit(the_floor_is_lava, (x_os, lava_y))
    screen.blit(the_floor_is_lava, (x_os + 1024, lava_y))

def rotate_chicken(chicken):
    return pygame.transform.rotozoom(chicken, -chicken_flying * 4, 1)

def create_obstacle():
    pos_y = 320 + 580 * random.random()
    bottom_obstacle = obstacle.get_rect(midtop = (1124, pos_y))
    top_obstacle = obstacle.get_rect(midbottom = (1124, pos_y - 300))
    return bottom_obstacle, top_obstacle

def move_obstacle(obstacles):
    for obs in obstacles:
        obs.centerx -= 5  #moving speed
    return [obs for obs in obstacles if obs.right > -20]  #ne vraca prepreke koje nisu na ekranu

def show_obstacles(obstacles):
    for obs in obstacles:
        if obs.bottom >= 920:
            screen.blit(obstacle, obs)
        else:
            flip_obstacle = pygame.transform.flip(obstacle, False, True)
            screen.blit(flip_obstacle, obs)

def collision_check(obstacles):
    for obs in obstacles:
        if chicken_rect.colliderect(obs):
            dead_sound.play()
            return 0
    if chicken_rect.top < -150 or chicken_rect.bottom > 920:
        dead_sound.play()
        return 0
    return 1

def main_menu():
    score_text = text_font.render(f'SCORE: {int(score)}', True, (233, 244, 246))  #(145, 86, 59)
    score_rect = score_text.get_rect(center = (512,730))
    screen.blit(score_text, score_rect)
    score_text = text_font.render('PRESS SPACE TO PLAY!', True, (233, 244, 246))
    score_rect = score_text.get_rect(center=(512, 800))
    screen.blit(score_text, score_rect)
    chicken_rect = chicken.get_rect(center=(100, 900))
    screen.blit(chicken, chicken_rect)

def real_time_score():
    score_text = text_font.render(str(score), True, (233, 244, 246))
    score_rect = score_text.get_rect(center=(512, 800))
    screen.blit(score_text, score_rect)



#pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=4096)
pygame.init() #basicly main
screen = pygame.display.set_mode((1024,1024))
clock = pygame.time.Clock()
text_font = pygame.font.Font('assets/font/04B_30__.TTF', 50)

#ingame vars
gravity = 0.25
chicken_flying = 0
game_active = -1  # -1=intro , 0=ded , 1=ingame
score = 0
#pozadina
bg = pygame.image.load('assets/skyBG.png').convert()
grass = pygame.image.load('assets/grass.png').convert()
the_floor_is_lava = pygame.image.load("assets/the_floor_is_lava.png").convert_alpha()
x_os = 0     #ground and bg speed
#kokosa
dead_chicken = pygame.image.load('assets/ded chicken.png').convert_alpha()
chicken0 = pygame.image.load('assets/little legs0.png').convert_alpha()
chicken1 = pygame.image.load('assets/little legs1.png').convert_alpha()
chicken_frames = [chicken0, chicken1]
frame_index = 0
chicken = chicken_frames[frame_index]
#chicken = pygame.transform.scale(chicken, (82,84)) #za smanjit/povecat kokos
chicken_rect = chicken.get_rect(center = (100, 500))
WINGFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(WINGFLAP, 250)

#prepreke
obstacle = pygame.image.load('assets/vele vile.png')
# obstacle = pygame.transform.scale2x(obstacle)
obstacle_list = []
SPAWNER = pygame.USEREVENT
pygame.time.set_timer(SPAWNER, 1200)

#Sounds
dead_sound = pygame.mixer.Sound('assets/sounds/bum.wav')
fly1 = pygame.mixer.Sound('assets/sounds/fly1.wav')
fly2 = pygame.mixer.Sound('assets/sounds/fly2.wav')
fly3 = pygame.mixer.Sound('assets/sounds/fly3.wav')
fly4 = pygame.mixer.Sound('assets/sounds/fly4.wav')
fly_sound_index = 0
fly_sound_list = [fly1, fly2, fly3, fly4]
intro_game_sound = pygame.mixer.Sound('assets/sounds/try again.wav')
start_sound = pygame.mixer.Sound('assets/sounds/start.wav')


intro_game_sound.play()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active == 1:
                fly_sound_list[fly_sound_index].play()
                fly_sound_index += 1
                if fly_sound_index == 4: fly_sound_index = 0
                chicken_flying = -10    #koliko poleti
            if event.key == pygame.K_SPACE and game_active < 1:
                restart_game()
        if event.type == SPAWNER:
            obstacle_list.extend(create_obstacle())
        if event.type == WINGFLAP:
            frame_index = abs(1-frame_index)
            chicken = chicken_frames[frame_index]


    #mirna pozadina: screen.blit(bg, (0,0))
    screen.blit(bg, (x_os, 0))
    screen.blit(bg, (x_os + 1024, 0))

    if game_active == 1:
        #kretanje kokosi
        chicken_flying += gravity
        rotated_chicken = rotate_chicken(chicken)
        chicken_rect.centery += chicken_flying
        #screen.blit(chicken, chicken_rect)   #mirna kokos
        screen.blit(rotated_chicken, chicken_rect)  #rotirajuca kokos

        game_active = collision_check(obstacle_list)

        real_time_score()
        score += 1

        obstacle_list = move_obstacle(obstacle_list)
        show_obstacles(obstacle_list)
    elif game_active == 0:
        chicken_flying += gravity
        chicken_rect.centery += chicken_flying
        screen.blit(dead_chicken, chicken_rect)
        main_menu()
    elif game_active == -1:
        main_menu()

    #kretanje pozadine
    x_os -= 1
    if (x_os < -1024): x_os = 0
    grass_floor()
    #lava_floor()

    pygame.display.update()
    clock.tick(120) #fps

