
import os
import pytest
from unittest.mock import MagicMock
from action import KoreaderAction

def test_get_calibre_uuid_from_sidecar():
    action = KoreaderAction(MagicMock(), MagicMock())
    
    # Test with valid identifiers
    sidecar = {'doc_props': {
        'identifiers': ('calibre:456 '
                        'uuid:d1fe7ad2-bf4f-4a92-bb23-931ccc23e571 '
                        'urn:uuid:fb126322-1c5c-465f-a4e6-29d357e86841')
    }}
    assert action.get_calibre_uuids_from_sidecar(sidecar) == [
        'd1fe7ad2-bf4f-4a92-bb23-931ccc23e571',
        'fb126322-1c5c-465f-a4e6-29d357e86841',
    ]
    assert action.get_calibre_uuid_from_sidecar(sidecar) == \
        'd1fe7ad2-bf4f-4a92-bb23-931ccc23e571'
    
    # Test with newline/backslash separator
    sidecar = {'stats': {
        'identifiers': ('uuid:8d62883d-1111-4222-8333-123456789abc\\'
                        'calibre:5ac8d90f-7d24-4b65-9f89-ff77df18bee9')
    }}
    assert action.get_calibre_uuid_from_sidecar(sidecar) == \
        '8d62883d-1111-4222-8333-123456789abc'
    
    # Test with no calibre identifier
    sidecar = {
        'stats': {
            'identifiers': 'uuid:abc isbn:123'
        }
    }
    assert action.get_calibre_uuid_from_sidecar(sidecar) is None

def test_uuid_mismatch_resolution_integration():
    # Setup
    wrong_uuid = "wrong-uuid-1234-5678"
    correct_uuid = "43bd8264-96fa-461a-a05e-1d1cb245d34f"
    sidecar_path = "Carroll, Lewis/Alice's Adventures in Wonderland - Lewis Carroll.sdr/metadata.epub.lua"
    
    class MockBook:
        def __init__(self, uuid, path):
            self.uuid = uuid
            self.path = path
    mock_book = MockBook(uuid=wrong_uuid, path=sidecar_path.replace(".sdr/metadata.epub.lua", ".epub"))
    
    mock_device = MagicMock()
    mock_device.books.return_value = [mock_book]
    def get_file_side_effect(path, outfile):
        real_path = os.path.join("dummy_device", path)
        with open(real_path, "rb") as f:
            outfile.write(f.read())
    mock_device.get_file.side_effect = get_file_side_effect

    mock_site_customization = MagicMock()
    mock_site_customization.name = 'KOReader Sync'
    mock_site_customization.version = (0, 8, 0)
    action = KoreaderAction(MagicMock(), mock_site_customization)
    
    # Mock DB
    mock_db = MagicMock()
    def lookup_by_uuid_side_effect(uuid):
        if uuid == correct_uuid: return 4
        return None
    mock_db.lookup_by_uuid.side_effect = lookup_by_uuid_side_effect
    
    # Simulate the worker loop logic
    # 1. Get sidecar
    sidecar_contents = action.get_sidecar(mock_device, sidecar_path)
    
    # 2. Inject the correct identifier (simulating what KOReader would have)
    sidecar_contents['stats']['identifiers'] = f'uuid:{wrong_uuid} calibre:{correct_uuid}'
    
    # 3. Test the fix: if initial lookup fails, try alternative
    book_id = mock_db.lookup_by_uuid(wrong_uuid)
    assert book_id is None # Initial failure
    
    resolved_uuid, book_id = action.resolve_book_uuid(
        wrong_uuid, sidecar_contents, mock_db)
    assert resolved_uuid == correct_uuid
    assert book_id == 4 # Success!
