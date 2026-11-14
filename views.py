import pygame
from settings import *
from hanoi_model import HanoiModel

# Global state and model instances
current_mode = "solver"
hanoi_game = HanoiModel(num_disks=3)

def toggle_mode():
    global current_mode
    current_mode = "manual" if current_mode == "solver" else "solver"

def handle_events_solver(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        btn_rect = pygame.Rect(30, 545, 150, 32)
        if btn_rect.collidepoint(event.pos):
            toggle_mode()

def handle_events_manual(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        btn_rect = pygame.Rect(30, 545, 150, 32)
        if btn_rect.collidepoint(event.pos):
            toggle_mode()
            return

        # Check if click is inside the main tower panel (Left box)
        main_tower_rect = pygame.Rect(15, 15, 540, 575)
        if main_tower_rect.collidepoint(event.pos):
            hanoi_game.handle_mouse_down(event.pos)

    elif event.type == pygame.MOUSEMOTION:
        if hanoi_game.dragging_disk is not None:
            hanoi_game.handle_mouse_motion(event.pos)

    elif event.type == pygame.MOUSEBUTTONUP:
        if hanoi_game.dragging_disk is not None:
            hanoi_game.handle_mouse_up(event.pos)

def handle_events(event):
    if current_mode == "solver":
        handle_events_solver(event)
    else:
        handle_events_manual(event)

def draw_button(screen, font, text, rect, active):
    bg_col = ACCENT_BLUE if active else PANEL_BG
    text_col = BG_COLOR if active else TEXT_COLOR
    pygame.draw.rect(screen, bg_col, rect, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 2, border_radius=6)
    txt_surf = font.render(text, True, text_col)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def draw_hanoi_towers(screen, font):
    """Renders the base, 3 vertical pegs, and colorful disks."""
    # Left panel bounds: x from 15 to 555, y from 15 to 590
    panel_left = 15
    panel_top = 15
    panel_width = 540
    panel_height = 575

    # Peg X centers
    peg_centers = [panel_left + 135, panel_left + 270, panel_left + 405]
    base_y = panel_top + 480
    base_width = 460
    base_rect = pygame.Rect(0, 0, base_width, 14)
    base_rect.centerx = panel_left + panel_width // 2
    base_rect.y = base_y

    # Draw Base
    pygame.draw.rect(screen, BORDER_COLOR, base_rect, border_radius=4)

    # Draw 3 Vertical Pegs
    peg_width = 10
    peg_height = 180
    for cx in peg_centers:
        peg_rect = pygame.Rect(0, 0, peg_width, peg_height)
        peg_rect.centerx = cx
        peg_rect.bottom = base_y
        pygame.draw.rect(screen, BORDER_COLOR, peg_rect, border_radius=3)

    # Draw Disks on Pegs
    disk_height = 20
    max_disk_width = 110
    min_disk_width = 40

    for peg_idx, disks in enumerate(hanoi_game.pegs):
        cx = peg_centers[peg_idx]
        for level, disk_size in enumerate(disks):
            # Calculate width based on disk size (1 is smallest, 3 is largest)
            d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, hanoi_game.num_disks - 1))
            d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
            d_rect.centerx = cx
            d_rect.bottom = base_y - (level * (disk_height + 3))

            # Pick color safely from DISK_COLORS
            color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, d_rect, border_radius=4)
            pygame.draw.rect(screen, BORDER_COLOR, d_rect, 2, border_radius=4)

    # Draw Floating Disk if dragging
    if hanoi_game.dragging_disk is not None:
        disk_size = hanoi_game.dragging_disk
        d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, hanoi_game.num_disks - 1))
        d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
        d_rect.center = hanoi_game.drag_pos
        color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, d_rect, border_radius=4)
        pygame.draw.rect(screen, BORDER_COLOR, d_rect, 2, border_radius=4)

def draw_screen_solver(screen, font):
    screen.fill(BG_COLOR)
    main_tower_rect = pygame.Rect(15, 15, 540, 575)
    pygame.draw.rect(screen, PANEL_BG, main_tower_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, main_tower_rect, 2, border_radius=8)
    
    txt_tower_title = font.render("Main Visualization (Three Towers)", True, TEXT_COLOR)
    screen.blit(txt_tower_title, (30, 30))

    btn_rect = pygame.Rect(30, 545, 150, 32)
    draw_button(screen, font, "Mode: Solver", btn_rect, active=True)

    code_rect = pygame.Rect(570, 15, 315, 275)
    pygame.draw.rect(screen, PANEL_BG, code_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, code_rect, 2, border_radius=8)
    txt_code_title = font.render("Algorithm Code", True, TEXT_COLOR)
    screen.blit(txt_code_title, (585, 30))

    stack_rect = pygame.Rect(570, 305, 315, 285)
    pygame.draw.rect(screen, PANEL_BG, stack_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, stack_rect, 2, border_radius=8)
    txt_stack_title = font.render("Call Stack (Beaker View)", True, TEXT_COLOR)
    screen.blit(txt_stack_title, (585, 320))

def draw_screen_manual(screen, font):
    screen.fill(BG_COLOR)
    main_tower_rect = pygame.Rect(15, 15, 540, 575)
    pygame.draw.rect(screen, PANEL_BG, main_tower_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, main_tower_rect, 2, border_radius=8)
    
    txt_tower_title = font.render("Main Visualization (Manual Play)", True, TEXT_COLOR)
    screen.blit(txt_tower_title, (30, 30))

    # Render towers and disks inside the manual main panel
    draw_hanoi_towers(screen, font)

    btn_rect = pygame.Rect(30, 545, 150, 32)
    draw_button(screen, font, "Mode: Manual", btn_rect, active=False)

    combined_rect = pygame.Rect(570, 15, 315, 575)
    pygame.draw.rect(screen, PANEL_BG, combined_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, combined_rect, 2, border_radius=8)
    
    txt_combined_title = font.render("Manual Play & Stats", True, TEXT_COLOR)
    screen.blit(txt_combined_title, (585, 30))

def draw_screen(screen, font):
    if current_mode == "solver":
        draw_screen_solver(screen, font)
    else:
        draw_screen_manual(screen, font)