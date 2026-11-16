def hanoi_moves_generator(n, source=0, target=2, aux=1, depth=1):
    """
    Generator yielding (current_n, source, target, active_line, current_depth, disk_to_move)
    Lines:
      1: def solve(n, A, C, B)
      2: if n == 0:
      3:     return
      4: solve(n - 1, A, B, C)
      5: move(n, A, C)
      6: solve(n - 1, B, C, A)
    """
    # Line 1: Function definition
    yield (n, source, target, 1, depth, None)
    
    if n == 0:
        # Line 2: if n == 0:
        yield (n, source, target, 2, depth, None)
        # Line 3: return
        yield (n, source, target, 3, depth, None)
        return

    # Line 4: First recursive call
    yield (n, source, aux, 4, depth, None)
    yield from hanoi_moves_generator(n - 1, source, aux, target, depth + 1)

    # Line 5: Move actual disk
    yield (n, source, target, 5, depth, n)

    # Line 6: Second recursive call
    yield (n, aux, target, 6, depth, None)
    yield from hanoi_moves_generator(n - 1, aux, target, source, depth + 1)