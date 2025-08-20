# Govee Light Automation for Home Assistant

This is a custom integration for Home Assistant that allows you to control your Govee smart lights using the Govee API.

## Features

- Control Govee smart lights from Home Assistant
- Full RGB color control
- Brightness control
- Power on/off functionality
- Automatic device discovery
- Real-time state updates
- **Smart Rate Limiting**: Prevents hitting the 10,000 requests/day API limit
- **Adaptive Polling**: Automatically adjusts polling intervals based on device count and usage
- **Rate Limit Monitoring**: Built-in sensors to track API usage and device count
- **Daily Reset**: Automatic daily reset of request counters

## Prerequisites

1. **Govee API Key**: You need to obtain an API key from Govee's developer portal
2. **Home Assistant**: This integration requires Home Assistant Core or Home Assistant OS

## Getting Your Govee API Key

1. Go to [Govee Developer Portal](https://developer.govee.com/)
2. Create an account or sign in
3. Create a new application
4. Copy your API key

## Installation

### Method 1: Manual Installation (Recommended)

1. Download this repository
2. Copy the `custom_components/govee_light_automation` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Integrations**
5. Click **+ Add Integration**
6. Search for "Govee Light Automation"
7. Enter your API key and follow the setup wizard

### Method 2: HACS Installation

1. Install HACS if you haven't already
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Follow the setup wizard

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Click **+ Add Integration**
3. Search for "Govee Light Automation"
4. Enter your Govee API key
5. The integration will automatically discover your devices

### Via YAML (Alternative)

Add the following to your `configuration.yaml`:

```yaml
govee_light_automation:
  api_key: YOUR_GOVEE_API_KEY
```

## Usage

Once configured, your Govee lights will appear as light entities in Home Assistant. You can:

- Turn lights on/off
- Adjust brightness
- Change colors using the color picker
- Use in automations and scripts
- Control via voice assistants (Google Assistant, Alexa, etc.)

### Rate Limiting & Monitoring

The integration includes smart rate limiting to prevent hitting the 10,000 requests/day API limit:

- **Automatic Request Counting**: Tracks all API requests made
- **Adaptive Polling**: Adjusts polling intervals based on device count and usage
- **Rate Limit Sensors**: Monitor your API usage in real-time:
  - `Govee API Rate Limit`: Shows usage percentage and remaining requests
  - `Govee Device Count`: Shows number of active devices
  - `Govee Polling Interval`: Shows current polling interval in seconds
  - `Govee API Calls`: **NEW!** Detailed API call tracking with real-time rate limit info from Govee API headers

### Configuration Options

During setup, you can configure:

- **API Key**: Your Govee API key
- **Enable Rate Limiting**: Toggle rate limiting on/off (default: enabled)

The integration will automatically:
- Count your daily API requests
- Adjust polling intervals based on device count
- Reset counters daily at midnight
- Prevent requests when approaching the limit

### New API Calls Sensor

The **Govee API Calls** sensor provides detailed information about your API usage:

**Main Value**: Total number of API calls made today

**Attributes**:
- `total_calls_today`: Number of API calls made today
- `remaining_calls`: Estimated remaining calls (based on local tracking)
- `usage_percentage`: Current usage percentage
- `daily_limit`: Maximum daily limit (10,000)
- `device_count`: Number of active devices
- `adaptive_polling_interval`: Current polling interval in seconds
- `last_reset_date`: Date when counters were last reset
- `rate_limit_status`: Status (Normal/Warning/Critical)
- `api_remaining_calls`: Real-time remaining calls from Govee API headers
- `api_reset_time`: When the rate limit will reset (from API headers)
- `last_api_call_time`: Timestamp of the last API call

**Dashboard Usage**: Add this sensor to your dashboard to monitor API usage in real-time!

## Supported Devices

This integration supports most Govee smart lights that are compatible with the Govee API, including:

- Govee LED Strip Lights
- Govee Bulbs
- Govee Light Bars
- Other Govee smart lighting products

## Troubleshooting

### No Devices Found

1. Verify your API key is correct
2. Ensure your Govee devices are connected to the internet
3. Check that your devices are registered in the Govee app

### Lights Not Responding

1. Check your internet connection
2. Verify the devices are online in the Govee app
3. Try restarting Home Assistant
4. Check the Home Assistant logs for error messages

### API Rate Limits

The Govee API has a 10,000 requests per day limit. The integration includes smart rate limiting to prevent hitting this limit:

- **Automatic Protection**: The integration automatically tracks and limits requests
- **Adaptive Polling**: Polling intervals adjust based on device count and usage
- **Daily Reset**: Request counters reset automatically at midnight
- **Monitoring**: Use the built-in sensors to monitor your API usage

If you experience rate limiting issues:
- Check the `Govee API Rate Limit` sensor for current usage
- The integration will automatically reduce polling frequency when approaching limits
- Consider disabling some devices if you have many lights

## Development

### Project Structure

```
custom_components/govee_light_automation/
├── __init__.py          # Main integration file
├── manifest.json        # Integration metadata
├── const.py            # Constants and configuration
├── config_flow.py      # Configuration flow
├── govee_api.py        # Govee API client
├── light.py            # Light platform implementation
└── translations/       # UI translations
    └── en.json
```

### Testing

To test the integration:

1. Install the integration in a development Home Assistant instance
2. Use the Govee API testing tools to verify API responses
3. Check Home Assistant logs for any errors

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Author

**Shiv Kumar Ganesh** - [gshiv.sk@gmail.com](mailto:gshiv.sk@gmail.com)

## License

This project is licensed under the MIT License.

## Support

For support:
1. Check the troubleshooting section above
2. Review Home Assistant logs
3. Open an issue on GitHub with detailed information about your problem

## Changelog

### Version 1.0.0
- Initial release
- Basic light control functionality
- RGB color support
- Brightness control
- Device discovery 