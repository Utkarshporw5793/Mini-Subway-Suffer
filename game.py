import pygame
import random
import time
import os
import sys

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GROUND_HEIGHT = 100
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Subway Surfer")
clock = pygame.time.Clock()

# Load Assets function (load once)
def load_image(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

# Asset paths - Adjust this path to your actual folder
asset_path = r"C:\Users\acer\Python Tutorial\SubwayRunnerGame\assets"
player_img = load_image(os.path.join(asset_path, "character.png"), (60, 90))
obstacle_img = load_image(os.path.join(asset_path, "barrier.png"), (50, 80))
coin_img = load_image(os.path.join(asset_path, "coin.png"), (40, 40))
powerup_img = load_image(os.path.join(asset_path, "jetpack.png"), (40, 40))
cloud_img = load_image(os.path.join(asset_path, "cloud.png"), (200, 150))

# Sound (optional, comment if slowing)
try:
    pygame.mixer.music.load(os.path.join(asset_path, "background.mp3"))
    jump_sound = pygame.mixer.Sound(os.path.join(asset_path, "jump.wav"))
    coin_sound = pygame.mixer.Sound(os.path.join(asset_path, "coin.wav"))
    score_sound = pygame.mixer.Sound(os.path.join(asset_path, "score.wav"))
    gameover_sound = pygame.mixer.Sound(os.path.join(asset_path, "gameover.wav"))
    pygame.mixer.music.set_volume(0.3)
except Exception as e:
    print("Sound load error:", e)
    jump_sound = coin_sound = score_sound = gameover_sound = None

# High Score handling
highscore_path = "highscore.txt"
if not os.path.exists(highscore_path):
    with open(highscore_path, "w") as f:
        f.write("0")
with open(highscore_path, "r") as f:
    high_score = int(f.read())

# Draw Text utility
def draw_text(text, x, y, size=36, color=BLACK):
    font = pygame.font.SysFont(None, size)
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

# Updated Gradient background function with smooth sky blue gradient
# Before main game loop, create gradient surface once:
def create_gradient_surface():
    gradient_surf = pygame.Surface((WIDTH, HEIGHT))
    top_color = pygame.Color(180, 220, 255)
    bottom_color = pygame.Color(120, 180, 255)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = top_color.r * (1 - ratio) + bottom_color.r * ratio
        g = top_color.g * (1 - ratio) + bottom_color.g * ratio
        b = top_color.b * (1 - ratio) + bottom_color.b * ratio
        pygame.draw.line(gradient_surf, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
    return gradient_surf

gradient_background = create_gradient_surface()

# Start Screen with input box
def start_screen():
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    user_text = ''
    font = pygame.font.SysFont(None, 48)
    prompt_text = "Type 'start' and press Enter to begin"
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If user clicks on the input box toggle active
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if user_text.strip().lower() == "start":
                            return  # start the game
                        else:
                            user_text = ''  # reset if wrong
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        # Limit input length to 10 chars
                        if len(user_text) < 10:
                            user_text += event.unicode

        screen.fill(WHITE)
        # Draw prompt
        draw_text(prompt_text, WIDTH//2 - 250, HEIGHT//2 - 60, size=32, color=BLACK)

        # Render the current text.
        txt_surface = font.render(user_text, True, color)
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width

        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

# Main game loop function
def main_game():
    # Initialize game variables
    player_x = 100
    player_y = HEIGHT - GROUND_HEIGHT - player_img.get_height()
    player_speed = 7
    velocity_y = 0
    gravity = 1
    jump_power = 15
    jump_count = 0
    max_jumps = 2

    obstacle_x = WIDTH
    obstacle_y = HEIGHT - GROUND_HEIGHT - obstacle_img.get_height()
    obstacle_speed = 9  # slightly faster for more excitement

    coin_x = WIDTH + 300
    coin_y = HEIGHT - GROUND_HEIGHT - 100
    coin_speed = 9

    powerup_x = WIDTH + 800
    powerup_y = HEIGHT - GROUND_HEIGHT - 150
    powerup_speed = 9

    clouds = [{"x": WIDTH + i * 300, "y": random.randint(50, 150)} for i in range(3)]
    cloud_speed = 2  # slight increase

    fly_active = False
    fly_timer = 0
    FLY_DURATION = 5
    score = 0
    game_over = False
    paused = False

    mission = random.choice(["collect 10 coins", "jump 5 times", "survive 30s"])
    mission_progress = 0
    mission_target = {"collect 10 coins": 10, "jump 5 times": 5, "survive 30s": 30}[mission]
    mission_start_time = time.time()

    global high_score

    while True:
        dt = clock.tick(FPS)
        screen.blit(gradient_background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p] and not game_over:
            paused = not paused
            time.sleep(0.2)

        if not game_over and not paused:
            if keys[pygame.K_LEFT]:
                player_x -= player_speed
                if player_x < 0: player_x = 0
            if keys[pygame.K_RIGHT]:
                player_x += player_speed
                if player_x > WIDTH - player_img.get_width():
                    player_x = WIDTH - player_img.get_width()

            if keys[pygame.K_SPACE] and jump_count < max_jumps and not fly_active:
                velocity_y = -jump_power
                jump_count += 1
                if mission == "jump 5 times":
                    mission_progress += 1
                if jump_sound:
                    jump_sound.play()

            if not fly_active:
                player_y += velocity_y
                velocity_y += gravity
            else:
                player_y = 150  # fixed flying height

            if not fly_active and player_y >= HEIGHT - GROUND_HEIGHT - player_img.get_height():
                player_y = HEIGHT - GROUND_HEIGHT - player_img.get_height()
                velocity_y = 0
                jump_count = 0

            if mission == "survive 30s":
                mission_progress = int(time.time() - mission_start_time)

            for cloud in clouds:
                cloud["x"] -= cloud_speed
                if cloud["x"] < -cloud_img.get_width():
                    cloud["x"] = WIDTH + random.randint(100, 300)
                screen.blit(cloud_img, (cloud["x"], cloud["y"]))

            obstacle_x -= obstacle_speed
            if obstacle_x < -obstacle_img.get_width():
                obstacle_x = WIDTH + random.randint(200, 400)
                score += 1
                if score_sound:
                    score_sound.play()

            coin_x -= coin_speed
            if coin_x < -coin_img.get_width():
                coin_x = WIDTH + random.randint(400, 600)
                coin_y = HEIGHT - GROUND_HEIGHT - random.randint(40, 120)

            powerup_x -= powerup_speed
            if powerup_x < -powerup_img.get_width():
                powerup_x = WIDTH + random.randint(1000, 1500)

            player_rect = pygame.Rect(player_x, player_y, player_img.get_width(), player_img.get_height())
            obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_img.get_width(), obstacle_img.get_height())
            coin_rect = pygame.Rect(coin_x, coin_y, coin_img.get_width(), coin_img.get_height())
            powerup_rect = pygame.Rect(powerup_x, powerup_y, powerup_img.get_width(), powerup_img.get_height())

            if player_rect.colliderect(obstacle_rect) and not fly_active:
                game_over = True
                pygame.mixer.music.stop()
                if gameover_sound:
                    gameover_sound.play()
                if score > high_score:
                    with open(highscore_path, "w") as f:
                        f.write(str(score))
                    high_score = score

            if player_rect.colliderect(coin_rect):
                score += 5
                if mission == "collect 10 coins":
                    mission_progress += 1
                coin_x = WIDTH + random.randint(400, 600)
                if coin_sound:
                    coin_sound.play()

            if player_rect.colliderect(powerup_rect):
                fly_active = True
                fly_timer = time.time()
                powerup_x = WIDTH + random.randint(1000, 1500)

            if fly_active and (time.time() - fly_timer > FLY_DURATION):
                fly_active = False

            # Draw all game elements
            screen.blit(player_img, (player_x, player_y))
            screen.blit(obstacle_img, (obstacle_x, obstacle_y))
            screen.blit(coin_img, (coin_x, coin_y))
            screen.blit(powerup_img, (powerup_x, powerup_y))

            # Ground
            pygame.draw.rect(screen, (0, 200, 0), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

            # HUD
            draw_text(f"Score: {score}", 10, 10)
            draw_text(f"High Score: {high_score}", 10, 40, size=28, color=(50, 50, 50))
            draw_text(f"Mission: {mission} ({mission_progress}/{mission_target})", 10, 70, size=24, color=(0, 100, 0))
            if mission_progress >= mission_target:
                draw_text("Mission Complete!", WIDTH // 2 - 120, 100, size=40, color=(0, 180, 0))

        elif paused:
            draw_text("Game Paused. Press 'P' to Resume.", WIDTH // 2 - 180, HEIGHT // 2 - 30, size=36, color=(255, 0, 0))

        else:
            draw_text("Game Over!", WIDTH // 2 - 100, HEIGHT // 2 - 50, size=60, color=(255, 0, 0))
            draw_text(f"Final Score: {score}", WIDTH // 2 - 100, HEIGHT // 2 + 10, size=40)
            draw_text("Press R to Restart or Q to Quit", WIDTH // 2 - 160, HEIGHT // 2 + 60, size=30)

            if keys[pygame.K_r]:
                # Reset game variables
                player_x = 100
                player_y = HEIGHT - GROUND_HEIGHT - player_img.get_height()
                velocity_y = 0
                obstacle_x = WIDTH
                coin_x = WIDTH + 300
                powerup_x = WIDTH + 800
                score = 0
                game_over = False
                jump_count = 0
                fly_active = False
                mission = random.choice(["collect 10 coins", "jump 5 times", "survive 30s"])
                mission_progress = 0
                mission_target = {"collect 10 coins": 10, "jump 5 times": 5, "survive 30s": 30}[mission]
                mission_start_time = time.time()
                pygame.mixer.music.play(-1)
                time.sleep(0.2)
            elif keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# Run game
if __name__ == "__main__":
    start_screen()
    if pygame.mixer.music.get_busy() == 0:
        pygame.mixer.music.play(-1)
    main_game()
