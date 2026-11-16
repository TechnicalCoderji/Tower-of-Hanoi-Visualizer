def hanoi_moves_generator(n, source=0, target=2, aux=1, depth=1, current_stack=None):
    if current_stack is None:
        current_stack = []

    # Map tower index (0, 1, 2) to letters ('A', 'B', 'C') based on your setup
    # source=0 -> A, aux=1 -> B (or C depending on call), target=2 -> C
    tower_map = {0: 'A', 1: 'B', 2: 'C'}
    # Wait, let's look at how you map sou, ext, des: source=0, aux=1, target=2.
    # Let's map 0->A, 1->B, 2->C or use whatever letters match your tower labels.
    # Let's use tower_map = {0: 'A', 1: 'B', 2: 'C'} or dynamic names.
    
    frame_info = {
        'n': n,
        'src': tower_map.get(source, 'A'),
        'tgt': tower_map.get(target, 'C'),
        'aux': tower_map.get(aux, 'B'),
        'depth': depth
    }
    
    # Push current frame to stack
    current_stack.append(frame_info)

    # Line 1: Function definition
    yield (n, source, target, 1, depth, None, list(current_stack))
    
    if n == 0:
        yield (n, source, target, 2, depth, None, list(current_stack))
        yield (n, source, target, 3, depth, None, list(current_stack))
        current_stack.pop()
        return

    # Line 4: First recursive call
    yield (n, source, aux, 4, depth, None, list(current_stack))
    yield from hanoi_moves_generator(n - 1, source, aux, target, depth + 1, current_stack)

    # Line 5: Move actual disk
    yield (n, source, target, 5, depth, n, list(current_stack))

    # Line 6: Second recursive call
    yield (n, aux, target, 6, depth, None, list(current_stack))
    yield from hanoi_moves_generator(n - 1, aux, target, source, depth + 1, current_stack)

    # Pop frame when returning from recursion
    current_stack.pop()