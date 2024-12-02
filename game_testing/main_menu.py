import pygame
import os
from game import main_game
from script.utils import load_image

#constants
SCREEN_Width = 640
SCREEN_HEIGHT = 480
SCREEN_Width = 1280
SCREEN_HEIGHT = 960
HALF_SCREEN_WIDTH = SCREEN_Width // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2
FPS = 60

class main_menu:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        pygame.display.set_caption("Koakuma's Adventure")
        self.screen = pygame.display.set_mode((SCREEN_Width, SCREEN_HEIGHT),pygame.SRCALPHA)

        self.clock = pygame.time.Clock()
        self.assets = {
            "background": load_image("標題畫面.jpg"),

        }
    def run(self):
        while True:
            self.screen.blit(self.assets["background"],(0,0))
            pygame.display.flip()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        main_game().run()




if __name__ == "__main__":
    main_menu().run()