import os


def filestructure_snapshot(path):
    """
    Create a filestructure snapshot by returning the paths of all files inside a path.
    """
    paths = []
    for dirpath, _dirnames, filenames in os.walk(path):
        paths.append(dirpath)
        for filename in filenames:
            paths.append(os.path.join(dirpath, filename))
    return paths


def cleanup_path(path, snapshot_before):
    """
    Remove all files and directories inside a path which did not exist in the snapshot_before.
    """
    snapshot_after = filestructure_snapshot(path)
    to_delete = reversed(sorted(set(snapshot_after) - set(snapshot_before)))
    for path in to_delete:
        if os.path.isfile(path):
            os.unlink(path)
        if os.path.isdir(path):
            os.removedirs(path)
