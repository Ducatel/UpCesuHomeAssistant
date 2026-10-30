# Up CESU Home Assistant Integration - Agent Guide

This document helps AI agents (like opencode) understand how to work with this repository.

## 📦 Project Overview

This is a **custom Home Assistant integration** for **Up CESU**, a French service for managing CESU (Chèque Emploi Service Universel) balances. The integration allows users to monitor their e-CESU and paper CESU balances through Home Assistant sensors.

## 🛠️ Development Environment

### Package Manager
- **Tool**: `uv` (Ultra-fast Python package manager)
- **Website**: https://github.com/astral-sh/uv
- **Installation**: 
  - **Linux/macOS**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - **Windows (PowerShell)**: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

### Virtual Environment
- **Tool**: Python venv managed by `uv`
- **Location**: `.venv/` in the project root
- **Activation**:
  - **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
  - **Linux/macOS (bash)**: `source .venv/bin/activate`

### Python Version
- **Required**: Python 3.10+
- **Recommended**: Python 3.12 (used in development)

### Docker Target
- **Image**: Official Home Assistant Docker image (`ghcr.io/home-assistant/home-assistant:stable`)
- **Usage**: This integration is designed to work within the official Home Assistant container
- **Testing**: Use `homeassistant` package from PyPI for local testing (latest stable version)

## 📁 Project Structure

```
UpCesuHomeAssistant/
├── custom_components/
│   └── up_cesu/
│       ├── __init__.py          # Integration setup/teardown
│       ├── api.py               # API client for Up CESU (Playwright-based)
│       ├── config_flow.py       # Configuration UI flow
│       ├── const.py             # Constants and configuration keys
│       ├── coordinator.py       # Data update coordinator
│       ├── sensor.py            # Sensor platform implementation
│       ├── manifest.json       # Integration metadata
│       ├── strings.json         # English strings
│       ├── translations/
│       │   └── fr.json          # French strings
│       └── brand/
│           └── icon.png         # Integration icon
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # Tests for API client
│   ├── test_coordinator.py     # Tests for coordinator
│   └── test_sensor.py          # Tests for sensors
│   └── requirements.txt        # Test dependencies
├── requirements.txt            # Development dependencies
├── AGENTS.md                  # This file - for AI agents
├── README.md                  # User documentation
└── .venv/                     # Virtual environment (excluded from git)
```

## 🚀 Common Commands

### Setup Development Environment
```powershell
# Create virtual environment with uv
uv venv .venv

# Activate the virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Activate the virtual environment (Linux/macOS)
source .venv/bin/activate

# Install development dependencies
uv pip install playwright pytest pytest-asyncio

# Install Playwright browsers
playwright install
```

### Install Home Assistant for Testing
```powershell
# Install Home Assistant (latest stable version)
uv pip install homeassistant
```

### Run Tests
```powershell
# Install test dependencies
uv pip install -r tests/requirements.txt

# Run all tests (Windows)
uv run pytest tests/ -v

# Run all tests (Linux/macOS)
uv run pytest tests/ -v

# Run tests with shorter output
uv run pytest tests/ -v --tb=short

# Run specific test file
uv run pytest tests/test_api.py -v

# Run specific test
uv run pytest tests/test_api.py::test_async_login_success -v
```

### Run Linting/Type Checking
```powershell
# Note: This project doesn't currently have linting configured
# If you want to add it, consider:
# - ruff for linting
# - mypy for type checking
```

## 📝 Key Files and Their Purpose

### `custom_components/up_cesu/const.py`
- Contains all constants used by the integration
- Base URLs, configuration keys
- **Important**: `UPDATE_INTERVAL = timedelta(hours=6)` (6 hours)

### `custom_components/up_cesu/api.py`
- **UpCesuClient**: Main client class using Playwright
  - Handles authentication via form-based login
  - Manages cookie consent (Cloudflare protection)
  - Scrapes balance data from dashboard HTML
- **Authentication Flow**:
  1. Navigate to login page
  2. Handle Cloudflare cookie consent if present
  3. Submit code CESU
  4. Submit password
  5. Extract balances from dashboard
- **Key Methods**:
  - `async_fetch()`: Main method to fetch balance data
  - `_async_login()`: Handle authentication
  - `_extract_balances()`: Parse HTML to extract balances

### `custom_components/up_cesu/coordinator.py`
- **UpCesuDataUpdateCoordinator**: Manages data updates
- Inherits from Home Assistant's `DataUpdateCoordinator`
- **Update Interval**: 6 hours (configurable)
- **Key Methods**:
  - `_async_update_data()`: Fetch and update data

### `custom_components/up_cesu/sensor.py`
- **UpCesuSensor**: Sensor entity for Home Assistant
- Creates sensors for: e-CESU balance, paper CESU balance
- **Key Features**:
  - Extracts values from coordinator data
  - Handles availability

### `custom_components/up_cesu/config_flow.py`
- **ConfigFlow**: Handles integration configuration via UI
- **Key Features**:
  - Validates credentials before creating config entry
  - Sets unique ID based on code CESU
  - Prevents duplicate configurations

