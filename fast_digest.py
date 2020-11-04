#!/usr/bin/env python3

import hashlib
from pathlib import Path

def fast_digest(file_path, step=1024, size=1024):
    """This function takes a file path and generates a partial checksum
    which can then be used to identify the file when synchronizing with
    a KOReader Sync Server. The original `fastDigest`, written in LUA,
    and used when syncing from within KOReader, can be found here:
    https://github.com/koreader/koreader/blob/8403154d4d36f4279828e0af90667a92685a4ebe/frontend/document/document.lua#L125
    """
    m = hashlib.md5()

    with file_path.open(mode='rb') as file:
        sample = file.read(size)
        m.update(sample)

        for i in range(0, 10):
            file.seek(step << (2 * i), 0)
            sample = file.read(size)
            if sample:
                m.update(sample)
            else:
                break

    return m.hexdigest()

if __name__ == '__main__':
    example_epub = Path('Robert Charles Wilson - Axis.epub')
    partial_md5_checksum = fast_digest(example_epub)
    print(partial_md5_checksum)