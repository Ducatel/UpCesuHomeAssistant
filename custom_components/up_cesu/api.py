"""Playwright client for the Up CESU website.

This module provides the UpCesuClient class to interact with the Up CESU website
using Playwright for browser automation. This is necessary because the site uses
Cloudflare anti-bot protection which blocks direct HTTP requests.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright, TimeoutError as PlaywrightTimeoutError

from .const import BASE_URL, CONF_CODE_CESU, CONF_PASSWORD, PLAYWRIGHT_TIMEOUT

# Logger for API-related operations
_LOGGER = logging.getLogger(__name__)


class UpCesuApiError(Exception):
    """Base exception for Up CESU API errors."""


class UpCesuAuthenticationError(UpCesuApiError):
    """Exception raised when Up CESU credentials are rejected."""


class UpCesuClient:
    """Client for interacting with the Up CESU website using Playwright.

    This class handles authentication and data scraping to retrieve
    e-CESU and paper CESU balance information.

    Attributes:
        _code_cesu: User code CESU for authentication.
        _password: User password for authentication.
    """

    def __init__(
        self,
        code_cesu: str,
        password: str,
    ) -> None:
        """Initialize the Up CESU client.

        Args:
            code_cesu: User code CESU for authentication.
            password: User password for authentication.
        """
        self._code_cesu = code_cesu
        self._password = password

    async def async_fetch(self) -> dict[str, Any]:
        """Fetch balance data from Up CESU website using Playwright.

        This method:
        1. Initializes Playwright browser.
        2. Navigates to the Up CESU website.
        3. Handles cookie consent modal.
        4. Authenticates with code CESU and password.
        5. Extracts e-CESU and paper CESU balances from the dashboard.

        Returns:
            dict: Data containing:
                - e_cesu_balance: Current e-CESU balance in €.
                - paper_cesu_balance: Current paper CESU balance in €.
                - generated_at: Timestamp of when the data was fetched.

        Raises:
            UpCesuAuthenticationError: If authentication fails.
            UpCesuApiError: If there is an issue with the website or scraping.
        """
        _LOGGER.debug("Starting async_fetch for code CESU: %s", self._code_cesu)

        playwright: Playwright | None = None
        browser: Browser | None = None
        context: BrowserContext | None = None
        page: Page | None = None

        try:
            # Initialize Playwright
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(PLAYWRIGHT_TIMEOUT)

            _LOGGER.debug("Playwright initialized successfully")

            # Navigate to the Up CESU website
            await page.goto(BASE_URL)
            _LOGGER.debug("Navigated to Up CESU website")

            # Handle cookie consent modal
            await self._handle_cookie_consent(page)
            _LOGGER.debug("Cookie consent handled")

            # Authenticate
            await self._async_login(page)
            _LOGGER.debug("Login successful")

            # Extract balances from the dashboard
            balances = await self._extract_balances(page)
            _LOGGER.debug("Balances extracted: %s", balances)

            return balances

        except PlaywrightTimeoutError as err:
            _LOGGER.error("Playwright timeout error: %s", err)
            raise UpCesuApiError(f"Timeout while accessing Up CESU website: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error during async_fetch: %s", err)
            raise UpCesuApiError(f"Error fetching Up CESU data: {err}") from err
        finally:
            # Clean up Playwright resources
            if page:
                await page.close()
            if context:
                await context.close()
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

    async def _handle_cookie_consent(self, page: Page) -> None:
        """Handle the cookie consent modal if it appears.

        Args:
            page: Playwright Page instance.
        """
        try:
            # Check if the cookie consent modal is visible
            cookie_modal = page.locator("text=Accepter & Fermer")
            cookie_modal_count = await cookie_modal.count()
            if cookie_modal_count > 0:
                await cookie_modal.click()
                _LOGGER.debug("Cookie consent modal accepted")
                # Wait for the modal to disappear
                await page.wait_for_selector("text=Accepter & Fermer", state="hidden", timeout=5000)
        except Exception as err:
            _LOGGER.warning("Failed to handle cookie consent: %s", err)

    async def _async_login(self, page: Page) -> None:
        """Authenticate with the Up CESU website.

        This method:
        1. Enters the code CESU.
        2. Clicks "Etape suivante".
        3. Enters the password.
        4. Clicks "Se connecter".

        Args:
            page: Playwright Page instance.

        Raises:
            UpCesuAuthenticationError: If credentials are invalid.
            UpCesuApiError: If there is an issue with the login process.
        """
        try:
            # Step 1: Enter code CESU
            code_input = page.get_by_role("textbox", name="12345")
            await code_input.fill(self._code_cesu)
            _LOGGER.debug("Code CESU entered")

            # Click "Etape suivante"
            next_button = page.get_by_role("button", name="Etape suivante")
            await next_button.click()
            _LOGGER.debug("Clicked Etape suivante")

            # Wait for password field to appear
            await page.wait_for_selector("text=Mon mot de passe", timeout=10000)

            # Step 2: Enter password
            password_input = page.get_by_role("textbox", name="Mon mot de passe")
            await password_input.fill(self._password)
            _LOGGER.debug("Password entered")

            # Click "Se connecter"
            login_button = page.get_by_role("button", name="Se connecter")
            await login_button.click()
            _LOGGER.debug("Clicked Se connecter")

            # Wait for dashboard to load (check for "Tableau de bord" or balance elements)
            await page.wait_for_selector("text=Tableau de bord", timeout=10000)
            _LOGGER.debug("Dashboard loaded successfully")

        except PlaywrightTimeoutError as err:
            _LOGGER.error("Login timeout or invalid credentials: %s", err)
            raise UpCesuAuthenticationError("Invalid code CESU or password") from err
        except Exception as err:
            _LOGGER.error("Login error: %s", err)
            raise UpCesuApiError(f"Error during login: {err}") from err

    async def _extract_balances(self, page: Page) -> dict[str, Any]:
        """Extract e-CESU and paper CESU balances from the dashboard.

        Args:
            page: Playwright Page instance.

        Returns:
            dict: Data containing:
                - e_cesu_balance: Current e-CESU balance in €.
                - paper_cesu_balance: Current paper CESU balance in €.
                - generated_at: Timestamp of when the data was fetched.

        Raises:
            UpCesuApiError: If there is an issue extracting the balances.
        """
        try:
            # Extract e-CESU balance
            e_cesu_parent = page.locator("text=Mon solde en e-CESU")
            e_cesu_strong = e_cesu_parent.locator("..").locator("strong")
            e_cesu_text = await e_cesu_strong.text_content()
            e_cesu_text = e_cesu_text or "0,00 €"
            e_cesu_balance = float(e_cesu_text.replace(" ", "").replace("€", "").replace(",", ".").strip())
            _LOGGER.debug("e-CESU balance extracted: %s", e_cesu_balance)

            # Extract paper CESU balance
            paper_cesu_parent = page.locator("text=Mon solde en chèques papier")
            paper_cesu_strong = paper_cesu_parent.locator("..").locator("strong")
            paper_cesu_text = await paper_cesu_strong.text_content()
            paper_cesu_text = paper_cesu_text or "0,00 €"
            paper_cesu_balance = float(paper_cesu_text.replace(" ", "").replace("€", "").replace(",", ".").strip())
            _LOGGER.debug("Paper CESU balance extracted: %s", paper_cesu_balance)

            return {
                "e_cesu_balance": e_cesu_balance,
                "paper_cesu_balance": paper_cesu_balance,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as err:
            _LOGGER.error("Failed to extract balances: %s", err)
            raise UpCesuApiError(f"Error extracting balances: {err}") from err
