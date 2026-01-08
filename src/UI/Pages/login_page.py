"""Page Object para la página de Login de Aspen Mtell."""
from playwright.sync_api import Page
from src.UI.Pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object para la página de login.
    
    La página de login es simple con un solo botón "Log In" que
    redirige al usuario al dashboard después de la autenticación.
    """

    # Selectores (Revisar si es el selector correcto)
    LOGIN_BUTTON = "#loginbutton"

    def __init__(self, page: Page):
        """
        Inicializa LoginPage.
        
        Args:
            page: Instancia de Playwright Page
        """
        super().__init__(page)

    def navigate(self) -> 'LoginPage':
        """
        Navega a la página de login.
        
        Returns:
            Self para method chaining
        """
        self.goto("")  # BASE_URL ya apunta al login
        self.logger.info("Navegado a la página de login")
        return self

    def is_login_button_visible(self) -> bool:
        """
        Verifica si el botón de login está visible.
        
        Returns:
            True si el botón es visible, False en caso contrario
        """
        return self.is_visible(self.LOGIN_BUTTON)

    def click_login(self) -> 'LoginPage':
        """
        Hace clic en el botón de login.
        
        Nota: Este método espera a que la página se cargue completamente
        después del click ya que Angular puede tardar en inicializar.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Haciendo clic en el botón 'Log In'")
        self.click(self.LOGIN_BUTTON)
        
        # Esperar a que Angular cargue completamente
        self.wait_for_load_state("networkidle")
        
        # Esperar a que la URL cambie al dashboard
        self.wait_for_url("**/dashboard")
        
        self.logger.info("Login completado, redirigido al dashboard")
        return self

    def login(self) -> 'LoginPage':
        """
        Realiza el proceso completo de login.
        
        Returns:
            Self para method chaining
        """
        self.navigate()
        self.click_login()
        return self

    # Esto puede ir en la BasePage si es genérico
    def get_page_title(self) -> str:
        """
        Obtiene el título de la página.
        
        Returns:
            Título de la página
        """
        return self.page.title()
