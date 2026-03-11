import sys
from unittest.mock import MagicMock

# Mock calibre before anything else imports it
mock_calibre = MagicMock()
mock_calibre.numeric_version = (6, 0, 0) # Mock a modern calibre version
sys.modules["calibre"] = mock_calibre
sys.modules["calibre.constants"] = mock_calibre
sys.modules["calibre.customize"] = mock_calibre
sys.modules["calibre.devices"] = mock_calibre
sys.modules["calibre.devices.usbms"] = mock_calibre
sys.modules["calibre.devices.usbms.driver"] = mock_calibre
sys.modules["calibre.utils"] = mock_calibre
sys.modules["calibre.utils.config"] = mock_calibre
