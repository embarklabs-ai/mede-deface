# Without this, Docker's default 64MB /dev/shm causes bus error crashes.
# Must be imported before any torch usage (entrypoint.py imports this first).
try:
    import torch.multiprocessing
    torch.multiprocessing.set_sharing_strategy('file_system')
except ImportError:
    pass
