
import sys
from time import sleep

import pygame

from bullet import Bullet
from alien import Alien


# Keydown press events.
def check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Responds to keypresses"""
    if event.key == pygame.K_RIGHT:
        # moves ship to the right
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        # Create a new bullet and add it to the bullets group
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        print("Game stopping")
        sys.exit()
    elif event.key == pygame.K_p:
        start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


# This stops  unnecessary movements.
def check_keyup_events(event, ship):
    """Responds to key releases"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


# the hub for all of the keydown and keyup events
def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens,
        bullets):
    """Responds to keypresses and mouse events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, sb, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship,
                aliens, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens,
        bullets, mouse_x, mouse_y):
    """Start new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)


def start_game(ai_settings, screen, stats, sb, ship, aliens, bullets):
    # Reset the game settings
    ai_settings.initialize_dynamic_settings()

    # hide mouse cursor
    pygame.mouse.set_visible(False)

    # for resetting the game
    stats.reset_stats()
    stats.game_active = True

    # Rest the scoreboard images.
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()

    # Empty the list of aliens and bullets
    aliens.empty()
    bullets.empty()

    # Create a new fleet and center ship
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, alien, bullets,
                  play_button):
    # Redraw the screen during each pass through the loop
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    alien.draw(screen)

    # Draw scoreboard
    sb.show_score()

    # Draw the play button if the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions.
    bullets.update()
    # Check for any bullets that have hit aliens
    # If so get rid of aliens and bullets

    # get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
        #print(len(bullets))

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship,
                                  aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship,
        aliens, bullets):
    """Respond to bullet-alien collisions."""
    # Remove any bullets and aliens that have collided
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # If whole fleet is destroyed, start a new level.
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level.
        stats.level += 1
        sb.prep_level()

        create_fleet(ai_settings, screen, ship, aliens)


def check_high_score(stats, sb):
    """Check to see if there's a new high score"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def get_number_aliens_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in the row"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen."""
    available_space_y = (ai_settings.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien and place it in a row."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens."""
    # Create an alien and find the number of aliens in a row.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
        alien.rect.height)

    # This creates the first row of aliens
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number,
            row_number)


def check_fleet_edges(ai_settings, aliens):
    """Respond appropriately if any aliens have reached an edge"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet and change the fleet's direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Response to ship being hit by alien."""
    # Decrement ships_left.
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # Update lives
        sb.prep_ships()

        # Empty list of aliens and bullets.
        aliens.empty()
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same sas if the ship got hit
            ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
            break


def update_aliens(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """
    Check if the fleet is at an edge,
    and then update the postions of all aliens in the fleet
    aliens """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # look for alien ship collisions.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)

    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)