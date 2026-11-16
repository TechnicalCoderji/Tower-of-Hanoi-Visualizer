def hanoi_moves_generator(n, source=0, target=2, aux=1):
    """
    Generator that yields each move step for n disks from source to target using auxiliary peg.
    Yields tuple: (disk_num, source_peg, target_peg)
    """
    if n == 1:
        yield (1, source, target)
        return
    
    yield from hanoi_moves_generator(n - 1, source, aux, target)
    yield (n, source, target)
    yield from hanoi_moves_generator(n - 1, aux, target, source)