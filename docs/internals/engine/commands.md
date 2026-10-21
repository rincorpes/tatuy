# Engine Commands

Game code should request runtime actions through engine commands instead of reaching directly into engine services.

Examples include scene changes and capture actions.

Commands are placed into the engine command queue and processed by the engine's command processor.

This keeps gameplay intent separate from runtime implementation.

---
