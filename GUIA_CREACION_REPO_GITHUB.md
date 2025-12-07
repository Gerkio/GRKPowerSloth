# Guía Paso a Paso: Configuración de GitHub para Actualizaciones OTA

Esta guía detalla cómo preparar tu entorno y tu repositorio para soportar el sistema de actualizaciones automáticas de GRK PowerSloth.

---

## 🚀 Fase 1: Preparación Local (Git debe estar instalado)

### 1. Inicializar el Repositorio
Abre una terminal en la carpeta del proyecto (`c:\Users\gerkio\Documents\CODE\GRK PowerSloth\GRKPowerSloth_py`) y ejecuta:

```bash
git init
```

### 2. Configurar "Ignorados" (.gitignore)
Es vital NO subir archivos basura, temporales o compilados. Crea un archivo llamado `.gitignore` en la raíz con este contenido:

```text
# Python
__pycache__/
*.py[cod]
*$py.class

# Entornos virtuales
venv/
env/
.env

# PyInstaller (Carpetas de compilación)
build/
dist/
*.spec

# IDEs
.vscode/
.idea/

# Logs y temporales
*.log
```

*(Si ya tienes archivos compilados, bórralos o asegúrate de que git los ignore)*

### 3. Guardar cambios (Commit)
Ejecuta estos comandos para guardar la versión actual como tu "base":

```bash
git add .
git commit -m "Versión Inicial v6.0.0 - GRK PowerSloth"
```

---

## ☁️ Fase 2: Configuración en GitHub

### 1. Crear el Repositorio
1.  Ve a [github.com/new](https://github.com/new).
2.  Nombre del repositorio: **`GRK_PowerSloth`** (o el nombre que prefieras, pero recuérdalo).
3.  Visibilidad: **Public** (comendado para facilitar la descarga sin autenticación compleja).
4.  No marques "Initialize with README", ni .gitignore, ni license (ya lo tenemos local).
5.  Click en **Create repository**.

### 2. Conectar tu PC con GitHub
En la pantalla siguiente, copia la URL (ej: `https://github.com/TU_USUARIO/GRK_PowerSloth.git`) y ejecuta en tu terminal:

```bash
# Reemplaza TU_USUARIO por tu nombre de usuario real de GitHub
git remote add origin https://github.com/TU_USUARIO/GRK_PowerSloth.git
git branch -M main
git push -u origin main
```

*(Te pedirá loguearte si es la primera vez)*

---

## 📦 Fase 3: Crear la Primera Release (CRÍTICO)

El sistema de actualizaciones buscará "Releases", no el código fuente.

1.  Ve a tu repositorio en GitHub.
2.  En la barra lateral derecha, busca **"Releases"** y dale click a **"Create a new release"**.
3.  **Choose a tag:** Escribe `v6.0.0` y selecciona "Create new tag".
4.  **Release title:** `Versión 6.0.0 - Lanzamiento Inicial`
5.  **Description:** Describe las novedades (ej: "Soporte multi-idioma, nuevos temas OTA, UI responsiva").
6.  **Attach binaries (IMPORTANTE):**
    *   Arrastra aquí tu archivo **`GRK_PowerSloth.exe`** que generaste (está en la carpeta `dist`).
    *   Este es el archivo que los usuarios descargarán.
7.  Click en **Publish release**.

---

## ✅ Resultado Final

Ahora tendrás una URL pública y estable que usaremos en el código Python para buscar actualizaciones:
`https://api.github.com/repos/TU_USUARIO/GRK_PowerSloth/releases/latest`
