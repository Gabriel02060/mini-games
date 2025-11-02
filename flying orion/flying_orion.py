import sys 
from time import sleep
import pygame
from pathlib import Path
import json
from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from settings import Settings
from alien import Alien
from button import Button


class OrionFlyer:
    "overall class to manage game assets and behavior"
    def __init__(self):
        """initialize the game, and create game resources"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
     
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Space Shooter")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens =  pygame.sprite.Group()

        self._create_fleet()
        #start game in an inactive state
        self.game_active = False

        #make the Play button
        self.play_button = Button(self, "Start")

    def run_game(self):
        """start the main loop for the game"""
        while True:
    #watch for keyboard and mouse movements
            self._check_events()
            if self.game_active:
                self.ship.update_x()
                self.ship.update_y()
                self._update_bullets()
                self._update_aliens()
            self._update_screen() 
            # the .tick() method will try it best to print 60 time a second
            self.clock.tick(60)

    def _check_events(self):
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
               self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    def _check_play_button(self, mouse_pos):
        """start a new game when the player hits start"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #reset game settings
            self.settings.initialize_dynamic_setings()
            # reset the game stats
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            #get rid of remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()
            #create new fleet and center ship
            self._create_fleet()
            self.ship._center_ship()
            #hide mouse cursor
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """respond to key presses"""
        if event.key == pygame.K_d:#detect if d key is pressed
           self.ship.moving_right = True
        elif event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_w:
            self.ship.moving_up = True
        elif event.key == pygame.K_s:
            self.ship.moving_down = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullets()

    def _check_keyup_events(self, event):
        """respond to key releases"""
        if event.key == pygame.K_d:#detect if right arrow key is released 
          self.ship.moving_right = False
        elif event.key == pygame.K_a:
            self.ship.moving_left = False
        elif event.key == pygame.K_w:
            self.ship.moving_up = False
        elif event.key == pygame.K_s:
            self.ship.moving_down = False

    def _fire_bullets(self):
        """create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
             new_bullet = Bullet(self)
             self.bullets.add(new_bullet)

    def _update_bullets(self):
        """update position of bullets"""
        #update bullet positions
        self.bullets.update()
         #get rid of bullet that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """respond to bullet-alien collisons"""
            #check if bullets have hit any aliens
            # if so, get rid of the bullet and the alien
            #false true to send bullet through aliens till the bullet reaches the top
            #true true to stop bullet when it hit an alien
        collisons = pygame.sprite.groupcollide(
            self.bullets, self.aliens, False, True)
        if collisons:
            for aliens in collisons.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            #destroy existing bullets and create new fleet
              self.bullets.empty()
              self._create_fleet()
              self.settings.increase_speed()
              #increase level
              self.stats.level += 1
              self.sb.prep_level()

    def _update_aliens(self):
        """Update the positions of all aliens in the fleet."""
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        #look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
           self._ship_hit()

        #look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 10 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """respond to the ship being hit by an alien """
        #decrement ships left
        if self.stats.ships_left > 0:
            self.ship._center_ship()
            #decrement ship to the left
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            #get rid of any remaining bullets and aliens 
            self.bullets.empty()
            self.aliens.empty()
            #create new fleet and center ship
            self._create_fleet()
            
            #pause
            sleep(0.5)
        else:
            self.ship._center_ship()
            self.game_active = False
            pygame.mouse.set_visible(True)
    def _check_aliens_bottom(self):
        """check if aliens have reached the bottom of the screen"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #treat this the same as if the ship got hit
                self._ship_hit()
                break


            
    
        
    def _update_screen(self):
            """update images on screen, and flip to the new screen"""
            #redraw the screen during each pass through the loop.
            self.screen.fill(self.settings.bg_color)
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)
            #draw the score information
            self.sb.show_score()
            if not self.game_active:
                self.play_button.draw_button()
            #make the most recently drawn screen visable
            pygame.display.flip()
    

if __name__ == "__main__":
   
   #make a game instance, and run the game
   ai = OrionFlyer()
   ai.run_game()