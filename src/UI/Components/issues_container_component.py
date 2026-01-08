"""Componente del contenedor de Issues/Alertas."""
from playwright.sync_api import Page
from src.UI.Pages.base_page import BasePage


class IssuesContainerComponent(BasePage):
    """
    Componente reutilizable para el contenedor de issues.
    
    Contiene:
    - Header con el título "Issues: All Sites"
    - Filtros (Fecha, Tipo, Sort By, Status, Assigned To)
    - Lista de issues/alertas
    """

    # Selectores
    CONTAINER = ".alerts"
    HEADER = ".alerts-header"
    HEADER_TITLE = ".alerts-header__title h2"
    
    # Filtros
    FILTERS_CONTAINER = ".alerts-header__filters"
    DATE_FILTER = "mat-form-field:has(mat-label:text('Date'))"
    TYPE_FILTER = "mat-form-field:has(mat-label:text('Type'))"
    SORT_BY_FILTER = "mat-form-field:has(mat-label:text('Sort By'))"
    STATUS_FILTER = "mat-form-field:has(mat-label:text('Status'))"
    ASSIGNED_TO_FILTER = "mat-form-field:has(mat-label:text('Assigned To'))"
    
    # Botón de filtro de compañía
    COMPANY_FILTER_BUTTON = ".company-filter__drawer__btn"

    def __init__(self, page: Page):
        """
        Inicializa IssuesContainerComponent.
        
        Args:
            page: Instancia de Playwright Page
        """
        super().__init__(page)

    def is_visible(self) -> bool:
        """
        Verifica si el contenedor de issues está visible.
        
        Returns:
            True si el contenedor es visible
        """
        return super().is_visible(self.CONTAINER)

    def get_header_title(self) -> str:
        """
        Obtiene el texto del título del header.
        
        Returns:
            Texto del título (ej: "Issues: All Sites")
        """
        return self.get_text(self.HEADER_TITLE)

    def is_filters_container_visible(self) -> bool:
        """
        Verifica si el contenedor de filtros está visible.
        
        Returns:
            True si el contenedor de filtros es visible
        """
        return super().is_visible(self.FILTERS_CONTAINER)

    # ============================================================
    # FILTROS - Métodos
    # ============================================================

    def click_date_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el filtro de fecha.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de fecha")
        self.click(self.DATE_FILTER)
        return self

    def click_type_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el filtro de tipo.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de tipo")
        self.click(self.TYPE_FILTER)
        return self

    def click_sort_by_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el filtro de ordenamiento.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de ordenamiento")
        self.click(self.SORT_BY_FILTER)
        return self

    def click_status_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el filtro de estado.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de estado")
        self.click(self.STATUS_FILTER)
        return self

    def click_assigned_to_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el filtro de asignado a.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de asignado a")
        self.click(self.ASSIGNED_TO_FILTER)
        return self

    def click_company_filter(self) -> 'IssuesContainerComponent':
        """
        Hace clic en el botón de filtro de compañía.
        
        Returns:
            Self para method chaining
        """
        self.logger.info("Click en filtro de compañía")
        self.click(self.COMPANY_FILTER_BUTTON)
        return self

    def is_date_filter_visible(self) -> bool:
        """
        Verifica si el filtro de fecha está visible.
        
        Returns:
            True si el filtro es visible
        """
        return super().is_visible(self.DATE_FILTER)

    def is_type_filter_visible(self) -> bool:
        """
        Verifica si el filtro de tipo está visible.
        
        Returns:
            True si el filtro es visible
        """
        return super().is_visible(self.TYPE_FILTER)

    def is_sort_by_filter_visible(self) -> bool:
        """
        Verifica si el filtro de ordenamiento está visible.
        
        Returns:
            True si el filtro es visible
        """
        return super().is_visible(self.SORT_BY_FILTER)

    def is_status_filter_visible(self) -> bool:
        """
        Verifica si el filtro de estado está visible.
        
        Returns:
            True si el filtro es visible
        """
        return super().is_visible(self.STATUS_FILTER)

    def is_assigned_to_filter_visible(self) -> bool:
        """
        Verifica si el filtro de asignado a está visible.
        
        Returns:
            True si el filtro es visible
        """
        return super().is_visible(self.ASSIGNED_TO_FILTER)
