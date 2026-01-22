class KomfoventCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("Please define an entity");
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    const lang = hass.language || "en";
    const t = KomfoventCard.translations[lang] || KomfoventCard.translations.en;

    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content" style="padding: 16px;">
            <div class="header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <div style="font-size: 1.2em; font-weight: 500;">Komfovent</div>
              <div class="mode" style="padding: 4px 12px; border-radius: 12px; background: var(--primary-color); color: white;"></div>
            </div>
            <div class="temps" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; margin-bottom: 16px;">
              <div><div class="label supply-label" style="font-size: 0.8em; color: var(--secondary-text-color);"></div><div class="supply-temp" style="font-size: 1.5em;"></div></div>
              <div><div class="label extract-label" style="font-size: 0.8em; color: var(--secondary-text-color);"></div><div class="extract-temp" style="font-size: 1.5em;"></div></div>
              <div><div class="label outdoor-label" style="font-size: 0.8em; color: var(--secondary-text-color);"></div><div class="outdoor-temp" style="font-size: 1.5em;"></div></div>
            </div>
            <div class="stats" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 0.9em;">
              <div><span class="fan-label"></span>: <span class="fan"></span></div>
              <div><span class="filter-label"></span>: <span class="filter"></span></div>
              <div><span class="power-label"></span>: <span class="power"></span></div>
              <div><span class="recovery-label"></span>: <span class="recovery"></span></div>
            </div>
          </div>
        </ha-card>
      `;
      this.content = this.querySelector(".card-content");
    }

    this.querySelector(".supply-label").textContent = t.supply;
    this.querySelector(".extract-label").textContent = t.extract;
    this.querySelector(".outdoor-label").textContent = t.outdoor;
    this.querySelector(".fan-label").textContent = t.fan;
    this.querySelector(".filter-label").textContent = t.filter;
    this.querySelector(".power-label").textContent = t.power;
    this.querySelector(".recovery-label").textContent = t.recovery;

    const prefix = this.config.entity.replace("sensor.", "").replace("_mode", "");
    const getState = (suffix) => {
      const entity = hass.states[`sensor.${prefix}_${suffix}`];
      return entity ? entity.state : "?";
    };

    this.querySelector(".mode").textContent = getState("mode");
    this.querySelector(".supply-temp").textContent = getState("supply_temperature") + "°C";
    this.querySelector(".extract-temp").textContent = getState("extract_temperature") + "°C";
    this.querySelector(".outdoor-temp").textContent = getState("outdoor_temperature") + "°C";
    this.querySelector(".fan").textContent = getState("supply_fan") + "%";
    this.querySelector(".filter").textContent = getState("filter_contamination") + "%";
    this.querySelector(".power").textContent = getState("power_consumption") + "W";
    this.querySelector(".recovery").textContent = getState("heat_recovery_power") + "W";
  }

  getCardSize() {
    return 3;
  }
}

KomfoventCard.translations = {
  en: { supply: "Supply", extract: "Extract", outdoor: "Outdoor", fan: "Fan", filter: "Filter", power: "Power", recovery: "Recovery" },
  pl: { supply: "Nawiew", extract: "Wywiew", outdoor: "Zewn.", fan: "Wentylator", filter: "Filtr", power: "Moc", recovery: "Odzysk" },
};

customElements.define("komfovent-card", KomfoventCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "komfovent-card",
  name: "Komfovent Card",
  description: "Status card for Komfovent ventilation units",
  preview: true,
});
