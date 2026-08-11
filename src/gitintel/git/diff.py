import pygit2

from gitintel.models import FileChange


def get_commit_diff(repository, commit):
    """
    Extract file changes from a commit.

    Args:
        repository: pygit2.Repository instance.
        commit: pygit2.Commit instance.

    Returns:
        List of FileChange objects.
    """

    changes = []

    # Handle initial commit (no parents) by diffing against an empty tree
    if not commit.parents:
        parent_tree = None
    else:
        parent = commit.parents[0]
        parent_tree = parent.tree

    # Handle initial commit: walk the tree and treat each blob as an added file
    if parent_tree is None:
        def walk_tree(tree, prefix=""):
            for entry in tree:
                # pygit2 uses numeric constants for object types (GIT_OBJECT_TREE / GIT_OBJECT_BLOB)
                if entry.type == pygit2.GIT_OBJECT_TREE:
                    walk_tree(repository.get(entry.id), prefix + entry.name + '/')
                elif entry.type == pygit2.GIT_OBJECT_BLOB:
                    blob = repository.get(entry.id)
                    try:
                        text = blob.data.decode('utf-8', errors='replace')
                    except Exception:
                        text = ''

                    additions = text.count('\n')

                    changes.append(
                        FileChange(
                            path=prefix + entry.name,
                            additions=additions,
                            deletions=0,
                        )
                    )

        walk_tree(commit.tree)
    else:
        diff = repository.diff(
            parent_tree,
            commit.tree,
        )

        diff.find_similar()

        for patch in diff:
            changes.append(
                FileChange(
                    path=patch.delta.new_file.path,
                    additions=patch.line_stats[1],
                    deletions=patch.line_stats[2],
                )
            )

    return changes


# def get_repository_changes(repository, commits):
#     """
#     Extract all file changes from repository commits.

#     Args:
#         repository: pygit2.Repository instance.
#         commits: List of GitIntel Commit models.

#     Returns:
#         List of FileChange objects.
#     """

#     changes = []

#     for commit_model in commits:
#         commit = repository.get(
#             commit_model.hash
#         )

#         if commit:
#             changes.extend(
#                 get_commit_diff(
#                     repository,
#                     commit,
#                 )
#             )

#     return changes