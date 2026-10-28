# 🦥 GRK PowerSloth

**El programador de apagado definitivo para Windows.**  
Automatiza el apagado, reinicio o suspensión de tu PC basándose en tiempo o actividad de procesos. Ideal para dejar renderizando, descargando o compilando por la noche.

## ✨ Novedades en v6.3.0

Actualización centrada en la **alta fidelidad del monitor de actividad** y **optimización del espacio de interfaz** (-15% más compacta).

*   **🌐 Al terminar descarga (Alta Fidelidad):** Detección inteligente de fin de descargas en navegadores, Steam y lanzadores mediante fusión de sensores (red global, I/O de disco de la familia de procesos y bloqueos de archivos `.crdownload`/`.part`), ignorando telemetría de fondo y contemplando la descompresión en disco.
*   **📐 Interfaz 15% más compacta:** Ancho estándar reducido de 480px a 408px, Mini Controller estilizado a 336x78px y erradicación del espacio muerto vertical de 550px.
*   **⚡ Soporte multi-proceso:** Detección de árboles de procesos para Chrome, Edge, Firefox, Steam y Epic Games sin requerir configuraciones complejas.
*   **🛡️ Estabilidad de ejecución portable:** Solución definitiva al error de carga de DLLs (`LoadLibrary` en `_MEIPASS`) al relanzar o actualizar la aplicación.
*   **🌍 Localización al 100%:** Términos, estados de telemetría en tiempo real y diálogos sincronizados en Español, Inglés, Portugués y Francés.

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
