
import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from alien import Alien
import game_functions as gf


def run_game():
    # This starts pygame, and initiates the settings. screen and objects.
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # Make play button
    play_button = Button(ai_settings, screen, "Play")

    # Create an instance of game stats and create a scoreboard
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    # Make a ship
    ship = Ship(ai_settings, screen)
    bullets = Group()
    aliens = Group()

    # Create the fleet of aliens
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # Main Loop
    while True:
        gf.check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets)

        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets)
            gf.update_aliens(ai_settings, stats, sb, screen, ship, aliens, bullets)

        gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
                         play_button)


run_game()