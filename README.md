# CSmonster
포켓몬 표절~~

## Debug Mode (Graduation Mode only)

You can enable a developer-friendly cheat/debug layer for Graduation Mode via CLI flags.

### Flags
- `--debug`  
  Enables debug mode (monster stat overlay; behaves like legacy "cheat name" mode).
- `--damage {True|False}` (default: True)  
  Controls whether the player takes damage in debug mode.
  - `True`: Player is invulnerable (legacy cheat behavior).
  - `False`: Player takes normal damage even in debug mode.
- `--skip`  
  When present, pressing Tab during your turn instantly wins the current battle and proceeds to the next screen/phase (healing, reward, etc.).

### Examples

```bash
# Classic cheat behavior: overlay + invulnerable
python main.py --debug

# Overlay but player takes damage normally  
python main.py --debug --damage False

# Debug + Skip hotkey (Tab to win current encounter)
python main.py --debug --skip

# Full control
python main.py --debug --damage False --skip
```

### Notes
- These flags only apply to Graduation Mode (ForGrd).
- Adventure Mode is unchanged.
- Name-based cheat activation ("cheat", "admin", "debug") still works.
- If both name-based cheat and `--debug` are used, CLI flags control the behavior.
