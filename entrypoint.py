#!/usr/bin/env python3
"""MEDE defacing entrypoint for XNAT Container Service.

Hardcodes '-de' (deface only CLI arg). No other MEDE features are exposed.
"""

import sys
import time
import logging

import shm_fix  # noqa: F401 — must run before any torch import
import torch

from pathlib import Path

from mede.deidentify import main as mede_main


def find_dicom_dir(input_dir: Path) -> Path | None:
    """Locate the directory containing .dcm files within the XNAT mount.

    XNAT may mount files directly at /input, under /input/DICOM,
    or nested under SCANS/<id>/RESOURCES/DICOM/.
    """
    if any(input_dir.glob("*.dcm")):
        return input_dir

    dicom_subdir = input_dir / "DICOM"
    if dicom_subdir.is_dir() and any(dicom_subdir.glob("*.dcm")):
        return dicom_subdir

    # Search nested structure
    for dcm_file in input_dir.rglob("*.dcm"):
        return dcm_file.parent

    return None


def count_dicoms(directory: Path) -> int:
    return sum(1 for _ in directory.rglob("*.dcm"))


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger(__name__)

    if len(sys.argv) != 3:
        log.error("Usage: %s <input_dir> <output_dir>", sys.argv[0])
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    log.info("Running MEDE Deface Container...")

    # GPU detection
    if torch.cuda.is_available():
        log.info("Mode: GPU (CUDA detected)...")
        gpu_args = ["--gpu", "0"]
    else:
        log.info("Mode: CPU - no CUDA available - inference will be slower...")
        gpu_args = []

    # Locate DICOM files
    dicom_dir = find_dicom_dir(input_dir)
    if dicom_dir is None:
        log.error("No DICOM files found under %s...", input_dir)
        sys.exit(1)

    input_count = count_dicoms(dicom_dir)
    log.info("Input directory: %s...", dicom_dir)
    log.info("Number of DICOM files found: %d...", input_count)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Run MEDE CLI, deface only is hardcoded "-de", no metadata anonymization
    log.info("Running MEDE Defacing...")
    start = time.monotonic()

    sys.argv = [
        "mede-deidentify",
        "-de",
        *gpu_args,
        "-i", str(input_dir),
        "-o", str(output_dir),
    ]
    mede_main()

    elapsed = time.monotonic() - start
    output_count = count_dicoms(output_dir)

    log.info("Complete")
    log.info("Elapsed: %.1fs", elapsed)
    log.info("Number of output DICOM files: %d", output_count)


if __name__ == "__main__":
    run()
