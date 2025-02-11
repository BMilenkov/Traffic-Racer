import pygame
import random
import sys
import json
import os

pygame.init()
pygame.mixer.init()

WIDTH = 700
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Racer")
DATA_FILE = "DataHolder/game_data.json"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
GRASS_GREEN = (34, 139, 34)
BLUE = (0, 0, 255)

FONT = pygame.font.SysFont(None, 35)
TITLE_FONT = pygame.font.Font(pygame.font.match_font("impact"), 80)
BUTTON_FONT = pygame.font.Font(pygame.font.match_font("arial"), 40)
DETAILS_FONT = pygame.font.SysFont(None, 32, italic=True)
MENU_FONT = pygame.font.SysFont(None, 40, italic=True)
INSTRUCTIONS_TITLE_FONT = pygame.font.Font(None, 48)
INSTRUCTIONS_DETAILS_FONT = pygame.font.Font(None, 26)
CAR_SHOP_TITLE_FONT = pygame.font.SysFont(None, 70, bold=True)

music1 = "./sounds/menusong.wav"
music2 = "./sounds/backgroundmusic.wav"
explosion_sound = pygame.mixer.Sound("./sounds/crash.wav")

background_image = pygame.transform.scale(pygame.image.load("images/backgrounds/background.jpg"), (WIDTH, HEIGHT))
background_image2 = pygame.transform.scale(pygame.image.load("images/backgrounds/background2.jpg"), (WIDTH, HEIGHT))
cash_image = pygame.transform.scale(pygame.image.load('images/icons/cash.png'), (120, 120))
crash_image = pygame.transform.scale(pygame.image.load('images/icons/crash.png'), (150, 150))
lock_image = pygame.image.load('images/icons/locked.png')
lock2_image = pygame.image.load('images/icons/locked2.jpg')

car_images = [
    pygame.transform.scale(pygame.image.load("images/vehicles/taxi.png"), (110, 180)),
    pygame.transform.scale(pygame.image.load("images/vehicles/pickup truck.png"), (110, 180)),
    pygame.transform.scale(pygame.image.load("images/vehicles/van.png"), (110, 180)),
    pygame.transform.scale(pygame.image.load("images/vehicles/truck.png"), (110, 180)),
    pygame.transform.scale(pygame.image.load("images/vehicles/car.png"), (110, 180))
]

car_shop = {
    "car": {"price": 15000, "speed": 200, "acceleration": 18, "power": 300,
            "image": pygame.transform.scale(pygame.image.load("images/vehicles/car.png"), (110, 180))},
    "taxi": {"price": 2000, "speed": 110, "acceleration": 14, "power": 150,
             "image": pygame.transform.scale(pygame.image.load("images/vehicles/taxi.png"), (110, 180))},
    "van": {"price": 9000, "speed": 90, "acceleration": 10, "power": 500,
            "image": pygame.transform.scale(pygame.image.load("images/vehicles/van.png"), (110, 180))},
    "truck": {"price": 50000, "speed": 100, "acceleration": 10, "power": 120,
              "image": pygame.transform.scale(pygame.image.load("images/vehicles/truck.png"), (110, 180))},
    "pickup truck": {"price": 3000, "speed": 100, "acceleration": 10, "power": 120,
                     "image": pygame.transform.scale(pygame.image.load("images/vehicles/pickup truck.png"), (110, 180))}
}

global money, owned_cars, selected_car
global HighScore, player_x, player_y, player_speed, enemy_speed, score, enemy_last_spawn, enemy_spawn_delay

road_width = WIDTH * 0.65
grass_width = (WIDTH - road_width) / 2
road_x = grass_width

player_width = 80
player_height = 170
enemy_width = 80
enemy_height = 170

lane_width = road_width / 2
lane_positions = [
    road_x + (lane_width - enemy_width) / 2,
    road_x + lane_width + (lane_width - enemy_width) / 2
]

lane_change_speed = 5
max_speed = 200
acceleration = 0.2
brake_strength = 0.5
player_car_image = pygame.image.load("images/vehicles/car.png")
player_car_image = pygame.transform.scale(player_car_image, (110, 180))


def play_music(music_file, loop=True):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1 if loop else 0)


def reset_game():
    global player_x, player_y, player_speed, enemy_speed, score, enemy_last_spawn, enemy_spawn_delay
    score = 0
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 10
    player_speed = 20
    enemy_speed = 5
    enemy_last_spawn = 0
    enemy_spawn_delay = 50


