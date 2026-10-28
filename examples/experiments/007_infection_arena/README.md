# Infection Arena

A separate Shatterphase mechanics laboratory. It does not import or change
the procedural-tree experiments.

## Run

From the Tatuy repository root, in the existing Poetry environment:

```powershell
poetry run python manage.py run experiment infection_arena
```

Use the CLI loader: app.py uses a package-relative import of ecology.py.
The arena is designed for the default 800 x 600 virtual canvas.

## Controls

| Input | Action |
| --- | --- |
| Mouse | Aim the shield around the fixed fungus core |
| Space | Launch the attached ball |
| C | Recall the ball |
| F | Send a fungal spore to the pointed tile; costs 25 energy |
| P | Pause or resume the simulation |
| N | Advance one 1/120-second simulation tick while paused |
| R | Reset to the same initial seed and settings |
| T | Toggle local bacterial reproduction |
| Y | Toggle creation of new airborne bacterial seeds |
| B / G | Place bacteria / a fungal colony under the pointer |
| M | Restore moss under the pointer |
| X | Remove the colony under the pointer, preserving moss |

Placement commands work while paused and bypass energy costs. T and Y
stop future reproduction/emission; already airborne seeds still settle.

## Rules in this prototype

- Each ground tile has moss health from zero to one. Brighter green means
  healthier moss; dark ground is depleted.
- Pink bacterial colonies stay fixed. They take two ball hits to clear.
  A diagonal mark indicates one remaining hit; the small bar shows time
  toward local reproduction.
- Every six seconds a colony can reproduce into one cardinal neighboring
  tile with enough moss. New colonies cannot reproduce immediately.
- Bacteria consume moss and replace fungal colonies when infection reaches
  them. Dead ground cannot receive a new bacterial colony.
- Every fifteen seconds a colony can send an airborne bacterial seed
  toward a random tile. The ball or shield can destroy it before landing.
- Purple fungal spores establish a friendly colony on uninfected ground,
  including depleted ground. Landing on bacteria fails without conversion.
- Fungal colonies restore their own tile and neighboring moss faster.
  Existing healthy moss also slowly supports ordinary neighboring recovery.
- Healthy, uninfected moss within 145 pixels of the player restores energy.
  Infected tiles contribute zero; protected core tiles are excluded.
- Low local moss support gradually damages the fungus; healthy support
  gradually restores health. Energy funds fungal spores.
- The ball bounces from all four arena walls and from bacteria. The shield
  redirects incoming balls according to their contact position.
- A ball reaching the core is recalled. There is no life penalty.
- Health reaching zero does not stop this laboratory. There are no waves,
  power-ups, final win/loss conditions, fire, or moving bacteria.
- Airborne seeds are capped at 96. Fixed 120 Hz simulation steps and short
  ball substeps bound collision travel. Long stalls discard excess time.

The initial arena uses seed 42, three bacterial colonies, and one friendly
fungal colony. Rules are experimental, not claims of biological accuracy.

## Suggested experiments

1. Press P to pause. Observe the initial layout, then resume without
   launching. Watch reproduction, moss consumption and distant outbreaks.
2. Reset. Disable airborne seeds with Y to isolate local spread. Aim and
   launch the ball; compare clearing young colonies with older fronts.
3. Pause and use B around the fungus. Resume and watch local support,
   energy recovery and health fall. Clear colonies and restore nearby
   moss with M to compare the opposite outcome.
4. Place a fungal colony with G on depleted ground, or launch one with F.
   Watch its tile and cardinal neighbors recover.
5. Re-enable bacterial seeds. Intercept pink seeds with the shield, and
   compare recovery when fungal spores land on clear versus infected tiles.

## Code and tuning

- app.py: Tatuy intent mapping, control and simulation GameSystems, scene
  composition and RenderQueue presentation.
- ecology.py: arena state, grid rules, ball contacts and seed settlement.
- Settings in ecology.py: reproduction/emission periods, consumption,
  recovery, projectile speeds and fungal-spore cost.

All game-specific rules remain in the experiment. No engine API changes.
The grid is arena-wide resource data; it is deliberately not one ECS
entity per tile. Specialized grid and orbital-shield contacts live here
rather than modifying Tatuy's general collision behavior.

## Verification

The simulation was exercised locally using a copy of Tatuy's current Vec2
implementation: reproduction, newborn timing, support loss, recovery,
spore costs/settlement, interception, ball contacts, resource bounds and
same-seed determinism. This does not substitute for running the desktop
scene and testing mouse feel and visual readability.

Mypy passed for the two implementation files. Pylint diagnostics and the
formatter tool outcome are reported in the delivery notes; no lint
suppressions or checker configuration changes were added.
