# 🔷 Módulo 1: Fundamentos del Framework UI con Playwright (POM)

## 📋 Índice
1. [Introducción y Objetivos](#introducción-y-objetivos)
2. [¿Qué es el Page Object Model (POM)?](#qué-es-el-page-object-model-pom)
3. [Arquitectura del Framework UI](#arquitectura-del-framework-ui)
4. [La Clase BasePage](#la-clase-basepage)
5. [Page Objects Específicos](#page-objects-específicos)
6. [Componentes Reutilizables](#componentes-reutilizables)
7. [Configuración de Playwright](#configuración-de-playwright)
8. [Fixtures de pytest](#fixtures-de-pytest)
9. [Estrategias de Localización y Selectores](#estrategias-de-localización-y-selectores)
10. [Sincronización y Esperas](#sincronización-y-esperas)
11. [Ejercicios Prácticos](#ejercicios-prácticos)
12. [Antipatrones Comunes](#antipatrones-comunes)
13. [Checklist de Validación](#checklist-de-validación)

---

## 🎯 Introducción y Objetivos

### ¿Qué aprenderás en este módulo?

Al finalizar este módulo serás capaz de:
- ✅ Entender profundamente el patrón Page Object Model (POM)
- ✅ Diseñar una arquitectura de framework UI escalable
- ✅ Implementar una clase BasePage robusta
- ✅ Crear Page Objects mantenibles y expresivos
- ✅ Reutilizar componentes entre diferentes páginas
- ✅ Configurar Playwright correctamente con pytest
- ✅ Manejar selectores estables y estrategias de localización
- ✅ Implementar sincronización sin flakiness

### 💡 ¿Por qué es importante?

Un framework de UI bien estructurado es la diferencia entre:
- **Tests frágiles** que fallan constantemente vs **tests estables** que generan confianza
- **Mantenimiento pesadilla** vs **cambios rápidos y seguros**
- **Duplicación masiva** vs **reutilización efectiva**
- **Debugging de horas** vs **fallas claras y accionables**

---

## 🏗️ ¿Qué es el Page Object Model (POM)?

### Definición

El **Page Object Model** es un patrón de diseño que crea una capa de abstracción entre los tests y la UI de la aplicación. Cada página (o componente significativo) de la aplicación se representa como una clase, encapsulando:
- Los **selectores** de elementos
- Las **acciones** que se pueden realizar
- Las **validaciones** específicas de esa página

### 🎯 Beneficios del POM

| Beneficio | Sin POM | Con POM |
|-----------|---------|---------|
| **Mantenibilidad** | Cambio en UI → editar 50 tests | Cambio en UI → editar 1 Page Object |
| **Legibilidad** | `page.click("#btn-submit")` | `login_page.click_submit()` |
| **Reutilización** | Código duplicado en cada test | Métodos compartidos en Page Object |
| **Encapsulación** | Selectores esparcidos | Selectores centralizados |
| **Testing** | Tests acoplados al DOM | Tests expresan intención de negocio |

### 📊 Ejemplo Visual: Sin POM vs Con POM

#### ❌ Sin POM (Antipatrón)
```python
def test_login_success():
    page.goto("https://app.example.com/login")
    page.locator("#email").fill("user@test.com")
    page.locator("#password").fill("password123")
    page.locator("button[type='submit']").click()
    assert "dashboard" in page.url
    assert page.locator(".welcome-message").is_visible()

def test_login_invalid_credentials():
    page.goto("https://app.example.com/login")
    page.locator("#email").fill("user@test.com")
    page.locator("#password").fill("wrong")
    page.locator("button[type='submit']").click()
    assert page.locator(".error-message").is_visible()
```

**Problemas:**
- ❌ Selectores duplicados (`#email`, `#password`)
- ❌ URL hardcodeada múltiples veces
- ❌ Lógica de negocio mezclada con detalles técnicos
- ❌ Si cambia un selector, hay que cambiar múltiples tests

#### ✅ Con POM (Correcto)
```python
# login_page.py
class LoginPage(BasePage):
    # Selectores centralizados
    _email_input = "#email"
    _password_input = "#password"
    _submit_button = "button[type='submit']"
    _error_message = ".error-message"
    _welcome_message = ".welcome-message"
    
    def navigate(self):
        """Navigate to login page."""
        self.goto("/login")
        return self
    
    def login(self, email: str, password: str):
        """Perform login with credentials."""
        self.fill(self._email_input, email)
        self.fill(self._password_input, password)
        self.click(self._submit_button)
        return self
    
    def is_error_displayed(self) -> bool:
        """Check if error message is visible."""
        return self.is_visible(self._error_message)
    
    def is_logged_in(self) -> bool:
        """Check if user is successfully logged in."""
        return "dashboard" in self.page.url and \
               self.is_visible(self._welcome_message)

# test_login.py
def test_login_success(login_page):
    login_page.navigate() \
              .login("user@test.com", "password123")
    
    assert login_page.is_logged_in()

def test_login_invalid_credentials(login_page):
    login_page.navigate() \
              .login("user@test.com", "wrong")
    
    assert login_page.is_error_displayed()
```

**Ventajas:**
- ✅ Tests expresan **intención de negocio** (login, verify logged in)
- ✅ Selectores en **un solo lugar**
- ✅ Tests son **legibles y concisos**
- ✅ Cambios en UI requieren **edición mínima**
- ✅ **Fluent interface** con method chaining

---

## 🏛️ Arquitectura del Framework UI

### Estructura de Carpetas Recomendada

```
src/
└── ui/
    ├── __init__.py
    ├── pages/
    │   ├── __init__.py
    │   ├── base_page.py          # 🔑 Clase base con métodos comunes
    │   ├── login_page.py          # Page Object específico
    │   ├── dashboard_page.py      # Page Object específico
    │   ├── user_profile_page.py   # Page Object específico
    │   └── checkout_page.py       # Page Object específico
    │
    └── components/
        ├── __init__.py
        ├── base_component.py      # Clase base para componentes
        ├── navbar.py              # Componente reutilizable
        ├── sidebar.py             # Componente reutilizable
        ├── modal.py               # Componente reutilizable
        └── dropdown.py            # Componente reutilizable
```

### 🔍 Decisiones de Arquitectura

#### 1. **¿Por qué separar `pages/` y `components/`?**

**Pages:**
- Representan **páginas completas** de la aplicación
- Tienen **URLs únicas**
- Contienen lógica de **flujos de negocio**
- Ejemplo: LoginPage, DashboardPage, CheckoutPage

**Components:**
- Representan **porciones reutilizables** de UI
- Aparecen en **múltiples páginas**
- No tienen URL propia
- Ejemplo: Navbar, Modal, Dropdown, DatePicker

```python
# ✅ BUENO: Dashboard page que usa componentes
class DashboardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.navbar = NavbarComponent(page)  # Componente reutilizable
        self.sidebar = SidebarComponent(page)  # Componente reutilizable
    
    def navigate_to_settings(self):
        self.navbar.click_settings()  # Delega al componente
        return SettingsPage(self.page)
```

#### 2. **¿BasePage o múltiples herencias?**

**✅ Recomendado: Una BasePage con composición**
```python
class BasePage:
    """Clase base con métodos comunes para todas las páginas."""
    def __init__(self, page):
        self.page = page
        self.logger = get_logger(__name__)
    
    def click(self, selector): ...
    def fill(self, selector, text): ...
    # ... métodos comunes

class LoginPage(BasePage):
    """Hereda de BasePage."""
    pass
```

**❌ Evitar: Herencias múltiples complejas**
```python
# Antipatrón: demasiada complejidad
class LoginPage(BasePage, FormMixin, NavigationMixin, ValidationMixin):
    pass
```

**Razón:** Herencia simple es más fácil de entender y mantener. Usa **composición** para funcionalidades específicas.

---

## 🔑 La Clase BasePage

La **BasePage** es el corazón del framework. Contiene todos los métodos comunes que se reutilizarán en todos los Page Objects.

### Implementación Completa de BasePage

```python
# src/ui/pages/base_page.py
from typing import Optional, List
from playwright.sync_api import Page, Locator, expect
from src.core.logger import get_logger

class BasePage:
    """
    Clase base que encapsula operaciones comunes de Playwright.
    Todas las páginas específicas deben heredar de esta clase.
    """
    
    def __init__(self, page: Page):
        """
        Initialize BasePage.
        
        Args:
            page: Playwright Page object
        """
        self.page = page
        self.logger = get_logger(self.__class__.__name__)
        self.base_url = "https://app.example.com"  # Desde config
    
    # ============================================================
    # NAVEGACIÓN
    # ============================================================
    
    def goto(self, path: str) -> 'BasePage':
        """
        Navigate to a specific path.
        
        Args:
            path: URL path (e.g., '/login', '/dashboard')
        
        Returns:
            Self for method chaining
        """
        url = self.base_url + path if path.startswith('/') else path
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        return self
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.page.url
    
    def reload(self) -> 'BasePage':
        """Reload current page."""
        self.logger.info("Reloading page")
        self.page.reload()
        return self
    
    # ============================================================
    # INTERACCIÓN CON ELEMENTOS
    # ============================================================
    
    def click(self, selector: str, timeout: int = 10000) -> 'BasePage':
        """
        Click an element.
        
        Args:
            selector: CSS selector or role selector
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Clicking element: {selector}")
        self.page.locator(selector).click(timeout=timeout)
        return self
    
    def fill(self, selector: str, text: str, timeout: int = 10000) -> 'BasePage':
        """
        Fill input field with text.
        
        Args:
            selector: CSS selector
            text: Text to fill
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Filling '{selector}' with: {text}")
        self.page.locator(selector).fill(text, timeout=timeout)
        return self
    
    def type_text(self, selector: str, text: str, delay: int = 50) -> 'BasePage':
        """
        Type text character by character (simula usuario real).
        
        Args:
            selector: CSS selector
            text: Text to type
            delay: Delay between keystrokes in ms
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Typing text in '{selector}'")
        self.page.locator(selector).type(text, delay=delay)
        return self
    
    def select_option(self, selector: str, value: str) -> 'BasePage':
        """
        Select option from dropdown.
        
        Args:
            selector: CSS selector of select element
            value: Value to select
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Selecting option '{value}' in '{selector}'")
        self.page.locator(selector).select_option(value)
        return self
    
    def check(self, selector: str) -> 'BasePage':
        """Check a checkbox."""
        self.logger.debug(f"Checking checkbox: {selector}")
        self.page.locator(selector).check()
        return self
    
    def uncheck(self, selector: str) -> 'BasePage':
        """Uncheck a checkbox."""
        self.logger.debug(f"Unchecking checkbox: {selector}")
        self.page.locator(selector).uncheck()
        return self
    
    def hover(self, selector: str) -> 'BasePage':
        """Hover over an element."""
        self.logger.debug(f"Hovering over: {selector}")
        self.page.locator(selector).hover()
        return self
    
    # ============================================================
    # OBTENCIÓN DE INFORMACIÓN
    # ============================================================
    
    def get_text(self, selector: str, timeout: int = 10000) -> str:
        """
        Get text content of element.
        
        Args:
            selector: CSS selector
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Text content of element
        """
        text = self.page.locator(selector).text_content(timeout=timeout)
        self.logger.debug(f"Text from '{selector}': {text}")
        return text.strip() if text else ""
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get attribute value from element.
        
        Args:
            selector: CSS selector
            attribute: Attribute name
        
        Returns:
            Attribute value or None
        """
        value = self.page.locator(selector).get_attribute(attribute)
        self.logger.debug(f"Attribute '{attribute}' from '{selector}': {value}")
        return value
    
    def get_all_texts(self, selector: str) -> List[str]:
        """
        Get text from all matching elements.
        
        Args:
            selector: CSS selector
        
        Returns:
            List of text contents
        """
        elements = self.page.locator(selector).all()
        texts = [elem.text_content().strip() for elem in elements]
        self.logger.debug(f"Found {len(texts)} elements matching '{selector}'")
        return texts
    
    # ============================================================
    # VALIDACIONES Y ESPERAS
    # ============================================================
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible.
        
        Args:
            selector: CSS selector
            timeout: Maximum wait time in milliseconds
        
        Returns:
            True if visible, False otherwise
        """
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False
    
    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is hidden."""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        return self.page.locator(selector).is_enabled()
    
    def is_checked(self, selector: str) -> bool:
        """Check if checkbox is checked."""
        return self.page.locator(selector).is_checked()
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = 30000) -> 'BasePage':
        """
        Wait for element to reach specific state.
        
        Args:
            selector: CSS selector
            state: Element state ('visible', 'hidden', 'attached', 'detached')
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Waiting for '{selector}' to be {state}")
        self.page.locator(selector).wait_for(state=state, timeout=timeout)
        return self
    
    def wait_for_url(self, url_pattern: str, timeout: int = 30000) -> 'BasePage':
        """
        Wait for URL to match pattern.
        
        Args:
            url_pattern: URL pattern to match
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Waiting for URL to match: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)
        return self
    
    # ============================================================
    # UTILIDADES
    # ============================================================
    
    def get_locator(self, selector: str) -> Locator:
        """
        Get Playwright Locator for advanced operations.
        
        Args:
            selector: CSS selector
        
        Returns:
            Playwright Locator object
        """
        return self.page.locator(selector)
    
    def screenshot(self, filename: str, full_page: bool = False) -> str:
        """
        Take screenshot.
        
        Args:
            filename: Name of screenshot file
            full_page: Whether to capture full page
        
        Returns:
            Path to screenshot file
        """
        path = f"screenshots/{filename}"
        self.logger.info(f"Taking screenshot: {path}")
        self.page.screenshot(path=path, full_page=full_page)
        return path
    
    def execute_script(self, script: str, *args):
        """
        Execute JavaScript in page context.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to script
        
        Returns:
            Script result
        """
        self.logger.debug(f"Executing script: {script[:50]}...")
        return self.page.evaluate(script, *args)
    
    def scroll_to_element(self, selector: str) -> 'BasePage':
        """Scroll element into view."""
        self.logger.debug(f"Scrolling to element: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()
        return self
    
    def press_key(self, key: str) -> 'BasePage':
        """
        Press keyboard key.
        
        Args:
            key: Key name (e.g., 'Enter', 'Escape', 'Tab')
        
        Returns:
            Self for method chaining
        """
        self.logger.debug(f"Pressing key: {key}")
        self.page.keyboard.press(key)
        return self
```

### 💡 Características Clave de BasePage

1. **Method Chaining:** Retorna `self` para permitir encadenar llamadas
2. **Logging:** Registra todas las acciones para debugging
3. **Timeouts configurables:** Flexibilidad en esperas
4. **Type hints:** Mejor autocompletado y validación
5. **Docstrings:** Documentación clara de cada método
6. **Manejo de errores:** Try-catch en validaciones booleanas

---

## 📄 Page Objects Específicos

Con la BasePage lista, crear Page Objects específicos es sencillo y expresivo.

### Ejemplo Completo: LoginPage

```python
# src/ui/pages/login_page.py
from src.ui.pages.base_page import BasePage
from src.ui.pages.dashboard_page import DashboardPage

class LoginPage(BasePage):
    """
    Page Object for Login page.
    URL: /login
    """
    
    # ============================================================
    # SELECTORES (Privados con underscore)
    # ============================================================
    
    _email_input = "input[name='email']"
    _password_input = "input[type='password']"
    _submit_button = "button[type='submit']"
    _remember_me_checkbox = "#remember-me"
    _forgot_password_link = "a:has-text('Forgot password?')"
    _error_message = ".alert-error"
    _success_message = ".alert-success"
    _loading_spinner = ".spinner"
    
    # ============================================================
    # ACCIONES
    # ============================================================
    
    def navigate(self) -> 'LoginPage':
        """Navigate to login page."""
        self.goto("/login")
        self.wait_for_element(self._email_input)
        return self
    
    def enter_email(self, email: str) -> 'LoginPage':
        """
        Enter email address.
        
        Args:
            email: Email address to enter
        
        Returns:
            Self for method chaining
        """
        self.fill(self._email_input, email)
        return self
    
    def enter_password(self, password: str) -> 'LoginPage':
        """
        Enter password.
        
        Args:
            password: Password to enter
        
        Returns:
            Self for method chaining
        """
        self.fill(self._password_input, password)
        return self
    
    def check_remember_me(self) -> 'LoginPage':
        """Check 'Remember me' checkbox."""
        self.check(self._remember_me_checkbox)
        return self
    
    def click_submit(self) -> 'LoginPage':
        """Click submit button."""
        self.click(self._submit_button)
        self.wait_for_loading()
        return self
    
    def click_forgot_password(self):
        """Click 'Forgot password' link."""
        self.click(self._forgot_password_link)
        # Retorna ForgotPasswordPage (importar cuando exista)
        return self
    
    def login(self, email: str, password: str, remember: bool = False) -> DashboardPage:
        """
        Perform complete login action.
        
        Args:
            email: User email
            password: User password
            remember: Whether to check 'Remember me'
        
        Returns:
            DashboardPage instance if login succeeds
        """
        self.logger.info(f"Logging in with email: {email}")
        self.enter_email(email)
        self.enter_password(password)
        
        if remember:
            self.check_remember_me()
        
        self.click_submit()
        
        # Si login exitoso, retorna página siguiente
        return DashboardPage(self.page)
    
    def wait_for_loading(self) -> 'LoginPage':
        """Wait for loading spinner to disappear."""
        if self.is_visible(self._loading_spinner, timeout=1000):
            self.wait_for_element(self._loading_spinner, state="hidden")
        return self
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def get_error_message(self) -> str:
        """
        Get error message text.
        
        Returns:
            Error message or empty string
        """
        if self.is_visible(self._error_message):
            return self.get_text(self._error_message)
        return ""
    
    def is_error_displayed(self) -> bool:
        """Check if error message is visible."""
        return self.is_visible(self._error_message)
    
    def is_on_login_page(self) -> bool:
        """
        Verify if currently on login page.
        
        Returns:
            True if on login page
        """
        return "/login" in self.get_current_url() and \
               self.is_visible(self._email_input)
    
    def is_submit_button_enabled(self) -> bool:
        """Check if submit button is enabled."""
        return self.is_enabled(self._submit_button)
```

### 🎯 Patrones y Convenciones

| Aspecto | Convención | Ejemplo |
|---------|-----------|---------|
| **Selectores** | Privados con `_` | `_email_input` |
| **Métodos de acción** | Verbos descriptivos | `enter_email()`, `click_submit()` |
| **Métodos de validación** | Prefijo `is_` o `get_` | `is_visible()`, `get_error()` |
| **Return type** | Retornar `self` o página siguiente | `return self` / `return DashboardPage` |
| **Documentación** | Docstrings en métodos públicos | Ver ejemplo arriba |

---

## 🧩 Componentes Reutilizables

Los **componentes** representan porciones de UI que aparecen en múltiples páginas (navbar, modals, dropdowns, etc.).

### BaseComponent

```python
# src/ui/components/base_component.py
from src.ui.pages.base_page import BasePage

class BaseComponent(BasePage):
    """
    Clase base para componentes reutilizables.
    Hereda de BasePage para acceder a métodos comunes.
    """
    
    def __init__(self, page, container_selector: str = ""):
        """
        Initialize component.
        
        Args:
            page: Playwright Page object
            container_selector: Optional selector to scope component
        """
        super().__init__(page)
        self.container = container_selector
    
    def _scoped(self, selector: str) -> str:
        """
        Scope selector dentro del container del componente.
        
        Args:
            selector: Selector relativo al componente
        
        Returns:
            Selector completo
        """
        if self.container:
            return f"{self.container} {selector}"
        return selector
```

### Ejemplo: NavbarComponent

```python
# src/ui/components/navbar.py
from src.ui.components.base_component import BaseComponent

class NavbarComponent(BaseComponent):
    """Navbar component present on all pages after login."""
    
    # Selectores
    _container = "nav.navbar"
    _logo = ".navbar-brand"
    _profile_dropdown = "#profile-dropdown"
    _logout_button = "a:has-text('Logout')"
    _settings_link = "a:has-text('Settings')"
    _notifications_icon = ".notifications-icon"
    _notifications_badge = ".notifications-badge"
    
    def __init__(self, page):
        super().__init__(page, self._container)
    
    def click_logo(self) -> 'NavbarComponent':
        """Click on application logo."""
        self.click(self._scoped(self._logo))
        return self
    
    def open_profile_dropdown(self) -> 'NavbarComponent':
        """Open profile dropdown menu."""
        self.click(self._scoped(self._profile_dropdown))
        return self
    
    def click_logout(self):
        """Click logout button."""
        self.open_profile_dropdown()
        self.click(self._scoped(self._logout_button))
        # Retornar LoginPage
        from src.ui.pages.login_page import LoginPage
        return LoginPage(self.page)
    
    def click_settings(self):
        """Navigate to settings page."""
        self.open_profile_dropdown()
        self.click(self._scoped(self._settings_link))
        # Retornar SettingsPage
        return self
    
    def get_notifications_count(self) -> int:
        """
        Get number of unread notifications.
        
        Returns:
            Number of notifications
        """
        if self.is_visible(self._scoped(self._notifications_badge)):
            text = self.get_text(self._scoped(self._notifications_badge))
            return int(text) if text.isdigit() else 0
        return 0
    
    def is_navbar_visible(self) -> bool:
        """Check if navbar is visible."""
        return self.is_visible(self.container)
```

### Uso en Page Objects

```python
# src/ui/pages/dashboard_page.py
from src.ui.pages.base_page import BasePage
from src.ui.components.navbar import NavbarComponent

class DashboardPage(BasePage):
    """Dashboard page (post-login)."""
    
    def __init__(self, page):
        super().__init__(page)
        self.navbar = NavbarComponent(page)  # ✅ Composición
    
    def navigate(self) -> 'DashboardPage':
        self.goto("/dashboard")
        return self
    
    def logout(self):
        """Logout using navbar component."""
        return self.navbar.click_logout()  # ✅ Delega al componente
    
    def get_notifications_count(self) -> int:
        """Get notifications from navbar."""
        return self.navbar.get_notifications_count()
```

---

## ⚙️ Configuración de Playwright

### pytest.ini

```ini
# pytest.ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marcadores
markers =
    smoke: Smoke tests (run on every commit)
    regression: Full regression suite
    ui: UI tests
    api: API tests
    slow: Tests that take > 5 seconds

# Playwright options
addopts = 
    -v
    --tb=short
    --strict-markers
    --html=reports/report.html
    --self-contained-html

# Logging
log_cli = true
log_cli_level = INFO
log_file = logs/test.log
log_file_level = DEBUG

# Timeouts
timeout = 300
```

### playwright.config

```python
# src/config/playwright_config.py
from typing import Dict, Any

def get_browser_config(browser_name: str = "chromium", headless: bool = True) -> Dict[str, Any]:
    """
    Get Playwright browser configuration.
    
    Args:
        browser_name: Browser to use ('chromium', 'firefox', 'webkit')
        headless: Whether to run in headless mode
    
    Returns:
        Configuration dictionary
    """
    config = {
        "headless": headless,
        "slowMo": 0 if headless else 500,  # Slow down for debugging
        "args": [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled"
        ],
        "viewport": {"width": 1920, "height": 1080},
        "timeout": 30000,  # 30 seconds default timeout
        "screenshot": "only-on-failure",
        "trace": "retain-on-failure",
    }
    
    if browser_name == "chromium":
        config["channel"] = "chrome"  # Usa Google Chrome en vez de Chromium
    
    return config

def get_context_config() -> Dict[str, Any]:
    """Get Playwright browser context configuration."""
    return {
        "viewport": {"width": 1920, "height": 1080"},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "permissions": ["geolocation", "notifications"],
        "record_video_dir": "videos/",
        "record_video_size": {"width": 1280, "height": 720},
    }
```

---

## 🧪 Fixtures de pytest

Los fixtures son fundamentales para configurar el ambiente de prueba.

### conftest.py Principal

```python
# tests/conftest.py
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from src.config.playwright_config import get_browser_config, get_context_config
from src.core.logger import get_logger

logger = get_logger(__name__)

# ============================================================
# BROWSER FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def browser_name(pytestconfig) -> str:
    """Get browser name from command line or default to chromium."""
    return pytestconfig.getoption("--browser", default="chromium")

@pytest.fixture(scope="session")
def headless(pytestconfig) -> bool:
    """Get headless mode from command line or default to True."""
    return pytestconfig.getoption("--headless", default=True)

@pytest.fixture(scope="session")
def playwright():
    """Start Playwright."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright, browser_name: str, headless: bool) -> Browser:
    """
    Launch browser instance.
    Shared across all tests in session.
    """
    logger.info(f"Launching {browser_name} browser (headless={headless})")
    config = get_browser_config(browser_name, headless)
    
    if browser_name == "chromium":
        browser = playwright.chromium.launch(**config)
    elif browser_name == "firefox":
        browser = playwright.firefox.launch(**config)
    elif browser_name == "webkit":
        browser = playwright.webkit.launch(**config)
    else:
        raise ValueError(f"Unknown browser: {browser_name}")
    
    yield browser
    logger.info("Closing browser")
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """
    Create new browser context for each test.
    Isolated cookies, localStorage, etc.
    """
    config = get_context_config()
    context = browser.new_context(**config)
    
    yield context
    
    # Cleanup
    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    Create new page for each test.
    Fresh page per test.
    """
    page = context.new_page()
    
    # Set default timeout
    page.set_default_timeout(30000)
    
    yield page
    
    # Screenshot on failure (handled by pytest-playwright)
    page.close()

# ============================================================
# PAGE OBJECT FIXTURES
# ============================================================

@pytest.fixture
def login_page(page: Page):
    """Provide LoginPage instance."""
    from src.ui.pages.login_page import LoginPage
    return LoginPage(page)

@pytest.fixture
def dashboard_page(page: Page):
    """Provide DashboardPage instance."""
    from src.ui.pages.dashboard_page import DashboardPage
    return DashboardPage(page)

# ============================================================
# AUTHENTICATION FIXTURES
# ============================================================

@pytest.fixture
def authenticated_page(page: Page, login_page):
    """
    Provide authenticated page (logged in).
    Use for tests that require authentication.
    """
    login_page.navigate()
    login_page.login(
        email="test@example.com",
        password="password123"
    )
    yield page

# ============================================================
# HOOKS
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test result.
    Take screenshot on failure.
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Get page fixture if exists
        page = None
        for fixture_name in item.fixturenames:
            if "page" in fixture_name:
                page = item.funcargs.get(fixture_name)
                break
        
        if page:
            screenshot_path = f"screenshots/{item.name}.png"
            page.screenshot(path=screenshot_path)
            logger.error(f"Test failed: {item.name}. Screenshot saved: {screenshot_path}")
```

### Opciones de Línea de Comandos

```python
# conftest.py (agregar al principio)
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="Browser to use: chromium, firefox, webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run in headless mode"
    )
    parser.addoption(
        "--slowmo",
        action="store",
        default=0,
        type=int,
        help="Slow down operations by N milliseconds"
    )
```

**Uso:**
```bash
# Ejecutar con Firefox en modo visible
pytest --browser=firefox

# Ejecutar headless
pytest --headless

# Ejecutar lento para debugging
pytest --slowmo=500
```

---

## 🎯 Estrategias de Localización y Selectores

### Jerarquía de Selectores (de mejor a peor)

| Prioridad | Selector | Ejemplo | Estabilidad | Razón |
|-----------|----------|---------|-------------|-------|
| 1️⃣ | `data-testid` | `[data-testid='submit-btn']` | ⭐⭐⭐⭐⭐ | Diseñado para testing |
| 2️⃣ | Role + Name | `role=button[name="Submit"]` | ⭐⭐⭐⭐ | Semántico, accesible |
| 3️⃣ | Label text | `label:has-text("Email")` | ⭐⭐⭐⭐ | Visible para usuario |
| 4️⃣ | Placeholder | `[placeholder='Enter email']` | ⭐⭐⭐ | Puede cambiar |
| 5️⃣ | ID | `#email-input` | ⭐⭐⭐ | Puede cambiar |
| 6️⃣ | Class | `.btn-primary` | ⭐⭐ | Cambios de estilo rompen |
| 7️⃣ | CSS path | `div > div > button:nth-child(2)` | ⭐ | Muy frágil |
| 8️⃣ | XPath | `//div[@id='app']//button[2]` | ⭐ | Complejo y frágil |

### ✅ Mejores Prácticas de Selectores

#### 1. **data-testid (Recomendado)**

```python
# ✅ MEJOR: data-testid específico para testing
_submit_button = "[data-testid='login-submit-btn']"
_email_input = "[data-testid='login-email-input']"

# HTML correspondiente:
# <input data-testid="login-email-input" type="email" />
# <button data-testid="login-submit-btn">Submit</button>
```

**Ventajas:**
- Explícito para testing
- No cambia por motivos de estilo o funcionalidad
- Fácil de identificar en code review

#### 2. **Role-based Selectors (Playwright)**

```python
# ✅ BUENO: Usa roles de ARIA (accesibilidad)
_submit_button = "role=button[name='Submit']"
_email_input = "role=textbox[name='Email']"
_main_heading = "role=heading[name='Welcome']"

# También válido:
self.page.get_by_role("button", name="Submit").click()
self.page.get_by_role("textbox", name="Email").fill("test@example.com")
```

**Ventajas:**
- Mejora accesibilidad automáticamente
- Semántico y expresivo
- Robusto ante cambios de estructura

#### 3. **Text-based Selectors**

```python
# ✅ BUENO: Texto visible para usuario
_forgot_password_link = "a:has-text('Forgot password?')"
_error_message = "text=Invalid credentials"

# Playwright helper:
self.page.get_by_text("Forgot password?").click()
```

#### 4. **ID o Name estables**

```python
# ✅ ACEPTABLE: Si IDs son estables
_email_input = "#email"
_password_input = "[name='password']"
```

### ❌ Antipatrones de Selectores

```python
# ❌ MAL: Selector basado en estructura (frágil)
_submit_button = "div.container > div:nth-child(3) > button"

# ❌ MAL: XPath complejo
_submit_button = "//div[@class='form']//div[@class='buttons']/button[1]"

# ❌ MAL: Clase genérica de CSS framework
_submit_button = ".btn.btn-primary.btn-lg"  # Bootstrap classes

# ❌ MAL: Selector que depende de orden
_first_product = "div.product:nth-child(1)"
```

### 🛠️ Herramientas para Generar Selectores

```bash
# Playwright Inspector (abre browser y genera selectores)
playwright codegen https://your-app.com

# Playwright CLI para selectores
playwright show-trace trace.zip
```

---

## ⏱️ Sincronización y Esperas

### Tipos de Esperas

#### 1. **Auto-waiting de Playwright (Built-in)**

```python
# ✅ MEJOR: Playwright espera automáticamente antes de la acción
self.page.click("#submit")  # Espera que sea visible, enabled, stable
self.page.fill("#email", "test@example.com")  # Espera que sea editable
```

**Playwright espera automáticamente que el elemento:**
- Exista en el DOM
- Sea visible
- Esté enabled
- Esté estable (no esté animando)

#### 2. **Esperas Explícitas**

```python
# ✅ Esperar estado específico
page.locator("#submit").wait_for(state="visible")
page.locator(".loading").wait_for(state="hidden")
page.locator("#content").wait_for(state="attached")

# ✅ Esperar URL
page.wait_for_url("**/dashboard")
page.wait_for_url(re.compile(r".*/dashboard$"))

# ✅ Esperar condición de red
with page.expect_response("**/api/users") as response_info:
    page.click("#load-users")
response = response_info.value
assert response.status == 200

# ✅ Esperar navegación
with page.expect_navigation():
    page.click("#submit")
```

#### 3. **Esperas Personalizadas**

```python
# ✅ Esperar condición custom
def wait_for_condition(page, condition_fn, timeout=30000):
    """Wait for custom condition."""
    import time
    start = time.time()
    while (time.time() - start) * 1000 < timeout:
        if condition_fn():
            return True
        time.sleep(0.1)
    raise TimeoutError("Condition not met")

# Uso:
wait_for_condition(
    page,
    lambda: page.locator(".product").count() > 10,
    timeout=5000
)
```

### ❌ Antipatrón: time.sleep()

```python
# ❌ NUNCA HACER ESTO
import time

def test_login_bad():
    page.goto("https://app.com/login")
    time.sleep(2)  # ❌ Espera arbitraria
    page.fill("#email", "test@example.com")
    time.sleep(1)  # ❌ Lento e inestable
    page.fill("#password", "password")
    time.sleep(3)  # ❌ Puede ser insuficiente o excesivo
    page.click("#submit")
    time.sleep(5)  # ❌ Ralentiza tests innecesariamente

# ✅ CORRECTO: Esperas inteligentes
def test_login_good(login_page):
    login_page.navigate()  # Espera implícita
    login_page.login("test@example.com", "password")  # Esperas automáticas
    # Playwright espera automáticamente que elementos sean interactuables
```

**¿Por qué time.sleep() es malo?**
- ❌ **Lento:** Siempre espera tiempo completo aunque elemento esté listo
- ❌ **Inestable:** Puede ser muy corto (falla) o muy largo (lento)
- ❌ **No escalable:** No se adapta a condiciones de carga
- ❌ **Oculta problemas:** Enmascara errores de sincronización real

---

## 🔧 Ejercicios Prácticos

### Ejercicio 1: Crear tu Primera Page Object

**Objetivo:** Implementar `DashboardPage` con métodos básicos.

**Requerimientos:**
- Hereda de `BasePage`
- Define selectores para:
  - Título de bienvenida
  - Card de estadísticas
  - Botón de crear nuevo item
- Implementa métodos:
  - `get_welcome_message()`
  - `get_stats_count()`
  - `click_create_new()`
- Agrega validación: `is_on_dashboard()`

**Solución:**
```python
# Tu código aquí (completa el ejercicio)
```

### Ejercicio 2: Componente Modal Reutilizable

**Objetivo:** Crear un componente `ModalComponent` genérico.

**Requerimientos:**
- Hereda de `BaseComponent`
- Métodos:
  - `is_modal_open()`
  - `get_modal_title()`
  - `click_close()`
  - `click_confirm()`
  - `click_cancel()`
- Debe funcionar con cualquier modal de la app

**Solución:**
```python
# Tu código aquí
```

### Ejercicio 3: Test End-to-End Completo

**Objetivo:** Escribir un test completo que use múltiples Page Objects.

**Flujo:**
1. Login
2. Crear nuevo item en Dashboard
3. Verificar item en lista
4. Logout

**Plantilla:**
```python
def test_create_item_e2e(login_page, dashboard_page):
    # 1. Login
    login_page.navigate()
    dashboard_page = login_page.login("user@test.com", "password123")
    
    # 2. Crear item
    # ... (completar)
    
    # 3. Verificar
    # ... (completar)
    
    # 4. Logout
    # ... (completar)
```

---

## ⚠️ Antipatrones Comunes

### 1. ❌ Selectores Duplicados

```python
# ❌ MAL: Selector hardcodeado en múltiples métodos
class LoginPage:
    def enter_email(self, email):
        self.page.locator("#email").fill(email)  # ❌
    
    def is_email_visible(self):
        return self.page.locator("#email").is_visible()  # ❌ Duplicado

# ✅ BIEN: Selector centralizado
class LoginPage:
    _email_input = "#email"  # ✅ Una sola definición
    
    def enter_email(self, email):
        self.page.locator(self._email_input).fill(email)
    
    def is_email_visible(self):
        return self.page.locator(self._email_input).is_visible()
```

### 2. ❌ Lógica de Negocio en Tests

```python
# ❌ MAL: Lógica en test
def test_login():
    page.goto("https://app.com/login")
    page.locator("#email").fill("test@example.com")
    page.locator("#password").fill("password")
    page.locator("#submit").click()
    assert "dashboard" in page.url

# ✅ BIEN: Lógica encapsulada en Page Object
def test_login(login_page):
    login_page.navigate()
    dashboard_page = login_page.login("test@example.com", "password")
    assert dashboard_page.is_on_dashboard()
```

### 3. ❌ Page Objects Gigantes (God Object)

```python
# ❌ MAL: Un Page Object hace demasiado
class AdminPage(BasePage):
    def manage_users(self): ...
    def manage_products(self): ...
    def generate_reports(self): ...
    def configure_settings(self): ...
    # ... 50 métodos más

# ✅ BIEN: Dividir en Page Objects específicos
class AdminUsersPage(BasePage): ...
class AdminProductsPage(BasePage): ...
class AdminReportsPage(BasePage): ...
class AdminSettingsPage(BasePage): ...
```

### 4. ❌ Esperas Innecesarias o Redundantes

```python
# ❌ MAL: Esperas redundantes
def login(self, email, password):
    time.sleep(2)  # ❌
    self.page.locator("#email").wait_for()  # ❌ Innecesario
    self.page.locator("#email").fill(email)  # Ya espera automáticamente
    time.sleep(1)  # ❌

# ✅ BIEN: Confía en auto-waiting de Playwright
def login(self, email, password):
    self.page.locator("#email").fill(email)  # Espera automática
    self.page.locator("#password").fill(password)
    self.page.locator("#submit").click()
```

---

## ✅ Checklist de Validación

Usa esta checklist para validar tu framework UI:

### Arquitectura
- [ ] Estructura de carpetas clara (`pages/`, `components/`)
- [ ] BasePage implementada con métodos comunes
- [ ] Componentes reutilizables identificados y extraídos
- [ ] Separación clara entre página y componente

### Page Objects
- [ ] Selectores privados (`_selector_name`)
- [ ] Métodos públicos descriptivos
- [ ] Docstrings en métodos importantes
- [ ] Type hints en parámetros y retornos
- [ ] Method chaining donde tiene sentido

### Selectores
- [ ] Prioridad a `data-testid` o roles
- [ ] Sin selectores frágiles (nth-child, XPath complejos)
- [ ] Selectores centralizados (no duplicados)
- [ ] Uso de selectores semánticos

### Sincronización
- [ ] Sin `time.sleep()` arbitrarios
- [ ] Uso de auto-waiting de Playwright
- [ ] Esperas explícitas solo cuando necesario
- [ ] Timeouts configurables

### Configuración
- [ ] pytest.ini configurado correctamente
- [ ] Fixtures de Playwright funcionando
- [ ] Fixtures de Page Objects disponibles
- [ ] Hooks para screenshots en fallas

### Testing
- [ ] Tests expresan intención de negocio
- [ ] Tests no dependen de detalles de implementación
- [ ] Tests son independientes entre sí
- [ ] Tests son repetibles y estables

---

## 🎓 Próximos Pasos

Has completado el Módulo 1! Ahora deberías:

1. ✅ **Practicar:** Implementa al menos 3 Page Objects completos
2. ✅ **Refactorizar:** Si tienes tests existentes, migra a POM
3. ✅ **Documentar:** Mantén README con estructura de tu framework
4. ✅ **Continuar:** Avanza al [Módulo 2: Framework de Automatización de API](modulo_02_framework_api.md)

---

## 📚 Recursos Adicionales

- [Playwright Documentation - Page Object Model](https://playwright.dev/python/docs/pom)
- [Playwright Best Practices](https://playwright.dev/python/docs/best-practices)
- [Playwright Selectors Guide](https://playwright.dev/python/docs/selectors)
- [pytest Fixtures Documentation](https://docs.pytest.org/en/stable/fixture.html)

---

**¡Continúa con tu aprendizaje! 🚀**

[← Volver al README](README.md) | [Siguiente: Módulo 2 - Framework API →](modulo_02_framework_api.md)
