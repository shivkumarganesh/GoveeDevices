# Govee Lights for Home Assistant

Control your Govee smart lights through Home Assistant with real-time updates, color control, and smart API usage management.

## 🌟 Features

- ✨ Complete light control (on/off, brightness, color, temperature)
- 🔄 Real-time state updates
- 🎨 Full RGB and color temperature support (2000K-9000K)
- 📊 Built-in API usage monitoring
- 🔋 Smart power management
- 🚦 Automatic rate limiting protection
- 📱 Custom dashboard cards included

## ⚡ Quick Start

1. Get your Govee API Key:
   - Go to [Govee Developer Portal](https://developer.govee.com)
   - Create an account or sign in
   - Click "Create API Key"
   - Copy your API key

2. Install in Home Assistant:
   ```yaml
   # Option 1: HACS
   1. Add this repository to HACS
   2. Install "Govee Lights" integration
   3. Restart Home Assistant

   # Option 2: Manual
   1. Download this repository
   2. Copy custom_components/govee to your config/custom_components/
   3. Restart Home Assistant
   ```

3. Configure:
   - Go to Settings → Integrations
   - Click "+ Add Integration"
   - Search for "Govee"
   - Enter your API key

## 🚨 Important Notes

### API Rate Limits
- Govee limits API calls to 10,000 requests per day
- This integration includes smart rate limiting to prevent reaching this limit
- Each device update counts as one API call
- Default polling interval is 1 minute per device
- Auto-updates occur when state changes (minimum 2-second delay)

### Device Compatibility
- Works with most Govee smart lights that support the Govee API
- Devices must be:
  - Connected to WiFi
  - Set up in the Govee app
  - Compatible with Govee's API (check your model in the Govee app)

### Known Limitations
- Color temperature range: 2000K-9000K
- Minimum update interval: 2 seconds
- Some older models may not support all features
- API key is tied to your Govee account
- API rate limit is shared across all devices

## 📊 Monitoring Tools

### 1. API Usage Sensor
- Entity ID: `sensor.govee_api_calls`
- Shows total daily API calls
- Tracks remaining calls
- Monitors rate limit status

### 2. Built-in Dashboard Card
Add to your dashboard:
```yaml
type: custom:govee-api-monitor-card
entity: sensor.govee_api_calls
```

### 3. Rate Limit States
- 🟢 NORMAL: Below 80% usage
- 🟡 WARNING: 80-90% usage
- 🔴 CRITICAL: Above 90% usage

## 🔧 Advanced Configuration

### Adjusting Update Intervals
The integration automatically manages polling intervals based on:
- Number of devices
- Current API usage
- Rate limit status

Default intervals:
- Minimum: 2 seconds between updates
- Regular polling: 1 minute
- Adaptive increase when approaching limits

### Recommended Setup for Large Installations
If you have many devices (10+):
1. Monitor `sensor.govee_api_calls` initially
2. Check actual usage patterns
3. Consider creating automations to adjust polling based on occupancy

## 🚧 Troubleshooting

### Devices Not Showing Up
1. Verify in Govee app:
   - Device is online
   - Device is connected to WiFi
   - Device supports API control

2. Check Home Assistant logs:
   ```bash
   2025-08-21 12:00:00 ERROR (MainThread) [custom_components.govee] 
   ```

3. Validate API key:
   - Test in Govee Developer Portal
   - Ensure key has permissions

### API Rate Limit Issues
1. Monitor usage with dashboard card
2. Check logs for rate limit warnings
3. Consider reducing polling interval
4. Look for automations causing excessive updates

### Connection Problems
1. Ensure stable internet connection
2. Check device WiFi connection
3. Verify Govee cloud service status
4. Restart Home Assistant

## 🔄 State Updates

The integration updates device states in three ways:
1. Regular polling (every minute)
2. On command (when you control the device)
3. Auto-updates (when state changes, min 2-second delay)

## 📱 Supported Commands

- 💡 Turn On/Off
- 🔆 Brightness (0-100%)
- 🎨 RGB Color
- 🌡️ Color Temperature (2000K-9000K)

## 🏗️ Examples

### Basic Light Control
```yaml
# Turn on light
service: light.turn_on
target:
  entity_id: light.govee_bedroom
data:
  brightness_pct: 100

# Set color
service: light.turn_on
target:
  entity_id: light.govee_bedroom
data:
  rgb_color: [255, 0, 0]  # Red

# Set color temperature
service: light.turn_on
target:
  entity_id: light.govee_bedroom
data:
  color_temp_kelvin: 3000  # Warm white
```

### Dashboard Examples
```yaml
# Simple light card
type: light
entity: light.govee_bedroom

# With API monitoring
type: vertical-stack
cards:
  - type: light
    entity: light.govee_bedroom
  - type: custom:govee-api-monitor-card
    entity: sensor.govee_api_calls
```

## 🆘 Common Issues

1. "Rate limit reached":
   - Normal protection mechanism
   - Wait for limit reset (midnight UTC)
   - Monitor usage with dashboard card

2. "Device not responding":
   - Check device WiFi connection
   - Verify device power
   - Reset device if persistent

3. "API key invalid":
   - Verify key in Govee Developer Portal
   - Check for spaces/typos
   - Generate new key if needed

## 🔒 Security Notes

- Keep your API key secure
- Don't share your key publicly
- One key works for all devices
- Keys can be revoked in Govee portal

## 📚 Additional Resources

- [Govee API Documentation](https://govee-public.s3.amazonaws.com/developer-docs/GoveeDeveloperAPIReference.pdf)
- [Home Assistant Forums](https://community.home-assistant.io/t/govee-integration)
- [GitHub Issues](https://github.com/shivkumarganesh/GoveeDevices/issues)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open pull request

## 📄 License

MIT License - See LICENSE file

## 👥 Support

- Open an issue on GitHub
- Join Discord community
- Check troubleshooting guide above

## ⭐ Star History

Show your support by starring the repository!

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