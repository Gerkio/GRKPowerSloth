# CHANGELOG - GRK PowerSloth

All notable changes to this project will be documented in this file.

## [6.1.0] - 2026-01-06

### ✨ New Features
- **Compact Mode Redesign (Mini Controller)**:
    - Entirely new minimalist interface with a "pill" or "bar" design.
    - Beautiful digital timer using `Consolas` font for clarity.
    - Contextual icons (🔌, 🔄, 🌙, etc.) that change based on the selected action.
    - Ultra-thin progress bar integrated into the bottom of the controller.
    - Smooth fade-in/fade-out animations when switching between modes.
- **Improved Usability in Compact Mode**:
    - **Dynamic Time Adjustment**: Added `+` and `-` buttons to adjust time (intervals of 5 minutes) directly from the mini controller, even while the timer is running.
    - **Quick Expand**: Dedicated button (↗️) to quickly return to the full dashboard.

### 🐛 Bug Fixes & Refactoring
- **Universal Single Instance**: Fixed issues with single instance detection on Windows.
- **Dependency Removal**: Removed external dependency `packaging` to ensure better portability of the compiled executable.
- **QSS Optimization**: Removed unsupported CSS properties (like `box-shadow`) to avoid parsing warnings in PyQt6.
- **Improved Validation**: Enhanced input validation for custom timers to prevent invalid time configurations.

## [6.0.2] - 2026-01-03
- Initial Python port of GRK PowerSloth.
- Implementation of MVP (Model-View-Presenter) pattern.
- Multi-language support (ES, EN, PT, FR).
- Theming system (Light, Dark, High Contrast).
- Activity monitoring (Process exit, Network idle).
- Automatic updates via GitHub Releases.
