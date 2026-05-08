# CHANGELOG - GRK PowerSloth

All notable changes to this project will be documented in this file.

## [6.1.1] - 2026-05-07

Maintenance release centrada en robustez, seguridad y consistencia de localización. Sin cambios funcionales mayores: el comportamiento visible al usuario es el mismo, pero la app es más resistente a entornos degradados (rutas con `%`, exe movido, hora del sistema cambiada, descarga interrumpida, etc.) y la UI cambia de idioma sin dejar fragmentos en español.

### 🐛 Bug Fixes
- **Eventos programados a fin de mes**: `ScheduledEvent.get_next_run` lanzaba `ValueError` en eventos `DAILY` los días 28-31 (`replace(day=day+1)`) y en `MONTHLY` con `day_of_month=31` cuando el mes objetivo tenía menos días. Ahora se usa `timedelta(days=1)` para diarios y `calendar.monthrange()` para clampar el día válido en mensuales (ej. día 31 en febrero → 28/29).
- **Aviso de instancia única en idioma equivocado**: el mensaje al detectar otra instancia ya viva era hardcoded en español. Ahora se carga el idioma del usuario antes del aviso y el texto sale del `LocalizationManager` en los 4 idiomas. El `QLockFile` se libera explícitamente con `unlock()` antes del `sys.exit`.
- **Calendario perdía o duplicaba eventos**: la combinación ventana ±30s + polling 30s permitía doble disparo. Ahora la ventana es `[0..60s]` con polling 60s, y el anti-rebote usa `abs((now - last_run)) < 120s` para sobrevivir a cambios de hora del sistema y DST.
- **Mini-controlador pisaba el countdown en curso**: `update_status` forzaba el mini-timer desde los spinboxes cuando el mensaje no llevaba `HH:MM:SS`, sobreescribiendo el countdown real. Ahora sólo se refresca desde los spinboxes cuando el timer está detenido.
- **Menús con mezcla de idiomas al cambiar idioma**: temas Nordic/Dracula/Blood, idiomas PT/FR y "Buscar Actualizaciones..." eran literales hardcoded. También los títulos de los menús de la barra (File/Settings/Help/Theme/Language) no se reaplicaban en `reapply_localization`. Todo localizado y reaplicado correctamente ahora.

### 🛡️ Robustez y seguridad
- **OTA — descarga**: añadido `timeout=(10, 300)` al `requests.get` (un servidor mudo cancela en vez de colgarse). Validación de `disk_usage` con margen 20% antes de empezar a escribir el `.new`. Timeout del check de la API de GitHub subido de 5s a 10s.
- **OTA — bat de swap**: el bat escapa `%` doblándolo (rutas con `%` rompían CMD), añade `cd /d "{dir}"` antes de los `move`, y aborta con `|| exit /b 1` si falla el primer move; revierte el primero si falla el segundo (no deja al usuario sin EXE).
- **OTA — cancelación**: si el usuario cierra el diálogo durante la descarga, `DownloadWorker` ya no queda huérfano emitiendo señales sobre objetos destruidos. Nuevo `cancel_download()` con `requestInterruption() + wait(3000)`. El `.new` parcial se borra. `cleanup_old_updates` ahora también limpia `update_runner.bat` residual.
- **Apagado/reinicio**: `subprocess.run` con lista de argumentos y `shell=False` (sin `cmd.exe` intermedio, sin riesgo de inyección si futuros parámetros vienen de settings). Suspensión vía `ctypes.windll.powrprof.SetSuspendState` directo.
- **Autostart con Windows**: `winreg.OpenKey` envuelto en `with` (handles cerrados aunque haya excepción). `is_startup_enabled` verifica que el ejecutable registrado siga existiendo en disco — si el usuario movió el `.exe` después de habilitar autostart, devuelve `False` en vez de devolver true sobre una ruta rota.
- **Schedule manager — escritura atómica**: `_save_events()` y `_save_history()` escriben a `*.json.tmp` y hacen `os.replace()`. Un crash entre escrituras no deja JSON corrupto. Save diferido a una sola escritura por tick (antes podía haber N escrituras si N eventos disparaban a la vez).
- **closeEvent**: `schedule_manager.stop_monitoring()` se llama al cerrar la ventana para que `_check_timer` no siga tickando hasta que muera el proceso.
- **Animaciones**: `_animate_transition` para la animación previa antes de reasignar `_fade_anim` (evita slots colgando al alternar modo compacto rápido). Excepciones acotadas a `(TypeError, RuntimeError)` en lugar de `except:` desnudo.
- **Process monitor**: eliminado el `time.sleep(retry_count)` recursivo que bloqueaba el hilo de la GUI hasta 6 segundos cuando el proceso a monitorear no existía o era inaccesible.

### 🧹 Limpieza
- Eliminada la dependencia `packaging>=23.0` del `requirements.txt` (sin usos en código desde 6.1.0; el CHANGELOG ya lo anunciaba pero la línea seguía).
- Eliminado `NotificationManager` (era código muerto que sólo hacía `print()` desde la migración a `QSystemTrayIcon` nativo).
- `GRK_PowerSloth.spec`: añadidos `hiddenimports=['win32timezone', 'pywintypes']` para que el EXE arranque limpio en Windows sin Python instalado.
- Watchdog: detecta `getattr(sys, 'frozen', False)` y lanza `sys.executable` directamente en vez de buscar un `main.py` que no existe en EXE empaquetado.
- Diálogos: quitados `setStyleSheet` con colores hardcodeados (`#888888`, `#f0f0f0`, `#0078D4`) que rompían en temas Dark / Blood Moon / High Contrast. Sustituidos por `objectName` para que el QSS del tema los pueda estilar.
- README: quitado el placeholder de imagen que apuntaba a `via.placeholder.com`.

### 🌍 Localización (38 claves nuevas × 4 idiomas)
- Singleton (`singleton_message`).
- Temas no-defaults (`theme_nordic`, `theme_dracula`, `theme_blood`).
- Idiomas en sus propios nombres (`menu_portuguese`, `menu_french`).
- `menu_check_updates`.
- Diálogo OTA completo (12 claves: título, mensaje "nueva versión", changelog, pregunta, estados, botones, diálogos de confirmación y error).
- Status del presenter (`status_executing`, `warn_select_process`, `update_already_latest`, `update_check_error`).
- Botones genéricos de diálogos (`dialog_btn_cancel/close/save`).
- Títulos y botones primarios de Schedule y History (`schedule_dialog_title`, `schedule_dialog_save_changes`, `history_dialog_title`, `history_btn_clear`).

### 🚧 Conocido — diferido a 6.2.0
- Verificación de hash SHA-256 en el binario OTA descargado (requiere publicar `.sha256` como asset en cada GitHub Release).
- Localización completa de las labels internas del editor de eventos programados y del historial (Nombre:, Hora:, Recurrencia:, etc.).

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
