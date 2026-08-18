# 🎯 Guía Práctica: Framework de Automatización para Aspen Mtell Alert Manager

## 📋 Tabla de Contenidos
1. [Análisis de la Aplicación](#análisis-de-la-aplicación)
2. [🔐 Autenticación: Evitar Login Repetido](#-autenticación-evitar-login-repetido-en-cada-test) ⭐ **NUEVO**
   - [El Problema](#el-problema)
   - [Solución: Storage State](#la-solución-playwright-storage-state-)
   - [Implementación](#implementación-paso-a-paso)
   - [Uso en Tests](#cómo-usar-en-tests)
   - [Manejo de Expiración](#qué-pasa-si-el-login-expira)
3. [⚡ Mejores Prácticas de Playwright](#mejores-prácticas-de-playwright-para-este-proyecto) ⭐
   - [URLs Dinámicas](#1-manejo-de-urls-dinámicas)
   - [Timeouts y Esperas](#2-estrategia-de-timeouts-y-esperas)
   - [get_by_role() vs CSS](#3-estrategia-de-selectores-get_by_role-vs-css)
   - [DO's y DON'Ts](#4-mejores-prácticas-iniciales-para-el-proyecto)
   - [Checklist Primera Semana](#5-checklist-para-empezar-primera-semana)
4. [Estructura del Framework](#estructura-del-framework)
5. [BasePage Implementada](#basepage-implementada)
6. [Page Objects Identificados](#page-objects-identificados)
7. [Componentes Reutilizables](#componentes-reutilizables)
8. [Fixtures y Configuración](#fixtures-y-configuración)
9. [Ejemplos de Tests](#ejemplos-de-tests)
10. [Roadmap de Implementación](#roadmap-de-implementación)

---

## 🔍 Análisis de la Aplicación

### Aplicación: Aspen Mtell Alert Manager
**URL:** `https://azqamtell06.qae.aspentech.com/Aspentech/AspenMtell/AlertManager/`

### Flujo Principal Identificado

```
1. Login Page (Simple)
   └─> Click en botón "Log In"
       └─> Dashboard (Main Page)
           ├─> Sidebar Navigation (Left Menu)
           ├─> Top Navigation Bar (Navbar)
           ├─> Issues Container (Main Content)
           └─> Filtros y Controles
```

### 📸 Capturas de Pantalla de la Exploración

Las capturas realizadas muestran:
1. **Login Page:** Página simple con un botón "Log In"
2. **Dashboard:** Página principal con múltiples componentes complejos
3. **Sidenav Abierto:** Menú lateral con opciones de navegación

---

## 🔐 Autenticación: Evitar Login Repetido en Cada Test

### El Problema

Cada ejecución de Playwright crea una **nueva sesión limpia** (sin cookies, sin localStorage). Si tu aplicación requiere login, hacer el login en cada test es:

- ❌ **Lento**: 5-10 segundos por test × 50 tests = 4-8 minutos desperdiciados
- ❌ **Frágil**: Más puntos de falla (si login falla, todo falla)
- ❌ **Repetitivo**: Viola DRY (Don't Repeat Yourself)

### La Solución: Playwright Storage State 🎯

Playwright puede **guardar el estado de autenticación** (cookies, localStorage, sessionStorage) después del login y **reutilizarlo** en todos los tests:

1. Hacer login **UNA VEZ** al inicio de toda la suite
2. Guardar el estado en un archivo `.json`
3. Todos los demás tests cargan ese estado → **ya están autenticados**

---

### Implementación Paso a Paso

#### 1️⃣ Estructura de Carpetas

```
tests/
├── auth/
│   ├── __init__.py
│   └── test_login.py              # Tests específicos de login
├── functional/
│   ├── __init__.py
│   ├── test_dashboard.py          # Tests que requieren estar logueado
│   └── test_issues.py
├── .auth/
│   └── user.json                  # Estado de autenticación guardado (gitignore!)
├── conftest.py                    # Fixtures principales
└── pytest.ini
```

#### 2️⃣ Global Setup: Hacer Login Una Vez

Crea `tests/global_setup.py`:

```python
"""
Global setup: ejecuta el login UNA VEZ antes de toda la suite de tests.
Guarda el estado de autenticación para reutilizarlo.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
from config.settings import settings

def global_setup():
    """Realiza el login y guarda el estado de autenticación."""
    
    # Crear directorio para auth state si no existe
    auth_dir = Path("tests/.auth")
    auth_dir.mkdir(parents=True, exist_ok=True)
    auth_file = auth_dir / "user.json"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True en CI
        context = browser.new_context()
        page = context.new_page()
        
        # Navegar y hacer login
        print(f"🔐 Iniciando login en {settings.BASE_URL}...")
        page.goto(settings.BASE_URL, wait_until="networkidle")
        
        # Click en botón de login (SSO)
        page.locator("#loginbutton").click()
        
        # Esperar a que el login se complete (verificar elemento del dashboard)
        page.wait_for_selector("#menu-btn", timeout=60000)
        print("✅ Login exitoso!")
        
        # GUARDAR EL ESTADO (cookies, localStorage, sessionStorage)
        context.storage_state(path=str(auth_file))
        print(f"💾 Estado guardado en {auth_file}")
        
        browser.close()

if __name__ == "__main__":
    global_setup()
```

**Agregar a `.gitignore`:**
```
tests/.auth/
*.json
```

#### 3️⃣ Configurar pytest para Usar Global Setup

En `pytest.ini`:

```ini
[pytest]
# Ejecutar global_setup.py ANTES de todos los tests
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    smoke: Smoke tests (subset crítico)
    regression: Regression tests (suite completa)
    login: Tests específicos de funcionalidad de login
    authenticated: Tests que requieren usuario autenticado (default)

# Opciones
addopts = 
    -v
    --tb=short
    --strict-markers
    -p no:warnings
```

Crear archivo `pytest_plugins.py` en la raíz:

```python
"""Configuración de pytest plugins."""

def pytest_configure(config):
    """Hook que se ejecuta ANTES de recolectar tests."""
    # Ejecutar global setup si no existe el archivo de auth
    from pathlib import Path
    auth_file = Path("tests/.auth/user.json")
    
    if not auth_file.exists():
        print("\n🔐 No se encontró archivo de autenticación. Ejecutando global setup...")
        from tests.global_setup import global_setup
        global_setup()
    else:
        print(f"\n✅ Usando autenticación existente: {auth_file}")
```

#### 4️⃣ Fixture Actualizado en `conftest.py`

```python
"""Fixtures principales del framework."""
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from pathlib import Path
from config.settings import settings

@pytest.fixture(scope="session")
def browser() -> Browser:
    """Browser compartido para toda la sesión de tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=settings.HEADLESS,
            slow_mo=settings.SLOW_MO
        )
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context_authenticated(browser: Browser) -> BrowserContext:
    """
    Context con autenticación pre-cargada.
    Usa el storage state guardado por global_setup.
    """
    auth_file = Path("tests/.auth/user.json")
    
    if not auth_file.exists():
        pytest.fail(
            "❌ Archivo de autenticación no encontrado. "
            "Ejecuta: python tests/global_setup.py"
        )
    
    # Crear contexto CARGANDO el estado de autenticación
    context = browser.new_context(
        storage_state=str(auth_file),  # 🎯 CLAVE: cargar cookies/localStorage
        viewport={"width": 1920, "height": 1080}
    )
    
    yield context
    context.close()

@pytest.fixture(scope="function")
def context_clean(browser: Browser) -> BrowserContext:
    """
    Context LIMPIO sin autenticación.
    Usar solo para tests de login.
    """
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page_authenticated(context_authenticated: BrowserContext) -> Page:
    """
    Page con autenticación pre-cargada.
    Usar en TODOS los tests funcionales (99% de casos).
    """
    page = context_authenticated.new_page()
    yield page
    page.close()

@pytest.fixture(scope="function")
def page_clean(context_clean: BrowserContext) -> Page:
    """
    Page limpia sin autenticación.
    Usar SOLO en tests de login.
    """
    page = context_clean.new_page()
    yield page
    page.close()
```

---

### Cómo Usar en Tests

#### ✅ Tests Funcionales (99% de casos)

```python
"""tests/functional/test_dashboard.py"""
import pytest
from pages.dashboard_page import DashboardPage

@pytest.mark.authenticated
def test_dashboard_displays_issues_count(page_authenticated):
    """Verificar que el dashboard muestra el conteo de issues."""
    # Given: Usuario ya autenticado (gracias a page_authenticated)
    dashboard = DashboardPage(page_authenticated)
    
    # When: Navegar al dashboard
    dashboard.navigate()
    
    # Then: Verificar elementos visibles
    assert dashboard.is_issues_container_visible()
    assert dashboard.get_open_issues_count() > 0
```

**Sin login manual** → La page ya tiene las cookies cargadas → Ya está autenticado ✅

#### ✅ Tests de Login (casos especiales)

```python
"""tests/auth/test_login.py"""
import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@pytest.mark.login
def test_login_button_redirects_to_sso(page_clean):
    """Verificar que el botón de login redirige a SSO."""
    # Given: Usuario NO autenticado (page_clean)
    login_page = LoginPage(page_clean)
    
    # When: Navegar a la app
    login_page.navigate()
    
    # Then: Botón de login visible
    assert login_page.is_login_button_visible()

@pytest.mark.login
def test_successful_login_redirects_to_dashboard(page_clean):
    """Verificar que login exitoso redirige al dashboard."""
    # Given: Usuario en página de login
    login_page = LoginPage(page_clean)
    login_page.navigate()
    
    # When: Hacer login
    login_page.click_login_button()
    
    # Then: Redirige al dashboard
    dashboard = DashboardPage(page_clean)
    dashboard.wait_for_page_load()
    assert dashboard.is_navbar_visible()
```

---

### Separación de Tests: Login vs Funcionales

#### `tests/auth/test_login.py`
- Usa `page_clean` (sin autenticación)
- Tests de UI del login
- Tests de flujo de autenticación
- Tests de logout
- **Marker**: `@pytest.mark.login`

#### `tests/functional/test_*.py`
- Usa `page_authenticated` (con autenticación)
- Todos los tests de funcionalidad
- Asumen que usuario ya está logueado
- **Marker**: `@pytest.mark.authenticated`

---

### Comandos para Ejecutar

```powershell
# 1. Generar autenticación manualmente (si es necesario)
python tests/global_setup.py

# 2. Ejecutar solo tests de login (sin auth previa)
pytest -m login

# 3. Ejecutar tests funcionales (con auth precargada)
pytest -m authenticated

# 4. Ejecutar TODA la suite
pytest

# 5. Regenerar autenticación (si expiró)
Remove-Item tests\.auth\user.json
pytest  # Se regenera automáticamente
```

---

### Manejo en Page Objects

Las pages **NO necesitan saber sobre autenticación**:

```python
"""pages/dashboard_page.py"""
from pages.base_page import BasePage

class DashboardPage(BasePage):
    """Page Object para Dashboard (asume usuario autenticado)."""
    
    def __init__(self, page):
        super().__init__(page)
        # NO hay código de login aquí
        # La page ya tiene las cookies cargadas
    
    def navigate(self):
        """Navegar al dashboard."""
        self.goto("/AlertManager/#/dashboard")  # Directo al dashboard
        self.wait_for_network_idle()
        return self
    
    def is_navbar_visible(self) -> bool:
        """Verificar que navbar está visible (confirma autenticación)."""
        return self.is_visible("#menu-btn", timeout=5000)
```

**Ventaja**: Las pages son más simples y enfocadas en su funcionalidad.

---

### ¿Qué Pasa si el Login Expira?

```python
"""tests/conftest.py - Manejo de expiración"""

@pytest.fixture(scope="function", autouse=True)
def handle_auth_expiration(page_authenticated):
    """
    Hook que verifica si la autenticación sigue válida.
    Si detecta página de login, regenera el storage state.
    """
    yield page_authenticated
    
    # Después del test, verificar si apareció página de login
    if page_authenticated.locator("#loginbutton").is_visible():
        print("⚠️ Sesión expirada detectada. Regenerando autenticación...")
        from tests.global_setup import global_setup
        global_setup()
        pytest.exit("Autenticación regenerada. Por favor, re-ejecutar tests.")
```

---

### Comparación: Con vs Sin Storage State

| Aspecto | ❌ Login en cada test | ✅ Storage State |
|---------|---------------------|-----------------|
| **Tiempo** | 10s × 50 tests = 8 min | 10s + (0.5s × 50) = 35s |
| **Complejidad** | Login en cada test | Login una vez |
| **Mantenimiento** | Si login cambia, actualizar 50 tests | Si login cambia, actualizar 1 archivo |
| **Fragilidad** | 50 puntos de falla | 1 punto de falla |
| **CI/CD** | Lento | Rápido |

---

### Checklist de Implementación

- [ ] Crear `tests/.auth/` y agregarlo a `.gitignore`
- [ ] Crear `tests/global_setup.py` con lógica de login
- [ ] Agregar `pytest_plugins.py` para auto-setup
- [ ] Actualizar `conftest.py` con fixtures `page_authenticated` y `page_clean`
- [ ] Separar tests: `tests/auth/` (login) vs `tests/functional/` (resto)
- [ ] Agregar markers: `@pytest.mark.login` y `@pytest.mark.authenticated`
- [ ] Actualizar pages para NO incluir lógica de login
- [ ] Probar con `pytest -m authenticated`
- [ ] Documentar en README cómo regenerar auth

---

## ⚡ Mejores Prácticas de Playwright para Este Proyecto

### 🌐 1. Manejo de URLs Dinámicas

Ya que la URL cambia según el servidor/máquina, **nunca** la hardcodees en el código:

#### ❌ NO HACER:
```python
# Malo - URL hardcodeada
def goto(self, path: str):
    self.page.goto("https://azqamtell06.qae.aspentech.com/Aspentech/AspenMtell/AlertManager/" + path)
```

#### ✅ HACER:
```python
# Bueno - URL desde configuración
# .env
BASE_URL=https://nombre-servidor.dominio.com/Aspentech/AspenMtell/AlertManager/

# settings.py
class Settings:
    BASE_URL = os.getenv("BASE_URL")
    if not BASE_URL:
        raise ValueError("BASE_URL no está configurada en .env")

# base_page.py
def goto(self, path: str = "") -> 'BasePage':
    if path.startswith("http"):
        url = path  # URL completa proporcionada
    else:
        url = f"{self.base_url}{path}"
    
    self.page.goto(url, wait_until="networkidle")
    return self
```

#### 📋 Archivo .env.example (para documentar)
```bash
# .env.example - Copiar a .env y configurar
BASE_URL=https://tu-servidor.dominio.com/Aspentech/AspenMtell/AlertManager/
DEFAULT_TIMEOUT=30000
HEADLESS=false
```

---

### ⏱️ 2. Estrategia de Timeouts y Esperas

#### La Jerarquía de Esperas en Playwright

Playwright tiene 3 niveles de timeouts:

```python
# 1. Timeout GLOBAL del test (pytest.ini)
[pytest]
timeout = 300  # 5 minutos para todo el test

# 2. Timeout DEFAULT de Playwright (por página)
page.set_default_timeout(30000)  # 30 segundos para todas las acciones

# 3. Timeout ESPECÍFICO por acción
page.locator("#button").click(timeout=5000)  # 5 segundos solo para este click
```

#### ✅ Configuración Recomendada para Aspen Mtell

```python
# src/config/settings.py
class Settings:
    # Timeouts en milisegundos
    DEFAULT_TIMEOUT = 30000      # 30s - Acciones normales
    SHORT_TIMEOUT = 5000         # 5s  - Validaciones rápidas (is_visible)
    LONG_TIMEOUT = 60000         # 60s - Operaciones pesadas (carga inicial)
    NAVIGATION_TIMEOUT = 45000   # 45s - Navegaciones (Angular tarda)
```

```python
# src/ui/pages/base_page.py
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.settings = Settings()
        # Configurar timeout default al crear la página
        self.page.set_default_timeout(self.settings.DEFAULT_TIMEOUT)
```

#### Cuándo Usar Cada Timeout

| Acción | Timeout Recomendado | Razón |
|--------|-------------------|-------|
| `click()`, `fill()`, `select_option()` | **DEFAULT (30s)** | Auto-waiting suficiente |
| `is_visible()`, `is_hidden()` | **SHORT (5s)** | Validación rápida, no bloquear |
| `goto()`, navegaciones | **LONG (45-60s)** | Angular + red pueden tardar |
| `wait_for_load_state("networkidle")` | **LONG (60s)** | Esperar todas las requests |
| Operaciones de filtrado | **DEFAULT (30s)** | Componentes Material |

#### 🚨 Auto-Waiting de Playwright (¡Úsalo!)

Playwright **automáticamente espera** antes de cada acción:

```python
# ✅ ESTO ES SUFICIENTE - No necesitas wait extra
page.locator("#loginbutton").click()
# Playwright espera automáticamente:
# - Que el elemento exista
# - Que sea visible
# - Que esté habilitado
# - Que no esté animando
# - Que no esté cubierto por otro elemento

# ❌ NO HACER ESTO (redundante)
page.locator("#loginbutton").wait_for(state="visible")  # ❌ Innecesario
page.locator("#loginbutton").click()
```

#### Cuándo SÍ Necesitas Esperas Explícitas

```python
# ✅ 1. Esperar que algo DESAPAREZCA
page.locator(".loading-spinner").wait_for(state="hidden", timeout=10000)

# ✅ 2. Esperar estado de carga de página (Angular)
page.wait_for_load_state("networkidle")  # Espera que no haya requests pendientes

# ✅ 3. Esperar cambio de URL
page.wait_for_url("**/dashboard")

# ✅ 4. Esperar respuesta de API específica
with page.expect_response("**/api/alerts") as response_info:
    page.click("#refresh-button")
response = response_info.value
```

#### Ejemplo Real para Aspen Mtell

```python
# src/ui/pages/login_page.py
def click_login(self):
    """Hace login con esperas apropiadas."""
    # Auto-waiting se encarga del click
    self.click(self._login_button)
    
    # Espera EXPLÍCITA necesaria porque Angular tarda
    self.wait_for_load_state("networkidle")
    
    # Validar que realmente cargó
    self.wait_for_element(".dashboard", timeout=self.settings.LONG_TIMEOUT)
    
    from src.ui.pages.dashboard_page import DashboardPage
    return DashboardPage(self.page)
```

---

### 🎯 3. Estrategia de Selectores: get_by_role() vs CSS

#### Jerarquía de Selectores Recomendada

| Prioridad | Método | Cuándo Usar | Ejemplo |
|-----------|--------|------------|---------|
| 🥇 **1** | `get_by_role()` | **Siempre que sea posible** | Semántico, accesible, estable |
| 🥈 **2** | `get_by_label()` | Inputs con labels | Robusto para forms |
| 🥉 **3** | `get_by_test_id()` | Cuando existe data-testid | Explícito para testing |
| 4️⃣ **4** | `locator()` con CSS específico | Cuando lo anterior no aplica | Más frágil |

#### 🥇 get_by_role() - Tu Primera Opción

**Ventajas:**
- ✅ Semántico - expresa intención
- ✅ Robusto ante cambios de CSS/estructura
- ✅ Mejora accesibilidad automáticamente
- ✅ Playwright espera mejor

```python
# ✅ MEJOR: Usa get_by_role()
page.get_by_role("button", name="Log In").click()
page.get_by_role("textbox", name="Email").fill("test@example.com")
page.get_by_role("navigation").get_by_role("button", name="Menu").click()

# ❌ PEOR: CSS selector
page.locator("#loginbutton").click()
page.locator("input[name='email']").fill("test@example.com")
```

#### Roles Comunes en Aspen Mtell

```python
# Botones
page.get_by_role("button", name="Log In")
page.get_by_role("button", name="Submit")

# Navegación
page.get_by_role("navigation")  # <nav>
page.get_by_role("menu")        # Menús

# Inputs
page.get_by_role("textbox", name="Email")      # <input type="text">
page.get_by_role("checkbox", name="Remember")  # <input type="checkbox">

# Headings
page.get_by_role("heading", name="Alert Manager")

# Links
page.get_by_role("link", name="Forgot Password")
```

#### 🎯 Estrategia Práctica para Aspen Mtell

```python
# src/ui/pages/base_page.py
class BasePage:
    """BasePage con métodos para ambos enfoques."""
    
    # Método 1: get_by_role() - Preferido
    def click_button(self, name: str, timeout: Optional[int] = None) -> 'BasePage':
        """Click en botón por su nombre visible."""
        timeout = timeout or self.timeout
        self.page.get_by_role("button", name=name).click(timeout=timeout)
        return self
    
    def fill_textbox(self, name: str, text: str) -> 'BasePage':
        """Llena textbox por su label."""
        self.page.get_by_role("textbox", name=name).fill(text)
        return self
    
    # Método 2: CSS selector - Cuando get_by_role() no funciona
    def click(self, selector: str, timeout: Optional[int] = None) -> 'BasePage':
        """Click usando CSS selector (fallback)."""
        timeout = timeout or self.timeout
        self.page.locator(selector).click(timeout=timeout)
        return self
```

#### Cuándo Usar CSS Selectors (locator)

```python
# ✅ Usar CSS cuando:
# 1. No hay role apropiado
page.locator(".loading-spinner").wait_for(state="hidden")

# 2. Necesitas scope específico
page.locator(".dashboard").locator(".issues-container")

# 3. data-testid está disponible
page.locator("[data-testid='admin-tool-button']").click()

# 4. Múltiples elementos del mismo tipo
page.locator(".sidenav-item").nth(1).click()
```

#### Refactorización de LoginPage con get_by_role()

```python
# src/ui/pages/login_page.py - VERSIÓN MEJORADA
class LoginPage(BasePage):
    """Login page con selectores robustos."""
    
    # Mantener CSS como fallback si get_by_role() falla
    _login_button_css = "#loginbutton"
    
    def click_login(self):
        """Hace login usando método más robusto."""
        self.logger.info("Haciendo login...")
        
        # Intenta con get_by_role() primero
        try:
            self.page.get_by_role("button", name="Log In").click()
        except:
            # Fallback a CSS selector
            self.logger.warning("get_by_role() falló, usando CSS selector")
            self.click(self._login_button_css)
        
        self.wait_for_load_state("networkidle")
        
        from src.ui.pages.dashboard_page import DashboardPage
        return DashboardPage(self.page)
```

---

### 🛠️ 4. Mejores Prácticas Iniciales para el Proyecto

#### ✅ DO's (Hacer)

```python
# 1. ✅ Usa auto-waiting de Playwright
page.get_by_role("button", name="Submit").click()  # No necesitas wait previo

# 2. ✅ Valida URLs dinámicamente
assert "/dashboard" in page.url
assert page.url.endswith("/dashboard")

# 3. ✅ Espera networkidle después de navegaciones
page.goto(url, wait_until="networkidle")

# 4. ✅ Usa timeouts cortos para validaciones
def is_visible(self, selector: str, timeout: int = 5000):
    # 5s es suficiente para saber si algo está visible

# 5. ✅ Scope selectores cuando sea necesario
navbar = page.locator("nav.navbar")
navbar.get_by_role("button", name="Menu").click()

# 6. ✅ Log todas las acciones importantes
self.logger.info(f"Navegando a: {url}")
self.logger.debug(f"Click en: {selector}")

# 7. ✅ Configura timeouts por tipo de acción
self.page.set_default_timeout(30000)  # Default 30s

# 8. ✅ Usa type hints
def click(self, selector: str, timeout: Optional[int] = None) -> 'BasePage':

# 9. ✅ Method chaining para fluidez
login_page.navigate().click_login()

# 10. ✅ Tests descriptivos con Given/When/Then
def test_login_successful(self, login_page):
    """
    Given: Usuario en login page
    When: Click en Log In
    Then: Dashboard carga correctamente
    """
```

#### ❌ DON'Ts (No Hacer)

```python
# 1. ❌ NUNCA uses time.sleep()
import time
time.sleep(3)  # ❌ MAL

# 2. ❌ No hardcodees URLs
page.goto("https://server123.com/app")  # ❌ MAL

# 3. ❌ No uses esperas redundantes
page.locator("#button").wait_for(state="visible")  # ❌ Innecesario
page.locator("#button").click()  # Ya espera automáticamente

# 4. ❌ No uses selectores frágiles
page.locator("div > div > button:nth-child(2)")  # ❌ Muy frágil

# 5. ❌ No captures excepciones sin log
try:
    page.click("#button")
except:
    pass  # ❌ Silenciar errores oculta problemas

# 6. ❌ No uses timeouts muy largos por default
page.set_default_timeout(120000)  # ❌ 2 minutos es excesivo

# 7. ❌ No valides con == True/False
assert page.is_visible("#button") == True  # ❌ Redundante
assert page.is_visible("#button")          # ✅ Mejor

# 8. ❌ No uses múltiples assertions en una línea
assert page.is_visible("#a") and page.is_visible("#b")  # ❌ Mal
# ✅ Mejor:
assert page.is_visible("#a"), "Elemento A no visible"
assert page.is_visible("#b"), "Elemento B no visible"
```

---

### 📋 5. Checklist para Empezar (Primera Semana)

- [ ] **Configuración de Ambiente**
  - [ ] Crear `.env` con BASE_URL de tu servidor local
  - [ ] Configurar timeouts en `settings.py`
  - [ ] Verificar que Playwright está instalado (`playwright install`)

- [ ] **BasePage Inicial**
  - [ ] Implementar métodos básicos: `goto()`, `click()`, `fill()`
  - [ ] Agregar `click_button()` y `fill_textbox()` con get_by_role()
  - [ ] Configurar logging
  - [ ] Probar con un test simple

- [ ] **LoginPage**
  - [ ] Usar get_by_role() para botón "Log In"
  - [ ] Agregar espera explícita: `wait_for_load_state("networkidle")`
  - [ ] Validar redirección al dashboard

- [ ] **Primer Test Smoke**
  - [ ] Test que valide login exitoso
  - [ ] Configurar screenshot en falla
  - [ ] Ejecutar en modo visible (`headless=false`) para ver qué pasa

- [ ] **Validación**
  - [ ] El test corre sin `time.sleep()`
  - [ ] URL viene de `.env`
  - [ ] Timeouts configurados apropiadamente
  - [ ] Logs generados correctamente

---

### 🔧 6. Código Starter Recomendado

#### Archivo: `.env`
```bash
# Configuración del ambiente local
BASE_URL=http://tu-servidor-local:8080/Aspentech/AspenMtell/AlertManager/
DEFAULT_TIMEOUT=30000
SHORT_TIMEOUT=5000
LONG_TIMEOUT=60000
HEADLESS=false
LOG_LEVEL=DEBUG
```

#### Archivo: `src/config/settings.py` (Mejorado)
```python
"""Configuración centralizada."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Settings de la aplicación."""
    
    # URLs - NUNCA hardcodear
    BASE_URL = os.getenv("BASE_URL")
    if not BASE_URL:
        raise ValueError(
            "BASE_URL no está configurada. "
            "Crea un archivo .env con BASE_URL=http://tu-servidor/..."
        )
    
    # Timeouts en milisegundos
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", "5000"))
    LONG_TIMEOUT = int(os.getenv("LONG_TIMEOUT", "60000"))
    
    # Browser
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    BROWSER = os.getenv("BROWSER", "chromium")
    
    # Logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Valida que la configuración sea correcta."""
        if not cls.BASE_URL.startswith("http"):
            raise ValueError("BASE_URL debe empezar con http:// o https://")
        
        print(f"✅ Configuración cargada:")
        print(f"   BASE_URL: {cls.BASE_URL}")
        print(f"   TIMEOUTS: {cls.SHORT_TIMEOUT}/{cls.DEFAULT_TIMEOUT}/{cls.LONG_TIMEOUT}ms")
        print(f"   HEADLESS: {cls.HEADLESS}")

# Validar al importar
Settings.validate()
```

#### Test de Validación Inicial

```python
# tests/ui/test_smoke_initial.py
"""Test inicial para validar configuración."""
import pytest
from src.config.settings import Settings

def test_configuration_loaded():
    """Valida que la configuración se cargue correctamente."""
    assert Settings.BASE_URL is not None
    assert Settings.BASE_URL.startswith("http")
    assert Settings.DEFAULT_TIMEOUT > 0

@pytest.mark.smoke
def test_browser_opens(page):
    """Valida que el browser se abre correctamente."""
    page.goto(Settings.BASE_URL)
    assert page.title()  # Debe tener un título
    
def test_login_page_loads(page):
    """Valida que la página de login carga."""
    page.goto(Settings.BASE_URL)
    page.wait_for_load_state("networkidle")
    
    # Validar con get_by_role()
    assert page.get_by_role("button", name="Log In").is_visible()
```

---

## 🏗️ Estructura del Framework

Basado en la exploración, esta es la estructura recomendada:

```
aspen-mtell-automation/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # URLs, timeouts, credenciales
│   │   └── playwright_config.py     # Configuración de Playwright
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logger.py                # Sistema de logging
│   │   └── errors.py                # Excepciones personalizadas
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── base_page.py        # BasePage con métodos comunes
│   │   │   ├── login_page.py       # Página de login
│   │   │   ├── dashboard_page.py   # Dashboard principal
│   │   │   └── alerts_page.py      # Página de alertas (future)
│   │   │
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── navbar_component.py      # Barra de navegación superior
│   │       ├── sidenav_component.py     # Menú lateral
│   │       ├── issues_container.py      # Contenedor de issues
│   │       ├── filters_component.py     # Componente de filtros
│   │       └── user_menu_component.py   # Menú de usuario
│   │
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py              # Funciones helper
│       └── test_data.py            # Datos de prueba
│
├── tests/
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── test_login.py
│   │   ├── test_dashboard.py
│   │   ├── test_navigation.py
│   │   └── test_filters.py
│   │
│   └── conftest.py                 # Fixtures compartidos
│
├── screenshots/                    # Screenshots de fallas
├── reports/                        # Reportes de ejecución
├── .env                           # Variables de entorno
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 🔑 BasePage Implementada

### Archivo: `src/ui/pages/base_page.py`

```python
"""BasePage con métodos comunes para Aspen Mtell."""
from typing import Optional
from playwright.sync_api import Page, Locator
from src.core.logger import get_logger
from src.config.settings import Settings

class BasePage:
    """
    Clase base para todas las páginas de Aspen Mtell.
    Encapsula operaciones comunes de Playwright.
    """
    
    def __init__(self, page: Page):
        """
        Inicializa BasePage.
        
        Args:
            page: Instancia de Playwright Page
        """
        self.page = page
        self.logger = get_logger(self.__class__.__name__)
        self.settings = Settings()
        self.base_url = self.settings.BASE_URL
        self.timeout = self.settings.DEFAULT_TIMEOUT
    
    # ============================================================
    # NAVEGACIÓN
    # ============================================================
    
    def goto(self, path: str = "") -> 'BasePage':
        """
        Navega a una ruta específica.
        
        Args:
            path: Ruta relativa o URL completa
        
        Returns:
            Self para method chaining
        """
        if path.startswith("http"):
            url = path
        else:
            url = f"{self.base_url}{path}"
        
        self.logger.info(f"Navegando a: {url}")
        self.page.goto(url, wait_until="networkidle")
        return self
    
    def get_current_url(self) -> str:
        """Obtiene la URL actual."""
        return self.page.url
    
    def reload(self) -> 'BasePage':
        """Recarga la página actual."""
        self.logger.info("Recargando página")
        self.page.reload()
        return self
    
    # ============================================================
    # INTERACCIÓN CON ELEMENTOS
    # ============================================================
    
    def click(self, selector: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Hace click en un elemento.
        
        Args:
            selector: Selector CSS o role
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or self.timeout
        self.logger.debug(f"Click en: {selector}")
        self.page.locator(selector).click(timeout=timeout)
        return self
    
    def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Llena un campo de input.
        
        Args:
            selector: Selector del input
            text: Texto a ingresar
            timeout: Timeout personalizado
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or self.timeout
        self.logger.debug(f"Llenando '{selector}' con: {text}")
        self.page.locator(selector).fill(text, timeout=timeout)
        return self
    
    def type_text(self, selector: str, text: str, delay: int = 50) -> 'BasePage':
        """
        Escribe texto caracter por caracter.
        
        Args:
            selector: Selector del elemento
            text: Texto a escribir
            delay: Delay entre caracteres en ms
        
        Returns:
            Self para method chaining
        """
        self.logger.debug(f"Escribiendo en '{selector}'")
        self.page.locator(selector).type(text, delay=delay)
        return self
    
    def select_option(self, selector: str, value: str) -> 'BasePage':
        """Selecciona opción de dropdown."""
        self.logger.debug(f"Seleccionando '{value}' en '{selector}'")
        self.page.locator(selector).select_option(value)
        return self
    
    def hover(self, selector: str) -> 'BasePage':
        """Hover sobre un elemento."""
        self.logger.debug(f"Hover sobre: {selector}")
        self.page.locator(selector).hover()
        return self
    
    # ============================================================
    # OBTENCIÓN DE INFORMACIÓN
    # ============================================================
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        Obtiene el texto de un elemento.
        
        Args:
            selector: Selector CSS
            timeout: Timeout en ms
        
        Returns:
            Texto del elemento
        """
        timeout = timeout or self.timeout
        text = self.page.locator(selector).text_content(timeout=timeout)
        return text.strip() if text else ""
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Obtiene un atributo de un elemento."""
        return self.page.locator(selector).get_attribute(attribute)
    
    def get_all_texts(self, selector: str) -> list[str]:
        """
        Obtiene texto de todos los elementos que coinciden.
        
        Args:
            selector: Selector CSS
        
        Returns:
            Lista de textos
        """
        elements = self.page.locator(selector).all()
        return [elem.text_content().strip() for elem in elements if elem.text_content()]
    
    def count_elements(self, selector: str) -> int:
        """
        Cuenta elementos que coinciden con el selector.
        
        Args:
            selector: Selector CSS
        
        Returns:
            Número de elementos
        """
        count = self.page.locator(selector).count()
        self.logger.debug(f"Encontrados {count} elementos con selector '{selector}'")
        return count
    
    # ============================================================
    # VALIDACIONES Y ESPERAS
    # ============================================================
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Verifica si un elemento es visible.
        
        Args:
            selector: Selector CSS
            timeout: Timeout en ms
        
        Returns:
            True si es visible, False si no
        """
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """Verifica si un elemento está oculto."""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """Verifica si un elemento está habilitado."""
        return self.page.locator(selector).is_enabled()
    
    def wait_for_element(
        self, 
        selector: str, 
        state: str = "visible", 
        timeout: Optional[int] = None
    ) -> 'BasePage':
        """
        Espera a que un elemento alcance un estado específico.
        
        Args:
            selector: Selector CSS
            state: Estado a esperar ('visible', 'hidden', 'attached', 'detached')
            timeout: Timeout en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or self.timeout
        self.logger.debug(f"Esperando a que '{selector}' esté {state}")
        self.page.locator(selector).wait_for(state=state, timeout=timeout)
        return self
    
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Espera a que la URL coincida con un patrón.
        
        Args:
            url_pattern: Patrón de URL
            timeout: Timeout en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or self.timeout
        self.logger.debug(f"Esperando URL: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)
        return self
    
    def wait_for_load_state(self, state: str = "networkidle") -> 'BasePage':
        """
        Espera a que la página alcance un estado de carga.
        
        Args:
            state: Estado ('load', 'domcontentloaded', 'networkidle')
        
        Returns:
            Self para method chaining
        """
        self.logger.debug(f"Esperando estado: {state}")
        self.page.wait_for_load_state(state)
        return self
    
    # ============================================================
    # UTILIDADES
    # ============================================================
    
    def get_locator(self, selector: str) -> Locator:
        """
        Obtiene un Locator de Playwright para operaciones avanzadas.
        
        Args:
            selector: Selector CSS
        
        Returns:
            Playwright Locator
        """
        return self.page.locator(selector)
    
    def screenshot(self, filename: str, full_page: bool = False) -> str:
        """
        Toma un screenshot.
        
        Args:
            filename: Nombre del archivo
            full_page: Si capturar página completa
        
        Returns:
            Ruta del screenshot
        """
        path = f"screenshots/{filename}.png"
        self.logger.info(f"Screenshot guardado: {path}")
        self.page.screenshot(path=path, full_page=full_page)
        return path
    
    def execute_script(self, script: str, *args):
        """
        Ejecuta JavaScript en el contexto de la página.
        
        Args:
            script: Código JavaScript
            *args: Argumentos para el script
        
        Returns:
            Resultado del script
        """
        self.logger.debug(f"Ejecutando script JS")
        return self.page.evaluate(script, *args)
    
    def scroll_to_element(self, selector: str) -> 'BasePage':
        """Scroll hacia un elemento."""
        self.logger.debug(f"Scroll hacia: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()
        return self
    
    def press_key(self, key: str) -> 'BasePage':
        """
        Presiona una tecla.
        
        Args:
            key: Nombre de la tecla ('Enter', 'Escape', etc.)
        
        Returns:
            Self para method chaining
        """
        self.logger.debug(f"Presionando tecla: {key}")
        self.page.keyboard.press(key)
        return self
```

---

## 📄 Page Objects Identificados

### 1. LoginPage

**Archivo:** `src/ui/pages/login_page.py`

```python
"""Page Object para la página de Login de Aspen Mtell."""
from src.ui.pages.base_page import BasePage

class LoginPage(BasePage):
    """
    Page Object para Login de Aspen Mtell Alert Manager.
    URL: /Aspentech/AspenMtell/AlertManager/
    """
    
    # ============================================================
    # SELECTORES
    # ============================================================
    
    _login_button = "#loginbutton"
    _aspen_logo = "img[alt='AspenTech Logo']"
    _login_container = ".login-form-container"
    _right_panel_title = "h1"  # "Alert Manager ™"
    
    # ============================================================
    # ACCIONES
    # ============================================================
    
    def navigate(self) -> 'LoginPage':
        """
        Navega a la página de login.
        
        Returns:
            Self para method chaining
        """
        self.goto("#/dashboard")
        self.wait_for_element(self._login_button)
        return self
    
    def click_login(self):
        """
        Hace click en el botón Login.
        Retorna DashboardPage cuando se complete la navegación.
        
        Returns:
            Instancia de DashboardPage
        """
        self.logger.info("Haciendo login...")
        self.click(self._login_button)
        
        # Esperar a que cargue el dashboard
        self.wait_for_load_state("networkidle")
        
        # Importar aquí para evitar circular import
        from src.ui.pages.dashboard_page import DashboardPage
        return DashboardPage(self.page)
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def is_on_login_page(self) -> bool:
        """
        Verifica si estamos en la página de login.
        
        Returns:
            True si estamos en login, False si no
        """
        return self.is_visible(self._login_button) and \
               self.is_visible(self._aspen_logo)
    
    def get_page_title(self) -> str:
        """
        Obtiene el título de la página.
        
        Returns:
            Título de la página
        """
        return self.get_text(self._right_panel_title)
    
    def is_login_button_visible(self) -> bool:
        """Verifica si el botón de login es visible."""
        return self.is_visible(self._login_button)
```

### 2. DashboardPage

**Archivo:** `src/ui/pages/dashboard_page.py`

```python
"""Page Object para el Dashboard de Aspen Mtell."""
from src.ui.pages.base_page import BasePage
from src.ui.components.navbar_component import NavbarComponent
from src.ui.components.sidenav_component import SidenavComponent
from src.ui.components.issues_container import IssuesContainerComponent

class DashboardPage(BasePage):
    """
    Page Object para Dashboard de Aspen Mtell Alert Manager.
    URL: /#/dashboard (después de login)
    """
    
    # ============================================================
    # SELECTORES
    # ============================================================
    
    _dashboard_container = ".dashboard"
    _company_filter = ".company-filter"
    _issues_header = ".alerts-header"
    _breadcrumb_all_sites = "button:has-text('All Sites')"
    
    # ============================================================
    # COMPONENTES
    # ============================================================
    
    def __init__(self, page):
        """
        Inicializa DashboardPage con componentes.
        
        Args:
            page: Playwright Page instance
        """
        super().__init__(page)
        self.navbar = NavbarComponent(page)
        self.sidenav = SidenavComponent(page)
        self.issues = IssuesContainerComponent(page)
    
    # ============================================================
    # ACCIONES
    # ============================================================
    
    def navigate(self) -> 'DashboardPage':
        """
        Navega al dashboard.
        
        Returns:
            Self para method chaining
        """
        self.goto("#/dashboard")
        self.wait_for_element(self._dashboard_container)
        return self
    
    def open_sidenav(self) -> 'DashboardPage':
        """
        Abre el menú lateral.
        
        Returns:
            Self para method chaining
        """
        self.sidenav.open()
        return self
    
    def close_sidenav(self) -> 'DashboardPage':
        """
        Cierra el menú lateral.
        
        Returns:
            Self para method chaining
        """
        self.sidenav.close()
        return self
    
    def navigate_to_section(self, section_name: str) -> 'DashboardPage':
        """
        Navega a una sección usando el sidenav.
        
        Args:
            section_name: Nombre de la sección (ej: "Dashboard", "STAR & Catch Report")
        
        Returns:
            Self para method chaining
        """
        self.open_sidenav()
        self.sidenav.click_section(section_name)
        return self
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def is_on_dashboard(self) -> bool:
        """
        Verifica si estamos en el dashboard.
        
        Returns:
            True si estamos en dashboard
        """
        return self.is_visible(self._dashboard_container) and \
               self.is_visible(self._issues_header) and \
               "#/dashboard" in self.get_current_url()
    
    def get_issues_title(self) -> str:
        """
        Obtiene el título del contenedor de issues.
        
        Returns:
            Título de issues (ej: "Issues: All Sites")
        """
        return self.issues.get_title()
    
    def get_current_site_filter(self) -> str:
        """
        Obtiene el filtro de sitio actual.
        
        Returns:
            Texto del filtro actual
        """
        return self.get_text(self._breadcrumb_all_sites)
```

---

## 🧩 Componentes Reutilizables

### 1. NavbarComponent (Barra Superior)

**Archivo:** `src/ui/components/navbar_component.py`

```python
"""Componente de la barra de navegación superior."""
from src.ui.pages.base_page import BasePage

class NavbarComponent(BasePage):
    """
    Componente para la barra de navegación superior de Aspen Mtell.
    Aparece en todas las páginas después del login.
    """
    
    # ============================================================
    # SELECTORES
    # ============================================================
    
    _container = "nav.navbar"
    _menu_button = "#menu-btn"
    _company_logo = ".navbar__logo"
    _title = ".navbar__title"
    _help_button = "[data-testid='help-button']"
    _theme_toggle_button = "[data-testid='toggle-theme-button']"
    _profile_menu = "[data-testid='profile-menu']"
    _admin_tool_button = "[data-testid='admin-tool-button']"
    _user_initials = ".user-initial-circle"
    
    # ============================================================
    # ACCIONES
    # ============================================================
    
    def click_menu_button(self) -> 'NavbarComponent':
        """
        Hace click en el botón del menú (hamburguer).
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo menú lateral")
        self.click(self._menu_button)
        return self
    
    def click_help(self) -> 'NavbarComponent':
        """Hace click en el botón de ayuda."""
        self.logger.info("Abriendo ayuda")
        self.click(self._help_button)
        return self
    
    def toggle_theme(self) -> 'NavbarComponent':
        """Cambia el tema (claro/oscuro)."""
        self.logger.info("Cambiando tema")
        self.click(self._theme_toggle_button)
        return self
    
    def open_profile_menu(self) -> 'NavbarComponent':
        """Abre el menú de perfil de usuario."""
        self.logger.info("Abriendo menú de perfil")
        self.click(self._profile_menu)
        return self
    
    def open_admin_tools(self) -> 'NavbarComponent':
        """Abre las herramientas de administrador."""
        self.logger.info("Abriendo herramientas de admin")
        self.click(self._admin_tool_button)
        return self
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def is_navbar_visible(self) -> bool:
        """Verifica si la navbar es visible."""
        return self.is_visible(self._container)
    
    def get_title_text(self) -> str:
        """
        Obtiene el texto del título de la aplicación.
        
        Returns:
            Texto del título (ej: "Aspen Mtell Alert Manager")
        """
        return self.get_text(self._title)
    
    def get_user_initials(self) -> str:
        """
        Obtiene las iniciales del usuario actual.
        
        Returns:
            Iniciales del usuario (ej: "DU")
        """
        return self.get_text(self._user_initials)
```

### 2. SidenavComponent (Menú Lateral)

**Archivo:** `src/ui/components/sidenav_component.py`

```python
"""Componente del menú lateral (sidenav)."""
from src.ui.pages.base_page import BasePage

class SidenavComponent(BasePage):
    """
    Componente para el menú lateral de navegación.
    Se abre al hacer click en el botón de menú en la navbar.
    """
    
    # ============================================================
    # SELECTORES
    # ============================================================
    
    _container = "mat-sidenav"
    _close_button = "button[aria-label='close menu button']"
    _company_logo = ".sidenav-company-info__logo"
    _company_title = ".sidenav-company-info-description__title"
    _greeting_message = ".sidenav-company-info-description__subtitle"
    
    # Secciones del menú
    _dashboard_item = ".sidenav-item:has-text('Dashboard')"
    _star_report_item = ".sidenav-item:has-text('STAR & Catch Report')"
    _alert_impact_item = ".sidenav-item:has-text('Alert Impact Quantification')"
    
    # ============================================================
    # ACCIONES
    # ============================================================
    
    def open(self) -> 'SidenavComponent':
        """
        Abre el sidenav (si está cerrado).
        
        Returns:
            Self para method chaining
        """
        if not self.is_open():
            self.logger.info("Abriendo sidenav")
            # El botón de abrir está en navbar
            self.click("#menu-btn")
            self.wait_for_element(self._container, state="visible")
        return self
    
    def close(self) -> 'SidenavComponent':
        """
        Cierra el sidenav.
        
        Returns:
            Self para method chaining
        """
        if self.is_open():
            self.logger.info("Cerrando sidenav")
            self.click(self._close_button)
            self.wait_for_element(self._container, state="hidden")
        return self
    
    def click_section(self, section_name: str) -> 'SidenavComponent':
        """
        Hace click en una sección del menú.
        
        Args:
            section_name: Nombre de la sección
        
        Returns:
            Self para method chaining
        """
        self.logger.info(f"Navegando a: {section_name}")
        
        selector_map = {
            "Dashboard": self._dashboard_item,
            "STAR & Catch Report": self._star_report_item,
            "Alert Impact Quantification": self._alert_impact_item
        }
        
        selector = selector_map.get(section_name)
        if selector:
            self.click(selector)
        else:
            raise ValueError(f"Sección desconocida: {section_name}")
        
        return self
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def is_open(self) -> bool:
        """
        Verifica si el sidenav está abierto.
        
        Returns:
            True si está abierto
        """
        return self.is_visible(self._container)
    
    def get_company_name(self) -> str:
        """
        Obtiene el nombre de la compañía mostrado.
        
        Returns:
            Nombre de la compañía
        """
        return self.get_text(self._company_title)
    
    def get_greeting_message(self) -> str:
        """
        Obtiene el mensaje de saludo.
        
        Returns:
            Mensaje de saludo (ej: "Good Afternoon Default")
        """
        return self.get_text(self._greeting_message)
    
    def get_available_sections(self) -> list[str]:
        """
        Obtiene todas las secciones disponibles en el menú.
        
        Returns:
            Lista de nombres de secciones
        """
        return self.get_all_texts(".sidenav-item span")
```

### 3. IssuesContainerComponent

**Archivo:** `src/ui/components/issues_container.py`

```python
"""Componente del contenedor de Issues."""
from src.ui.pages.base_page import BasePage

class IssuesContainerComponent(BasePage):
    """
    Componente para el contenedor de Issues en el dashboard.
    Maneja la visualización y filtrado de alertas/issues.
    """
    
    # ============================================================
    # SELECTORES
    # ============================================================
    
    _container = ".alerts.custom_scrollbar.card"
    _header = ".alerts-header"
    _title = ".alerts-header__title h2"
    
    # Filtros
    _date_range_input = "mat-date-range-input"
    _date_start_input = "input[formcontrolname='dateStart']"
    _date_end_input = "input[formcontrolname='dateEnd']"
    _type_filter = ".alerts-header__filters-issues"
    _sort_by_filter = ".alerts-header__filters-sort"
    _status_filter = ".alerts-header__status"
    
    # Botones de filtro
    _calendar_button = "button[aria-label='Open calendar']"
    _type_dropdown = ".alerts-header__filters-issues mat-form-field"
    _sort_dropdown = ".alerts-header__filters-sort mat-form-field"
    
    # ============================================================
    # ACCIONES - FILTROS
    # ============================================================
    
    def open_date_picker(self) -> 'IssuesContainerComponent':
        """
        Abre el date picker.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo date picker")
        self.click(self._calendar_button)
        return self
    
    def open_type_filter(self) -> 'IssuesContainerComponent':
        """Abre el filtro de tipo."""
        self.logger.info("Abriendo filtro de tipo")
        self.click(self._type_dropdown)
        return self
    
    def open_sort_filter(self) -> 'IssuesContainerComponent':
        """Abre el filtro de ordenamiento."""
        self.logger.info("Abriendo filtro de sort")
        self.click(self._sort_dropdown)
        return self
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def is_container_visible(self) -> bool:
        """Verifica si el contenedor es visible."""
        return self.is_visible(self._container)
    
    def get_title(self) -> str:
        """
        Obtiene el título del contenedor.
        
        Returns:
            Título (ej: "Issues: All Sites")
        """
        return self.get_text(self._title)
    
    def get_current_date_range(self) -> str:
        """
        Obtiene el rango de fechas actual mostrado.
        
        Returns:
            Texto del rango de fechas
        """
        return self.get_attribute(self._date_start_input, "placeholder") or ""
```

---

## ⚙️ Fixtures y Configuración

### Archivo: `tests/conftest.py`

```python
"""Fixtures compartidos para tests de Aspen Mtell."""
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from src.config.playwright_config import get_browser_config, get_context_config
from src.ui.pages.login_page import LoginPage
from src.ui.pages.dashboard_page import DashboardPage
from src.core.logger import get_logger

logger = get_logger(__name__)

# ============================================================
# BROWSER FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def playwright():
    """Inicia Playwright."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright) -> Browser:
    """Lanza el browser (session scope)."""
    logger.info("Lanzando browser")
    config = get_browser_config()
    browser = playwright.chromium.launch(**config)
    yield browser
    logger.info("Cerrando browser")
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """Crea un nuevo contexto para cada test."""
    config = get_context_config()
    context = browser.new_context(**config)
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Crea una nueva página para cada test."""
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page
    page.close()

# ============================================================
# PAGE OBJECT FIXTURES
# ============================================================

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Provee instancia de LoginPage."""
    return LoginPage(page)

@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    """Provee instancia de DashboardPage."""
    return DashboardPage(page)

# ============================================================
# AUTHENTICATION FIXTURES
# ============================================================

@pytest.fixture
def authenticated_page(login_page: LoginPage) -> DashboardPage:
    """
    Provee una página ya autenticada (logged in).
    Útil para tests que no necesitan probar login.
    
    Returns:
        Instancia de DashboardPage después del login
    """
    logger.info("Realizando login para test")
    login_page.navigate()
    dashboard = login_page.click_login()
    return dashboard

# ============================================================
# HOOKS
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook para capturar resultado de test.
    Toma screenshot en caso de falla.
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = None
        for fixture_name in item.fixturenames:
            if "page" in fixture_name:
                page = item.funcargs.get(fixture_name)
                break
        
        if page:
            screenshot_path = f"screenshots/{item.name}_failure.png"
            page.screenshot(path=screenshot_path)
            logger.error(f"Test fallido: {item.name}. Screenshot: {screenshot_path}")

def pytest_addoption(parser):
    """Agrega opciones de línea de comandos."""
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="Browser: chromium, firefox, webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Ejecutar en modo headless"
    )
```

### Archivo: `src/config/settings.py`

```python
"""Configuración centralizada de la aplicación."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Settings de la aplicación."""
    
    # URLs
    BASE_URL = os.getenv(
        "BASE_URL",
        "https://azqamtell06.qae.aspentech.com/Aspentech/AspenMtell/AlertManager/"
    )
    
    # Timeouts (en milisegundos)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", "5000"))
    LONG_TIMEOUT = int(os.getenv("LONG_TIMEOUT", "60000"))
    
    # Browser
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    BROWSER = os.getenv("BROWSER", "chromium")
    
    # Screenshots
    SCREENSHOT_ON_FAILURE = True
    SCREENSHOT_DIR = "screenshots"
    
    # Logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/test.log"
```

---

## 🧪 Ejemplos de Tests

### Test 1: Login Básico

**Archivo:** `tests/ui/test_login.py`

```python
"""Tests de Login para Aspen Mtell."""
import pytest
from src.ui.pages.login_page import LoginPage
from src.ui.pages.dashboard_page import DashboardPage

class TestLogin:
    """Suite de tests para funcionalidad de Login."""
    
    @pytest.mark.smoke
    def test_login_button_visible(self, login_page: LoginPage):
        """
        Verifica que el botón de login sea visible en la página de login.
        
        Given: Usuario está en la página de login
        When: La página carga completamente
        Then: El botón de login debe ser visible
        """
        # Arrange & Act
        login_page.navigate()
        
        # Assert
        assert login_page.is_login_button_visible(), \
            "El botón de login no es visible"
        assert login_page.is_on_login_page(), \
            "No estamos en la página de login"
    
    @pytest.mark.smoke
    def test_successful_login(self, login_page: LoginPage):
        """
        Verifica que el login sea exitoso y redirija al dashboard.
        
        Given: Usuario está en la página de login
        When: Usuario hace click en el botón "Log In"
        Then: Usuario debe ser redirigido al dashboard
        """
        # Arrange
        login_page.navigate()
        
        # Act
        dashboard_page = login_page.click_login()
        
        # Assert
        assert dashboard_page.is_on_dashboard(), \
            "No se redirigió correctamente al dashboard"
    
    def test_login_page_title(self, login_page: LoginPage):
        """
        Verifica que el título de la página de login sea correcto.
        
        Given: Usuario está en la página de login
        When: La página carga
        Then: El título debe mostrar "Alert Manager ™"
        """
        # Arrange & Act
        login_page.navigate()
        title = login_page.get_page_title()
        
        # Assert
        assert "Alert Manager" in title, \
            f"Título incorrecto. Esperado: 'Alert Manager ™', Obtenido: '{title}'"
```

### Test 2: Navegación en Dashboard

**Archivo:** `tests/ui/test_dashboard.py`

```python
"""Tests del Dashboard de Aspen Mtell."""
import pytest
from src.ui.pages.dashboard_page import DashboardPage

class TestDashboard:
    """Suite de tests para el Dashboard."""
    
    @pytest.mark.smoke
    def test_dashboard_loads_after_login(self, authenticated_page: DashboardPage):
        """
        Verifica que el dashboard cargue correctamente después del login.
        
        Given: Usuario ha hecho login exitosamente
        When: Dashboard se carga
        Then: Todos los componentes principales deben ser visibles
        """
        # Arrange (ya autenticado via fixture)
        dashboard = authenticated_page
        
        # Assert
        assert dashboard.is_on_dashboard(), \
            "Dashboard no cargó correctamente"
        assert dashboard.navbar.is_navbar_visible(), \
            "Navbar no es visible"
    
    @pytest.mark.regression
    def test_sidenav_opens_and_closes(self, authenticated_page: DashboardPage):
        """
        Verifica que el menú lateral se abra y cierre correctamente.
        
        Given: Usuario está en el dashboard
        When: Usuario hace click en el botón de menú
        Then: El sidenav debe abrirse
        And: Al hacer click en cerrar, debe cerrarse
        """
        # Arrange
        dashboard = authenticated_page
        
        # Act - Abrir
        dashboard.open_sidenav()
        
        # Assert - Abierto
        assert dashboard.sidenav.is_open(), \
            "Sidenav no se abrió"
        
        # Act - Cerrar
        dashboard.close_sidenav()
        
        # Assert - Cerrado
        assert not dashboard.sidenav.is_open(), \
            "Sidenav no se cerró"
    
    @pytest.mark.regression
    def test_sidenav_sections_available(self, authenticated_page: DashboardPage):
        """
        Verifica que todas las secciones del menú estén disponibles.
        
        Given: Usuario está en el dashboard
        When: Usuario abre el sidenav
        Then: Todas las secciones esperadas deben estar disponibles
        """
        # Arrange
        dashboard = authenticated_page
        expected_sections = [
            "Dashboard",
            "STAR & Catch Report",
            "Alert Impact Quantification"
        ]
        
        # Act
        dashboard.open_sidenav()
        available_sections = dashboard.sidenav.get_available_sections()
        
        # Assert
        for section in expected_sections:
            assert section in available_sections, \
                f"Sección '{section}' no encontrada. Disponibles: {available_sections}"
    
    def test_issues_container_visible(self, authenticated_page: DashboardPage):
        """
        Verifica que el contenedor de issues sea visible.
        
        Given: Usuario está en el dashboard
        When: Dashboard se carga
        Then: El contenedor de issues debe ser visible
        """
        # Arrange
        dashboard = authenticated_page
        
        # Assert
        assert dashboard.issues.is_container_visible(), \
            "Contenedor de issues no es visible"
        
        title = dashboard.get_issues_title()
        assert "Issues" in title, \
            f"Título del contenedor incorrecto: {title}"
    
    def test_navbar_user_initials_displayed(self, authenticated_page: DashboardPage):
        """
        Verifica que las iniciales del usuario se muestren en la navbar.
        
        Given: Usuario está en el dashboard autenticado
        When: Navbar se carga
        Then: Las iniciales del usuario deben estar visibles
        """
        # Arrange
        dashboard = authenticated_page
        
        # Act
        user_initials = dashboard.navbar.get_user_initials()
        
        # Assert
        assert user_initials, \
            "No se encontraron iniciales de usuario"
        assert len(user_initials) >= 1, \
            f"Iniciales inválidas: {user_initials}"
```

### Test 3: Navegación entre Secciones

**Archivo:** `tests/ui/test_navigation.py`

```python
"""Tests de navegación en Aspen Mtell."""
import pytest
from src.ui.pages.dashboard_page import DashboardPage

class TestNavigation:
    """Suite de tests para navegación entre secciones."""
    
    @pytest.mark.parametrize("section_name", [
        "Dashboard",
        "STAR & Catch Report",
        "Alert Impact Quantification"
    ])
    def test_navigate_to_section(
        self, 
        authenticated_page: DashboardPage, 
        section_name: str
    ):
        """
        Verifica que se pueda navegar a cada sección del menú.
        
        Given: Usuario está en el dashboard
        When: Usuario hace click en una sección del sidenav
        Then: La aplicación debe navegar a esa sección
        """
        # Arrange
        dashboard = authenticated_page
        
        # Act
        dashboard.navigate_to_section(section_name)
        
        # Assert
        # Verificar que el sidenav se cierre después de navegar
        # (comportamiento esperado de la app)
        # Agregar validaciones específicas según la sección
        assert True  # Placeholder - agregar validaciones reales
    
    def test_navbar_menu_button_opens_sidenav(
        self, 
        authenticated_page: DashboardPage
    ):
        """
        Verifica que el botón de menú en navbar abra el sidenav.
        
        Given: Usuario está en el dashboard
        And: Sidenav está cerrado
        When: Usuario hace click en el botón de menú
        Then: Sidenav debe abrirse
        """
        # Arrange
        dashboard = authenticated_page
        if dashboard.sidenav.is_open():
            dashboard.close_sidenav()
        
        # Act
        dashboard.navbar.click_menu_button()
        
        # Assert
        assert dashboard.sidenav.is_open(), \
            "Sidenav no se abrió después de click en menu button"
```

---

## 🗺️ Roadmap de Implementación

### Fase 1: Fundamentos (Semana 1)
- [ ] Crear estructura de carpetas del proyecto
- [ ] Implementar `BasePage` con métodos comunes
- [ ] Configurar `pytest.ini` y fixtures básicos
- [ ] Implementar `Settings` y configuración
- [ ] Implementar sistema de logging básico

### Fase 2: Pages Principales (Semana 2)
- [ ] Implementar `LoginPage` completamente
- [ ] Implementar `DashboardPage` con componentes básicos
- [ ] Escribir tests de login (smoke)
- [ ] Escribir tests de dashboard básicos

### Fase 3: Componentes Reutilizables (Semana 3)
- [ ] Implementar `NavbarComponent`
- [ ] Implementar `SidenavComponent`
- [ ] Implementar `IssuesContainerComponent`
- [ ] Escribir tests de navegación
- [ ] Escribir tests de componentes

### Fase 4: Filtros y Funcionalidades Avanzadas (Semana 4)
- [ ] Implementar funcionalidad de filtros de fecha
- [ ] Implementar funcionalidad de filtros de tipo
- [ ] Implementar funcionalidad de ordenamiento
- [ ] Escribir tests de filtros
- [ ] Implementar manejo de tablas de alertas

### Fase 5: Mejoras y Estabilización (Semana 5)
- [ ] Agregar retry logic para elementos dinámicos
- [ ] Implementar esperas inteligentes
- [ ] Mejorar manejo de errores
- [ ] Agregar más assertions y validaciones
- [ ] Optimizar screenshots y reportes

### Fase 6: CI/CD y Documentación (Semana 6)
- [ ] Configurar pipeline de CI/CD
- [ ] Implementar reportes HTML detallados
- [ ] Documentar todos los Page Objects
- [ ] Crear guía de contribución
- [ ] Agregar ejemplos de uso

---

## 📝 Notas Importantes

### Selectores Identificados

Los selectores más estables identificados en la exploración:

1. **IDs únicos:**
   - `#loginbutton` - Botón de login
   - `#menu-btn` - Botón de menú en navbar

2. **data-testid (ideales):**
   - `[data-testid='help-button']` - Botón de ayuda
   - `[data-testid='toggle-theme-button']` - Toggle de tema
   - `[data-testid='profile-menu']` - Menú de perfil
   - `[data-testid='admin-tool-button']` - Herramientas de admin

3. **Clases semánticas:**
   - `.navbar` - Barra de navegación
   - `.sidenav-item` - Items del menú lateral
   - `.dashboard` - Contenedor principal del dashboard
   - `.alerts-header` - Header del contenedor de alertas

### Tecnologías de la Aplicación

Basado en el HTML:
- **Framework:** Angular (versión 19.2.13)
- **UI Library:** Angular Material
- **Componentes:** mat-sidenav, mat-icon, mat-form-field, etc.

### Recomendaciones

1. **Esperas:** La aplicación usa Angular, puede tener delays en renderizado:
   - Usar `wait_for_load_state("networkidle")` después de acciones
   - Implementar esperas personalizadas para componentes Angular Material

2. **Selectores:** Priorizar `data-testid` cuando estén disponibles:
   - Los data-testid ya presentes son muy estables
   - Solicitar al equipo de dev agregar más si es necesario

3. **Componentes Angular Material:** 
   - Pueden ser complejos de interactuar
   - Usar esperas explícitas para dropdowns y modals
   - Considerar usar `page.wait_for_selector()` con timeouts generosos

4. **Screenshots:** 
   - Implementar screenshots en cada paso crítico
   - Útil para debugging en CI/CD

---

## 🎓 Conclusión

Esta guía proporciona una base sólida para implementar un framework de automatización para Aspen Mtell Alert Manager siguiendo el patrón POM.

### Próximos Pasos para Ti:

1. **Crear el proyecto** en un nuevo workspace siguiendo la estructura propuesta
2. **Implementar BasePage** con los métodos mostrados
3. **Crear LoginPage y DashboardPage** como primeros Page Objects
4. **Escribir tus primeros tests** de smoke
5. **Iterar y expandir** agregando más componentes y tests

### Recursos de Aprendizaje:

- Revisa el [Módulo 1: Fundamentos Framework UI (POM)](modulo_01_framework_ui_pom.md)
- Usa esta guía como referencia práctica
- Adapta los selectores según la app evolucione
- Mantén la estructura modular y escalable

---

**¡Éxito construyendo tu framework! 🚀**

[← Volver al README](README.md) | [Ver Módulo 1](modulo_01_framework_ui_pom.md)
