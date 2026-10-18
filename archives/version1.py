import math
import pygame

pygame.init()

window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("hextoria")

x = 400
y = 300

zoom = 1.0

blocks = []

player_image = pygame.image.load("player_sprite.png")
player_image = pygame.transform.scale(player_image, (70, 70))

running = True
while running:
    camera_x = x + 35
    camera_y = y + 35

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
                if [bx, by] not in blocks:
                    blocks.append([bx, by])

            if event.button == 3:
                if [bx, by] in blocks:
                    blocks.remove([bx, by])

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        x = x - 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x = x + 5
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        y = y - 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        y = y + 5

    camera_x = x + 35
    camera_y = y + 35

    colour_black = (0,0,0)
    window.fill(colour_black)

    block_size = math.ceil(40 * zoom)

    for b in blocks:

        colour_white = (255, 255, 255)
        screen_x = (b[0] * 40 - camera_x) * zoom + 400
        screen_y = (b[1] * 40 - camera_y) * zoom + 300
        pygame.draw.rect(window, colour_white, (math.floor(screen_x), math.floor(screen_y), block_size, block_size))
        
    player_size = max(1, int(70 * zoom))
    
    scaled_player = pygame.transform.scale(player_image, (player_size, player_size))
    
    window.blit(scaled_player, (400 - player_size // 2, 300 - player_size // 2))

    pygame.display.flip()
    pygame.time.delay(15)

pygame.quit()
