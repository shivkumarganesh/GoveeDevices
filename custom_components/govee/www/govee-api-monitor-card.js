const LitElement = customElements.get('hui-masonry-view') 
  ? Object.getPrototypeOf(customElements.get('hui-masonry-view')) 
  : Object.getPrototypeOf(customElements.get('hui-view'));

const html = LitElement.prototype.html;
const css = LitElement.prototype.css;

class GoveeApiMonitorCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _api_calls: { type: Number },
      _usage_percent: { type: Number },
      _status: { type: String },
      _device_count: { type: Number },
      _polling_interval: { type: Number },
      _last_reset: { type: String },
      _next_reset: { type: String },
    };
  }

  static get styles() {
    return css`
      :host {
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 4px);
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
        color: var(--primary-text-color);
        display: block;
        padding: 16px;
        transition: all 0.3s ease-out;
      }

      .header {
        font-size: 1.5em;
        font-weight: 500;
        margin-bottom: 16px;
      }

      .status-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        margin-bottom: 16px;
      }

      .status-normal { background-color: rgba(var(--rgb-success), 0.2); }
      .status-warning { background-color: rgba(var(--rgb-warning), 0.2); }
      .status-critical { background-color: rgba(var(--rgb-error), 0.2); }

      .status-text {
        font-size: 1.2em;
        font-weight: 500;
        margin-bottom: 8px;
      }

      .status-normal .status-text { color: var(--success-color); }
      .status-warning .status-text { color: var(--warning-color); }
      .status-critical .status-text { color: var(--error-color); }

      .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-top: 16px;
      }

      .stat-item {
        background: rgba(var(--rgb-primary-color), 0.05);
        padding: 12px;
        border-radius: 4px;
      }

      .stat-label {
        font-size: 0.9em;
        color: var(--secondary-text-color);
      }

      .stat-value {
        font-size: 1.2em;
        font-weight: 500;
        margin-top: 4px;
      }

      .progress-bar {
        width: 100%;
        height: 4px;
        background: rgba(var(--rgb-primary-color), 0.1);
        border-radius: 2px;
        margin-top: 16px;
      }

      .progress-value {
        height: 100%;
        background: var(--primary-color);
        border-radius: 2px;
        transition: width 0.3s ease-out;
      }

      ha-icon {
        color: var(--primary-color);
        margin-right: 8px;
      }
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) {
      return html``;
    }

    const entity = this.hass.states[this.config.entity];
    if (!entity) {
      return html`
        <ha-card>
          <div class="header">
            Entity ${this.config.entity} not found
          </div>
        </ha-card>
      `;
    }

    const attrs = entity.attributes;
    const status = attrs.rate_limit_status;
    const statusClass = `status-circle status-${status.toLowerCase()}`;
    const usage = attrs.usage_percentage;

    return html`
      <ha-card>
        <div class="header">
          <ha-icon icon="mdi:api"></ha-icon>
          Govee API Monitor
        </div>

        <div class="${statusClass}">
          <div class="status-text">${status}</div>
          <div>${usage}%</div>
        </div>

        <div class="progress-bar">
          <div class="progress-value" style="width: ${usage}%"></div>
        </div>

        <div class="grid-container">
          <div class="stat-item">
            <div class="stat-label">
              <ha-icon icon="mdi:counter"></ha-icon>
              API Calls Today
            </div>
            <div class="stat-value">${attrs.total_calls_today}</div>
          </div>

          <div class="stat-item">
            <div class="stat-label">
              <ha-icon icon="mdi:timer-sand"></ha-icon>
              Remaining Calls
            </div>
            <div class="stat-value">${attrs.remaining_calls}</div>
          </div>

          <div class="stat-item">
            <div class="stat-label">
              <ha-icon icon="mdi:devices"></ha-icon>
              Active Devices
            </div>
            <div class="stat-value">${attrs.device_count}</div>
          </div>

          <div class="stat-item">
            <div class="stat-label">
              <ha-icon icon="mdi:clock-outline"></ha-icon>
              Polling Interval
            </div>
            <div class="stat-value">${attrs.adaptive_polling_interval}s</div>
          </div>
        </div>

        <div class="stat-item" style="margin-top: 16px;">
          <div class="stat-label">
            <ha-icon icon="mdi:clock-check"></ha-icon>
            Next Reset
          </div>
          <div class="stat-value">${attrs.api_reset_time}</div>
        </div>
      </ha-card>
    `;
  }
}

customElements.define('govee-api-monitor-card', GoveeApiMonitorCard);
