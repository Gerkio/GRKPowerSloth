# 🦥 GRK PowerSloth

**El programador de apagado definitivo para Windows.**  
Automatiza el apagado, reinicio o suspensión de tu PC basándose en tiempo o actividad de procesos. Ideal para dejar renderizando, descargando o compilando por la noche.

## ✨ Novedades en v6.1.2

Versión de mantenimiento centrada en **robustez** y **consistencia de UI**. Sin cambios funcionales mayores; mismo comportamiento de cara al usuario, pero más resistente y pulida.

*   **🌍 Localización al 100%:** Los menús, el aviso de "ya en ejecución" y el diálogo de actualización ahora cambian de idioma sin dejar fragmentos en español. Temas Nordic / Dracula / Blood Moon e idiomas Português / Français se traducen al cambiar idioma.
*   **🛡️ Calendario más fiable:** Mejor manejo de eventos a fin de mes (día 31 en febrero, etc.), cambios de hora del sistema y DST. Sin doble disparo. Escritura atómica de eventos e historial.
*   **🔒 OTA más robusto:** Timeout en la descarga, validación de espacio en disco, cancelación limpia desde el botón cerrar, y rollback automático si falla el swap del `.exe`.
*   **⚙️ Iniciar con Windows:** Si mueves el `.exe` a otra carpeta tras habilitar autostart, la app lo detecta y desactiva la opción en vez de fallar al arrancar Windows.
*   **🐛 Bugfixes destacados:** Eliminado el bug del countdown que se reescribía con el valor del spinbox; animaciones del modo compacto sin slots colgando al alternar rápido; el `closeEvent` detiene todos los timers correctamente.

> Para el detalle completo de los 23 ítems de auditoría aplicados, ver [`CHANGELOG.md`](CHANGELOG.md).

## 🚀 Características Principales

*   **⏱️ Modos de Disparo Flexibles:**
    *   **Cuenta Regresiva:** "Apagar en 2 horas".
    *   **Hora Fija:** "Apagar a las 03:00 AM".
    *   **Monitor de Actividad:** "Apagar cuando termine de renderizar" o "Cuando la red esté inactiva".
*   **🎨 Temas Visuales Premium:** Nordic Night, Dracula, Blood Moon, Dark & Light y Alto Contraste.
*   **🌍 Multi-idioma:** Español, Inglés, Portugués, Francés.
*   **🚀 Auto-Update (OTA):** Actualizaciones automáticas desde la app.
*   **🔧 Herramientas Útiles:** Forzar cierre de apps y modo "Keep Awake".

## 📥 Descarga e Instalación

1.  Ve a la sección de **[Releases](https://github.com/Gerkio/GRKPowerSloth/releases)**.
2.  Descarga el archivo `GRK_PowerSloth.exe`.
3.  ¡Listo! Es portable, no requiere instalación.

## 🛠️ Tecnologías

*   **Lenguaje:** Python 3.12+
*   **GUI:** PyQt6 (Modern & Responsive UI)
*   **Sistema:** Windows API

---
*Desarrollado con ❤️ por **Gerkio***
