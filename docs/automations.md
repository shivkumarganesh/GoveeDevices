# Govee API Monitoring Automations

Here are example automations to help monitor and manage your Govee API usage. Add these to your `configuration.yaml` or through the automations UI.

## 1. Rate Limit Warning Notification

```yaml
alias: "Govee API - Rate Limit Warning"
description: "Notify when API usage reaches warning levels"
trigger:
  - platform: state
    entity_id: sensor.govee_api_calls
    attribute: rate_limit_status
    to: "WARNING"
condition: []
action:
  - service: persistent_notification.create
    data:
      title: "⚠️ Govee API Usage Warning"
      message: >
        API usage has reached {{ states('sensor.govee_api_rate_limit') }}%.
        
        Current calls today: {{ state_attr('sensor.govee_api_calls', 'total_calls_today') }}
        Remaining calls: {{ state_attr('sensor.govee_api_calls', 'remaining_calls') }}
        
        Consider increasing polling interval if this happens frequently.
  - service: notify.mobile_app_your_phone  # Replace with your notification service
    data:
      title: "⚠️ Govee API Usage Warning"
      message: "API usage at {{ states('sensor.govee_api_rate_limit') }}%"
```

## 2. Critical Rate Limit Alert

```yaml
alias: "Govee API - Critical Rate Limit"
description: "Alert when API usage reaches critical levels"
trigger:
  - platform: state
    entity_id: sensor.govee_api_calls
    attribute: rate_limit_status
    to: "CRITICAL"
condition: []
action:
  - service: persistent_notification.create
    data:
      title: "🚨 Govee API Critical Alert"
      message: >
        API usage has reached CRITICAL level at {{ states('sensor.govee_api_rate_limit') }}%.
        
        Current calls today: {{ state_attr('sensor.govee_api_calls', 'total_calls_today') }}
        Remaining calls: {{ state_attr('sensor.govee_api_calls', 'remaining_calls') }}
        
        Some automations may be temporarily disabled to prevent API exhaustion.
  - service: notify.mobile_app_your_phone  # Replace with your notification service
    data:
      title: "🚨 Govee API Critical Alert"
      message: "API usage critical at {{ states('sensor.govee_api_rate_limit') }}%!"
      priority: high
```

## 3. Daily Usage Report

```yaml
alias: "Govee API - Daily Usage Report"
description: "Send daily report of API usage"
trigger:
  - platform: time
    at: "23:00:00"
condition: []
action:
  - service: persistent_notification.create
    data:
      title: "📊 Govee API Daily Report"
      message: >
        Daily API Usage Summary:
        
        Total Calls: {{ state_attr('sensor.govee_api_calls', 'total_calls_today') }}
        Usage Percentage: {{ states('sensor.govee_api_rate_limit') }}%
        Active Devices: {{ state_attr('sensor.govee_api_calls', 'device_count') }}
        Current Polling Interval: {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') }}s
        
        Status: {{ state_attr('sensor.govee_api_calls', 'rate_limit_status') }}
  - service: notify.mobile_app_your_phone  # Replace with your notification service
    data:
      title: "📊 Govee API Daily Report"
      message: "Used {{ states('sensor.govee_api_rate_limit') }}% of daily limit"
```

## 4. Adaptive Polling Adjustment

```yaml
alias: "Govee API - Adaptive Polling Adjustment"
description: "Automatically adjust polling interval based on usage"
trigger:
  - platform: numeric_state
    entity_id: sensor.govee_api_rate_limit
    above: 80
condition:
  - condition: template
    value_template: >
      {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') < 300 }}
action:
  - service: homeassistant.update_entity
    target:
      entity_id: sensor.govee_polling_interval
  - delay:
      seconds: 5
  - service: persistent_notification.create
    data:
      title: "⚙️ Govee API Polling Adjusted"
      message: >
        Polling interval increased due to high usage.
        New interval: {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') }}s
```

## 5. Reset Notification

```yaml
alias: "Govee API - Reset Notification"
description: "Notify when API counters reset"
trigger:
  - platform: template
    value_template: "{{ state_attr('sensor.govee_api_calls', 'total_calls_today') == 0 }}"
action:
  - service: persistent_notification.create
    data:
      title: "🔄 Govee API Counter Reset"
      message: >
        API counters have been reset for the new day.
        
        Previous day usage: {{ states('sensor.govee_api_rate_limit') }}%
        Current polling interval: {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') }}s
```

## Installation Instructions

1. Copy these automations to your `configuration.yaml` or create them through the UI
2. Replace `notify.mobile_app_your_phone` with your actual notification service
3. Adjust the time and thresholds as needed
4. Restart Home Assistant

## Customization Options

### Notification Thresholds

You can adjust the warning and critical thresholds in the automations:

```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.govee_api_rate_limit
    above: 75  # Change this value for earlier/later warnings
```

### Polling Interval Adjustments

Modify the adaptive polling automation thresholds:

```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.govee_api_rate_limit
    above: 80  # Adjust when polling should be increased
condition:
  - condition: template
    value_template: >
      {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') < 240 }}  # Max interval
```

### Daily Report Timing

Change when you receive the daily report:

```yaml
trigger:
  - platform: time
    at: "21:00:00"  # Change to your preferred time
```

## Additional Tips

1. Create a dedicated notification group for Govee API alerts
2. Use different notification priorities for different alert levels
3. Consider creating a custom Lovelace card to display these automations' status
4. Add conditions based on time of day or home occupancy
5. Create scripts to temporarily disable/enable polling during specific events
