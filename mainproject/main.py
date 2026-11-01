#REFERENCES

#Modified from: CDcodes. (2020, November 26). Pygame Tile Based Game Tutorial: Collisions [Video]. Youtube. https://www.youtube.com/watch?v=vAfveKX1pSc&t=2s 
#Modified from: CDcodes. (2021, August 1). Pygame Saving and Loading Tutorial: Creating Customizable Controls [Video]. Youtube. https://www.youtube.com/watch?v=1UCaiX8ESsQ
#Modified from: Coding With Russ. (2020, December 2). PyGame Tile Based Platformer Game Beginner Tutorial in Python - PART 1 | Creating the World [Video]. Youtube. 
#https://www.youtube.com/watch?v=Ongc4EVqRjo&t=922s
#Modified from: DaFluffyPotato. (2023, July 18). Pygame Platformer Tutorial - Full Course [Video]. Youtube. https://www.youtube.com/watch?v=2gABYM5M0ww 
#Modified from: Dreamset Services. (2025, August 26). How to Create Random Number Generator in Python. [Video]. Youtube. https://www.youtube.com/watch?v=QtkVyzaFpFQ

import json
import math
import random
import pygame

pygame.init()

window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("hextoria")

#world size
world_columns = 300
world_rows = 200
world_width = world_columns * 40
world_height = world_rows * 40

zoom = 1.0

selected = 1

facing_left = False

#player settings
velocity_y = 0
on_ground = False
gravity = 0.8
jump_speed = -12
max_fall_speed = 15
jumps_used = 0
max_jumps = 2

#block sprites
block_names = {
    1: "grass",
    2: "dirt",
    3: "stone",
    4: "cobweb",
    5: "vine",
}

walkable_blocks = [4, 5]

font = pygame.font.Font(None, 18)

#sounds
#Nimlos. (2018). Ambience city night DPA semibinaural [Audio file]. Freesound. https://freesound.org/people/Nimlos/sounds/454822/  
#Fredricksen, E. (2011). jsfxr [Computer software]. https://sfxr.me/ 
jump_sound = pygame.mixer.Sound("jump.wav")
jump_sound.set_volume(0.25)

ambience_sound = pygame.mixer.Sound("ambience.wav")
ambience_sound.set_volume(0.03)
                   
ambience_sound.play(loops=-1)

#load bat images and make them smaller to approx one block
player_visible_size = 36

bat_images = [
    pygame.image.load("bat1.png").convert_alpha(),
    pygame.image.load("bat2.png").convert_alpha(),
]

first_bounds = bat_images[0].get_bounding_rect(128)
player_scale = player_visible_size / max(first_bounds.width, first_bounds.height)

player_frames = []
frame_offset_x = 0
frame_offset_y = 0

for number in range(len(bat_images)):
    small_width = max(1, round(bat_images[number].get_width() * player_scale))
    small_height = max(1, round(bat_images[number].get_height() * player_scale))
    small_bat = pygame.transform.scale(bat_images[number], (small_width, small_height))

    if number == 0:
        small_bounds = small_bat.get_bounding_rect(128)
        frame_offset_x = 35 - small_bounds.centerx
        frame_offset_y = 35 - small_bounds.centery

    frame_canvas = pygame.Surface((70, 70), pygame.SRCALPHA)
    frame_canvas.blit(small_bat, (frame_offset_x, frame_offset_y))
    player_frames.append(frame_canvas)

#bat animation settings
frame_index = 0
frame_delay = 150
last_frame_change = pygame.time.get_ticks()

#block images
block_images = {
    1: pygame.image.load("block_grass.png").convert_alpha(),
    2: pygame.image.load("block_dirt.png").convert_alpha(),
    3: pygame.image.load("block_gothic.png").convert_alpha(),
    4: pygame.image.load("block_cobwebs.png").convert_alpha(),
    5: pygame.image.load("block_vine.png").convert_alpha(),
}

slot_images = {}
for block_type in block_images:
    slot_images[block_type] = pygame.transform.scale(block_images[block_type], (50, 50))

scaled_images = {}

#hitbox that works for both flapping bat frames
half_width = 1
hitbox_top = 70
hitbox_bottom = 0

for frame in player_frames:
    frame_bounds = frame.get_bounding_rect(128)
    half_width = max(half_width, 35 - frame_bounds.left, frame_bounds.right - 35)
    hitbox_top = min(hitbox_top, frame_bounds.top)
    hitbox_bottom = max(hitbox_bottom, frame_bounds.bottom - 1)

hitbox_left = 35 - half_width
hitbox_right = 34 + half_width

#world generation
blocks = {}
surface_heights = []

surface_row = 15
for column in range(world_columns):
    step = random.randint(1, 4)
    if step == 1:
        surface_row = surface_row - 1
    if step == 2:
        surface_row = surface_row + 1
    if surface_row < 11:
        surface_row = 11
    if surface_row > 19:
        surface_row = 19

    surface_heights.append(surface_row)
    blocks[(column, surface_row)] = 1
    for row in range(surface_row + 1, world_rows):
        blocks[(column, row)] = 2

