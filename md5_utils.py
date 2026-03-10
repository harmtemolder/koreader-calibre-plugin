#!/usr/bin/env python3

import hashlib
import io
from typing import BinaryIO

STEP = 1024
SIZE = 1024


def partial_md5_checksum(device, path: str) -> str:
    """
    Compute the partial MD5 for file at `path` using the same algorithm
    as KOReader, but retrieving the file via `device.get_file`.

    :param device: a device object providing get_file(path, outfile)
    :param path: Path to the file on the device
    :return: MD5 hex digest (lowercase)
    :raises FileNotFoundError: If file doesn't exist or cannot be retrieved
    """
    md5 = hashlib.md5()

    # Récupérer le fichier entier dans un buffer mémoire
    with io.BytesIO() as outfile:
        try:
            device.get_file(path, outfile)
        except Exception as e:
            raise FileNotFoundError(f"Could not get file from device: {path}") from e

        contents = outfile.getvalue()
        
    # Vérifier que le fichier n'est pas vide
    if not contents:
        raise ValueError(f"File is empty: {path}")

    # On travaille maintenant sur contents comme si c'était le fichier
    f = io.BytesIO(contents)  # type: BinaryIO
    file_size = len(contents)

    for i in range(-1, 11):  # -1 .. 10 inclus
        shift = (2 * i) & 31
        pos = (STEP << shift) & 0xFFFFFFFF

        # Ne pas essayer de lire au-delà de la taille du fichier
        if pos >= file_size:
            continue

        try:
            f.seek(pos)
        except (OSError, IOError):
            continue
        
        chunk = f.read(SIZE)

        if chunk:
            md5.update(chunk)

    return md5.hexdigest()
