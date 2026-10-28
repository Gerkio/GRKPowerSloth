# 🦥 GRK PowerSloth

**El programador de apagado definitivo para Windows.**  
Automatiza el apagado, reinicio o suspensión de tu PC basándose en tiempo o actividad de procesos. Ideal para dejar renderizando, descargando o compilando por la noche.

## ✨ Novedades en v6.2.0

Actualización técnica integral de rendimiento, huella de memoria, estabilidad y escalabilidad. Sin adición de nuevas funciones ni alteraciones de la interfaz: el programa es más ligero, arranca más rápido, consume menos recursos y resuelve bugs latentes y restricciones arquitectónicas.

*   **⚡ Modelos ultra-ligeros (`slots=True`):** Entidades de configuración, procesos, historial y calendario optimizadas en memoria para Python 3.12+.
*   **🚀 Carga perezosa (Lazy loading):** `requests` solo se carga bajo demanda al buscar actualizaciones, liberando 12-15 MB de RAM en frío y acelerando el arranque.
*   **🛡️ Persistencia atómica:** Guardado a prueba de cortes de energía en `settings.json` mediante escritura atómica con archivo temporal.
*   **🌍 Localización al 100%:** Diálogos de eventos, historial y panel Acerca de actualizados y localizados al 100% en Español, Inglés, Portugués y Francés.
*   **🐛 Bugfixes y estabilidad:** Solucionado el crash por `AttributeError` en botones +/- en modo compacto y elevación UAC nativa con manifiesto integrado en el ejecutable.

> Para el detalle completo de cambios, ver [`CHANGELOG.md`](CHANGELOG.md).

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
