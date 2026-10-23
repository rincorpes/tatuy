"""Public effects feature API."""

from tatuy.features.fx.camera import CameraFX
from tatuy.features.fx.components import Particle, Trail, TrailPoint
from tatuy.features.fx.particles import (
    ParticleBurst,
    ParticleEmitResult,
    ParticleEmitter,
)
from tatuy.features.fx.screen import ScreenEffectStack
from tatuy.features.fx.screen_effects import FlashEffect, ScreenEffect
from tatuy.features.fx.systems import (
    ParticleUpdateSystem,
    TrailRenderSystem,
    TrailSystem,
)

__all__ = [
    "CameraFX",
    "FlashEffect",
    "Particle",
    "ParticleBurst",
    "ParticleEmitResult",
    "ParticleEmitter",
    "ParticleUpdateSystem",
    "ScreenEffect",
    "ScreenEffectStack",
    "Trail",
    "TrailPoint",
    "TrailRenderSystem",
    "TrailSystem",
]
