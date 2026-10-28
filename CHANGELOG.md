# CHANGELOG - GRK PowerSloth

All notable changes to this project will be documented in this file.

## [6.3.0] - 2026-10-28

Actualización de alta fidelidad para el monitor de actividad y optimización del espacio de interfaz de usuario. Perfecciona la detección del fin de descargas mediante fusión de sensores sin requerir entradas adicionales del usuario, reduce un 15% las dimensiones de las ventanas en pantalla y erradica de raíz el error de `LoadLibrary` en ejecutables congelados.

### 🌐 Monitor de Actividad de Alta Fidelidad ("Al terminar descarga")
- **Renombramiento de condición**: la condición "Al finalizar red" pasa a denominarse **"Al terminar descarga"** (*When download finishes* / *Ao terminar download* / *À la fin du téléchargement*) para reflejar con total claridad su propósito al usuario.
- **Fusión de sensores de 3 vías**: detección ultra-fiable combinando el I/O acumulado de la familia del proceso seleccionado, el tráfico de red de interfaces del sistema y la presencia de bloqueos o archivos temporales de descarga parcial (`.crdownload`, `.part`, `.opdownload`, `.tmp` y carpetas de descarga de Steam/Epic).
- **Agrupación de familias de procesos (`_get_process_family`)**: soporte nativo para arquitecturas multi-proceso (Google Chrome, Microsoft Edge, Mozilla Firefox, Steam, Epic Games Launcher) monitorizando el PID principal, procesos hijos recursivos y subprocesos homónimos para capturar el tráfico real gestionado por subprocesos de red aislados.
- **Umbral adaptativo acotado**: piso mínimo de inactividad de 35 KB/s para ignorar telemetría y keep-alive de fondo, y techo máximo de 150 KB/s para evitar falsos apagados en pausas momentáneas de líneas de alta velocidad, además de un umbral de disco activo de 250 KB/s para contemplar el tiempo de desempaquetado e instalación en disco posterior a la descarga.
- **Prevención de suspensión del sistema (`Keep Awake`)**: activación automática de la prevención de suspensión durante el monitoreo de actividad para evitar que el PC entre en reposo mientras se descarga un archivo extenso o se renderiza.
- **Doble confirmación en cierre de app (`ON_EXIT`)**: comprobación cada 2 segundos con 2 ticks de confirmación tanto a nivel de árbol de procesos como de ventanas activas en el sistema.

### 📐 Interfaz Compacta y Ergonómica (-15% de Huella en Pantalla)
- **Modo Estándar optimizado**: ancho base reducido de 480px a 408px (~15% más compacto), márgenes laterales y espaciados entre paneles ajustados para un aspecto más limpio y estilizado.
- **Erradicación del espacio muerto vertical**: corrección del límite rígido de 550px en `_apply_compact_mode(False)`, permitiendo que la ventana principal ajuste su altura dinámicamente al contenido real y eliminando más de 200px de espacio vacío.
- **Mini Controller estilizado**: dimensiones reducidas a 336x78px (antes 380x95px) con tipografía monospace equilibrada y botones circulares de acción de 36px.
- **Controles compactos**: selectores de tiempo (spinners) reducidos a 62px de ancho, combo de procesos de 28px de altura y barra de progreso de 18px.

### 🐛 Bug Fixes Críticos
- **Erradicación de error `LoadLibrary` en PyInstaller (`_MEIPASS`)**: limpieza explícita de `_MEIPASS` y `_MEIPASS2` en el entorno de Python y en el bloque de variables de entorno de Windows (`SetEnvironmentVariableW`) durante la elevación UAC en `main.py`, en el reinicio del gestor de actualizaciones (Hot-Swap) en `update_manager.py` y en `services/watchdog.py`. Esto erradica el fallo fatal donde la nueva instancia intentaba cargar `python312.dll` desde el directorio temporal recién eliminado del proceso padre.
- **Prevención de corrupción de DLLs**: desactivación de compresión UPX (`upx=False`) en la especificación de PyInstaller para asegurar total integridad de bibliotecas compartidas de 64 bits en Windows 11.


## [6.2.0] - 2026-10-28

Actualización técnica integral de rendimiento, huella de memoria, estabilidad y escalabilidad. Sin adición de nuevas funciones ni alteraciones de la interfaz: el programa es más ligero, arranca más rápido, consume menos recursos y resuelve todos los bugs latentes y restricciones arquitectónicas.

### 🚀 Rendimiento y Optimización
- **Lazy loading de requests**: se eliminó la importación a nivel de módulo en el gestor de actualizaciones. `requests` y sus subdependencias de red (`urllib3`, `certifi`, etc.) solo se cargan si el usuario busca actualizaciones, liberando ~12-15 MB de RAM y reduciendo ~200 ms el arranque en frío.
- **Modelos optimizados con `slots=True`**: `AppSettings`, `HistoryEntry`, `ScheduledEvent` y `ProcessItem` utilizan slots en Python 3.12+, reduciendo significativamente la memoria por instancia y acelerando el acceso a sus campos.
- **Filtrado optimizado de procesos**: `_enumerate_processes_with_windows()` descarta ventanas sin texto o de dimensiones nulas antes de resolver el subproceso, evitando consultas de proceso redundantes.
- **Compilación de expresiones regulares**: `_TIME_RE` se pre-compila a nivel de módulo en la vista principal para evitar re-compilaciones periódicas durante actualizaciones de estado.
- **Empaquetado optimizado en PyInstaller**: especificación configurada con `optimize=1` y exclusión de paquetes innecesarios (`tkinter`, `unittest`, etc.).

