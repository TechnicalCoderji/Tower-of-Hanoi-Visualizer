import pygame
from settings import *
from hanoi_model import HanoiModel

# Global state and model instances
current_mode = "solver"
hanoi_game = HanoiModel(num_disks=3)

# Solver mode specific state
solver_num_disks = 3
solver_state = "idle" # "idle" or "solving"
solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]

def toggle_mode():
    global current_mode
    current_mode = "manual" if current_mode == "solver" else "solver"

def handle_events_solver(event):
    global current_mode, solver_num_disks, solver_state, solver_pegs
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Toggle button
        btn_mode_rect = pygame.Rect(30, 545, 150, 32)
        if btn_mode_rect.collidepoint(event.pos):
            toggle_mode()
            return

        # If solver is currently running/solving, disable button clicks
        if solver_state == "solving":
            return

        # Solve button: Rect(190, 545, 110, 32)
        btn_solve_rect = pygame.Rect(190, 545, 110, 32)
        if btn_solve_rect.collidepoint(event.pos):
            solver_state = "solving"
            return

        # Disk counter box controls: "Disks: [ - | count | + ]" starting around x: 380, y: 545
        # Minus button: Rect(440, 548, 22, 26)
        # Plus button: Rect(500, 548, 22, 26)
        btn_minus = pygame.Rect(440, 548, 22, 26)
        btn_plus = pygame.Rect(500, 548, 22, 26)

        if btn_minus.collidepoint(event.pos):
            solver_num_disks = max(3, solver_num_disks - 1)
            solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]
        elif btn_plus.collidepoint(event.pos):
            solver_num_disks = min(15, solver_num_disks + 1)
            solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]

def handle_events_manual(event):
    global current_mode
    if event.type == pygame.MOUSEBUTTONDOWN:
        btn_mode_rect = pygame.Rect(30, 545, 150, 32)
        if btn_mode_rect.collidepoint(event.pos):
            toggle_mode()
            return

        # Corrected button bounds for [-] and [+] inside stats panel
        btn_minus = pygame.Rect(775, 233, 25, 25)
        btn_plus = pygame.Rect(810, 233, 25, 25)
        
        if btn_minus.collidepoint(event.pos):
            new_count = max(3, hanoi_game.num_disks - 1)
            hanoi_game.reset(new_count)
            return
        elif btn_plus.collidepoint(event.pos):
            new_count = min(7, hanoi_game.num_disks + 1)
            hanoi_game.reset(new_count)
            return

        btn_reset = pygame.Rect(600, 525, 255, 35)
        if btn_reset.collidepoint(event.pos):
            hanoi_game.reset(hanoi_game.num_disks)
            return

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
    panel_left = 15
    panel_top = 15
    panel_width = 540
    panel_height = 575

    peg_centers = [panel_left + 135, panel_left + 270, panel_left + 405]
    
    # Moved base higher up to reduce blank space (e.g., base_y = panel_top + 380)
    base_y = panel_top + 380
    base_width = 460
    base_rect = pygame.Rect(0, 0, base_width, 14)
    base_rect.centerx = panel_left + panel_width // 2
    base_rect.y = base_y

    # Draw Base
    pygame.draw.rect(screen, BORDER_COLOR, base_rect, border_radius=4)

    # Draw 3 Vertical Pegs
    peg_width = 10
    peg_height = 220  # Taller peg since base moved up
    for cx in peg_centers:
        peg_rect = pygame.Rect(0, 0, peg_width, peg_height)
        peg_rect.centerx = cx
        peg_rect.bottom = base_y
        pygame.draw.rect(screen, BORDER_COLOR, peg_rect, border_radius=3)

    # Draw Tower Labels below base: source, extra, destination
    labels = ["source", "extra", "destination"]
    for i, cx in enumerate(peg_centers):
        lbl_surf = font.render(labels[i], True, TEXT_COLOR)
        lbl_rect = lbl_surf.get_rect(center=(cx, base_y + 25))
        screen.blit(lbl_surf, lbl_rect)

    # Draw Disks on Pegs with size number in center
    disk_height = 22
    max_disk_width = 120
    min_disk_width = 45

    for peg_idx, disks in enumerate(hanoi_game.pegs):
        cx = peg_centers[peg_idx]
        for level, disk_size in enumerate(disks):
            d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, 6))
            d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
            d_rect.centerx = cx
            d_rect.bottom = base_y - (level * (disk_height + 3))

            color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, d_rect, border_radius=4)
            pygame.draw.rect(screen, BORDER_COLOR, d_rect, 2, border_radius=4)

            # Render disk size number in center of each disk
            num_surf = font.render(str(disk_size), True, BG_COLOR)
            num_rect = num_surf.get_rect(center=d_rect.center)
            screen.blit(num_surf, num_rect)

    # Draw Floating Disk if dragging
    if hanoi_game.dragging_disk is not None:
        disk_size = hanoi_game.dragging_disk
        d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, 6))
        d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
        d_rect.center = hanoi_game.drag_pos
        color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, d_rect, border_radius=4)
        pygame.draw.rect(screen, BORDER_COLOR, d_rect, 2, border_radius=4)

        num_surf = font.render(str(disk_size), True, BG_COLOR)
        num_rect = num_surf.get_rect(center=d_rect.center)
        screen.blit(num_surf, num_rect)

