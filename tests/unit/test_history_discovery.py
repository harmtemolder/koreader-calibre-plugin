from unittest.mock import MagicMock

from action import KoreaderAction
from calibre_plugins.koreader.config import CONFIG


THEO = ("/mnt/onboard/.adds/koreader/libraries/books/"
        "Allen Levi - Theo of Golden_ A Novel.epub")
TRESS_RELATIVE = ("books/Cosmere/"
                  "Tress of the Emerald Sea - Brandon Sanderson (290).epub")
TRESS = "/mnt/onboard/.adds/koreader/libraries/" + TRESS_RELATIVE


class SMART_DEVICE_APP:
    def __init__(self, books, files):
        self._books = books
        self._files = files

    def books(self):
        return self._books

    def get_file(self, path, outfile):
        outfile.write(self._files[path])


class MockBook:
    def __init__(self, book_uuid, path):
        self.uuid = book_uuid
        self.path = path


def make_action():
    customization = MagicMock()
    customization.name = 'KOReader Sync'
    customization.version = (0, 8, 3)
    return KoreaderAction(MagicMock(), customization)


def test_extract_and_infer_history_paths():
    action = make_action()
    history = {1: {'file': THEO}, 2: {'file': TRESS}}
    paths = action.extract_history_document_paths(history)
    assert paths == [THEO, TRESS]
    assert action.infer_wireless_inbox_root(paths, [TRESS_RELATIVE]) == \
        '/mnt/onboard/.adds/koreader/libraries'


def test_history_adds_unregistered_import_path_only():
    action = make_action()
    registered_uuid = '6a0b0f97-e219-4a84-b30f-a4f31a33748a'
    book = MockBook(registered_uuid, TRESS_RELATIVE)
    history_lua = ("return {\n"
                   f"  [1] = {{ file = [[{THEO}]] }},\n"
                   f"  [2] = {{ file = [[{TRESS}]] }},\n"
                   "}\n").encode()
    device = SMART_DEVICE_APP([book], {'../history.lua': history_lua})
    CONFIG['checkbox_discover_from_history'] = True

    import_paths = action.get_import_paths(device)
    restore_paths = action.get_restore_paths(device)

    theo_sidecar = ("books/Allen Levi - Theo of Golden_ A Novel.sdr/"
                    "metadata.epub.lua")
    assert (None, theo_sidecar) in import_paths
    assert all(path != theo_sidecar for _, path in restore_paths)
    assert len(import_paths) == 2
    assert len(restore_paths) == 1


def test_history_rejects_paths_outside_inbox():
    action = make_action()
    book = MockBook('6a0b0f97-e219-4a84-b30f-a4f31a33748a', TRESS_RELATIVE)
    outside = '/mnt/onboard/private/secret.epub'
    history_lua = ("return {\n"
                   f"  [1] = {{ file = [[{outside}]] }},\n"
                   f"  [2] = {{ file = [[{TRESS}]] }},\n"
                   "}\n").encode()
    device = SMART_DEVICE_APP([book], {'../history.lua': history_lua})
    CONFIG['checkbox_discover_from_history'] = True

    paths = action.get_import_paths(device)
    assert len(paths) == 1
