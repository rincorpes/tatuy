# SceneService Implementation

`SceneService` stores scene stack entries.

Responsibilities:

- register scene factories
- resolve registered scenes
- push scenes
- pop scenes
- change scenes
- determine visible entries
- determine input recipient
- determine update entries
- build each scene's system pipeline

Scene entry occurs before system-pipeline construction.

That ordering lets scene configuration influence systems and overrides.

---
