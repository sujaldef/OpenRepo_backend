import os
import numpy as np
from collections import defaultdict


class StructureAnalyzer:

    def analyze(self, repo_path: str) -> dict:

        folder_depths = []
        files_per_folder = defaultdict(int)
        total_files = 0

        for root, dirs, files in os.walk(repo_path):

            rel_path = os.path.relpath(root, repo_path)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1

            folder_depths.append(depth)
            files_per_folder[root] += len(files)
            total_files += len(files)

        if total_files == 0:
            return {}

        avg_depth = np.mean(folder_depths)
        max_depth = np.max(folder_depths)
        depth_std = np.std(folder_depths)

        avg_files = np.mean(list(files_per_folder.values()))
        max_files = np.max(list(files_per_folder.values()))

        entropy = self._compute_entropy(list(files_per_folder.values()))

        return {
            "total_files": total_files,
            "avg_depth": float(avg_depth),
            "max_depth": int(max_depth),
            "depth_std": float(depth_std),
            "avg_files_per_folder": float(avg_files),
            "max_files_in_folder": int(max_files),
            "folder_entropy": float(entropy),
        }

    def _compute_entropy(self, values):
        values = np.array(values)
        probs = values / np.sum(values)
        return -np.sum(probs * np.log2(probs + 1e-9))