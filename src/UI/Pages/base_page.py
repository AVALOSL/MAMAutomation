"""BasePage con métodos comunes para el framework de Aspen Mtell."""
from typing import Optional, Union
from playwright.sync_api import Page, Locator, expect
from src.core.logger import get_logger
from src.config.settings import Settings


class BasePage:
    """
    Clase base para todos los Page Objects.
    
    Proporciona métodos comunes para interactuar con la aplicación web,
    incluyendo navegación, clics, relleno de campos, y validaciones.
    Usa auto-waiting de Playwright y logging integrado.
    """

    def __init__(self, page: Page):
        """
        Inicializa la página base.
        
        Args:
            page: Instancia de Playwright Page
        """
        self.page = page
        self.logger = get_logger(self.__class__.__name__)
        self.page.set_default_timeout(Settings.DEFAULT_TIMEOUT)

    # ============================================================
    # NAVEGACIÓN
    # ============================================================

    def goto(self, path: str = "", wait_until: str = "networkidle") -> 'BasePage':
        """
        Navega a una URL.
        
        Args:
            path: Ruta relativa a BASE_URL o URL completa
            wait_until: Estado de espera ('load', 'domcontentloaded', 'networkidle')
        
        Returns:
            Self para method chaining
        """
        if path.startswith("http"):
            url = path
        else:
            url = Settings.BASE_URL.rstrip("/") + "/" + path.lstrip("/")
        
        self.logger.info(f"Navegando a: {url}")
        self.page.goto(url, wait_until=wait_until, timeout=Settings.NAVIGATION_TIMEOUT)
        return self

    def get_current_url(self) -> str:
        """
        Obtiene la URL actual.
        
        Returns:
            URL actual de la página
        """
        return self.page.url

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Espera hasta que la URL coincida con el patrón.
        
        Args:
            url_pattern: Patrón de URL a esperar (puede usar glob)
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.debug(f"Esperando URL que coincida con: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)
        return self

    # ============================================================
    # INTERACCIÓN CON ELEMENTOS (ROLE-BASED)
    # ============================================================

    def click_button(self, name: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Hace clic en un botón usando get_by_role().
        
        Args:
            name: Nombre visible del botón
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Haciendo clic en botón: '{name}'")
        self.page.get_by_role("button", name=name).click(timeout=timeout)
        return self

    def fill_textbox(self, name: str, value: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Rellena un campo de texto usando get_by_role().
        
        Args:
            name: Label del campo de texto
            value: Valor a ingresar
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Rellenando campo '{name}' con valor: '{value}'")
        self.page.get_by_role("textbox", name=name).fill(value, timeout=timeout)
        return self

    def click_link(self, name: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Hace clic en un link usando get_by_role().
        
        Args:
            name: Texto del link
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Haciendo clic en link: '{name}'")
        self.page.get_by_role("link", name=name).click(timeout=timeout)
        return self

    # ============================================================
    # INTERACCIÓN CON ELEMENTOS (SELECTOR-BASED)
    # ============================================================

    def click(self, selector: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Hace clic en un elemento usando selector CSS.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Haciendo clic en: {selector}")
        self.page.locator(selector).click(timeout=timeout)
        return self

    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Rellena un campo usando selector CSS.
        
        Args:
            selector: Selector CSS del elemento
            value: Valor a ingresar
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Rellenando '{selector}' con: '{value}'")
        self.page.locator(selector).fill(value, timeout=timeout)
        return self

    def select_option(self, selector: str, value: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Selecciona una opción de un dropdown.
        
        Args:
            selector: Selector CSS del select
            value: Valor a seleccionar
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.info(f"Seleccionando opción '{value}' en: {selector}")
        self.page.locator(selector).select_option(value, timeout=timeout)
        return self

    def hover(self, selector: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        Mueve el mouse sobre un elemento.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.debug(f"Hover sobre: {selector}")
        self.page.locator(selector).hover(timeout=timeout)
        return self

    def press_key(self, key: str) -> 'BasePage':
        """
        Presiona una tecla.
        
        Args:
            key: Tecla a presionar ('Enter', 'Escape', 'Tab', etc.)
        
        Returns:
            Self para method chaining
        """
        self.logger.debug(f"Presionando tecla: {key}")
        self.page.keyboard.press(key)
        return self

    # ============================================================
    # VALIDACIONES Y VERIFICACIONES
    # ============================================================

    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Verifica si un elemento es visible.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms (por defecto SHORT_TIMEOUT)
        
        Returns:
            True si el elemento es visible, False en caso contrario
        """
        timeout = timeout or Settings.SHORT_TIMEOUT
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except Exception:
            return False

    def is_hidden(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Verifica si un elemento está oculto.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms (por defecto SHORT_TIMEOUT)
        
        Returns:
            True si el elemento está oculto, False en caso contrario
        """
        timeout = timeout or Settings.SHORT_TIMEOUT
        try:
            return self.page.locator(selector).is_hidden(timeout=timeout)
        except Exception:
            return False

    def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Verifica si un elemento está habilitado.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms (por defecto SHORT_TIMEOUT)
        
        Returns:
            True si el elemento está habilitado, False en caso contrario
        """
        timeout = timeout or Settings.SHORT_TIMEOUT
        try:
            return self.page.locator(selector).is_enabled(timeout=timeout)
        except Exception:
            return False

    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        Obtiene el texto de un elemento.
        
        Args:
            selector: Selector CSS del elemento
            timeout: Timeout personalizado en ms
        
        Returns:
            Texto del elemento
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        return self.page.locator(selector).inner_text(timeout=timeout)

    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Obtiene un atributo de un elemento.
        
        Args:
            selector: Selector CSS del elemento
            attribute: Nombre del atributo
            timeout: Timeout personalizado en ms
        
        Returns:
            Valor del atributo o None
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        return self.page.locator(selector).get_attribute(attribute, timeout=timeout)

    def count_elements(self, selector: str) -> int:
        """
        Cuenta el número de elementos que coinciden con el selector.
        
        Args:
            selector: Selector CSS del elemento
        
        Returns:
            Número de elementos encontrados
        """
        return self.page.locator(selector).count()

    # ============================================================
    # ESPERAS EXPLÍCITAS
    # ============================================================

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> 'BasePage':
        """
        Espera hasta que un elemento esté en el estado especificado.
        
        Args:
            selector: Selector CSS del elemento
            state: Estado a esperar ('visible', 'hidden', 'attached', 'detached')
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.DEFAULT_TIMEOUT
        self.logger.debug(f"Esperando selector '{selector}' en estado '{state}'")
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
        return self

    def wait_for_load_state(self, state: str = "networkidle", timeout: Optional[int] = None) -> 'BasePage':
        """
        Espera hasta que la página esté en el estado de carga especificado.
        
        Args:
            state: Estado a esperar ('load', 'domcontentloaded', 'networkidle')
            timeout: Timeout personalizado en ms
        
        Returns:
            Self para method chaining
        """
        timeout = timeout or Settings.LONG_TIMEOUT
        self.logger.debug(f"Esperando load state: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)
        return self

    def wait_for_timeout(self, timeout: int) -> 'BasePage':
        """
        Espera un tiempo específico (usar solo cuando sea necesario).
        
        Args:
            timeout: Tiempo a esperar en ms
        
        Returns:
            Self para method chaining
        """
        self.logger.warning(f"Usando wait_for_timeout: {timeout}ms (evitar si es posible)")
        self.page.wait_for_timeout(timeout)
        return self

    # ============================================================
    # UTILIDADES
    # ============================================================

    def get_locator(self, selector: str) -> Locator:
        """
        Obtiene un locator de Playwright.
        
        Args:
            selector: Selector CSS del elemento
        
        Returns:
            Locator de Playwright
        """
        return self.page.locator(selector)

    def screenshot(self, filename: str, full_page: bool = False) -> 'BasePage':
        """
        Toma una captura de pantalla.
        
        Args:
            filename: Nombre del archivo (sin extensión)
            full_page: Si tomar captura de página completa
        
        Returns:
            Self para method chaining
        """
        from pathlib import Path
        screenshot_dir = Path(__file__).parent.parent.parent.parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        
        filepath = screenshot_dir / f"{filename}.png"
        self.logger.info(f"Tomando screenshot: {filepath}")
        self.page.screenshot(path=str(filepath), full_page=full_page)
        return self

    def reload(self) -> 'BasePage':
        """
        Recarga la página actual.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Recargando página")
        self.page.reload(wait_until="networkidle")
        return self

    def go_back(self) -> 'BasePage':
        """
        Navega hacia atrás en el historial.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Navegando hacia atrás")
        self.page.go_back(wait_until="networkidle")
        return self

    def go_forward(self) -> 'BasePage':
        """
        Navega hacia adelante en el historial.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Navegando hacia adelante")
        self.page.go_forward(wait_until="networkidle")
        return self
    