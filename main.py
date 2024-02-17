import pygame
import random
import pickle  # Import the pickle module for saving and loading game state

pygame.init()
square_width = 750
pixel_width = 50
screen = pygame.display.set_mode([square_width] * 2)
clock = pygame.time.Clock()
running = True
paused = False  # Variable to track whether the game is paused or not

font = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 72)
score = 0
high_score = 0
snake_length = 1

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def generate_starting_position():
    position_range = (pixel_width // 2, square_width - pixel_width // 2, pixel_width)
    return [random.randrange(*position_range), random.randrange(*position_range)]

def reset():
    global score
    score = 0
    target.center = generate_starting_position()
    snake_pixel.center = generate_starting_position()
    return snake_pixel.copy()

def is_out_of_bounds():
    return snake_pixel.bottom > square_width or snake_pixel.top < 0 \
        or snake_pixel.left < 0 or snake_pixel.right > square_width

def collision_with_self():
    return any(snake_part.colliderect(snake_pixel) for snake_part in snake[:-1])

snake_pixel = pygame.rect.Rect([0, 0, pixel_width - 2, pixel_width - 2])
snake_pixel.center = generate_starting_position()
snake = [snake_pixel.copy()]
snake_direction = (0, 0)
snake_length = 1

target = pygame.rect.Rect([0, 0, pixel_width - 2, pixel_width - 2])
target.center = generate_starting_position()

# Settings
speed = 5
difficulty = "Easy"

def save_game_state():
    # Save the game state using pickle
    game_state = {
        'score': score,
        'snake_length': snake_length,
        'snake': snake,
        'snake_pixel': snake_pixel,
        'snake_direction': snake_direction,
        'target': target
    }
    with open('game_state.pkl', 'wb') as file:
        pickle.dump(game_state, file)

def load_game_state():
    # Load the game state using pickle
    with open('game_state.pkl', 'rb') as file:
        game_state = pickle.load(file)
    return game_state['score'], game_state['snake_length'], game_state['snake'], \
           game_state['snake_pixel'], game_state['snake_direction'], game_state['target']

def display_game_over():
    global high_score

    # Display final score
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(final_score_text, (square_width // 2 - 80, square_width // 2 - 82))

    # Update high score if needed
    if score > high_score:
        high_score = score

    # Display high score
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (square_width // 2 - 80, square_width // 2 - 36))

    # Congratulatory message
    congrats_text = font_large.render("Congratulations!", True, WHITE)
    screen.blit(congrats_text, (square_width // 2 - 200, square_width // 2))

    # Try Again button
    try_again_text = font.render("Try Again", True, WHITE)
    try_again_rect = try_again_text.get_rect(center=(square_width // 2, square_width // 2 + 80))
    pygame.draw.rect(screen, RED, try_again_rect, 2)
    screen.blit(try_again_text, try_again_rect)

    pygame.display.flip()

    waiting_for_try_again = True
    while waiting_for_try_again:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if try_again_rect.collidepoint(x, y):
                    waiting_for_try_again = False

        clock.tick(10)

# Initialize fonts for user interface enhancements
ui_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 36)

# Power-up variables
power_up_active = False
power_up_position = [0, 0]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Toggle pause when 'P' key is pressed
                paused = not paused
                if paused:
                    save_game_state()
                else:
                    score, snake_length, snake, snake_pixel, snake_direction, target = load_game_state()

    if paused:
        # Display "Paused" message
        paused_text = font_large.render("Paused", True, WHITE)
        screen.blit(paused_text, (square_width // 2 - 100, square_width // 2))
        pygame.display.flip()
        clock.tick(5)  # Lower the clock speed when paused
        continue

    screen.fill(BLACK)

    if is_out_of_bounds() or collision_with_self():
        display_game_over()
        snake_pixel = reset()
        snake = [snake_pixel.copy()]

    # Check collision with power-up
    if power_up_active and snake_pixel.colliderect(pygame.Rect(power_up_position, [pixel_width - 2, pixel_width - 2])):
        power_up_active = False
    # Implement the effects of the power-up here

    if not power_up_active and random.random() < 0.01:  # 1% chance of generating a power-up
        power_up_active = True
        power_up_position = generate_starting_position()

    # Draw power-up
    if power_up_active:
        pygame.draw.rect(screen, BLUE, pygame.Rect(power_up_position, [pixel_width - 2, pixel_width - 2]))

    if snake_pixel.center == target.center:
        target.center = generate_starting_position()
        score += 1
        snake_length += 1
        snake.append(snake_pixel.copy())

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        snake_direction = (0, - pixel_width)
    if keys[pygame.K_s]:
        snake_direction = (0, pixel_width)
    if keys[pygame.K_a]:
        snake_direction = (- pixel_width, 0)
    if keys[pygame.K_d]:
        snake_direction = (pixel_width, 0)

    for snake_part in snake:
        pygame.draw.rect(screen, GREEN, snake_part)

    pygame.draw.rect(screen, RED, target)

    snake_pixel.move_ip(snake_direction)
    snake.append(snake_pixel.copy())
    snake = snake[-snake_length:]

    # Display the score
    score_text = ui_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display UI buttons
    start_new_game_text = button_font.render("Start New Game", True, WHITE)
    start_new_game_rect = start_new_game_text.get_rect(topleft=(2, square_width - 80))
    pygame.draw.rect(screen, RED, start_new_game_rect, 2)
    screen.blit(start_new_game_text, start_new_game_rect)

    exit_game_text = button_font.render("Exit", True, WHITE)
    exit_game_rect = exit_game_text.get_rect(topright=(square_width - 10, square_width - 80))
    pygame.draw.rect(screen, RED, exit_game_rect, 2)
    screen.blit(exit_game_text, exit_game_rect)

    # Display settings
    settings_text = button_font.render(f"Speed: {speed} | Difficulty: {difficulty}", True, WHITE)
    screen.blit(settings_text, (square_width // 2 - 180, 10))

    pygame.display.flip()

    clock.tick(speed)

pygame.quit()
