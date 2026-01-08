"""Page Object para el Dashboard de Aspen Mtell."""
from playwright.sync_api import Page
from src.UI.Pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object para el Dashboard principal.
    
    El dashboard contiene:
    - Navbar superior con botones de menú, ayuda, tema y usuario
    - Sidenav lateral con opciones de navegación
    - Contenedor de issues con filtros y alertas
    """

    # Selectores - Navbar (estos selectores podrian ir en la basepage o en un componente separado)
    NAVBAR = "nav.navbar"
    MENU_BUTTON = "#menu-btn"
    ADMIN_TOOLS_BUTTON = "[data-testid='admin-tool-button']"
    HELP_BUTTON = "[data-testid='help-button']"
    THEME_TOGGLE_BUTTON = "[data-testid='toggle-theme-button']"
    PROFILE_MENU_BUTTON = "[data-testid='profile-menu']"
    NAVBAR_TITLE = ".navbar__title"
    
    # Selectores - Sidenav (estos selectores podrian ir en la basepage o en un componente separado)
    SIDENAV = "mat-sidenav"
    SIDENAV_CLOSE_BUTTON = ".sidenav-button"
    SIDENAV_ITEM = ".sidenav-item"
    SIDENAV_ITEM_SELECTED = ".sidenav-item--selected"
    
    # Selectores - Dashboard Content
    DASHBOARD_CONTAINER = "app-dashboard"
    ISSUES_HEADER = ".alerts-header__title h2"
    COMPANY_FILTER_BUTTON = ".company-filter__drawer__btn"
    
    # Selectores - Filtros
    DATE_FILTER = "mat-form-field:has(mat-label:text('Date'))"
    TYPE_FILTER = "mat-form-field:has(mat-label:text('Type'))"
    SORT_BY_FILTER = "mat-form-field:has(mat-label:text('Sort By'))"
    STATUS_FILTER = "mat-form-field:has(mat-label:text('Status'))"
    ASSIGNED_TO_FILTER = "mat-form-field:has(mat-label:text('Assigned To'))"

    def __init__(self, page: Page):
        """
        Inicializa DashboardPage.
        
        Args:
            page: Instancia de Playwright Page
        """
        super().__init__(page)

    def navigate(self) -> 'DashboardPage':
        """
        Navega al dashboard.
        
        Returns:
            Self para method chaining
        """
        self.goto("#/dashboard")
        self.wait_for_load_state("networkidle")
        self.logger.info("Navegado al dashboard")
        return self

    # ============================================================
    # NAVBAR - Métodos (tal vez estos métodos deban ir en un componente separado o en la BasePage)
    # ============================================================

    def is_navbar_visible(self) -> bool:
        """
        Verifica si la navbar está visible.
        
        Returns:
            True si la navbar es visible
        """
        return self.is_visible(self.NAVBAR)

    def click_menu_button(self) -> 'DashboardPage':
        """
        Hace clic en el botón de menú para abrir el sidenav.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo sidenav")
        self.click(self.MENU_BUTTON)
        self.wait_for_selector(self.SIDENAV, state="visible")
        return self

    def click_admin_tools(self) -> 'DashboardPage':
        """
        Hace clic en el botón de herramientas de administrador.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo herramientas de administrador")
        self.click(self.ADMIN_TOOLS_BUTTON)
        return self

    def click_help_button(self) -> 'DashboardPage':
        """
        Hace clic en el botón de ayuda.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo ayuda")
        self.click(self.HELP_BUTTON)
        return self

    def click_theme_toggle(self) -> 'DashboardPage':
        """
        Hace clic en el botón para cambiar el tema.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Cambiando tema")
        self.click(self.THEME_TOGGLE_BUTTON)
        return self

    def click_profile_menu(self) -> 'DashboardPage':
        """
        Hace clic en el menú de perfil de usuario.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo menú de perfil")
        self.click(self.PROFILE_MENU_BUTTON)
        return self

    def get_navbar_title(self) -> str:
        """
        Obtiene el título de la navbar.
        
        Returns:
            Texto del título de la navbar
        """
        return self.get_text(self.NAVBAR_TITLE)

    # ============================================================
    # SIDENAV - Métodos (tal vez estos métodos deban ir en un componente separado o en la BasePage)
    # ============================================================

    def is_sidenav_open(self) -> bool:
        """
        Verifica si el sidenav está abierto.
        
        Returns:
            True si el sidenav está visible
        """
        return self.is_visible(self.SIDENAV)

    def close_sidenav(self) -> 'DashboardPage':
        """
        Cierra el sidenav.
        
        Returns:
            Self para method chaining
        """
        if self.is_sidenav_open():
            self.logger.info("Cerrando sidenav")
            self.click(self.SIDENAV_CLOSE_BUTTON)
            self.wait_for_selector(self.SIDENAV, state="hidden")
        return self

    def get_sidenav_items(self) -> list[str]:
        """
        Obtiene la lista de items del sidenav.
        
        Returns:
            Lista de textos de los items del sidenav
        """
        items = []
        count = self.count_elements(self.SIDENAV_ITEM)
        for i in range(count):
            text = self.get_locator(self.SIDENAV_ITEM).nth(i).inner_text()
            items.append(text.strip())
        return items

    def click_sidenav_item(self, item_name: str) -> 'DashboardPage':
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

    def get_selected_sidenav_item(self) -> str:
        """
        Obtiene el item actualmente seleccionado del sidenav.
        
        Returns:
            Texto del item seleccionado
        """
        return self.get_text(self.SIDENAV_ITEM_SELECTED)

    # ============================================================
    # DASHBOARD CONTENT - Métodos 
    # ============================================================

    def is_dashboard_loaded(self) -> bool:
        """
        Verifica si el dashboard está cargado.
        
        Returns:
            True si el contenedor del dashboard está visible
        """
        return self.is_visible(self.DASHBOARD_CONTAINER)

    def get_issues_header_text(self) -> str:
        """
        Obtiene el texto del header de issues.
        
        Returns:
            Texto del header (ej: "Issues: All Sites")
        """
        return self.get_text(self.ISSUES_HEADER)

    def click_company_filter(self) -> 'DashboardPage':
        """
        Hace clic en el botón de filtro de compañía.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de compañía")
        self.click(self.COMPANY_FILTER_BUTTON)
        return self

    # ============================================================
    # FILTROS - Métodos
    # ============================================================

    def is_date_filter_visible(self) -> bool:
        """
        Verifica si el filtro de fecha está visible.
        
        Returns:
            True si el filtro es visible
        """
        return self.is_visible(self.DATE_FILTER)

    def is_type_filter_visible(self) -> bool:
        """
        Verifica si el filtro de tipo está visible.
        
        Returns:
            True si el filtro es visible
        """
        return self.is_visible(self.TYPE_FILTER)

    def click_date_filter(self) -> 'DashboardPage':
        """
        Hace clic en el filtro de fecha.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de fecha")
        self.click(self.DATE_FILTER)
        return self

    def click_type_filter(self) -> 'DashboardPage':
        """
        Hace clic en el filtro de tipo.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de tipo")
        self.click(self.TYPE_FILTER)
        return self

    def click_sort_by_filter(self) -> 'DashboardPage':
        """
        Hace clic en el filtro de ordenamiento.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de ordenamiento")
        self.click(self.SORT_BY_FILTER)
        return self

    def click_status_filter(self) -> 'DashboardPage':
        """
        Hace clic en el filtro de estado.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de estado")
        self.click(self.STATUS_FILTER)
        return self

    def click_assigned_to_filter(self) -> 'DashboardPage':
        """
        Hace clic en el filtro de asignado a.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Abriendo filtro de asignado a")
        self.click(self.ASSIGNED_TO_FILTER)
        return self
