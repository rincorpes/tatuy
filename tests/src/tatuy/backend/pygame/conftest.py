"""Small offscreen surfaces; no real window or audio device is opened."""

from types import SimpleNamespace

import pygame
import pytest

from tatuy.backend.pygame.components.renderer import PygameRenderer
from tatuy.backend.pygame.config import PygameRendererConfig
from tatuy.graphics.viewport.transform import ViewportTransform


@pytest.fixture
def render_target():
    screen = pygame.Surface((40, 40), pygame.SRCALPHA)
    screen.fill((0, 0, 0, 255))
    transform = ViewportTransform()
    window = SimpleNamespace(screen=screen)
    renderer = PygameRenderer(PygameRendererConfig(), window, transform)
    return SimpleNamespace(
        screen=screen,
        transform=transform,
        window=window,
        renderer=renderer,
    )
