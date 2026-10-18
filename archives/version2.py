import math
import pygame

pygame.init()

window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("hextoria")

x = 400
y = 300

zoom = 1.0

blocks = []
selected = 1

colours = {
    1: (139, 90, 43),
    2: (0, 0, 255),
    3: (0, 255, 0),
    4: (255, 0, 0),
}

player_image = pygame.image.load("player_sprite.png")
player_image = pygame.transform.scale(player_image, (70, 70))


def get_block(bx, by):
    for b in blocks:
        if b[0] == bx and b[1] == by:
            return b
    return None


def get_cells(px, py):
    left = math.floor((px + 20) / 40)
    right = math.floor((px + 49) / 40)
    top = math.floor((py + 20) / 40)
    bottom = math.floor((py + 49) / 40)
    cells = []
    for cx in range(left, right + 1):
        for cy in range(top, bottom + 1):
            cells.append((cx, cy))
    return cells


def touching_solid(px, py):
    for cell in get_cells(px, py):
        b = get_block(cell[0], cell[1])
        if b is not None and b[2] != 1:
            return True
    return False


running = True
while running:
    camera_x = x + 35
    camera_y = y + 35

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

        if event.type == pygame.MOUSEWHEEL:
            zoom = zoom * (1.1 ** event.y)
            if zoom < 0.3:
                zoom = 0.3
            if zoom > 3:
                zoom = 3

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            world_x = (mx - 400) / zoom + camera_x
            world_y = (my - 300) / zoom + camera_y
            bx = math.floor(world_x / 40)
            by = math.floor(world_y / 40)

            if event.button == 1:
                if get_block(bx, by) is None:
                    inside_player = (bx, by) in get_cells(x, y)
                    if selected == 1 or not inside_player:
                        blocks.append([bx, by, selected])

            if event.button == 3:
                b = get_block(bx, by)
                if b is not None:
                    blocks.remove(b)

    keys = pygame.key.get_pressed()

    move_x = 0
    move_y = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_x = move_x - 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_x = move_x + 5
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_y = move_y - 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_y = move_y + 5

    if not touching_solid(x + move_x, y):
        x = x + move_x
    if not touching_solid(x, y + move_y):
        y = y + move_y

    camera_x = x + 35
    camera_y = y + 35

    colour_black = (0, 0, 0)
    window.fill(colour_black)

    block_size = math.ceil(40 * zoom)

    for b in blocks:
        screen_x = (b[0] * 40 - camera_x) * zoom + 400
        screen_y = (b[1] * 40 - camera_y) * zoom + 300
        pygame.draw.rect(window, colours[b[2]], (math.floor(screen_x), math.floor(screen_y), block_size, block_size))

    player_size = max(1, int(70 * zoom))

    scaled_player = pygame.transform.scale(player_image, (player_size, player_size))

    window.blit(scaled_player, (400 - player_size // 2, 300 - player_size // 2))

    colour_white = (255, 255, 255)
    for i in range(1, 5):
        slot_x = 290 + (i - 1) * 60
        pygame.draw.rect(window, colours[i], (slot_x, 530, 50, 50))
        if i == selected:
            pygame.draw.rect(window, colour_white, (slot_x, 530, 50, 50), 3)

    pygame.display.flip()
    pygame.time.delay(15)

pygame.quit()
