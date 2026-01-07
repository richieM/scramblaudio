#!/usr/bin/env python3
"""
Visualize Semantic Space - Terminal visualization of semantic audio space

Shows 2D projection of samples with ASCII art and plots paths through the space.
"""

import numpy as np
from typing import List, Optional, Dict
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scramblaudio_v2.core.semantic_space import SemanticSpace
from scramblaudio_v2.core.sample_bank import Sample


class SpaceVisualizer:
    """
    Visualize semantic space in the terminal

    Shows 2D projection with samples as points.
    """

    def __init__(self, width: int = 80, height: int = 40):
        """
        Initialize visualizer

        Args:
            width: Terminal width in characters
            height: Terminal height in characters
        """
        self.width = width
        self.height = height

    def visualize(self, space: SemanticSpace, show_labels: bool = False,
                 highlight_samples: Optional[List[Sample]] = None,
                 path_points: Optional[List[np.ndarray]] = None) -> str:
        """
        Create ASCII visualization of semantic space

        Args:
            space: SemanticSpace to visualize
            show_labels: Whether to show sample labels
            highlight_samples: Samples to highlight
            path_points: List of 2D points to draw as a path

        Returns:
            ASCII art string
        """
        # Get 2D projection
        projection = space.compute_2d_projection()

        if len(projection) == 0:
            return "No samples to visualize"

        # Normalize to fit in terminal
        min_x, max_x = projection[:, 0].min(), projection[:, 0].max()
        min_y, max_y = projection[:, 1].min(), projection[:, 1].max()

        # Add padding
        padding = 0.1
        x_range = max_x - min_x
        y_range = max_y - min_y
        min_x -= x_range * padding
        max_x += x_range * padding
        min_y -= y_range * padding
        max_y += y_range * padding

        # Create canvas
        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw axes
        origin_x = int(self.width / 2)
        origin_y = int(self.height / 2)

        # Horizontal axis
        for x in range(self.width):
            canvas[origin_y][x] = '─'

        # Vertical axis
        for y in range(self.height):
            canvas[y][origin_x] = '│'

        # Origin
        canvas[origin_y][origin_x] = '┼'

        # Plot path if provided
        if path_points is not None:
            for i in range(len(path_points) - 1):
                p1 = path_points[i]
                p2 = path_points[i + 1]

                # Normalize
                x1 = int((p1[0] - min_x) / (max_x - min_x) * (self.width - 1))
                y1 = self.height - 1 - int((p1[1] - min_y) / (max_y - min_y) * (self.height - 1))
                x2 = int((p2[0] - min_x) / (max_x - min_x) * (self.width - 1))
                y2 = self.height - 1 - int((p2[1] - min_y) / (max_y - min_y) * (self.height - 1))

                # Draw line (simple bresenham)
                points = self._line_points(x1, y1, x2, y2)
                for px, py in points:
                    if 0 <= px < self.width and 0 <= py < self.height:
                        if canvas[py][px] == ' ':
                            canvas[py][px] = '·'

        # Highlight samples
        highlight_indices = set()
        if highlight_samples:
            for sample in highlight_samples:
                if sample in space.samples:
                    highlight_indices.add(space.samples.index(sample))

        # Plot samples
        for i, (x, y) in enumerate(projection):
            # Normalize to canvas coordinates
            canvas_x = int((x - min_x) / (max_x - min_x) * (self.width - 1))
            canvas_y = self.height - 1 - int((y - min_y) / (max_y - min_y) * (self.height - 1))

            # Bounds check
            if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                if i in highlight_indices:
                    canvas[canvas_y][canvas_x] = '●'  # Highlighted
                else:
                    canvas[canvas_y][canvas_x] = '·'  # Normal

        # Convert to string
        lines = [''.join(row) for row in canvas]

        # Add title and stats
        output = []
        output.append("=" * self.width)
        output.append(f"Semantic Space Visualization ({len(space.samples)} samples)")
        output.append("=" * self.width)
        output.extend(lines)
        output.append("=" * self.width)

        # Legend
        if highlight_samples:
            output.append("Legend: · = sample, ● = highlighted")

        return '\n'.join(output)

    def _line_points(self, x0: int, y0: int, x1: int, y1: int) -> List[tuple]:
        """Bresenham's line algorithm"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            points.append((x, y))

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    def visualize_path(self, space: SemanticSpace, path_samples: List[Sample]) -> str:
        """
        Visualize a path through semantic space

        Args:
            space: SemanticSpace
            path_samples: List of samples forming a path

        Returns:
            ASCII visualization with path highlighted
        """
        # Get 2D coordinates for path samples
        path_points = []
        projection = space.compute_2d_projection()

        for sample in path_samples:
            if sample in space.samples:
                idx = space.samples.index(sample)
                path_points.append(projection[idx])

        return self.visualize(space, highlight_samples=path_samples, path_points=path_points)


def create_example_visualization():
    """Create an example visualization with dummy data"""
    from scramblaudio_v2.core.sample_bank import SampleBank

    # Load some samples
    bank = SampleBank()

    # Try to load existing samples
    sample_dirs = [
        '../samples/kicks/',
        '../samples/snares/',
        '../samples/hihats/',
    ]

    for sample_dir in sample_dirs:
        if Path(sample_dir).exists():
            category = Path(sample_dir).name.rstrip('/')
            bank.load_directory(sample_dir, category, extract_features=True)

    if not bank.samples:
        print("No samples found. Generate some samples first with test_with_samples.py")
        return

    # Create semantic space
    space = SemanticSpace(bank.samples)

    print(f"\n📊 Creating visualization of {len(space.samples)} samples...")
    print(f"   Feature dimensions: {len(space.feature_keys)}")

    # Compute projection
    print("   Computing 2D projection (this may take a moment)...")
    space.compute_2d_projection(method='tsne')

    # Visualize
    visualizer = SpaceVisualizer(width=100, height=50)
    viz = visualizer.visualize(space)
    print(viz)

    # Create and visualize a path
    if len(space.samples) >= 10:
        print("\n\n📍 Showing a path through the space...")
        start = space.samples[0]
        end = space.samples[-1]
        path = space.interpolate_path(start, end, steps=10)
        viz_path = visualizer.visualize_path(space, path)
        print(viz_path)

    # Show random walk
    if len(space.samples) >= 20:
        print("\n\n🚶 Showing a random walk...")
        start = space.samples[len(space.samples) // 2]
        walk = space.random_walk(start, steps=15, step_size=0.5)
        viz_walk = visualizer.visualize_path(space, walk)
        print(viz_walk)


if __name__ == "__main__":
    create_example_visualization()
