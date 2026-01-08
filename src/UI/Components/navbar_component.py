"""Componente de la barra de navegación superior (Navbar)."""
from playwright.sync_api import Page
from src.UI.Pages.base_page import BasePage


class NavbarComponent(BasePage):
    """
    Componente reutilizable para la barra de navegación superior.
    
    Contiene:
    - Botón de menú
    - Logo de la compañía
    - Título de la aplicación
    - Herramientas de administrador
    - Ayuda
    - Toggle de tema
    - Menú de perfil de usuario
    """

    # Selectores
    NAVBAR = "nav.navbar"
    MENU_BUTTON = "#menu-btn"
    LOGO = ".navbar__logo"
    TITLE = ".navbar__title"
    ADMIN_TOOLS_BUTTON = "[data-testid='admin-tool-button']"
    HELP_BUTTON = "[data-testid='help-button']"
    THEME_TOGGLE_BUTTON = "[data-testid='toggle-theme-button']"
    PROFILE_MENU_BUTTON = "[data-testid='profile-menu']"

    def __init__(self, page: Page):
        """
        Inicializa NavbarComponent.
        
        Args:
            page: Instancia de Playwright Page
        """
        super().__init__(page)

    def is_visible(self) -> bool:
        """
        Verifica si la navbar está visible.
        
        Returns:
            True si la navbar es visible
        """
        return super().is_visible(self.NAVBAR)

    def click_menu(self) -> 'NavbarComponent':
        """
        Hace clic en el botón de menú.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en botón de menú")
        self.click(self.MENU_BUTTON)
        return self

    def click_admin_tools(self) -> 'NavbarComponent':
        """
        Hace clic en herramientas de administrador.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en herramientas de administrador")
        self.click(self.ADMIN_TOOLS_BUTTON)
        return self

    def click_help(self) -> 'NavbarComponent':
        """
        Hace clic en el botón de ayuda.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en ayuda")
        self.click(self.HELP_BUTTON)
        return self

    def toggle_theme(self) -> 'NavbarComponent':
        """
        Hace clic en el toggle de tema.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Toggle de tema")
        self.click(self.THEME_TOGGLE_BUTTON)
        return self

    def click_profile_menu(self) -> 'NavbarComponent':
        """
        Hace clic en el menú de perfil.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en menú de perfil")
        self.click(self.PROFILE_MENU_BUTTON)
        return self

    def get_title(self) -> str:
        """
        Obtiene el título de la aplicación.
        
        Returns:
            Texto del título
        """
        return self.get_text(self.TITLE)
