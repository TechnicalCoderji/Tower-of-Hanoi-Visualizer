class HanoiModel:
    def __init__(self, num_disks=3):
        self.num_disks = num_disks
        # Pegs 0, 1, 2. Disks represented by sizes 1 (smallest) to N (largest)
        # Peg 0 starts with all disks (largest at bottom, smallest at top)
        self.pegs = [list(range(num_disks, 0, -1)), [], []]
        self.dragging_disk = None
        self.source_peg = None
        self.drag_pos = (0, 0)
        self.move_count = 0
        self.game_status = "start"  # "start", "running", "completed"

    def reset(self, num_disks=3):
        self.num_disks = num_disks
        self.pegs = [list(range(num_disks, 0, -1)), [], []]
        self.dragging_disk = None
        self.source_peg = None
        self.move_count = 0
        self.game_status = "start"

    def get_peg_from_pos(self, x):
        """Maps x coordinate to peg index (0, 1, or 2) within the left panel."""
        # Left panel X ranges from 15 to 555 (width 540)
        # Peg center X positions are roughly at 150, 315, 480
        peg_regions = [(15, 195), (195, 375), (375, 555)]
        for idx, (xmin, xmax) in enumerate(peg_regions):
            if xmin <= x <= xmax:
                return idx
        return None

    def handle_mouse_down(self, pos):
        x, y = pos
        peg_idx = self.get_peg_from_pos(x)
        if peg_idx is not None and self.pegs[peg_idx]:
            # Pick up the top disk of the clicked peg
            self.source_peg = peg_idx
            self.dragging_disk = self.pegs[peg_idx].pop()
            self.drag_pos = pos

    def handle_mouse_motion(self, pos):
        if self.dragging_disk is not None:
            self.drag_pos = pos

    def handle_mouse_up(self, pos):
        if self.dragging_disk is not None:
            x, y = pos
            target_peg = self.get_peg_from_pos(x)
            
            valid_move = False
            if target_peg is not None:
                if not self.pegs[target_peg] or self.pegs[target_peg][-1] > self.dragging_disk:
                    self.pegs[target_peg].append(self.dragging_disk)
                    valid_move = True
                else:
                    self.pegs[self.source_peg].append(self.dragging_disk)
            else:
                self.pegs[self.source_peg].append(self.dragging_disk)

            if valid_move and target_peg != self.source_peg:
                self.move_count += 1
                self.game_status = "running"
                # Check win condition: all disks on destination peg (peg 2)
                if len(self.pegs[2]) == self.num_disks:
                    self.game_status = "completed"

            self.dragging_disk = None
            self.source_peg = None