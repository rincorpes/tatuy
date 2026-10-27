"""Logical asset providers for Tatuy applications."""

from tatuy.assets.contracts import AssetProvider
from tatuy.assets.filesystem import FilesystemAssetProvider

__all__ = ["AssetProvider", "FilesystemAssetProvider"]
