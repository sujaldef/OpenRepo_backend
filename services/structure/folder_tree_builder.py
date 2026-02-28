import os


def build_folder_tree(repo_path):

    tree = {}

    for root, dirs, files in os.walk(repo_path):

        rel = os.path.relpath(root, repo_path)
        current = tree

        if rel != ".":
            parts = rel.split(os.sep)
            for part in parts:
                current = current.setdefault(part, {})

        for file in files:
            current[file] = None

    return tree