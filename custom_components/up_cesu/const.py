"""Constants for the Up CESU integration.

This module defines constants used across the Up CESU Home Assistant integration,
including configuration keys and update intervals.
"""

from datetime import timedelta

# Domain name for this integration (used in entity IDs, service names, etc.)
DOMAIN = "up_cesu"

# Configuration entry keys
CONF_CODE_CESU = "code_cesu"  # User code CESU for Up authentication
CONF_PASSWORD = "password"    # User password for Up authentication

# How often to refresh data from the Up CESU website (default: every 6 hours)
UPDATE_INTERVAL = timedelta(hours=6)

# Base URL for the Up CESU website
BASE_URL = "https://monespace-cheque-domicile.up.coop/beneficiaire/"

# Timeout for Playwright operations (in milliseconds)
PLAYWRIGHT_TIMEOUT = 30000
