"""Componente del menú lateral (Sidenav)."""
from playwright.sync_api import Page
from src.UI.Pages.base_page import BasePage


class SidenavComponent(BasePage):
    """
    Componente reutilizable para el menú lateral.
    
    Contiene:
    - Botón de cerrar
    - Logo e información de la compañía
    - Items de navegación (Dashboard, STAR & Catch Report, Alert Impact Quantification)
    """

    # Selectores
    SIDENAV = "mat-sidenav"
    CLOSE_BUTTON = ".sidenav-button"
    COMPANY_LOGO = ".sidenav-company-info__logo"
    COMPANY_TITLE = ".sidenav-company-info-description__title"
    COMPANY_SUBTITLE = ".sidenav-company-info-description__subtitle"
    SIDENAV_ITEM = ".sidenav-item"
    SIDENAV_ITEM_SELECTED = ".sidenav-item--selected"

    def __init__(self, page: Page):
        """
        Inicializa SidenavComponent.
        
        Args:
            page: Instancia de Playwright Page
        """
        super().__init__(page)

    def is_open(self) -> bool:
        """
        Verifica si el sidenav está abierto.
        
        Returns:
            True si el sidenav es visible
        """
        return super().is_visible(self.SIDENAV)

    def close(self) -> 'SidenavComponent':
        """
        Cierra el sidenav.
        
        Returns:
            Self para method chaining
        """
        if self.is_open():
            self.logger.info("Cerrando sidenav")
            self.click(self.CLOSE_BUTTON)
            self.wait_for_selector(self.SIDENAV, state="hidden")
        return self

    def get_company_title(self) -> str:
        """
        Obtiene el título de la compañía.
        
        Returns:
            Texto del título
        """
        return self.get_text(self.COMPANY_TITLE)

    def get_company_subtitle(self) -> str:
        """
        Obtiene el subtítulo de la compañía.
        
        Returns:
            Texto del subtítulo (ej: "Good Afternoon Default")
        """
        return self.get_text(self.COMPANY_SUBTITLE)

    def get_all_items(self) -> list[str]:
        """
        Obtiene todos los items del sidenav.
        
        Returns:
            Lista de textos de los items
        """
        items = []
        count = self.count_elements(self.SIDENAV_ITEM)
        for i in range(count):
            text = self.get_locator(self.SIDENAV_ITEM).nth(i).inner_text()
            items.append(text.strip())
        return items

    def get_selected_item(self) -> str:
        """
        Obtiene el item actualmente seleccionado.
        
        Returns:
            Texto del item seleccionado
        """
        return self.get_text(self.SIDENAV_ITEM_SELECTED)

    def click_item(self, item_name: str) -> 'SidenavComponent':
        """
        Hace clic en un item del sidenav por su nombre.
        
        Args:
            item_name: Nombre del item (ej: "Dashboard", "STAR & Catch Report")
        
        Returns:
            Self para method chaining
        """
        self.logger.info(f"Navegando a: {item_name}")
        self.page.locator(self.SIDENAV_ITEM, has_text=item_name).click()
        self.wait_for_load_state("networkidle")
        return self

    def click_dashboard(self) -> 'SidenavComponent':
        """
        Hace clic en el item "Dashboard".
        
        Returns:
            Self para method chaining
        """
        return self.click_item("Dashboard")

    def click_star_catch_report(self) -> 'SidenavComponent':
        """
        Hace clic en el item "STAR & Catch Report".
        
        Returns:
            Self para method chaining
        """
        return self.click_item("STAR & Catch Report")

    def click_alert_impact_quantification(self) -> 'SidenavComponent':
        """
        Hace clic en el item "Alert Impact Quantification".
        
        Returns:
            Self para method chaining
        """
        return self.click_item("Alert Impact Quantification")
