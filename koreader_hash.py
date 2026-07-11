#!/usr/bin/env python3

"""KOReader's partial-content document hash.

KOReader identifies documents by hashing small chunks of file content read
at a fixed, deterministic set of offsets, rather than the whole file - this
keeps hashing fast even for very large books. This module replicates that
algorithm so Calibre can compute the same hash locally (see GitHub issue
kyxap/koreader-calibre-plugin#150), instead of only ever learning it from a
device that has already synced the book via genuine KOReader software.

Verified directly against KOReader's own reference implementation,
util.partialMD5() in koreader/koreader's frontend/util.lua - including its
i = -1 special case, which relies on a 32-bit left-shift overflow
(1024 << -2, masked to a 5-bit shift count of 30) landing on exactly 0.
Also cross-checked against a from-scratch reimplementation of the same
algorithm: franssjz/cpr-vcodex's lib/KOReaderSync/KOReaderDocumentId.cpp.
"""

import hashlib
import os

CHUNK_SIZE = 1024
OFFSET_COUNT = 12


def _offset_for_index(i):
    """Byte offset for index i: 0 for i == -1, else 1024 << (2*i)."""
    if i < 0:
        return 0
    return CHUNK_SIZE << (2 * i)


def calculate_koreader_md5(file_path):
    """Calculate KOReader's partial-content MD5 hash for a file.

    Reads up to 1024 bytes at each offset in the sequence 0, 1KB, 4KB, 16KB,
    ... up to 1GB (any offset at or beyond the file's size is skipped), and
    returns the MD5 hex digest of the concatenated chunks - matching the
    hash KOReader itself would compute and send to a ProgressSync server.

    :param file_path: path to the file to hash
    :return: 32-character lowercase hex digest, or None if the file can't be read
    """
    try:
        file_size = os.path.getsize(file_path)
    except OSError:
        return None

    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for i in range(-1, OFFSET_COUNT - 1):
                offset = _offset_for_index(i)
                if offset >= file_size:
                    continue
                f.seek(offset)
                chunk = f.read(CHUNK_SIZE)
                if chunk:
                    md5.update(chunk)
    except OSError:
        return None

    return md5.hexdigest()
