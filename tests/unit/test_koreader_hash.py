import hashlib
import os

import pytest

from koreader_hash import calculate_koreader_md5

# Offsets independently derived here (not imported from the module under
# test), so a bug in the module's own offset table would still be caught.
OFFSETS = [0] + [1024 << (2 * i) for i in range(10)]
CHUNK_SIZE = 1024


def expected_partial_md5(data):
    """Reference implementation used only by tests, built independently of
    koreader_hash.py, to compute the expected hash for a given byte string."""
    md5 = hashlib.md5()
    for offset in OFFSETS:
        if offset >= len(data):
            continue
        md5.update(data[offset:offset + CHUNK_SIZE])
    return md5.hexdigest()


def write_file(tmp_path, name, data):
    path = tmp_path / name
    path.write_bytes(data)
    return str(path)


def test_file_smaller_than_first_chunk(tmp_path):
    data = os.urandom(500)
    path = write_file(tmp_path, "small.epub", data)
    assert calculate_koreader_md5(path) == expected_partial_md5(data)


def test_file_spanning_several_offsets(tmp_path):
    # 5000 bytes: offsets 0 and 1024 fully within range, 4096 partially
    # (only 904 bytes available) - exercises the "partial last chunk" path.
    data = os.urandom(5000)
    path = write_file(tmp_path, "medium.epub", data)
    assert calculate_koreader_md5(path) == expected_partial_md5(data)


def test_file_exactly_at_an_offset_boundary(tmp_path):
    # Exactly 1024 bytes: offset 1024 is NOT < file size, so it must be
    # skipped entirely (only offset 0's chunk should be hashed).
    data = os.urandom(1024)
    path = write_file(tmp_path, "boundary.epub", data)
    assert calculate_koreader_md5(path) == hashlib.md5(data).hexdigest()


def test_large_file_uses_many_offsets(tmp_path):
    # ~5MB, enough to cross several of the larger offsets (65536, 262144,
    # 1048576, 4194304), while staying fast to generate in a test.
    data = os.urandom(5 * 1024 * 1024)
    path = write_file(tmp_path, "large.epub", data)
    assert calculate_koreader_md5(path) == expected_partial_md5(data)


def test_empty_file(tmp_path):
    path = write_file(tmp_path, "empty.epub", b"")
    # Every offset is >= file size (0), so nothing gets hashed at all -
    # this is the MD5 of an empty byte string.
    assert calculate_koreader_md5(path) == hashlib.md5(b"").hexdigest()


def test_missing_file_returns_none(tmp_path):
    assert calculate_koreader_md5(str(tmp_path / "does-not-exist.epub")) is None


def test_same_file_produces_same_hash_every_time(tmp_path):
    data = os.urandom(10000)
    path = write_file(tmp_path, "repeat.epub", data)
    assert calculate_koreader_md5(path) == calculate_koreader_md5(path)


def test_returns_lowercase_32_char_hex_digest(tmp_path):
    data = os.urandom(2000)
    path = write_file(tmp_path, "digest_shape.epub", data)
    digest = calculate_koreader_md5(path)
    assert len(digest) == 32
    assert digest == digest.lower()
    int(digest, 16)  # raises ValueError if not valid hex