#random bits of stone
for number in range(600):
    stone_column = random.randint(0, world_columns - 1)
    stone_row = random.randint(21, world_rows - 1)
    stone_width = random.randint(1, 3)
    stone_height = random.randint(1, 2)
    for offset_x in range(stone_width):
        for offset_y in range(stone_height):
            cell = (stone_column + offset_x, stone_row + offset_y)
            if blocks.get(cell) == 2:
                blocks[cell] = 3

#clouds
clouds = []
for number in range(7):
    cloud_column = random.randint(0, world_columns - 1)
    cloud_row = random.randint(1, 7)
    cloud_width = random.randint(3, 5)
    clouds.append([cloud_column, cloud_row, cloud_width])

cloud_timer = 0

#spawn
spawn_column = world_columns // 2
x = spawn_column * 40 + 20 - 35

left_column = math.floor((x + hitbox_left) / 40)
right_column = math.floor((x + hitbox_right) / 40)

highest_surface = surface_heights[spawn_column]
for column in range(left_column, right_column + 1):
    if surface_heights[column] < highest_surface:
        highest_surface = surface_heights[column]

y = highest_surface * 40 - (hitbox_bottom + 1)

camera_x = x + 35
camera_y = y + 35


def get_block(bx, by):
    return blocks.get((bx, by))


def get_cells(px, py):
    left = math.floor((px + hitbox_left) / 40)
    right = math.floor((px + hitbox_right) / 40)
    top = math.floor((py + hitbox_top) / 40)
    bottom = math.floor((py + hitbox_bottom) / 40)
    cells = []
    for cx in range(left, right + 1):
        for cy in range(top, bottom + 1):
            cells.append((cx, cy))
    return cells

#collison
def touching_solid(px, py):
    for cell in get_cells(px, py):
        if cell[0] < 0 or cell[0] >= world_columns:
            return True
        if cell[1] < 0 or cell[1] >= world_rows:
            return True
        block_type = get_block(cell[0], cell[1])
        if block_type is not None and block_type not in walkable_blocks:
            return True
    return False

#camera system
def update_camera():
    global camera_x, camera_y
    camera_x = x + 35
    camera_y = y + 35

    half_screen_width = 400 / zoom
    half_screen_height = 300 / zoom

    if camera_x < half_screen_width:
        camera_x = half_screen_width
    if camera_x > world_width - half_screen_width:
        camera_x = world_width - half_screen_width
    if camera_y < half_screen_height:
        camera_y = half_screen_height
    if camera_y > world_height - half_screen_height:
        camera_y = world_height - half_screen_height


def screen_x_of(cell):
    return math.floor((cell * 40 - camera_x) * zoom + 400 + 0.5)


def screen_y_of(cell):
    return math.floor((cell * 40 - camera_y) * zoom + 300 + 0.5)


def get_block_image(block_type, width, height):
    key = (block_type, width, height)
    if key not in scaled_images:
        scaled_images[key] = pygame.transform.scale(block_images[block_type], (width, height))
    return scaled_images[key]


def draw_text(text, centre_x, centre_y):
    black_text = font.render(text, True, (0, 0, 0))
    white_text = font.render(text, True, (255, 255, 255))
    for offset_x in (-1, 0, 1):
        for offset_y in (-1, 0, 1):
            if offset_x != 0 or offset_y != 0:
                outline_rect = black_text.get_rect(center=(centre_x + offset_x, centre_y + offset_y))
                window.blit(black_text, outline_rect)
    white_rect = white_text.get_rect(center=(centre_x, centre_y))
    window.blit(white_text, white_rect)


running = True
while running:
    update_camera()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected = 1
            if event.key == pygame.K_2:
                selected = 2
            if event.key == pygame.K_3:
                selected = 3
            if event.key == pygame.K_4:
                selected = 4
            if event.key == pygame.K_5:
                selected = 5

            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                if jumps_used < max_jumps:
                    velocity_y = jump_speed
                    jumps_used = jumps_used + 1
                    jump_sound.play()

#save
            if event.key == pygame.K_n:
                save_blocks = []
                for position in blocks:
                    save_blocks.append([position[0], position[1], blocks[position]])
                save_data = {"blocks": save_blocks, "x": x, "y": y}
                with open("hextoria_save.json", "w") as save_file:
                    json.dump(save_data, save_file)

#load
            if event.key == pygame.K_m:
                try:
                    with open("hextoria_save.json", "r") as save_file:
                        save_data = json.load(save_file)
                    loaded_blocks = {}
                    for item in save_data["blocks"]:
                        if item[2] in block_names:
                            loaded_blocks[(item[0], item[1])] = item[2]
                    blocks = loaded_blocks
                    x = save_data["x"]
                    y = save_data["y"]
                    velocity_y = 0
                except FileNotFoundError:
                    pass

#zoom
        if event.type == pygame.MOUSEWHEEL:
            zoom = zoom * (1.1 ** event.y)
            if zoom < 0.5:
                zoom = 0.5
            if zoom > 3:
                zoom = 3

