# Changelog

All notable changes to EyeCare will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-13

### Added
- Initial release of EyeCare
- Multi-language support (English, Russian, Ukrainian)
- Customizable work and rest timers (1-60 minutes work, 10-300 seconds rest)
- 4 built-in color themes (Neon, Dark, Light, Ocean) + custom theme
- 8 eye exercises with random selection
- Smart pause feature with configurable idle threshold
- Multi-monitor support
- Break statistics tracking (daily, weekly, all-time)
- Strict mode for mandatory breaks
- Fullscreen app detection
- Windows autostart option
- Customizable overlay opacity with live preview
- 4 sound options (Alert, Beep, Custom File, No Sound)
- Window position and size saving
- Settings reset functionality
- System tray integration
- First-run settings window

### Features
- DPI-aware rendering for high-DPI displays
- Adaptive UI that scales with window size
- Subprocess-based overlay for stability
- Graceful shutdown with proper cleanup
- Automatic config and stats file creation

### Technical
- Python 3.12+ support
- Windows primary platform
- MIT License
