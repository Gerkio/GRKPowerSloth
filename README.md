# 🦥 GRK PowerSloth

**El programador de apagado definitivo para Windows.**  
Automatiza el apagado, reinicio o suspensión de tu PC basándose en tiempo o actividad de procesos. Ideal para dejar renderizando, descargando o compilando por la noche.

## ✨ Novedades en v6.1.2

Versión de **rendimiento y fluidez** (2 de junio de 2026). Sin cambios funcionales ni de interfaz: la app se siente más ligera y rápida, y la configuración sigue siendo compatible con versiones anteriores.

*   **🚀 Cuenta atrás más ligera:** El color de la barra de progreso solo se actualiza al cruzar un umbral, no cada segundo. Menos uso de CPU mientras corre el temporizador.
*   **🎨 Cambio de tema/idioma sin tirones:** Los iconos de los temas se cachean y el estilo completo solo se reconstruye cuando el tema cambia de verdad; cambiar de idioma ya no regenera toda la hoja de estilos.
*   **🔄 "Buscar actualizaciones" no bloqueante:** La consulta a GitHub corre en segundo plano. La ventana ya no se congela con red lenta o sin conexión.
*   **⚡ Arranque más fluido:** En modo monitor, la lista de procesos se carga sin retrasar el dibujado de la ventana, con caché breve para refrescos repetidos.
*   **💾 Guardado de ajustes optimizado:** Las escrituras de configuración se agrupan y se elimina una consulta al registro de Windows en cada guardado, con escritura garantizada al cerrar (también desde la bandeja).

> Para el detalle completo, ver [`CHANGELOG.md`](CHANGELOG.md).



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
