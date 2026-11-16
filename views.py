import pygame
from settings import *
from hanoi_model import HanoiModel
from algorithm import hanoi_moves_generator

# Global state and model instances
current_mode = "solver"
hanoi_game = HanoiModel(num_disks=3)

# Solver mode specific state

# Solver mode state
solver_num_disks = 3
solver_state = "idle"  # "idle", "solving", "completed"
solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]
solver_generator = None

# Smooth animation states
solver_state = "idle"       # "idle", "solving", "completed"
current_anim_move = None    # Holds (disk, src, tgt)
anim_phase = None           # "LIFT", "SLIDE", "DROP"

# Step counter and solver states
solver_num_disks = 3
active_call_stack = []
solver_state = "idle"
solver_current_step = 0
solver_total_steps = (2 ** solver_num_disks) - 1
anim_disk_pos = [0, 0]      # Current floating pixel (x, y)
anim_target_y = 0           # Target landing y coordinate
ANIMATION_SPEED = 12        # Pixels per frame for smooth glide speed (1 to 4: Slow & Cinematic, 6 to 12: Smooth & Balanced, 15 to 30+: Fast & Teleporting)

# Code panel runtime state
active_code_line = 1
current_recursion_depth = 1
active_code_n = 3  # Track real runtime n value

def toggle_mode():
    global current_mode
    current_mode = "manual" if current_mode == "solver" else "solver"

def handle_events_solver(event):
    global current_mode, solver_num_disks, solver_state, solver_pegs, solver_generator, animation_frame_counter, current_anim_move, solver_current_step, solver_total_steps
    if event.type == pygame.MOUSEBUTTONDOWN:
        btn_mode_rect = pygame.Rect(30, 545, 150, 32)
        if btn_mode_rect.collidepoint(event.pos):
            if solver_state != "solving":  # Prevent mode switch mid-solve
                toggle_mode()
            return

        # Solve / Reset button: Rect(190, 545, 110, 32)
        btn_solve_rect = pygame.Rect(190, 545, 110, 32)
        if btn_solve_rect.collidepoint(event.pos):
            if solver_state == "idle":
                solver_state = "solving"
                solver_generator = hanoi_moves_generator(solver_num_disks)
                current_anim_move = None
            elif solver_state == "completed":
                # --- FIX HERE: Reset pegs, state, and step counter ---
                solver_state = "idle"
                solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]
                solver_generator = None
                current_anim_move = None
                solver_current_step = 0
                solver_total_steps = (2 ** solver_num_disks) - 1
            return

        # Lock disk counter buttons while solving
        if solver_state == "solving":
            return

        btn_minus = pygame.Rect(382, 549, 24, 24)
        btn_plus = pygame.Rect(500, 549, 24, 24)

        if btn_minus.collidepoint(event.pos):
            solver_num_disks = max(3, solver_num_disks - 1)
            solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]
            solver_state = "idle"  # <--- Reset state to idle
            solver_generator = None
            current_anim_move = None
            solver_total_steps = (2 ** solver_num_disks) - 1
            solver_current_step = 0

        elif btn_plus.collidepoint(event.pos):
            solver_num_disks = min(15, solver_num_disks + 1)
            solver_pegs = [list(range(solver_num_disks, 0, -1)), [], []]
            solver_state = "idle"  # <--- Reset state to idle
            solver_generator = None
            current_anim_move = None
            solver_total_steps = (2 ** solver_num_disks) - 1
            solver_current_step = 0

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

    # Draw Tower Labels
    labels = ["source", "extra", "destination"]
    for i, cx in enumerate(peg_centers):
        lbl_surf = font.render(labels[i], True, (240, 245, 250))
        lbl_rect = lbl_surf.get_rect(center=(cx, base_y + 25))
        screen.blit(lbl_surf, lbl_rect)

    # Draw Disks on Pegs
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

            num_surf = font.render(str(disk_size), True, BG_COLOR)
            num_rect = num_surf.get_rect(center=d_rect.center)
            screen.blit(num_surf, num_rect)

    # Draw animated floating disk if moving
    if current_anim_move is not None:
        disk_size, src, tgt = current_anim_move
        d_width = min_disk_width + (disk_size - 1) * ((max_disk_width - min_disk_width) / max(1, 14))
        
        d_rect = pygame.Rect(0, 0, int(d_width), disk_height)
        d_rect.center = (int(anim_disk_pos[0]), int(anim_disk_pos[1]))
        
        color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, d_rect, border_radius=3)
        pygame.draw.rect(screen, BORDER_COLOR, d_rect, 1, border_radius=3)

        num_surf = font.render(str(disk_size), True, BG_COLOR)
        num_rect = num_surf.get_rect(center=d_rect.center)
        screen.blit(num_surf, num_rect)

