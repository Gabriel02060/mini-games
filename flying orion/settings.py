class Settings:
    """a class to store all settings for alien invasion"""
    def __init__(self):
     """initialize games static settings"""
     #screen settings
     self.screen_width = 1200
     self.screen_height = 800
     #set backround color (r g b) 230 230 230 makes grey. it goes to a max of 255
     self.bg_color = (125, 35, 255)
     #ship settings
     self.ship_limit = 3
     #bullet settings 
     self.bullet_width = 5
     self.bullet_height = 15
     self.bullet_color = (0,191,0)
     self.bullets_allowed = 3
     #alien settings
     #self.alien_speed = 10.0
     self.fleet_drop_speed = 10
     # how quickly the game speeds up
     self.speedup_scale = 1.1
     self.increase_bulletsby = 1.05
     #how quickly the score goes up
     self.score_scale = 1.5
     
     self.initialize_dynamic_setings()

    def initialize_dynamic_setings(self):
        """initialize settings that change throughout the game"""
        self.ship_speed = 2.5
        self.bullet_speed = 5.5
        self.bullets_allowed = 4
        self.alien_speed = 3.5
        #scoring settings
        self.alien_points = 50
       

        # fleet_direction of 1 represents right; -1 represents left:
        self.fleet_direction = 1
    def increase_speed(self):
       """increase speed settings"""
       self.ship_speed *= self.speedup_scale
       self.bullet_speed *= self.speedup_scale
       self.bullets_allowed *= self.increase_bulletsby
       self.alien_speed *= self.speedup_scale
       self.alien_points = int(self.alien_points * self.score_scale)
       print(self.alien_points)
     
