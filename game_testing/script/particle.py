import pygame

class Particle:
    def __init__(self, game, p_type,pos,velocity=[0,0],frame=0,flip=False):
        self.game = game
        self.flip = flip    
        self.p_type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/'+p_type].copy()
        self.animation.frame = frame
    def update(self):
        kill = False
        if self.animation.done:
            kill = True
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.animation.update()     

        return kill 
    
    def render(self, surface, offset = [0,0]):  
        img = self.animation.img() if not self.flip else pygame.transform.flip(self.animation.img(), True, False)
        surface.blit(img, (self.pos[0]-offset[0]-img.get_width()//2, self.pos[1]-offset[1]-img.get_height()//2))   

    def render_new(self, surface, offset = [0,0]):  
        img = self.animation.img() if not self.flip else pygame.transform.flip(self.animation.img(), True, False)
        #img = pygame.transform.scale(img, (int(img.get_width()*2), int(img.get_height()*2)))
        surface.blit(img, (2*int(self.pos[0]-offset[0]-img.get_width()//2), 2*int(self.pos[1]-offset[1]-img.get_height()//2)))