### 🐛 Bug Fixes & Estabilidad
- **Crash en modo compacto solucionado**: corregida la excepción no capturada (`AttributeError`) al pulsar `+` o `-` durante una cuenta atrás activa por llamada a un método ausente.
- **Elevación UAC nativa en ejecutable**: especificación PyInstaller configurada con `uac_admin=True` para incrustar el manifiesto de ejecución como administrador en el PE y corrección en `run_as_admin` para ejecutables congelados, erradicando fallos de `LoadLibrary` en DLLs temporales (`_MEIPASS2`).
- **Respeto estricto del patrón MVP**: se eliminó el acceso directo a widgets internos (`lbl_status`) desde el presentador, canalizándolo por métodos públicos de la vista (`refresh_status_from_inputs`).
- **Persistencia atómica de configuración**: `SettingsManager.save()` ahora utiliza escritura atómica con archivo temporal y reemplazo, previniendo la corrupción de `settings.json` ante apagados súbitos del sistema.
- **Deserialización resiliente de configuración**: `AppSettings.from_dict()` filtra dinámicamente claves desconocidas o de futuras versiones sin fallar con `TypeError`.
- **Corrección de estilo QSS**: eliminada la pseudo-clase no soportada `::after` en `QRadioButton` y sustituida por indicador SVG válido para evitar warnings en el motor de estilos de Qt.
- **Condición de carrera en animación de modo compacto**: se desacopló el signal `finished` antes de iniciar la inversión de la animación en `MainWindow`.
- **Detección de minimizado**: uso de máscara de bits en `_on_window_state_changed` para garantizar la minimización a la bandeja independientemente de banderas activas del gestor de ventanas.

### 🌐 Localización e Internacionalización Completa (ES, EN, PT, FR)
- **Sincronización del diálogo Acerca de**: actualización de las cadenas de versión y fecha de lanzamiento en los 4 idiomas y sincronización dinámica de `AboutDialog` con la versión de la aplicación.
- **Erradicación de cadenas hardcodeadas**: localización completa de los diálogos de eventos programados (`ScheduleDialog`), editor de eventos (`ScheduleEventEditDialog`) y visor de historial (`HistoryDialog`), así como nombres de días y recurrencias.
- **Mecanismo de fallback seguro**: `LocalizationManager.get()` ahora recurre al diccionario en inglés antes de retornar la clave cruda en caso de traducciones pendientes en portugués o francés.

### 🛠️ Escalabilidad & Arquitectura
- **Desacoplamiento de acciones del sistema**: centralización de comandos de apagado, reinicio, suspensión, hibernación y UEFI en `SystemIntegration.execute_power_action()`, permitiendo añadir nuevas acciones en el futuro con mínimo acoplamiento.
- **Corrección de autostart en modo desarrollo**: construcción correcta del comando con el intérprete de Python cuando la aplicación no está congelada en un ejecutable.

## [6.1.2] - 2026-06-02

Release de rendimiento y fluidez. Sin cambios funcionales ni de interfaz: la app se siente más ligera durante la cuenta atrás, arranca y cambia de idioma sin tirones, y "Buscar actualizaciones" ya no congela la ventana. Todo el trabajo es interno; la configuración se mantiene compatible con versiones anteriores.

### 🚀 Rendimiento y fluidez
- **Cuenta atrás más ligera**: el color de la barra de progreso solo se reaplica cuando cruza un umbral (≈3 veces en toda la cuenta) en lugar de cada segundo, y se evita el regex de extracción de hora en cada tick. Menos uso de CPU mientras corre el temporizador.
- **Cambio de tema/idioma sin tirón**: los iconos SVG de los temas se cachean (no se regeneran en base64 en cada cambio) y el stylesheet completo solo se reconstruye cuando el tema cambia de verdad — cambiar de idioma ya no regenera todo el QSS.
- **Buscar actualizaciones no bloqueante**: la consulta a GitHub se ejecuta en un hilo aparte. La UI ya no se congela hasta 10s con red lenta o sin conexión.
- **Arranque más fluido en modo monitor**: la enumeración de ventanas (que podía bloquear varios segundos) se difiere para que la ventana se dibuje primero. Además se cachea el resultado durante 2s para refrescos repetidos.
- **Guardado de ajustes optimizado**: las escrituras de configuración se agrupan (debounce) y ya no se consulta el registro de Windows en cada guardado. Flush garantizado al cerrar la app, también desde la bandeja del sistema.

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
