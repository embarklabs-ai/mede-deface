# Without this, Docker's default 64MB /dev/shm causes bus error crashes.
# Installed as sitecustomize.py so CPython runs it on every interpreter startup,
# including spawned DataLoader workers that don't inherit the parent's sharing strategy.
try:
    import torch.multiprocessing
    torch.multiprocessing.set_sharing_strategy('file_system')
except ImportError:
    pass
