"""Test de ejemplo para validar el framework."""
import pytest
from playwright.sync_api import Page, sync_playwright
from src.UI.Pages.login_page import LoginPage
from src.UI.Pages.dashboard_page import DashboardPage


def test_login_and_dashboard():
    """
    Test de ejemplo que valida el login y navegación básica.
    
    Este test demuestra:
    1. Login exitoso
    2. Verificación del dashboard
    3. Apertura del sidenav
    4. Navegación entre secciones
    """
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 1. Login
            print("\n1. Realizando login...")
            login_page = LoginPage(page)
            login_page.login()
            
            # Verificar que estamos en el dashboard
            assert "#/dashboard" in page.url, "No se redirigió al dashboard"
            print("✓ Login exitoso")
            
            # 2. Dashboard
            print("\n2. Validando dashboard...")
            dashboard = DashboardPage(page)
            
            # Verificar que el dashboard está cargado
            assert dashboard.is_dashboard_loaded(), "Dashboard no cargó"
            print("✓ Dashboard cargado")
            
            # Verificar navbar
            assert dashboard.is_navbar_visible(), "Navbar no visible"
            print("✓ Navbar visible")
            
            # Obtener título del header de issues
            issues_title = dashboard.get_issues_header_text()
            print(f"✓ Issues header: '{issues_title}'")
            assert "Issues" in issues_title
            
            # 3. Abrir sidenav
            print("\n3. Abriendo sidenav...")
            dashboard.click_menu_button()
            assert dashboard.is_sidenav_open(), "Sidenav no se abrió"
            print("✓ Sidenav abierto")
            
            # Obtener items del menú
            items = dashboard.get_sidenav_items()
            print(f"✓ Items del menú: {items}")
            assert len(items) == 3, f"Se esperaban 3 items, encontrados {len(items)}"
            assert "Dashboard" in items
            assert "STAR & Catch Report" in items
            
            # Verificar item seleccionado
            selected = dashboard.get_selected_sidenav_item()
            print(f"✓ Item seleccionado: '{selected}'")
            assert "Dashboard" in selected
            
            # 4. Navegar a otra sección
            print("\n4. Navegando a STAR & Catch Report...")
            dashboard.click_sidenav_item("STAR & Catch Report")
            
            # Verificar cambio de URL
            assert "star-catch-report" in page.url, "No navegó a STAR & Catch Report"
            print("✓ Navegación exitosa")
            
            print("\n✅ Todos los tests pasaron exitosamente!")
            
        finally:
            # Cerrar navegador
            browser.close()


if __name__ == "__main__":
    test_login_and_dashboard()
