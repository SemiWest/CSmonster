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

## Logging System

The game includes a comprehensive logging system for debugging, monitoring, and troubleshooting.

### Logging Flags

- `--log` (default: True)  
  Enables logging system. Logging is **enabled by default**.
- `--no-log`  
  **Completely disables** logging system for maximum performance.
- `--log-level {DEBUG|INFO|WARNING|ERROR|CRITICAL}` (default: DEBUG)  
  Sets the minimum logging level. DEBUG provides the most detailed output.
- `--log-file PATH` (default: logs/game.log)  
  Saves logs to the specified file path with automatic rotation (10MB max, 5 files).
- `--log-stdout`  
  Outputs logs to the console/terminal in addition to file logging.

### Examples

```bash
# Default execution (automatic DEBUG logging to logs/game.log)
python main.py

# Also output logs to console
python main.py --log-stdout

# Change log level to INFO only
python main.py --log-level INFO

# Custom log file location
python main.py --log-file my_logs/session.log

# Disable logging completely for maximum performance
python main.py --no-log

# Combined with debug mode
python main.py --debug --log-stdout
```

### Log Content

The logging system captures:
- **Lifecycle Events**: Game start/stop, mode selection, screen transitions
- **Battle System**: Combat start/end, skill usage, damage calculations, battle outcomes
- **UI/Menu Events**: Menu navigation, option selections, input handling
- **Debug Information**: Player stats, game state changes, performance metrics
- **Error Handling**: File operations, asset loading, system errors

### File Rotation

When using `--log-file`, logs automatically rotate:
- Maximum file size: 10MB
- Maximum backup files: 5
- Files are rotated as `game.log`, `game.log.1`, `game.log.2`, etc.
- Logs are saved in UTF-8 encoding for Korean text support.

### Performance

Logging uses `isEnabledFor()` checks to avoid performance impact when logging is disabled or when messages are below the configured level.
