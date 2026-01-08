"""Configuración centralizada del framework."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Configuración de la aplicación."""
    
    # URLs
    BASE_URL = os.getenv("BASE_URL", "https://azqamtell06.qae.aspentech.com/Aspentech/AspenMtell/AlertManager/")
    
    # Timeouts (en milisegundos)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # 30 segundos
    SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", "5000"))      # 5 segundos
    LONG_TIMEOUT = int(os.getenv("LONG_TIMEOUT", "60000"))       # 60 segundos
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "45000"))  # 45 segundos
    
    # Playwright
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/test.log"
    
    @classmethod
    def validate(cls):
        """Valida que la configuración sea correcta."""
        if not cls.BASE_URL:
            raise ValueError("BASE_URL no está configurada en .env")
        if cls.DEFAULT_TIMEOUT <= 0:
            raise ValueError("DEFAULT_TIMEOUT debe ser mayor a 0")


# Validar al importar
Settings.validate()
