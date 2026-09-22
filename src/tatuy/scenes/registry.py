from __future__ import annotations

import onomasticon

from tatuy.scenes.scene import Scene


class SceneRegistry(onomasticon.ImplementationRegistry[Scene]):
    implementation_base = Scene