#building
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            world_x = (mx - 400) / zoom + camera_x
            world_y = (my - 300) / zoom + camera_y
            bx = math.floor(world_x / 40)
            by = math.floor(world_y / 40)

            inside_world = 0 <= bx < world_columns and 0 <= by < world_rows

            if event.button == 1 and inside_world:
                if get_block(bx, by) is not None:
                    del blocks[(bx, by)]

            if event.button == 3 and inside_world:
                if get_block(bx, by) is None:
                    inside_player = (bx, by) in get_cells(x, y)
                    if selected in walkable_blocks or not inside_player:
                        blocks[(bx, by)] = selected

#stuck help
    while touching_solid(x, y) and y > 0:
        y = y - 1

    keys = pygame.key.get_pressed()

#sprint
    speed = 5
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        speed = 8

    move_x = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_x = move_x - speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_x = move_x + speed

    if move_x < 0:
        facing_left = True
    if move_x > 0:
        facing_left = False

    direction_x = 1
    if move_x < 0:
        direction_x = -1

    for step in range(abs(move_x)):
        if not touching_solid(x + direction_x, y):
            x = x + direction_x

#gravity
    velocity_y = velocity_y + gravity
    if velocity_y > max_fall_speed:
        velocity_y = max_fall_speed

    direction_y = 1
    if velocity_y < 0:
        direction_y = -1

    for step in range(int(abs(velocity_y))):
        if not touching_solid(x, y + direction_y):
            y = y + direction_y
        else:
            velocity_y = 0
            break

    on_ground = touching_solid(x, y + 1)
    if on_ground and velocity_y > 0:
        velocity_y = 0

    if on_ground:
        jumps_used = 0
    elif jumps_used == 0:
        jumps_used = 1

    update_camera()
    
#moving the clouds
    cloud_timer = cloud_timer + 1
    if cloud_timer >= 90:
        cloud_timer = 0
        for cloud in clouds:
            cloud[0] = cloud[0] + 1
            if cloud[0] > world_columns:
                cloud[0] = -cloud[2]

#sky and clouds
    colour_sky = (45, 45, 55)
    window.fill(colour_sky)

    colour_cloud = (255, 255, 255)
    for cloud in clouds:
        cloud_cells = []
        for cell_x in range(cloud[0], cloud[0] + cloud[2]):
            cloud_cells.append((cell_x, cloud[1] + 1))
        for cell_x in range(cloud[0] + 1, cloud[0] + cloud[2] - 1):
            cloud_cells.append((cell_x, cloud[1]))

        for cell in cloud_cells:
            cloud_left = screen_x_of(cell[0])
            cloud_top = screen_y_of(cell[1])
            cloud_block_width = screen_x_of(cell[0] + 1) - cloud_left
            cloud_block_height = screen_y_of(cell[1] + 1) - cloud_top
            pygame.draw.rect(window, colour_cloud, (cloud_left, cloud_top, cloud_block_width, cloud_block_height))

#blocks
    first_column = math.floor((camera_x - 400 / zoom) / 40)
    last_column = math.floor((camera_x + 400 / zoom) / 40)
    first_row = math.floor((camera_y - 300 / zoom) / 40)
    last_row = math.floor((camera_y + 300 / zoom) / 40)

    for bx in range(first_column, last_column + 1):
        for by in range(first_row, last_row + 1):
            block_type = get_block(bx, by)
            if block_type is not None:
                block_left = screen_x_of(bx)
                block_top = screen_y_of(by)
                block_width = screen_x_of(bx + 1) - block_left
                block_height = screen_y_of(by + 1) - block_top
                block_picture = get_block_image(block_type, block_width, block_height)
                window.blit(block_picture, (block_left, block_top))

#bat animation
    now = pygame.time.get_ticks()
    if now - last_frame_change >= frame_delay:
        last_frame_change = now
        frame_index = (frame_index + 1) % len(player_frames)

#player
    player_size = max(1, int(70 * zoom))

    scaled_player = pygame.transform.scale(player_frames[frame_index], (player_size, player_size))

    if not facing_left:
        scaled_player = pygame.transform.flip(scaled_player, True, False)

    player_screen_x = math.floor((x + 35 - camera_x) * zoom + 400)
    player_screen_y = math.floor((y + 35 - camera_y) * zoom + 300)

    window.blit(scaled_player, (player_screen_x - player_size // 2, player_screen_y - player_size // 2))

#hotbar
    colour_white = (255, 255, 255)
    colour_slot_back = (70, 70, 70)
    for i in range(1, 6):
        slot_x = 255 + (i - 1) * 60
        pygame.draw.rect(window, colour_slot_back, (slot_x, 530, 50, 50))
        window.blit(slot_images[i], (slot_x, 530))
        if i == selected:
            pygame.draw.rect(window, colour_white, (slot_x, 530, 50, 50), 3)
        draw_text(block_names[i], slot_x + 25, 555)

    pygame.display.flip()
    pygame.time.delay(15)

pygame.quit()