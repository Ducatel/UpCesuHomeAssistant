# Up CESU Home Assistant Integration

[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Ducatel/UpCesuHomeAssistant)](https://github.com/Ducatel/UpCesuHomeAssistant/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A **custom Home Assistant integration** for monitoring your **Up CESU** balances (e-CESU and paper CESU) through sensors.

## Features

- **Two sensors**:
  - `sensor.up_cesu_<code_cesu>_e_cesu_balance` - Current e-CESU balance in €
  - `sensor.up_cesu_<code_cesu>_paper_cesu_balance` - Current paper CESU balance in €
- **Automatic updates**: Data is refreshed every 6 hours (configurable)
- **Secure authentication**: Uses your Up CESU code and password
- **HACS compatible**: Easy installation via HACS
- **Docker support**: Works with official Home Assistant Docker image

## Requirements

- Home Assistant 2024.10.0 or later
- Playwright 1.40.0 or later (for browser automation)

## Installation

### Option 1: Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Go to **Integrations** tab
3. Click **Add** and search for "Up CESU"
4. Click **Install**
5. Restart Home Assistant
6. Add the integration via **Settings > Devices & Services > Add Integration > Up CESU**

### Option 2: Manual Installation

1. Copy the `custom_components/up_cesu` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration via **Settings > Devices & Services > Add Integration > Up CESU**

## Configuration

1. After installation, go to **Settings > Devices & Services**
2. Click **Add Integration**
3. Search for and select **Up CESU**
4. Enter your **Code CESU** and **Password**
5. Click **Submit**

The integration will validate your credentials and create two sensors:
- One for your e-CESU balance
- One for your paper CESU balance

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| Code CESU | string | required | Your Up CESU code |
| Password | string | required | Your Up CESU password |

## Usage

Once configured, the sensors will appear in your Home Assistant and can be used in:

- **Dashboards**: Add the sensors to any Lovelace dashboard
- **Automations**: Trigger automations based on balance changes
- **Templates**: Use in template sensors or other integrations
- **Notifications**: Get alerts when balance is low

### Example Automation

```yaml
automation:
  - alias: "Notify when e-CESU balance is low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.up_cesu_12345_e_cesu_balance
        below: 50
    action:
      - service: notify.notify
        data:
          message: "Your e-CESU balance is below 50€!"
```

## Troubleshooting

### Authentication Failed

**Error**: "Invalid code CESU or password"

**Solution**:
- Verify your code CESU and password are correct
- Check if Up CESU website is accessible
- Try logging in manually at https://monespace-cheque-domicile.up.coop/beneficiaire/

### Sensors Showing as Unavailable

**Error**: Sensors show "Unavailable" state

**Solution**:
- Check Home Assistant logs for errors
- Enable debug logging for the integration:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.up_cesu: debug
  ```
- Verify your internet connection
- Check if the Up CESU website has changed its structure

### Playwright Issues

**Error**: "Playwright browsers not installed"

**Solution**:
```bash
# Install Playwright browsers
playwright install
```

## Development

### Setup

```bash
# Create virtual environment
uv venv .venv

# Activate environment
# Windows: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install homeassistant

# Install Playwright browsers
playwright install
```

### Running Tests

```bash
# Install test dependencies
uv pip install -r tests/requirements.txt

# Run all tests
uv run pytest tests/ -v -s

# Run specific test
uv run pytest tests/test_api.py::test_real_api_call -v -s
```

### Project Structure

```
UpCesuHomeAssistant/
├── custom_components/
│   └── up_cesu/
│       ├── __init__.py          # Integration setup/teardown
│       ├── api.py               # API client (Playwright-based)
│       ├── config_flow.py       # Configuration UI flow
│       ├── const.py             # Constants
│       ├── coordinator.py       # Data update coordinator
│       ├── sensor.py            # Sensor entities
│       ├── manifest.json        # Integration metadata
│       ├── strings.json         # English strings
│       ├── translations/
│       │   └── fr.json          # French strings
│       └── brand/
│           └── icon.png         # Integration icon
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API tests
│   ├── test_coordinator.py     # Coordinator tests
│   └── test_sensor.py          # Sensor tests
├── requirements.txt            # Development dependencies
├── tests/requirements.txt      # Test dependencies
├── pytest.ini                 # Pytest configuration
├── README.md                  # This file
├── AGENTS.md                  # AI agent guide
└── .gitignore
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Ducatel/UpCesuHomeAssistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ducatel/UpCesuHomeAssistant/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## Credits

- **Author**: Ducatel
- **Inspiration**: Shiva Home Assistant integration
- **Dependencies**: Playwright, Home Assistant

---

*This integration is not officially affiliated with Up CESU or Up Coop.*
