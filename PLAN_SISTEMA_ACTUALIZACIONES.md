# Plan de Implementación: Sistema de Actualizaciones Automáticas (OTA)
**Objetivo:** Permitir que la aplicación se actualice automáticamente descargando la última versión desde GitHub Releases, sin intervención manual compleja del usuario.

---

## 🏗 1. Arquitectura del Sistema

Utilizaremos **GitHub Releases** como nuestra "Fuente de la Verdad" y CDN (Content Delivery Network).

*   **Repositorio (Server):** Alojará el código y las "Releases" (versiones compiladas).
*   **Cliente (App):** Consultará periódicamente si hay una nueva "Release" en GitHub.
*   **Mecanismo de Actualización:** Estrategia de **"Renombrado en Caliente"** (Hot-Swap) compatible con Windows.

### Componentes Clave:
1.  **GitHub Repo:** Necesitas crear un repo (público o privado*) para el proyecto.
    *   *Nota: Si es privado, requerirá gestión de Tokens, lo cual es más complejo. Se asume repo PÚBLICO para distribución sencilla.*
2.  **Versioning Semántico:** Seguiremos el formato `vX.Y.Z` (ej: `v6.0.1`).
3.  **UpdateManager:** Un nuevo módulo en Python encargado de la lógica.

---

## 🔄 2. Flujo de Actualización (The "Update Dance")

Windows no permite sobrescribir un `.exe` mientras se está ejecutando, pero **SÍ permite renombrarlo**. Usaremos este truco:

1.  **Check:** La App consulta `api.github.com/repos/{usuario}/{repo}/releases/latest`.
2.  **Compare:** Compara `tag_name` (ej: `v6.1.0`) con la versión interna `v6.0.0`.
3.  **Download:** Si hay nueva versión, descarga el nuevo `GRK_PowerSloth.exe` en una carpeta temporal o al lado del actual con nombre `GRK_PowerSloth.new`.
4.  **Install (The Trick):**
    *   Renombrar el ejecutable actual `GRK_PowerSloth.exe` -> `GRK_PowerSloth.exe.old`.
    *   Renombrar la descarga `GRK_PowerSloth.new` -> `GRK_PowerSloth.exe`.
5.  **Restart:** La App se reinicia automáticamente lanzando el "nuevo" `.exe`.
6.  **Cleanup:** Al iniciar, la App detecta si existe un `.old` y intenta borrarlo.

---

## 💻 3. Implementación Técnica

### A. Preparación del Repositorio
1.  Crear repo en GitHub: `GRK_PowerSloth`.
2.  Subir el código.
3.  Crear una "Release" inicial con el tag `v6.0.0` y adjuntar el `GRK_PowerSloth.exe` actual.

### B. Módulo `UpdateManager` (Python)
Necesitaremos las librerías `requests` y `packaging`.

```python
class UpdateManager:
    # URL de la API de GitHub
    GITHUB_API_URL = "https://api.github.com/repos/{usuario}/{repo}/releases/latest"
    
    def check_for_updates(self, current_version):
        # 1. GET request al API
        # 2. Parsear JSON
        # 3. Comparar versiones
        return update_info # (url_descarga, version_nueva, changelog)
    
    def download_update(self, download_url, progress_callback):
        # Descargar archivo con stream para mostrar barra de progreso
        pass
        
    def apply_update(self):
        # Lógica de renombrado y reinicio
        pass
```

### C. Integración en UI
1.  **Botón "Buscar Actualizaciones":** En el menú "Ayuda".
2.  **Indicador Visual:** Un pequeño punto o icono si hay una actualización pendiente.
3.  **Diálogo de Progreso:** Una ventana modal que muestre la descarga y pida permiso para reiniciar.

---

## 🛡 4. Consideraciones de Seguridad y Robustez

1.  **Rate Limiting:** La API de GitHub tiene límites. No hacer la comprobación cada segundo. Hacerla una vez al iniciar la App o solo manual.
2.  **Validación de Integridad:** (Opcional pero recomendado) Verificar el hash SHA256 del archivo descargado si GitHub lo provee.
3.  **Fallbacks:** Si la descarga falla a la mitad, no romper el ejecutable actual (por eso descargamos a `.new` primero).
4.  **Permisos:** Asegurarse de que el usuario tenga permisos de escritura en la carpeta donde está el `.exe` (normalmente "Mis Documentos" o "AppData" está bien; "Program Files" requerirá Admin).

---

## 📅 5. Pasos a Seguir (Action Plan)

1.  [ ] **Crear Repo en GitHub** y subir la versión actual.
2.  [ ] **Implementar `UpdateManager.py`** con la lógica de consulta y descarga.
3.  [ ] **Crear `UpdateDialog.py`** para la interfaz visual de descarga.
4.  [ ] **Conectar** el botón en `MainWindow`.
5.  [ ] **Probar** el sistema simulando una versión nueva en GitHub.
