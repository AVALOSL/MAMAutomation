from typing import Optional
from playwright.sync_api import Page, Locator

class BasePage: 
#Base class for all page objects in the application.

    def __init__(self, page: Page):
        self.page = page
        # Line pending for Login
        # Line pending for Settings
    def goto(self, url: str) -> None:
            #Navigate to a specified URL."""
        self.page.goto(url)
        return self
    def get_current_url(self) -> str:
        #Get the current URL of the page."""
        return self.page.url
    def click_element(self, selector: str) -> 'BasePage':
        #Click an element specified by the selector."""
        self.page.locator(selector).click()
        return self
    