def load_data():
    global money, owned_cars, selected_car, player_speed, max_speed, acceleration, brake_strength, player_car_image
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            money = data.get("money", 0)
            owned_cars = data.get("owned_cars", ['car'])
            selected_car = data.get("selected_car", 'car')
            player_car_image = pygame.image.load("./images/vehicles/" + selected_car + ".png")
            player_car_image = pygame.transform.scale(player_car_image, (110, 180))
            max_speed = car_shop[selected_car]["speed"]
            acceleration = car_shop[selected_car]["acceleration"] * 0.01


def save_data():
    global money, owned_cars, selected_car, player_speed, max_speed, acceleration, brake_strength, player_car_image, HighScore
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            existing_data = json.load(f)
            previous_high_score = existing_data.get("high_score", 0)
            previous_money_state = existing_data.get("money", 0)
    else:
        previous_high_score = 0
        previous_money_state = 0

    new_high_score = max(previous_high_score, score)
    HighScore = new_high_score
    new_money_state = previous_money_state + score * 10
    data = {
        "high_score": new_high_score,
        "money": new_money_state,
        "owned_cars": owned_cars,
        "selected_car": selected_car,
        "car_properties": {
            "speed": car_shop[selected_car]['speed'],
            "acceleration": car_shop[selected_car]['acceleration'],
            "power": car_shop[selected_car]['power']
        }
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def draw_road():
    pygame.draw.rect(screen, GRASS_GREEN, (0, 0, grass_width, HEIGHT))
    pygame.draw.rect(screen, GRAY, (road_x, 0, road_width, HEIGHT))
    pygame.draw.rect(screen, GRASS_GREEN, (road_x + road_width, 0, grass_width, HEIGHT))

    pygame.draw.line(screen, WHITE, (road_x, 0), (road_x, HEIGHT), 7)
    pygame.draw.line(screen, WHITE, (road_x + road_width, 0), (road_x + road_width, HEIGHT), 7)

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, WHITE, (WIDTH // 2, y), (WIDTH // 2, y + 20), 5)


def draw_player(x, y):
    screen.blit(player_car_image, (x, y))


def display_info(score, speed):
    screen.blit(FONT.render(f"Score: {score}", True, BLACK), (10, 10))
    screen.blit(FONT.render(f"Speed: {int(speed)} km/h", True, BLACK), (10, 50))


def game_over(enemies, a, b):
    global score, player_speed, enemy_speed, player_y, player_x
    save_data()
    for enemy in enemies:
        screen.blit(enemy[2], (enemy[0], enemy[1]))

    draw_player(a, b)
    screen.blit(crash_image, (a - 10, b - 40))

    window_width = 400
    window_height = 230
    window_x = WIDTH // 2 - window_width // 2
    window_y = HEIGHT // 2 - window_height // 2 - 50

    pygame.draw.rect(screen, (240, 240, 240), (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, (0, 0, 0), (window_x, window_y, window_width, window_height), 3)

    game_over_text = MENU_FONT.render('GAME OVER!', True, (255, 0, 0))
    screen.blit(game_over_text, (window_x + window_width // 2 - game_over_text.get_width() // 2, window_y + 30))

    screen.blit(DETAILS_FONT.render(f"Score: {score}", True, BLACK), (window_width // 2 - 10, window_height // 2 + 200))
    screen.blit(DETAILS_FONT.render(f"High Score:  {HighScore}", True, BLACK), (window_width // 2 + 130, window_height // 2 + 200))


    restart_button_rect = pygame.draw.rect(screen, GRASS_GREEN,
                                           (window_width // 2 - 10, window_height // 2 + 250, 140, 60), border_radius=7)
    draw_button(restart_button_rect, "Restart", MENU_FONT, GRASS_GREEN, GRASS_GREEN, True)

    main_menu_rect = pygame.draw.rect(screen, BLUE, (window_width // 2 + 150, window_height // 2 + 250, 170, 60),
                                      border_radius=7)
    draw_button(main_menu_rect, "Main menu", MENU_FONT, (30, 144, 255), (50, 180, 255), True)

    pygame.display.update()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_x, mouse_y):
                    running = False
                    reset_game()
                    game_loop()
                elif main_menu_rect.collidepoint(mouse_x, mouse_y):
                    running = False
                    reset_game()
                    main_menu()


def draw_button(rect, text, font, base_color, hover_color, is_owned):
    color = hover_color if rect.collidepoint(pygame.mouse.get_pos()) and is_owned else base_color
    pygame.draw.rect(screen, color, rect, border_radius=7)
    pygame.draw.rect(screen, BLACK, rect, width=3, border_radius=7)
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, rect.move(12, 12))


def drawGradient():
    gradient_top = (10, 10, 10)
    gradient_bottom = (50, 50, 50)
    for y in range(HEIGHT):
        if y < 80:
            color = (0, 0, 0)
        else:
            blend_factor = (y - 80) / (HEIGHT - 80)
            color = (
                int(gradient_top[0] + (gradient_bottom[0] - gradient_top[0]) * blend_factor),
                int(gradient_top[1] + (gradient_bottom[1] - gradient_top[1]) * blend_factor),
                int(gradient_top[2] + (gradient_bottom[2] - gradient_top[2]) * blend_factor)
            )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))


def drawBox(instruction_lines):
    text_color = (255, 255, 255)
    box_color = (20, 20, 20)
    border_color = (255, 215, 0)
    padding = 30
    box_x, box_y, box_width, box_height = WIDTH // 6, HEIGHT // 6, WIDTH * 2 // 3, HEIGHT * 2 // 3
    pygame.draw.rect(screen, border_color, (box_x - 4, box_y - 4, box_width + 8, box_height + 8), border_radius=12)
    pygame.draw.rect(screen, box_color, (box_x, box_y, box_width, box_height), border_radius=12)
    title_surface = INSTRUCTIONS_TITLE_FONT.render("TRAFFIC RACER GUIDE", True, text_color)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, box_y + 20))
    y_offset = box_y + 70
    for line in instruction_lines:
        text_surface = INSTRUCTIONS_DETAILS_FONT.render(line, True, text_color)
        screen.blit(text_surface, (box_x + padding, y_offset))
        y_offset += 30


def drawMainMenuButton():
    back_button_rect = pygame.Rect(WIDTH - 160, 10, 150, 45)
    draw_button(back_button_rect, "Main menu", DETAILS_FONT, (255, 255, 0), (255, 255, 100), True)
    return back_button_rect


def drawCashState():
    screen.blit(cash_image, (-40, -40))
    money_text = f"${money:.2f}"
    money_font = pygame.font.SysFont(None, 30)
    money_render = money_font.render(money_text, True, WHITE)
    screen.blit(money_render, (40, 15))


def instructions():
    instruction_lines = [
        "",
        "CONTROLS:",
        "• LEFT / RIGHT arrow keys to steer",
        "• UP arrow to accelerate",
        "• DOWN arrow to brake",
        "",
        "HOW TO EARN MONEY:",
        "• Drive fast and avoid collisions",
        "• Overtake cars closely for bonus points",
        "• The longer you survive, the more you earn!",
        "",
        "BUYING NEW CARS:",
        "• Earn money from races",
        "• Visit the Car Shop to unlock another vehicles"
    ]

    drawGradient()

    drawBox(instruction_lines)

    back_button_rect = drawMainMenuButton()

    drawCashState()

    pygame.display.update()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if back_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                running = False
                main_menu()


def main_menu():
    global selected_car, score, player_speed, enemy_speed
    reset_game()
    load_data()
    running = True
    play_music(music1)
    while running:
        screen.blit(background_image, (0, 0))
        screen.blit(TITLE_FONT.render("Traffic Racer", True, BLACK), (WIDTH // 2 - 200, HEIGHT / 20))

        start_button_rect = pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 150, HEIGHT // 2, 300, 60), border_radius=7)
        draw_button(start_button_rect, "Start Game", MENU_FONT, (30, 144, 255), (50, 180, 255), True)

        shop_button_rect = pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 150, HEIGHT // 2 + 70, 300, 60),
                                            border_radius=7)
        draw_button(shop_button_rect, "Car Shop", MENU_FONT, (30, 144, 255), (50, 180, 255), True)

        instructions_button_rect = pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 150, HEIGHT // 2 + 140, 300, 60),
                                                    border_radius=7)
        draw_button(instructions_button_rect, "Instructions", MENU_FONT, (30, 144, 255), (50, 180, 255),
                    True)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    score = 0
                    player_speed = 20
                    enemy_speed = 5
                    running = False
                    game_loop()
                elif shop_button_rect.collidepoint(mouse_pos):
                    running = False
                    shop_menu()
                elif instructions_button_rect.collidepoint(mouse_pos):
                    running = False
                    instructions()

def selectNewCar(current_selected_car):
    global selected_car
    selected_car = current_selected_car
    save_data()


def buyNewCar(current_selected_car):
    global money, owned_cars
    car_price = car_shop[current_selected_car]["price"]
    if money >= car_price and current_selected_car not in owned_cars:
        money -= car_price
        owned_cars.append(current_selected_car)
        save_data()


def drawLock(is_owned, can_afford, box_x, box_y):
    if is_owned == False and can_afford == False:
        image = pygame.transform.scale(lock_image, (20, 20))
        screen.blit(image, (box_x + 354, box_y + 90))
        image = pygame.transform.scale(lock2_image, (70, 70))
        screen.blit(image, (box_x + 80, box_y + 10))


def arrowNavigation(offset_x, card_width, total_width, max_visible_cards):
    left_arrow_x = WIDTH // 2 - 40
    right_arrow_x = WIDTH // 2 + 40
    arrow_y = HEIGHT // 2 + 5
    left_arrow_rect = pygame.draw.polygon(screen, (140, 140, 140), [
        (left_arrow_x, arrow_y),
        (left_arrow_x + 30, arrow_y - 15),
        (left_arrow_x + 30, arrow_y + 15)
    ])
    right_arrow_rect = pygame.draw.polygon(screen, (140, 140, 140), [
        (right_arrow_x, arrow_y),
        (right_arrow_x - 30, arrow_y - 15),
        (right_arrow_x - 30, arrow_y + 15)
    ])

    if left_arrow_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        offset_x = max(0, offset_x - card_width - 30)
    if right_arrow_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        offset_x = min(total_width - max_visible_cards * (card_width + 30), offset_x + card_width + 30)
    return offset_x


def drawCarShopTitle():
    title_text = CAR_SHOP_TITLE_FONT.render("Car Shop", True, WHITE)
    shadow_text = TITLE_FONT.render("Car Shop", True, BLACK)
    screen.blit(shadow_text, (WIDTH // 2 - title_text.get_width() // 2 + 2, 18))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))


def drawCarts(start_x, card_box_y, card_width, card_height, offset_x,
              selected_car_details, selected_car_image, current_selected_car):
    car_keys = list(car_shop.keys())
    font = pygame.font.SysFont(None, 40)
    for i, car in enumerate(car_keys):
        car_x = start_x + (i * (card_width + 30)) - offset_x
        if car_x + card_width > 0 and car_x < WIDTH:
            details = car_shop[car]
            car_image = pygame.transform.scale(details['image'], (card_width - 50, card_height - 100))
            car_name_text = font.render(car.capitalize(), True, BLACK)

            pygame.draw.rect(screen, (120, 120, 120), (car_x, card_box_y, card_width, card_height), 0, 10)
            pygame.draw.rect(screen, (120, 120, 120), (car_x, card_box_y, card_width, card_height), 3, 10)

            screen.blit(car_image, (car_x + (card_width - car_image.get_width()) // 2, card_box_y + 10))

            screen.blit(car_name_text,
                        (car_x + card_width // 2 - car_name_text.get_width() // 2, card_box_y + card_height - 40))

            car_rect = pygame.Rect(car_x, card_box_y, card_width, card_height)
            if car_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                current_selected_car = car
                selected_car_image = car_image
                selected_car_details = details
    return current_selected_car, selected_car_image, selected_car_details


def drawCarDetails(current_selected_car, selected_car_image, selected_car_details):
    box_width, box_height = 420, 320
    box_x, box_y = WIDTH // 2 - box_width // 2, HEIGHT - 350

    overlay = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    overlay.fill(WHITE)
    screen.blit(overlay, (box_x, box_y))
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), width=4)

    car_display = pygame.transform.scale(selected_car_image, (50, 80))
    screen.blit(car_display, (box_x + 20, box_y + 20))

    detail_texts = [
        f"Name: {current_selected_car.capitalize()}",
        f"Price: ${selected_car_details['price']}",
        f"Speed: {selected_car_details['speed']} km/h",
        f"Acceleration: {selected_car_details['acceleration']} m/s²",
        f"Power: {selected_car_details['power']} hp"
    ]

    for i, text in enumerate(detail_texts):
        text_render = DETAILS_FONT.render(text, True, BLACK)
        screen.blit(text_render, (box_x + 20, box_y + 120 + i * 32))
    return box_x, box_y


def shop_menu():
    global money, selected_car, owned_cars, background_image2
    selected_car_image = car_shop[selected_car]['image']
    selected_car_details = car_shop[selected_car]
    current_selected_car = selected_car

    card_width = 180
    card_height = 270
    car_keys = list(car_shop.keys())
    num_cars = len(car_keys)
    max_visible_cards = 3
    total_width = card_width * num_cars + 30 * (num_cars - 1)
    start_x = WIDTH // 2 - (max_visible_cards * (card_width + 30)) // 2
    offset_x = 0

    card_box_y = HEIGHT // 2 - card_height // 2 - 155
    card_box_height = card_height

    running = True
    while running:
        screen.blit(background_image2, (0, 0))

        drawCarShopTitle()

        drawCashState()

        card_box_x = WIDTH // 2 - (max_visible_cards * (card_width + 30)) // 2 - 10
        pygame.draw.rect(screen, BLACK,
                         (card_box_x, card_box_y, max_visible_cards * (card_width + 30), card_box_height),
                         3)

        current_selected_car, selected_car_image, selected_car_details = drawCarts(start_x, card_box_y, card_width,
                                                                                   card_height, offset_x,
                                                                                   selected_car_details,
                                                                                   selected_car_image,
                                                                                   current_selected_car)

        if current_selected_car:
            box_x, box_y = drawCarDetails(current_selected_car, selected_car_image, selected_car_details)

            is_owned = current_selected_car in owned_cars
            can_afford = money >= car_shop[current_selected_car]['price']

            select_button_rect = pygame.Rect(box_x + 250, box_y + 30, 140, 45)
            draw_button(select_button_rect, "Select Car", DETAILS_FONT, (30, 144, 255), (50, 180, 255),
                        is_owned)
            buy_button_rect = pygame.Rect(box_x + 250, box_y + 80, 130, 45)
            draw_button(buy_button_rect, "Buy Car", DETAILS_FONT, (71, 174, 44), (90, 200, 60), is_owned)
            back_button_rect = pygame.Rect(WIDTH - 160, 10, 150, 45)
            draw_button(back_button_rect, "Main menu", DETAILS_FONT, (255, 255, 0), (255, 255, 100), True)

            drawLock(is_owned, can_afford, box_x, box_y)

            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if back_button_rect.collidepoint(mouse_pos):
                    running = False
                    main_menu()
                if select_button_rect.collidepoint(mouse_pos) and is_owned:
                    selectNewCar(current_selected_car)
                elif buy_button_rect.collidepoint(mouse_pos) and can_afford and not is_owned:
                    buyNewCar(current_selected_car)

        offset_x = arrowNavigation(offset_x, card_width, total_width, max_visible_cards)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False


def game_loop():
    global player_x, player_y, player_speed, score, enemy_speed, enemy_last_spawn, money
    clock = pygame.time.Clock()
    play_music(music2)
    enemies = []
    while True:
        screen.fill(BLACK)
        draw_road()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player_x > road_x:
            player_x -= lane_change_speed

        if keys[pygame.K_RIGHT] and player_x < road_x + road_width - player_width:
            player_x += lane_change_speed

        if keys[pygame.K_UP] and player_speed < max_speed:
            player_speed += acceleration

        if keys[pygame.K_DOWN] and player_speed >= 30:
            player_speed -= brake_strength

        player_speed = min(player_speed, max_speed)

        if player_speed > 20:
            enemy_speed = 7
        elif player_speed > 10:
            enemy_speed = 6
        else:
            enemy_speed = 5

        enemy_last_spawn += 1
        if enemy_last_spawn >= enemy_spawn_delay:
            enemy_last_spawn = 0
            available_lanes = lane_positions[:]
            for enemy in enemies:
                if enemy[0] in available_lanes and enemy[1] < HEIGHT // 2:
                    available_lanes.remove(enemy[0])

            if available_lanes:
                enemy_lane = random.choice(available_lanes)
                enemy_image = random.choice(car_images)
                enemies.append([enemy_lane - enemy_width // 2 + 40, -enemy_height, enemy_image])

        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            if enemy[1] > HEIGHT:
                enemies.remove(enemy)
                score += 1

            if (player_x < enemy[0] + enemy_width and
                    player_x + player_width > enemy[0] and
                    player_y < enemy[1] + enemy_height and
                    player_y + player_height > enemy[1]):
                explosion_sound.play()
                pygame.mixer.music.stop()
                game_over(enemies, player_x, player_y)

            screen.blit(enemy[2], (enemy[0], enemy[1]))

            draw_player(player_x, player_y)

        if player_x <= road_x or player_x + player_width >= road_x + road_width:
            explosion_sound.play()
            pygame.mixer.music.stop()
            game_over(enemies, player_x, player_y)

        display_info(score, player_speed)

        pygame.display.update()

        clock.tick(60 + int(player_speed))

if __name__ == "__main__":
    main_menu()
