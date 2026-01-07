"""
Semantic Space module - Navigate samples based on MIR features

Organizes samples in a multi-dimensional feature space and enables
intelligent sample selection based on similarity, proximity, etc.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from .sample_bank import Sample

# Optional dimensionality reduction
try:
    from sklearn.manifold import TSNE
    TSNE_AVAILABLE = True
except ImportError:
    TSNE_AVAILABLE = False

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False


class SemanticSpace:
    """
    Organize and navigate samples in MIR feature space

    Enables queries like:
    - Find samples similar to a given sample
    - Get samples in a specific region of feature space
    - Navigate smoothly through timbral dimensions
    """

    def __init__(self, samples: List[Sample], feature_keys: Optional[List[str]] = None):
        """
        Initialize semantic space from samples

        Args:
            samples: List of Sample objects with extracted features
            feature_keys: Which feature keys to use for the space
                         If None, uses all common features
        """
        self.samples = samples
        self._projection_2d = None  # Cache for 2D projection

        # Determine which features to use
        if feature_keys is None:
            # Find features common to all samples
            # Exclude tempo by default as it can be NaN for short samples
            exclude_features = {'tempo'}

            if samples:
                all_keys = set(samples[0].features.keys())
                for sample in samples[1:]:
                    all_keys &= set(sample.features.keys())

                # Remove excluded features
                all_keys -= exclude_features

                self.feature_keys = sorted(list(all_keys))
            else:
                self.feature_keys = []
        else:
            self.feature_keys = feature_keys

        # Build feature matrix
        self._build_feature_matrix()

    def _build_feature_matrix(self):
        """Build normalized feature matrix from samples"""
        if not self.samples or not self.feature_keys:
            self.feature_matrix = np.array([])
            return

        # Extract features into matrix
        features_list = []
        for sample in self.samples:
            feature_vec = []
            for key in self.feature_keys:
                val = sample.features.get(key, 0.0)
                # Handle both scalar and array features
                if isinstance(val, (list, np.ndarray)):
                    feature_vec.extend(val)
                else:
                    feature_vec.append(val)
            features_list.append(feature_vec)

        self.feature_matrix = np.array(features_list)

        # Normalize features (z-score normalization)
        if len(self.feature_matrix) > 1:
            mean = np.mean(self.feature_matrix, axis=0)
            std = np.std(self.feature_matrix, axis=0)
            # Avoid division by zero
            std[std == 0] = 1.0
            self.feature_matrix = (self.feature_matrix - mean) / std

    def find_similar(self, sample: Sample, n: int = 5,
                    exclude_self: bool = True) -> List[Sample]:
        """
        Find n most similar samples to the given sample

        Args:
            sample: Reference sample
            n: Number of similar samples to return
            exclude_self: If True, exclude the reference sample from results

        Returns:
            List of similar samples, sorted by similarity
        """
        if sample not in self.samples:
            return []

        sample_idx = self.samples.index(sample)
        sample_features = self.feature_matrix[sample_idx]

        # Compute distances to all samples
        distances = np.linalg.norm(
            self.feature_matrix - sample_features,
            axis=1
        )

        # Get indices of closest samples
        sorted_indices = np.argsort(distances)

        # Filter and limit results
        results = []
        for idx in sorted_indices:
            if exclude_self and idx == sample_idx:
                continue
            results.append(self.samples[idx])
            if len(results) >= n:
                break

        return results

    def find_in_region(self, center_features: Dict[str, float],
                      radius: float = 1.0, n: int = 10) -> List[Sample]:
        """
        Find samples within a region of feature space

        Args:
            center_features: Dict of feature values defining region center
                           e.g., {'brightness': 0.7, 'noisiness': 0.3}
            radius: Maximum distance from center (in normalized units)
            n: Maximum number of samples to return

        Returns:
            List of samples within the region
        """
        # Build center vector
        center_vec = []
        for key in self.feature_keys:
            if key in center_features:
                center_vec.append(center_features[key])
            else:
                # Use mean if feature not specified
                center_vec.append(0.0)

        center_vec = np.array(center_vec)

        # Compute distances
        distances = np.linalg.norm(
            self.feature_matrix - center_vec,
            axis=1
        )

        # Filter by radius and sort
        in_region = distances <= radius
        indices = np.where(in_region)[0]
        sorted_indices = indices[np.argsort(distances[indices])]

        # Return up to n samples
        return [self.samples[idx] for idx in sorted_indices[:n]]

    def get_random_weighted(self, feature_weights: Dict[str, float]) -> Sample:
        """
        Get a random sample, weighted by feature preferences

        Args:
            feature_weights: Dict mapping feature names to desired values
                           Samples closer to these values are more likely

        Returns:
            Randomly selected sample (weighted by similarity to preferences)
        """
        # Build target vector
        target_vec = []
        for key in self.feature_keys:
            target_vec.append(feature_weights.get(key, 0.0))

        target_vec = np.array(target_vec)

        # Compute distances (smaller = more similar)
        distances = np.linalg.norm(
            self.feature_matrix - target_vec,
            axis=1
        )

        # Convert to weights (inverse distance)
        # Add small epsilon to avoid division by zero
        weights = 1.0 / (distances + 1e-6)
        weights /= weights.sum()

        # Random choice weighted by similarity
        idx = np.random.choice(len(self.samples), p=weights)
        return self.samples[idx]

    def interpolate_path(self, start_sample: Sample, end_sample: Sample,
                        steps: int = 10) -> List[Sample]:
        """
        Create a path through feature space between two samples

        Useful for creating smooth timbral transitions.

        Args:
            start_sample: Starting sample
            end_sample: Ending sample
            steps: Number of intermediate samples to select

        Returns:
            List of samples forming a path from start to end
        """
        if start_sample not in self.samples or end_sample not in self.samples:
            return []

        start_idx = self.samples.index(start_sample)
        end_idx = self.samples.index(end_sample)

        start_features = self.feature_matrix[start_idx]
        end_features = self.feature_matrix[end_idx]

        # Generate interpolated points
        path_samples = [start_sample]

        for i in range(1, steps - 1):
            alpha = i / (steps - 1)
            interp_features = (1 - alpha) * start_features + alpha * end_features

            # Find closest sample to interpolated point
            distances = np.linalg.norm(
                self.feature_matrix - interp_features,
                axis=1
            )
            closest_idx = np.argmin(distances)
            path_samples.append(self.samples[closest_idx])

        path_samples.append(end_sample)

        return path_samples

    def get_feature_summary(self) -> Dict[str, Any]:
        """Get summary statistics of features in the space"""
        if len(self.feature_matrix) == 0:
            return {}

        summary = {}
        for i, key in enumerate(self.feature_keys):
            values = self.feature_matrix[:, i]
            summary[key] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }

        return summary

    def compute_2d_projection(self, method: str = 'tsne',
                             perplexity: int = 30,
                             n_neighbors: int = 15,
                             random_state: int = 42) -> np.ndarray:
        """
        Compute 2D projection of feature space for visualization

        Args:
            method: 'tsne' or 'umap'
            perplexity: t-SNE perplexity parameter
            n_neighbors: UMAP n_neighbors parameter
            random_state: Random seed for reproducibility

        Returns:
            Array of shape (n_samples, 2) with 2D coordinates
        """
        if len(self.feature_matrix) < 2:
            return np.array([])

        # Use cached projection if available
        if self._projection_2d is not None:
            return self._projection_2d

        if method == 'tsne' and TSNE_AVAILABLE:
            # Adjust perplexity if we have few samples
            actual_perplexity = min(perplexity, len(self.samples) - 1)
            tsne = TSNE(n_components=2, perplexity=actual_perplexity,
                       random_state=random_state, n_iter=1000)
            self._projection_2d = tsne.fit_transform(self.feature_matrix)

        elif method == 'umap' and UMAP_AVAILABLE:
            actual_neighbors = min(n_neighbors, len(self.samples) - 1)
            reducer = umap.UMAP(n_components=2, n_neighbors=actual_neighbors,
                              random_state=random_state)
            self._projection_2d = reducer.fit_transform(self.feature_matrix)

        else:
            # Fallback: PCA (always available via numpy)
            print(f"Warning: {method} not available, using PCA fallback")
            # Center the data
            centered = self.feature_matrix - np.mean(self.feature_matrix, axis=0)
            # Compute covariance
            cov = np.cov(centered.T)
            # Get top 2 eigenvectors
            eigenvalues, eigenvectors = np.linalg.eig(cov)
            idx = eigenvalues.argsort()[::-1][:2]
            components = eigenvectors[:, idx].real
            self._projection_2d = centered @ components

        return self._projection_2d

    def navigate_vector(self, start_sample: Sample, direction: np.ndarray,
                       distance: float = 1.0) -> Optional[Sample]:
        """
        Navigate through space in a specific direction vector

        Args:
            start_sample: Starting sample
            direction: Direction vector in feature space (will be normalized)
            distance: How far to move

        Returns:
            Closest sample to the target point
        """
        if start_sample not in self.samples:
            return None

        start_idx = self.samples.index(start_sample)
        start_features = self.feature_matrix[start_idx]

        # Normalize direction
        direction = np.array(direction)
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)

        # Calculate target point
        target = start_features + direction * distance

        # Find closest sample
        distances = np.linalg.norm(self.feature_matrix - target, axis=1)
        closest_idx = np.argmin(distances)

        return self.samples[closest_idx]

    def navigate_gradient(self, start_sample: Sample, feature_name: str,
                         amount: float = 1.0) -> Optional[Sample]:
        """
        Navigate along a specific feature dimension

        Args:
            start_sample: Starting sample
            feature_name: Which feature to move along ('brightness', 'energy', etc.)
            amount: How much to increase/decrease (in standard deviations)

        Returns:
            Sample moved along that feature dimension
        """
        if start_sample not in self.samples:
            return None

        # Find feature index
        feature_idx = None
        current_dim = 0
        for key in self.feature_keys:
            sample_val = self.samples[0].features.get(key)
            if isinstance(sample_val, (list, np.ndarray)):
                num_dims = len(sample_val)
                if key == feature_name:
                    # For multi-dimensional features, use first dimension
                    feature_idx = current_dim
                    break
                current_dim += num_dims
            else:
                if key == feature_name:
                    feature_idx = current_dim
                    break
                current_dim += 1

        if feature_idx is None:
            print(f"Warning: Feature '{feature_name}' not found")
            return start_sample

        # Create direction vector along this feature
        direction = np.zeros(self.feature_matrix.shape[1])
        direction[feature_idx] = 1.0

        return self.navigate_vector(start_sample, direction, amount)

    def orbit_sample(self, center_sample: Sample, radius: float = 1.0,
                    steps: int = 8) -> List[Sample]:
        """
        Get samples in a circle around a center point

        Args:
            center_sample: Center of the orbit
            radius: Orbit radius
            steps: Number of samples around the circle

        Returns:
            List of samples around the orbit
        """
        if center_sample not in self.samples:
            return []

        center_idx = self.samples.index(center_sample)
        center_features = self.feature_matrix[center_idx]

        # If we have 2D projection, orbit in that space; otherwise use first 2 dims
        if self._projection_2d is not None:
            center_2d = self._projection_2d[center_idx]
            work_space = self._projection_2d
        else:
            center_2d = center_features[:2]
            work_space = self.feature_matrix[:, :2]

        orbit_samples = []
        for i in range(steps):
            angle = 2 * np.pi * i / steps
            offset = radius * np.array([np.cos(angle), np.sin(angle)])
            target = center_2d + offset

            # Find closest in 2D space
            distances = np.linalg.norm(work_space - target, axis=1)
            closest_idx = np.argmin(distances)
            orbit_samples.append(self.samples[closest_idx])

        return orbit_samples

    def random_walk(self, start_sample: Sample, steps: int = 10,
                   step_size: float = 0.5) -> List[Sample]:
        """
        Perform a random walk through feature space

        Args:
            start_sample: Starting point
            steps: Number of steps to take
            step_size: Size of each random step

        Returns:
            List of samples along the walk path
        """
        if start_sample not in self.samples:
            return []

        path = [start_sample]
        current_sample = start_sample

        for _ in range(steps - 1):
            # Random direction in full feature space
            direction = np.random.randn(self.feature_matrix.shape[1])
            next_sample = self.navigate_vector(current_sample, direction, step_size)

            if next_sample is not None:
                path.append(next_sample)
                current_sample = next_sample
            else:
                break

        return path

    def __repr__(self):
        return (f"SemanticSpace({len(self.samples)} samples, "
                f"{len(self.feature_keys)} features)")