### `custom_components/up_cesu/__init__.py`
- Integration setup and teardown
- **Key Functions**:
  - `async_setup_entry()`: Set up integration from config entry
  - `async_unload_entry()`: Clean up integration

## 🔧 Configuration

### Integration Configuration
- **Required**: Code CESU and password
- **Update Interval**: 6 hours (default, configurable in const.py)

### Sensor Types
- `sensor.up_cesu_<code_cesu>_e_cesu_balance`: e-CESU balance in €
- `sensor.up_cesu_<code_cesu>_paper_cesu_balance`: Paper CESU balance in €

## 🧪 Testing

### Test Dependencies
- pytest>=7.0.0
- pytest-asyncio>=0.21.0
- playwright>=1.40.0
- homeassistant (latest stable version)

### Running Tests in CI
```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv pip install -r tests/requirements.txt
      - name: Install Playwright browsers
        run: playwright install
      - name: Run tests
        run: uv run pytest tests/ -v
```

## 🐛 Debugging

### Enable Debug Logging in Home Assistant
1. Go to **Settings** > **System** > **Logging**
2. Add a new logger:
   - Logger: `custom_components.up_cesu`
   - Level: Debug

### Common Issues

#### Authentication Failures
- **Cause**: Invalid credentials, Cloudflare protection, site changes
- **Debug**: Check logs for "Cloudflare", "cookie consent", "Login failed"
- **Solution**: Verify credentials, check if Up CESU changed their login flow

#### Playwright Issues
- **Cause**: Missing browsers, timeout, headless mode issues
- **Debug**: Check logs for "Playwright", "browser", "timeout"
- **Solution**: Run `playwright install`, check Docker environment

#### Sensors Showing as Unavailable
- **Cause**: `coordinator.last_update_success` is False or `native_value` is None
- **Debug**: Check if data fetch succeeded in logs
- **Note**: Sensors with value 0 are considered available

## 🔒 Security Considerations

### Sensitive Data
- **Never log**: Passwords, full HTML responses with personal data
- **Masked in logs**: Passwords are logged as `[REDACTED]`

### Credentials Storage
- Stored in Home Assistant's config entries (encrypted at rest in HA)
- Not logged or exposed in frontend

## 📝 Release Process

1. Update version in `manifest.json`
2. Update changelog in README.md
3. Test with real Up CESU credentials
4. Commit changes with message following [Conventional Commits](https://www.conventionalcommits.org/)
5. Create GitHub release
6. Submit to HACS (if applicable)

## 🤖 AI Agent Tips

### When Working on This Repo:
1. **Always check `const.py` first** - Most configuration is there
2. **Use `uv` for package management** - Don't use pip directly
3. **Activate the venv** before running commands
4. **Install Home Assistant** for testing: `uv pip install homeassistant`
5. **Install Playwright browsers**: `playwright install`
6. **Run tests** to verify changes: `uv run pytest tests/ -v`

### Common Tasks:
- **Adding a new sensor**: Update sensor descriptions in `sensor.py`
- **Changing update frequency**: Change `UPDATE_INTERVAL` in `const.py`
- **Modifying authentication**: Update `api.py`
- **Adding configuration options**: Update `config_flow.py` and `const.py`

### Debugging Tips:
- **Check logs** for `custom_components.up_cesu`
- **Enable debug logging** in Home Assistant
- **Test with real credentials** to verify authentication flow
- **Verify HTML structure** if scraping fails (site may have changed)

## 📞 Support

- **Issues**: https://github.com/Ducatel/UpCesuHomeAssistant/issues
- **Documentation**: https://github.com/Ducatel/UpCesuHomeAssistant
- **Home Assistant Community**: https://community.home-assistant.io/

## 🐳 Docker Considerations

### Playwright in Docker
When running this integration in the official Home Assistant Docker container:

1. **Playwright browsers** must be installed in the container
2. **Required packages** in Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y \
       # Playwright dependencies
       libnss3 \
       libnspr4 \
       libatk1.0-0 \
       libatk-bridge2.0-0 \
       libcups2 \
       libdrm2 \
       libdbus-1-3 \
       libxkbcommon0 \
       libatspi2.0-0 \
       libxcomposite1 \
       libxdamage1 \
       libxfixes3 \
       libxrandr2 \
       libgbm1 \
       libasound2 \
       libpango-1.0-0 \
       libcairo2 \
   ```

3. **Install Playwright browsers** during container build:
   ```dockerfile
   RUN playwright install chromium
   ```

4. **Set appropriate flags** for headless Chromium:
   ```python
   browser = await playwright.chromium.launch(
       headless=True,
       args=['--no-sandbox', '--disable-setuid-sandbox']
   )
   ```

### Testing in Docker
To test the integration in a Docker environment:
```bash
# Build custom Home Assistant image with Playwright
docker build -t homeassistant-upcesu .

# Run container
docker run -d --name homeassistant \
  -v /path/to/config:/config \
  -v /path/to/UpCesuHomeAssistant/custom_components:/config/custom_components/up_cesu \
  --restart unless-stopped \
  homeassistant-upcesu
```
