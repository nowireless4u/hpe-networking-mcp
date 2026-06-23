"""Platform → canonical readers."""

from hpe_networking_mcp.translations.readers.aos8 import aos8_read_wlan
from hpe_networking_mcp.translations.readers.mist import mist_read_wlan

__all__ = ["aos8_read_wlan", "mist_read_wlan"]