def draw_solver_towers(screen, font):
    panel_left = 15
    panel_top = 15
    panel_width = 540

    peg_centers = [panel_left + 135, panel_left + 270, panel_left + 405]
    
    # Base positioned lower to accommodate 2x taller vertical space
    base_y = panel_top + 460
    base_width = 460
    base_rect = pygame.Rect(0, 0, base_width, 14)
    base_rect.centerx = panel_left + panel_width // 2
    base_rect.y = base_y

    # Draw Base
    pygame.draw.rect(screen, BORDER_COLOR, base_rect, border_radius=4)

    # Draw 3 Vertical Pegs (2x taller: height 340)
    peg_width = 10
    peg_height = 340
    for cx in peg_centers:
        peg_rect = pygame.Rect(0, 0, peg_width, peg_height)
        peg_rect.centerx = cx
        peg_rect.bottom = base_y
        pygame.draw.rect(screen, BORDER_COLOR, peg_rect, border_radius=3)

    # Draw Tower Labels: source, extra, destination
    labels = ["source", "extra", "destination"]
    for i, cx in enumerate(peg_centers):
        lbl_surf = font.render(labels[i], True, (240, 245, 250))
        lbl_rect = lbl_surf.get_rect(center=(cx, base_y + 25))
        screen.blit(lbl_surf, lbl_rect)

    # Draw Disks (proportioned for up to 15 disks with clear numbering)
    disk_height = 18
    max_disk_width = 130
    min_disk_width = 30

    for peg_idx, disks in enumerate(solver_pegs):
        cx = peg_centers[peg_idx]
        for level, disk_size in enumerate(disks):
            d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, 14))
            d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
            d_rect.centerx = cx
            d_rect.bottom = base_y - (level * (disk_height + 2))

            color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, d_rect, border_radius=3)
            pygame.draw.rect(screen, BORDER_COLOR, d_rect, 1, border_radius=3)

            # Disk number inside disk
            num_surf = font.render(str(disk_size), True, BG_COLOR)
            num_rect = num_surf.get_rect(center=d_rect.center)
            screen.blit(num_surf, num_rect)

def draw_screen_solver(screen, font):
    screen.fill(BG_COLOR)
    
    BRIGHT_TEXT = (240, 245, 250)

    # 1. Main Tower Panel
    main_tower_rect = pygame.Rect(15, 15, 540, 575)
    pygame.draw.rect(screen, PANEL_BG, main_tower_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, main_tower_rect, 2, border_radius=8)
    
    txt_tower_title = font.render("Main Visualization (Computer Solver)", True, BRIGHT_TEXT)
    screen.blit(txt_tower_title, (30, 30))

    # Draw Towers
    draw_solver_towers(screen, font)

    # --- Bottom Row Controls ---
    # 1. Mode Toggle Button
    btn_mode_rect = pygame.Rect(30, 545, 150, 32)
    draw_button(screen, font, "Mode: Solver", btn_mode_rect, active=True)

    # 2. Solve Button (Next to toggle)
    btn_solve_rect = pygame.Rect(190, 545, 110, 32)
    if solver_state == "solving":
        # Non-clickable / disabled solving state styling
        pygame.draw.rect(screen, (60, 70, 85), btn_solve_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_COLOR, btn_solve_rect, 2, border_radius=6)
        txt_surf = font.render("Solving...", True, (150, 160, 170))
        screen.blit(txt_surf, txt_surf.get_rect(center=btn_solve_rect.center))
    else:
        draw_button(screen, font, "Solve", btn_solve_rect, active=False)

    # 3. Disk Counter Component: "Disks: [ - | count | + ]"
    lbl_disks = font.render("Disks:", True, BRIGHT_TEXT)
    screen.blit(lbl_disks, (325, 551))

    # Outer container box for counter
    counter_box = pygame.Rect(375, 545, 155, 32)
    pygame.draw.rect(screen, (35, 39, 46), counter_box, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, counter_box, 1, border_radius=6)

    # Minus button inside box
    btn_minus = pygame.Rect(382, 549, 24, 24)
    draw_button(screen, font, "-", btn_minus, active=False)

    # Disk number display
    val_surf = font.render(str(solver_num_disks), True, BRIGHT_TEXT)
    screen.blit(val_surf, val_surf.get_rect(center=(452, counter_box.centery)))

    # Plus button inside box
    btn_plus = pygame.Rect(500, 549, 24, 24)
    draw_button(screen, font, "+", btn_plus, active=False)

    # 2. Code Panel (Top Right)
    code_rect = pygame.Rect(570, 15, 315, 275)
    pygame.draw.rect(screen, PANEL_BG, code_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, code_rect, 2, border_radius=8)
    screen.blit(font.render("Algorithm Code", True, BRIGHT_TEXT), (585, 30))

    # 3. Stack Beaker Panel (Bottom Right)
    stack_rect = pygame.Rect(570, 305, 315, 285)
    pygame.draw.rect(screen, PANEL_BG, stack_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, stack_rect, 2, border_radius=8)
    screen.blit(font.render("Call Stack (Beaker View)", True, BRIGHT_TEXT), (585, 320))