def update_solver_animation():
    global solver_state, solver_generator, solver_pegs, current_anim_move, anim_phase, anim_disk_pos, anim_target_y, solver_current_step
    
    panel_left = 15
    panel_top = 15
    peg_centers = [panel_left + 135, panel_left + 270, panel_left + 405]
    base_y = panel_top + 460
    disk_height = 18

    if solver_state == "solving":
        if current_anim_move is None and solver_generator is not None:
            try:
                item = next(solver_generator)
                current_n, src, tgt, line_num, depth, disk, stack_frames = item
                global active_code_line, current_recursion_depth, active_code_n, active_call_stack
                active_code_line = line_num
                current_recursion_depth = depth
                active_code_n = current_n
                active_call_stack = stack_frames  # <--- Capture current stack list!

                if disk is not None:  
                    if solver_pegs[src]:
                        d = solver_pegs[src].pop()
                        current_anim_move = (d, src, tgt)
                        
                        src_level = len(solver_pegs[src])
                        start_x = peg_centers[src]
                        start_y = base_y - (src_level * (disk_height + 2)) - disk_height // 2
                        
                        anim_disk_pos = [float(start_x), float(start_y)]
                        anim_phase = "LIFT"
            except StopIteration:
                solver_state = "completed"
                solver_generator = None
                current_anim_move = None

        # Execute kinematic animation phases
        if current_anim_move is not None:
            disk, src, tgt = current_anim_move
            target_x = float(peg_centers[tgt])
            # Hover lift height well above pegs
            lift_y = float(panel_top + 80)
            
            # Target landing y calculation
            tgt_level = len(solver_pegs[tgt])
            landing_y = float(base_y - (tgt_level * (disk_height + 2)) - disk_height // 2)

            if anim_phase == "LIFT":
                # Move upward to lift_y
                if anim_disk_pos[1] > lift_y:
                    anim_disk_pos[1] = max(lift_y, anim_disk_pos[1] - ANIMATION_SPEED)
                else:
                    anim_phase = "SLIDE"

            elif anim_phase == "SLIDE":
                # Slide horizontally towards target peg X
                if abs(anim_disk_pos[0] - target_x) > ANIMATION_SPEED:
                    if anim_disk_pos[0] < target_x:
                        anim_disk_pos[0] += ANIMATION_SPEED
                    else:
                        anim_disk_pos[0] -= ANIMATION_SPEED
                else:
                    anim_disk_pos[0] = target_x
                    anim_phase = "DROP"

            elif anim_phase == "DROP":
                if anim_disk_pos[1] < landing_y:
                    anim_disk_pos[1] = min(landing_y, anim_disk_pos[1] + ANIMATION_SPEED)
                else:
                    solver_pegs[tgt].append(disk)
                    current_anim_move = None
                    anim_phase = None
                    solver_current_step += 1

def draw_call_stack_panel(screen, font):
    stack_rect = pygame.Rect(570, 300, 315, 275)
    pygame.draw.rect(screen, PANEL_BG, stack_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, stack_rect, 2, border_radius=8)
    
    # Title
    screen.blit(font.render("Call Stack (Beaker View)", True, (240, 245, 250)), (585, 310))

    # Inner beaker container box
    inner_box = pygame.Rect(582, 340, 291, 225)
    pygame.draw.rect(screen, (25, 29, 36), inner_box, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, inner_box, 1, border_radius=6)

    stack_font = pygame.font.SysFont("Courier New", 15, True)

    if solver_state == "idle" or not active_call_stack:
        placeholder = stack_font.render("Stack empty (Idle)", True, (100, 110, 120))
        screen.blit(placeholder, (inner_box.x + 15, inner_box.y + 15))
        return

    max_visible = 5
    total_elements = len(active_call_stack)
    overflow_count = max(0, total_elements - max_visible)

    # Start drawing from the bottom of the inner box
    start_y = inner_box.bottom - 36

    # 1. If there is an overflow, reserve the very bottom slot for "(+ X more elements)"
    if overflow_count > 0:
        overflow_str = f"(+ {overflow_count} more elements)"
        overflow_surf = stack_font.render(overflow_str, True, (140, 150, 160))
        screen.blit(overflow_surf, (inner_box.x + 15, start_y + 6))
        start_y -= 36  # Shift upward so active frames stack above it

    # 2. Slice to show the most recent active frames (cutoff the bottom/older ones)
    visible_frames = active_call_stack[-max_visible:] if overflow_count > 0 else active_call_stack

    # 3. Draw the active frames upward from start_y
    for frame in visible_frames:
        n_val = frame['n']
        src_val = frame['src']
        tgt_val = frame['tgt']
        aux_val = frame['aux']

        try:
            disk_col = DISK_COLORS[n_val - 1] if 0 <= n_val - 1 < len(DISK_COLORS) else (152, 195, 121)
        except (TypeError, IndexError):
            disk_col = (152, 195, 121)

        strip_rect = pygame.Rect(inner_box.x + 6, start_y, inner_box.width - 12, 32)
        pygame.draw.rect(screen, (35, 41, 51), strip_rect, border_radius=5)
        pygame.draw.rect(screen, disk_col, (strip_rect.x, strip_rect.y, 6, strip_rect.height), border_top_left_radius=5, border_bottom_left_radius=5)

        text_str = f"solve(n={n_val}, {src_val}, {tgt_val}, {aux_val})"
        txt_surf = stack_font.render(text_str, True, (220, 225, 230))
        screen.blit(txt_surf, (strip_rect.x + 16, strip_rect.y + 6))

        start_y -= 36  # Move upward for the next element

def draw_algorithm_code_panel(screen, font):
    code_rect = pygame.Rect(570, 15, 315, 275)
    pygame.draw.rect(screen, PANEL_BG, code_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, code_rect, 2, border_radius=8)
    
    # Title
    screen.blit(font.render("Algorithm Code", True, (240, 245, 250)), (585, 25))

    # Inner code container box
    inner_box = pygame.Rect(582, 58, 291, 202)
    pygame.draw.rect(screen, (25, 29, 36), inner_box, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, inner_box, 1, border_radius=6)

    # Your preferred font setting
    code_font = pygame.font.SysFont("Courier New", 17, True)  

    d_n = active_code_n if solver_state == "solving" else solver_num_disks

    code_lines = [
        f"def solve(n={d_n}, A, C, B):",
        "    if n == 0:",
        "        return",
        "    solve(n - 1, A, B, C)",
        "    move(n, A, C)",
        "    solve(n - 1, B, C, A)"
    ]

    # Render code lines with active line highlight
    line_y = inner_box.y + 10
    for idx, text in enumerate(code_lines, start=1):
        line_color = (150, 160, 170)
        
        if solver_state == "solving" and active_code_line == idx:
            hl_rect = pygame.Rect(inner_box.x + 4, line_y - 2, inner_box.width - 8, 24)
            pygame.draw.rect(screen, (40, 60, 50), hl_rect, border_radius=4)
            line_color = (152, 195, 121)  # Accent green

        txt_surf = code_font.render(text, True, line_color)
        screen.blit(txt_surf, (inner_box.x + 8, line_y))
        line_y += 32

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

    # 2. Solve / Reset Button (Next to toggle)
    btn_solve_rect = pygame.Rect(190, 545, 110, 32)
    if solver_state == "idle":
        # Green Idle Button
        pygame.draw.rect(screen, ACCENT_GREEN, btn_solve_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_COLOR, btn_solve_rect, 2, border_radius=6)
        txt_surf = font.render("Solve", True, BG_COLOR)
        screen.blit(txt_surf, txt_surf.get_rect(center=btn_solve_rect.center))
    elif solver_state == "solving":
        # Disabled Solving State
        pygame.draw.rect(screen, (60, 70, 85), btn_solve_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_COLOR, btn_solve_rect, 2, border_radius=6)
        txt_surf = font.render("Solving...", True, (150, 160, 170))
        screen.blit(txt_surf, txt_surf.get_rect(center=btn_solve_rect.center))
    else:
        # Red Reset Button after completion
        pygame.draw.rect(screen, ACCENT_RED, btn_solve_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_COLOR, btn_solve_rect, 2, border_radius=6)
        txt_surf = font.render("Reset", True, BG_COLOR)
        screen.blit(txt_surf, txt_surf.get_rect(center=btn_solve_rect.center))

    # 3. Disk Counter Component: "Disks: [ - | count | + ]"
    lbl_disks = font.render("Disks:", True, BRIGHT_TEXT)
    screen.blit(lbl_disks, (315, 551))

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

    # --- Step Counter at top right of main panel ---
    min_steps = (2 ** solver_num_disks) - 1
    step_text = f"Steps: [{solver_current_step} / {min_steps}]"
    
    # Render Step Counter text and background container box
    step_surf = font.render(step_text, True, BRIGHT_TEXT)
    step_padding = 10
    step_box_rect = pygame.Rect(0, 0, step_surf.get_width() + (step_padding * 2), 28)
    step_box_rect.topright = (545, 26)  # Aligned near top-right of main box
    
    pygame.draw.rect(screen, (35, 39, 46), step_box_rect, border_radius=6)
    pygame.draw.rect(screen, BORDER_COLOR, step_box_rect, 1, border_radius=6)
    
    screen.blit(step_surf, (step_box_rect.x + step_padding, step_box_rect.y + 5))

    # 2. Code Panel (Top Right)
    draw_algorithm_code_panel(screen, font)

    # 3. Call Stack Panel (Bottom Right)
    draw_call_stack_panel(screen, font)

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
        update_solver_animation()

    else:
        draw_screen_manual(screen, font)