# 🎯 Framework de Automatización UI - Aspen Mtell Alert Manager

Framework de automatización de pruebas UI para **Aspen Mtell Alert Manager** usando **Playwright** y **Python** con el patrón **Page Object Model (POM)**.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Arquitectura](#arquitectura)
- [Uso Básico](#uso-básico)
- [Documentación](#documentación)

---

## 🔧 Requisitos

- **Python**: 3.10 o superior
- **Playwright**: Última versión
- **pytest**: Para ejecutar tests

---

## 📦 Instalación

### 1. Clonar el repositorio

```powershell
git clone <url-del-repo>
cd MAMAutomation
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Instalar navegadores de Playwright

```powershell
playwright install chromium
```

### 5. Configurar variables de entorno

Copiar `.env.example` a `.env` y ajustar los valores:

```powershell
Copy-Item .env.example .env
```

Editar `.env` con tu configuración:

```env
BASE_URL=https://azqamtell06.qae.aspentech.com/Aspentech/AspenMtell/AlertManager/
HEADLESS=false
```

---

## 📁 Estructura del Proyecto

```
MAMAutomation/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuración centralizada
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py                # Sistema de logging
│   │
│   └── UI/
│       ├── __init__.py
│       ├── Components/
│       │   ├── __init__.py
│       │   ├── navbar_component.py      # Componente de navbar
│       │   ├── sidenav_component.py     # Componente de sidenav
│       │   └── issues_container_component.py  # Contenedor de issues
│       │
│       └── Pages/
│           ├── __init__.py
│           ├── base_page.py         # BasePage con métodos comunes
│           ├── login_page.py        # Login page
│           └── dashboard_page.py    # Dashboard page
│
├── tests/                           # Tests (por crear)
│   ├── __init__.py
│   └── conftest.py
│
├── logs/                            # Logs de ejecución
├── screenshots/                     # Screenshots de tests
├── .env                            # Variables de entorno (no versionar)
├── .env.example                    # Ejemplo de configuración
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuración

### Variables de Entorno (`.env`)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `BASE_URL` | URL de la aplicación | `https://azqamtell06...` |
| `DEFAULT_TIMEOUT` | Timeout por defecto (ms) | `30000` |
| `SHORT_TIMEOUT` | Timeout corto (ms) | `5000` |
| `LONG_TIMEOUT` | Timeout largo (ms) | `60000` |
| `NAVIGATION_TIMEOUT` | Timeout navegación (ms) | `45000` |
| `HEADLESS` | Ejecutar sin UI | `false` |
| `BROWSER_TYPE` | Tipo de navegador | `chromium` |
| `VIEWPORT_WIDTH` | Ancho del viewport | `1920` |
| `VIEWPORT_HEIGHT` | Alto del viewport | `1080` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

---

## 🏗️ Arquitectura

### BasePage

Clase base que proporciona métodos comunes para todos los Page Objects:

**Métodos principales:**
- `goto(path)` - Navegar a una URL
- `click(selector)` - Hacer clic en un elemento
- `fill(selector, value)` - Rellenar un campo
- `is_visible(selector)` - Verificar visibilidad
- `wait_for_selector(selector)` - Esperar elemento
- `screenshot(filename)` - Tomar captura

**Métodos basados en roles (get_by_role):**
- `click_button(name)` - Clic en botón por nombre
- `fill_textbox(name, value)` - Rellenar campo por label
- `click_link(name)` - Clic en link por texto

### Page Objects

#### LoginPage
- `navigate()` - Ir a la página de login
- `click_login()` - Hacer clic en botón de login
- `login()` - Proceso completo de login

#### DashboardPage
- `navigate()` - Ir al dashboard
- `click_menu_button()` - Abrir sidenav
- `get_sidenav_items()` - Obtener items del menú
- `click_sidenav_item(name)` - Navegar a una sección
- `get_issues_header_text()` - Obtener texto del header

### Componentes Reutilizables

#### NavbarComponent
- `click_menu()` - Abrir menú lateral
- `click_admin_tools()` - Abrir herramientas admin
- `click_help()` - Abrir ayuda
- `toggle_theme()` - Cambiar tema
- `click_profile_menu()` - Abrir perfil

#### SidenavComponent
- `is_open()` - Verificar si está abierto
- `close()` - Cerrar sidenav
- `get_all_items()` - Obtener todos los items
- `click_item(name)` - Click en item específico
- `click_dashboard()` - Ir a Dashboard
- `click_star_catch_report()` - Ir a STAR & Catch Report

#### IssuesContainerComponent
- `get_header_title()` - Obtener título
- `click_date_filter()` - Abrir filtro de fecha
- `click_type_filter()` - Abrir filtro de tipo
- `is_date_filter_visible()` - Verificar filtro

---

## 🚀 Uso Básico

### Ejemplo 1: Login Simple

```python
from playwright.sync_api import sync_playwright
from src.UI.Pages.login_page import LoginPage

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Login
    login_page = LoginPage(page)
    login_page.login()
    
    # Verificar que estamos en el dashboard
    assert "#/dashboard" in page.url
    
    browser.close()
```

### Ejemplo 2: Navegar en el Dashboard

```python
from playwright.sync_api import sync_playwright
from src.UI.Pages.login_page import LoginPage
from src.UI.Pages.dashboard_page import DashboardPage

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Login
    LoginPage(page).login()
    
    # Dashboard
    dashboard = DashboardPage(page)
    
    # Abrir sidenav
    dashboard.click_menu_button()
    
    # Obtener items
    items = dashboard.get_sidenav_items()
    print(f"Items del menú: {items}")
    
    # Navegar a otra sección
    dashboard.click_sidenav_item("STAR & Catch Report")
    
    browser.close()
```

### Ejemplo 3: Usar Componentes

```python
from playwright.sync_api import sync_playwright
from src.UI.Pages.login_page import LoginPage
from src.UI.Components.navbar_component import NavbarComponent
from src.UI.Components.sidenav_component import SidenavComponent

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Login
    LoginPage(page).login()
    
    # Usar componentes
    navbar = NavbarComponent(page)
    sidenav = SidenavComponent(page)
    
    # Abrir menú
    navbar.click_menu()
    
    # Verificar items
    assert sidenav.is_open()
    print(f"Item seleccionado: {sidenav.get_selected_item()}")
    
    # Navegar
    sidenav.click_star_catch_report()
    
    browser.close()
```

---


## 🔍 Hallazgos de la Exploración

### Tecnologías Detectadas
- **Framework**: Angular 19.2.13
- **UI Library**: Angular Material
- **Componentes**: mat-sidenav, mat-icon, mat-form-field

### Selectores Identificados

**Navbar:**
- `#menu-btn` - Botón de menú
- `[data-testid='admin-tool-button']` - Herramientas admin
- `[data-testid='help-button']` - Ayuda
- `[data-testid='toggle-theme-button']` - Toggle tema
- `[data-testid='profile-menu']` - Menú perfil

**Sidenav:**
- `.sidenav-item` - Items del menú
- `.sidenav-item--selected` - Item seleccionado

**Dashboard:**
- `.alerts-header__title h2` - Título de issues
- Filtros: Date, Type, Sort By, Status, Assigned To

### Flujo de Navegación
1. Login (botón simple `#loginbutton`)
2. Dashboard principal con sidenav
3. Opciones: Dashboard, STAR & Catch Report, Alert Impact Quantification

---

## ✅ Mejores Prácticas

### 1. Auto-Waiting
Playwright espera automáticamente, no usar `time.sleep()`:

```python
# ✅ BIEN
page.click("#button")

# ❌ MAL
time.sleep(2)
page.click("#button")
```

### 2. Preferir get_by_role()
Usar selectores semánticos cuando sea posible:

```python
# ✅ MEJOR
page.get_by_role("button", name="Log In").click()

# ⚠️ ACEPTABLE
page.click("#loginbutton")
```

### 3. Timeouts Apropiados
- **Navegación**: 45-60s (Angular puede tardar)
- **Acciones**: 30s (default)
- **Validaciones**: 5s (short timeout)

### 4. Logging
Todas las acciones importantes se loggean automáticamente.

---

## 🐛 Troubleshooting

### Error: "No .env file found"
Crear `.env` copiando `.env.example`:
```powershell
Copy-Item .env.example .env
```

### Error: "BASE_URL not configured"
Verificar que `.env` tenga `BASE_URL` configurada.

### Tests lentos
- Usar `HEADLESS=true` para CI/CD
- Ajustar timeouts en `.env`

---

## 📝 TODOs

- [ ] Crear tests iniciales en `tests/`
- [ ] Configurar pytest fixtures en `conftest.py`
- [ ] Implementar autenticación con Storage State
- [ ] Agregar más componentes según necesidad
- [ ] Configurar CI/CD pipeline

---

## 👤 Autor

Framework desarrollado para el proyecto MAMAutomation.

---

## 📄 Licencia

[Especificar licencia]