def draw_screen_manual(screen, font):
    screen.fill(BG_COLOR)
    
    # Larger font for completion message
    font_large = pygame.font.SysFont("consolas", 20, bold=True)
    
    # Brighter text color for high visibility
    BRIGHT_TEXT = (240, 245, 250)

    # 1. Main Tower Panel
    main_tower_rect = pygame.Rect(15, 15, 540, 575)
    pygame.draw.rect(screen, PANEL_BG, main_tower_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, main_tower_rect, 2, border_radius=8)
    
    txt_tower_title = font.render("Main Visualization (Manual Play)", True, BRIGHT_TEXT)
    screen.blit(txt_tower_title, (30, 30))

    draw_hanoi_towers(screen, font)

    btn_rect = pygame.Rect(30, 545, 150, 32)
    draw_button(screen, font, "Mode: Manual", btn_rect, active=False)

    # 2. Right-Side Box for Stats and Rules
    combined_rect = pygame.Rect(570, 15, 315, 575)
    pygame.draw.rect(screen, PANEL_BG, combined_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, combined_rect, 2, border_radius=8)
    
    txt_combined_title = font.render("Manual Play & Stats", True, BRIGHT_TEXT)
    screen.blit(txt_combined_title, (585, 25))

    # --- Rules Box ---
    rules_rect = pygame.Rect(585, 55, 285, 150)
    pygame.draw.rect(screen, (35, 39, 46), rules_rect, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, rules_rect, 1, border_radius=6)
    
    rules_title = font.render("Rules:", True, ACCENT_BLUE)
    screen.blit(rules_title, (595, 63))
    
    rule_lines = [
        "1. Move one disk at a time.",
        "2. Larger disk cannot be",
        "   placed on smaller disk.",
        "3. Shift all disks to the",
        "   destination peg."
    ]
    for idx, line in enumerate(rule_lines):
        r_surf = font.render(line, True, BRIGHT_TEXT)
        screen.blit(r_surf, (595, 88 + idx * 20))

    # --- Aligned Stats Section (Moved down safely) ---
    stats_start_y = 235
    colon_x = 720  
    min_moves = (2 ** hanoi_game.num_disks) - 1
    
    # Disks Row
    screen.blit(font.render("Number of Disks", True, BRIGHT_TEXT), (585, stats_start_y))
    screen.blit(font.render(":", True, BRIGHT_TEXT), (colon_x + 10, stats_start_y))
    screen.blit(font.render(str(hanoi_game.num_disks), True, BRIGHT_TEXT), (colon_x + 30, stats_start_y))
    
    # [-] and [+] buttons
    btn_minus_rect = pygame.Rect(colon_x + 55, stats_start_y - 2, 25, 25)
    btn_plus_rect = pygame.Rect(colon_x + 90, stats_start_y - 2, 25, 25)
    draw_button(screen, font, "-", btn_minus_rect, active=False)
    draw_button(screen, font, "+", btn_plus_rect, active=False)

    stat_items = [
        ("Minimum Moves", str(min_moves)),
        ("Your Moves", str(hanoi_game.move_count)),
        ("Game Status", hanoi_game.game_status)
    ]

    for idx, (label, val) in enumerate(stat_items):
        y_pos = stats_start_y + ((idx + 1) * 42)
        screen.blit(font.render(label, True, BRIGHT_TEXT), (585, y_pos))
        screen.blit(font.render(":", True, BRIGHT_TEXT), (colon_x + 10, y_pos))
        
        if label == "Game Status":
            if val == "start":
                val_color = (240, 198, 116)
            elif val == "running":
                val_color = ACCENT_BLUE
            else:
                val_color = ACCENT_GREEN
        else:
            val_color = BRIGHT_TEXT
            
        screen.blit(font.render(val, True, val_color), (colon_x + 30, y_pos))

    # --- Larger Completion Message ---
    if hanoi_game.game_status == "completed":
        if hanoi_game.move_count == min_moves:
            msg_surf = font_large.render("Perfect Play!", True, ACCENT_GREEN)
        else:
            msg_surf = font_large.render("Good Play!", True, ACCENT_BLUE)
        msg_rect = msg_surf.get_rect(center=(combined_rect.centerx, 490))
        screen.blit(msg_surf, msg_rect)

    # --- Reset Button ---
    btn_reset_rect = pygame.Rect(600, 525, 255, 35)
    draw_button(screen, font, "Reset Game", btn_reset_rect, active=True)

def draw_screen(screen, font):
    if current_mode == "solver":
        draw_screen_solver(screen, font)
    else:
        draw_screen_manual(screen, font)