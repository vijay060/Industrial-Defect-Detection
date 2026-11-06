#!/usr/bin/env python3
"""Select a reproducible sample of normal and anomaly VisA images."""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def image_files(folder: Path) -> list[Path]:
    """Return supported image files in a folder, sorted by path."""
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def select_images(
    dataset_root: Path,
    output_dir: Path,
    samples_per_condition: int = 15,
    seed: int = 42,
) -> int:
    """Copy a fixed-seed sample of each class and condition to a flat folder.

    Args:
        dataset_root: Root containing VisA class directories.
        output_dir: Destination for selected images; must be empty or absent.
        samples_per_condition: Number of images selected per class/condition pair.
        seed: Random seed used to make selection reproducible.

    Returns:
        The number of copied images.
    """
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"{output_dir} is not empty. Use a new folder to avoid overwriting data."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    classes = sorted(
        path
        for path in dataset_root.iterdir()
        if path.is_dir() and (path / "Data" / "Images").is_dir()
    )
    if not classes:
        raise FileNotFoundError(
            f"No VisA class folders were found under {dataset_root}"
        )

    rng = random.Random(seed)
    copied = 0
    for class_dir in classes:
        for condition in ("Normal", "Anomaly"):
            source_dir = class_dir / "Data" / "Images" / condition
            candidates = image_files(source_dir)
            if len(candidates) < samples_per_condition:
                raise ValueError(
                    f"{class_dir.name}/{condition} has only {len(candidates)} images"
                )
            for source in rng.sample(candidates, samples_per_condition):
                destination = output_dir / (
                    f"{class_dir.name}_{condition}_{source.stem}{source.suffix}"
                )
                shutil.copy2(source, destination)
                copied += 1
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("selected_15_normal_15_abnormal_flat"),
    )
    parser.add_argument("--samples-per-condition", type=int, default=15)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = select_images(
        dataset_root=args.dataset_root.resolve(),
        output_dir=args.output.resolve(),
        samples_per_condition=args.samples_per_condition,
        seed=args.seed,
    )
    print(f"Saved {count} images to {args.output.resolve()}")


if __name__ == "__main__":
    main()
