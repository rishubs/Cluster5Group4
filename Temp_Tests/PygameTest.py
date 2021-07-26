import pygame
import time
import os

pygame.init()

white = (255, 255, 255)

direction = "left"
X = 1000
Y = 690
tri_x1 = 860
tri_y1 = 325
tri_x2 = 820
tri_y2 = 312
tri_x3 = 860
tri_y3 = 299

display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Map')

image = pygame.image.load('DownstairsStraightened.png')
image2 = pygame.image.load('UpstairsStraightened.png')

while True:
    display_surface.fill(white)
    display_surface.blit(image, (0, 0))
    pygame.draw.polygon(display_surface, (244, 113, 116), points=[(tri_x1, tri_y1), (tri_x2, tri_y2), (tri_x3, tri_y3)])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if pygame.mouse.get_pressed() == (1,0,0):
           print(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction == "right":
                for i in range(1,51,1):
                    pygame.draw.polygon(display_surface, (244, 113, 116), points=[(tri_x1+i, tri_y1), (tri_x2+i, tri_y2), (tri_x3+i, tri_y3)])
                tri_x1 += 50
                tri_x2 += 50
                tri_x3 += 50
            elif event.key == pygame.K_UP and direction == "left":
                for i in range(1,51,1):
                    pygame.draw.polygon(display_surface, (244, 113, 116), points=[(tri_x1-i, tri_y1), (tri_x2-i, tri_y2), (tri_x3-i, tri_y3)])
                    display_surface.fill(white)
                    display_surface.blit(image, (0, 0))

                tri_x1 -= 50
                tri_x2 -= 50
                tri_x3 -= 50
        pygame.display.update()