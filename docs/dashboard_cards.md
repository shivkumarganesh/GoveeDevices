# Govee API Dashboard Cards

Here are some examples of dashboard cards you can use to monitor your Govee API usage.

## 1. Simple Markdown Card

```yaml
type: markdown
title: Govee API Usage
content: >
  ## API Usage Today: {{ states('sensor.govee_api_calls') }} calls

  **Status**: {{ state_attr('sensor.govee_api_calls', 'rate_limit_status') }}
  
  {% set usage = state_attr('sensor.govee_api_calls', 'usage_percentage') | float %}
  {% set color = 'green' if usage < 70 else 'orange' if usage < 90 else 'red' %}
  
  **Usage**: <span style="color: {{color}}">{{ usage | round(1) }}%</span>
  
  **Remaining Calls**: {{ state_attr('sensor.govee_api_calls', 'remaining_calls') }}
  
  **Devices**: {{ state_attr('sensor.govee_api_calls', 'device_count') }}
  
  **Polling Interval**: {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') }}s
  
  **Next Reset**: {{ state_attr('sensor.govee_api_calls', 'api_reset_time') }}
```

## 2. Grid Card with Multiple Entities

```yaml
type: grid
title: Govee API Monitor
columns: 2
square: false
cards:
  - type: entity
    name: API Calls Today
    entity: sensor.govee_api_calls
    icon: mdi:api
  
  - type: entity
    name: Usage
    entity: sensor.govee_api_rate_limit
    icon: mdi:percent
    
  - type: entity
    name: Polling Interval
    entity: sensor.govee_polling_interval
    icon: mdi:timer-outline
    
  - type: entity
    name: Device Count
    entity: sensor.govee_api_calls
    attribute: device_count
    icon: mdi:devices
```

## 3. Custom Vertical Stack with Gauge

```yaml
type: vertical-stack
cards:
  - type: gauge
    name: API Usage
    entity: sensor.govee_api_rate_limit
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 70
      red: 90
      
  - type: entities
    entities:
      - entity: sensor.govee_api_calls
        name: Total Calls Today
        icon: mdi:counter
      - entity: sensor.govee_api_calls
        name: Remaining Calls
        icon: mdi:timer-sand
        attribute: remaining_calls
      - entity: sensor.govee_api_calls
        name: Rate Limit Status
        icon: mdi:alert-circle-outline
        attribute: rate_limit_status
      - entity: sensor.govee_polling_interval
        name: Current Polling Interval
        icon: mdi:clock-outline
```

## 4. Comprehensive Monitoring Card

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: custom:mini-graph-card
        name: API Usage Trend
        entities:
          - entity: sensor.govee_api_rate_limit
        hours_to_show: 24
        points_per_hour: 4
        line_color: var(--primary-color)
        
      - type: custom:apexcharts-card
        graph_span: 24h
        header:
          title: API Calls Distribution
          show: true
        series:
          - entity: sensor.govee_api_calls
            type: column
            
  - type: custom:mushroom-entity-card
    entity: sensor.govee_api_calls
    icon: mdi:api
    primary_info: name
    secondary_info: state
    icon_color: |
      {% set status = state_attr('sensor.govee_api_calls', 'rate_limit_status') %}
      {% if status == 'NORMAL' %}
        green
      {% elif status == 'WARNING' %}
        orange
      {% else %}
        red
      {% endif %}
        
  - type: markdown
    content: >
      ### Device Status
      
      * **Active Devices**: {{ state_attr('sensor.govee_api_calls', 'device_count') }}
      * **Polling Every**: {{ state_attr('sensor.govee_api_calls', 'adaptive_polling_interval') }} seconds
      * **Last Reset**: {{ state_attr('sensor.govee_api_calls', 'last_reset_date') }}
      * **Next Reset**: {{ state_attr('sensor.govee_api_calls', 'api_reset_time') }}
```

## Installation Requirements

For the comprehensive monitoring card, you'll need to install these HACS frontend integrations:

1. Mini Graph Card
2. ApexCharts Card
3. Mushroom Cards

To install these:

1. Open HACS in Home Assistant
2. Go to "Frontend"
3. Click the "+ Explore & Download Repositories" button
4. Search for and install each card:
   - Search for "mini-graph-card"
   - Search for "apexcharts-card"
   - Search for "mushroom"

## Usage Instructions

1. Open your Home Assistant dashboard
2. Click the three dots menu in the top right
3. Click "Edit Dashboard"
4. Click the "+" button to add a new card
5. Click "Manual" at the bottom
6. Copy and paste any of the YAML configurations above
7. Click "Save"

## Customization

You can customize these cards by:

1. Adjusting the colors in the gauge card
2. Changing the time span in the graph cards
3. Modifying the layout of the grid
4. Adding or removing entities from the entities card

Remember to replace any entity IDs if they differ in your installation.
