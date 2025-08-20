# Govee API Monitor Card

A custom Lovelace card for monitoring Govee API usage in Home Assistant.

## Features

- Real-time API usage monitoring
- Visual status indicator with color coding
- Progress bar for usage percentage
- Detailed statistics display
- Responsive design
- Theme-aware styling
- Automatic updates

## Installation

1. Copy the `govee-api-monitor-card.js` file to your `www` directory
2. Add the following to your Lovelace resources:

```yaml
resources:
  - url: /local/govee-api-monitor-card.js
    type: module
```

## Usage

Add the card to your dashboard:

```yaml
type: custom:govee-api-monitor-card
entity: sensor.govee_api_calls
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | Required | The entity ID of your Govee API Calls sensor |
| `title` | string | "Govee API Monitor" | Custom title for the card |
| `show_progress` | boolean | true | Show/hide the progress bar |
| `show_status` | boolean | true | Show/hide the status circle |
| `show_reset` | boolean | true | Show/hide the next reset time |

Example with all options:

```yaml
type: custom:govee-api-monitor-card
entity: sensor.govee_api_calls
title: My Govee API Usage
show_progress: true
show_status: true
show_reset: true
```

## Styling

The card uses your Home Assistant theme colors by default. You can customize the appearance using theme variables:

```yaml
# In your theme.yaml
govee-card-background: 'rgba(0, 0, 0, 0.05)'
govee-card-normal: 'var(--success-color)'
govee-card-warning: 'var(--warning-color)'
govee-card-critical: 'var(--error-color)'
```

## Customization Examples

### Minimal View
```yaml
type: custom:govee-api-monitor-card
entity: sensor.govee_api_calls
show_progress: false
show_reset: false
```

### Dashboard Grid
```yaml
type: grid
columns: 2
cards:
  - type: custom:govee-api-monitor-card
    entity: sensor.govee_api_calls
  - type: custom:mini-graph-card
    entity: sensor.govee_api_rate_limit
    hours_to_show: 24
```

### Combined with Automations
```yaml
type: vertical-stack
cards:
  - type: custom:govee-api-monitor-card
    entity: sensor.govee_api_calls
  - type: entities
    entities:
      - automation.govee_api_rate_limit_warning
      - automation.govee_api_critical_alert
      - automation.govee_api_daily_report
```

## Troubleshooting

### Card Not Loading
- Make sure the resource is properly added to Lovelace
- Check your browser's console for errors
- Verify the entity exists and is working

### Styling Issues
- Check if your theme is properly loaded
- Verify custom theme variables if used
- Try clearing your browser cache

### Updates Not Showing
- Ensure the sensor is updating correctly
- Check the entity state in Developer Tools
- Verify your polling interval settings

## Integration with Other Cards

The Govee API Monitor card works well with other cards. Here are some combinations:

### Comprehensive Dashboard
```yaml
type: vertical-stack
cards:
  - type: custom:govee-api-monitor-card
    entity: sensor.govee_api_calls
  - type: horizontal-stack
    cards:
      - type: custom:mini-graph-card
        entity: sensor.govee_api_rate_limit
        name: "Usage Trend"
        hours_to_show: 24
      - type: custom:apexcharts-card
        entity: sensor.govee_api_calls
        name: "Daily Calls"
  - type: markdown
    content: |
      Last Updated: {{ state_attr('sensor.govee_api_calls', 'last_api_call_time') }}
```

## Advanced Usage

### Conditional Card
```yaml
type: conditional
conditions:
  - entity: sensor.govee_api_calls
    state_not: "unavailable"
card:
  type: custom:govee-api-monitor-card
  entity: sensor.govee_api_calls
```

### With Custom Header
```yaml
type: custom:hui-element
card_type: custom:govee-api-monitor-card
card_mod:
  style: |
    ha-card {
      --ha-card-background: var(--govee-card-background, rgba(0, 0, 0, 0.05));
    }
entity: sensor.govee_api_calls
```
