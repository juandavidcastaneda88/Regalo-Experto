(() => {
  "use strict";

  const DIRECT_FILE_MODE = window.location.protocol === "file:";
  const API_BASE = DIRECT_FILE_MODE ? "http://127.0.0.1:5000" : "";

  const state = {
    view: "home",
    step: 1,
    catalog: null,
    ocasion: "",
    intereses: new Set(),
    lastQuery: null,
    lastResults: [],
    visibleResults: 3,
    history: [],
    backendReady: false
  };

  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  const money = value => new Intl.NumberFormat("es-CO", {
    style: "currency", currency: "COP", maximumFractionDigits: 0
  }).format(value);

  const viewMap = {
    home: $("#homeView"), wizard: $("#wizardView"),
    results: $("#resultsView"), history: $("#historyView")
  };

  async function api(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    const headers = { ...(options.headers || {}) };
    if (options.body !== undefined) headers["Content-Type"] = "application/json";
    try {
      const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers,
        signal: controller.signal,
        cache: "no-store"
      });
      let payload;
      try { payload = await response.json(); }
      catch { payload = { ok: false, errores: ["El servidor devolvió una respuesta no válida."] }; }
      if (!response.ok || payload.ok === false) {
        throw new Error((payload.errores || ["No fue posible completar la operación."]).join(" "));
      }
      return payload;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("El motor Python tardó demasiado en responder.");
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  function setBackendStatus(ready, message = "") {
    state.backendReady = ready;
    const status = $("#backendStatus");
    const banner = $("#connectionBanner");
    status.dataset.state = ready ? "online" : "offline";
    status.querySelector("strong").textContent = ready ? "Python activo" : "Sin conexión";
    if (ready) {
      if (DIRECT_FILE_MODE) {
        banner.classList.remove("hidden");
        banner.classList.add("connected");
        $("#connectionTitle").textContent = "Vista directa conectada";
        $("#connectionText").textContent = "El index.html está usando el motor Python en http://127.0.0.1:5000.";
        setTimeout(() => banner.classList.add("hidden"), 4500);
      } else {
        banner.classList.add("hidden");
      }
    } else {
      banner.classList.remove("hidden", "connected");
      $("#connectionTitle").textContent = "Motor Python desconectado";
      $("#connectionText").textContent = message || "Ejecuta EJECUTAR_GIFT_EXPERT.bat para activar la aplicación.";
    }
  }

  function showConnectionModal() {
    $("#connectionModal").classList.remove("hidden");
  }

  function requireBackend() {
    if (state.backendReady) return true;
    showConnectionModal();
    return false;
  }

  function showView(view) {
    Object.values(viewMap).forEach(section => section.classList.remove("active"));
    viewMap[view].classList.add("active");
    state.view = view;
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (view === "history") loadHistory();
  }

  function showToast(message) {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => toast.classList.remove("show"), 3000);
  }

  function fillSelect(selector, items) {
    const select = $(selector);
    items.forEach(item => {
      const option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      select.appendChild(option);
    });
  }

  function buildOptions() {
    const data = state.catalog;
    fillSelect("#relacion", data.relaciones);
    fillSelect("#personalidad", data.personalidades);
    fillSelect("#tipoRegalo", data.tipos_regalo);

    data.ocasiones.forEach(item => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "occasion-option";
      button.dataset.value = item.nombre;
      button.innerHTML = `<span>${item.icono}</span><strong>${item.nombre}</strong>`;
      button.addEventListener("click", () => {
        $$(".occasion-option").forEach(btn => btn.classList.remove("selected"));
        button.classList.add("selected");
        state.ocasion = item.nombre;
        $("#occasionError").textContent = "";
      });
      $("#occasionGrid").appendChild(button);
    });

    data.intereses.forEach(item => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "interest-option";
      button.dataset.value = item.nombre;
      button.innerHTML = `<span>${item.icono}</span><strong>${item.nombre}</strong>`;
      button.addEventListener("click", () => {
        button.classList.toggle("selected");
        if (button.classList.contains("selected")) state.intereses.add(item.nombre);
        else state.intereses.delete(item.nombre);
        $("#interesesError").textContent = "";
      });
      $("#interestGrid").appendChild(button);
    });
  }

  function validateStep(step) {
    let valid = true;
    const section = $(`.form-step[data-step="${step}"]`);
    section.querySelectorAll("[required]").forEach(input => {
      const error = input.closest(".field")?.querySelector(".field-error");
      let message = "";
      if (!String(input.value).trim()) message = "Este campo es obligatorio.";
      if (input.id === "edad") {
        const value = Number(input.value);
        if (!value || value < 1 || value > 110) message = "Ingresa una edad entre 1 y 110 años.";
      }
      if (input.id === "presupuesto") {
        const value = Number(input.value);
        if (!value || value < 10000) message = "El presupuesto mínimo es de $10.000 COP.";
      }
      if (error) error.textContent = message;
      if (message) valid = false;
    });
    if (step === 2 && !state.ocasion) {
      $("#occasionError").textContent = "Selecciona una ocasión.";
      valid = false;
    }
    if (step === 3 && state.intereses.size === 0) {
      $("#interesesError").textContent = "Selecciona al menos un interés.";
      valid = false;
    }
    return valid;
  }

  const stepNames = ["Persona", "Ocasión", "Intereses", "Estilo", "Presupuesto"];

  function goToStep(step) {
    state.step = Math.max(1, Math.min(5, step));
    $$(".form-step").forEach(section => section.classList.toggle("active", Number(section.dataset.step) === state.step));
    $$('[data-step-indicator]').forEach(item => {
      const current = Number(item.dataset.stepIndicator);
      item.classList.toggle("active", current === state.step);
      item.classList.toggle("completed", current < state.step);
      item.querySelector(":scope > span").textContent = current < state.step ? "✓" : current;
    });
    $("#mobileStepText").textContent = `Paso ${state.step} de 5`;
    $("#mobileStepName").textContent = stepNames[state.step - 1];
    $("#progressFill").style.width = `${state.step * 20}%`;
    $("#prevButton").classList.toggle("hidden", state.step === 1);
    $("#nextButton").classList.toggle("hidden", state.step === 5);
    $("#submitButton").classList.toggle("hidden", state.step !== 5);
    if (state.step === 5) updateSummary();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function collectForm() {
    return {
      edad: Number($("#edad").value),
      relacion: $("#relacion").value,
      ocasion: state.ocasion,
      urgencia: $("#urgencia").value,
      intereses: [...state.intereses],
      personalidad: $("#personalidad").value,
      tipo_regalo: $("#tipoRegalo").value,
      presupuesto: Number($("#presupuesto").value),
      restricciones: $$('input[name="restricciones"]:checked').map(el => el.value)
    };
  }

  function updateSummary() {
    const query = collectForm();
    $("#querySummary").innerHTML = `
      <strong>Resumen de la consulta</strong>
      <p>${query.edad || "—"} años · ${query.relacion || "Relación pendiente"} · ${query.ocasion || "Ocasión pendiente"}</p>
      <p>Intereses: ${query.intereses.join(", ") || "Ninguno seleccionado"}</p>
      <p>Presupuesto máximo: ${money(query.presupuesto || 0)}</p>`;
  }

  function renderResults(query, payload) {
    state.lastQuery = query;
    state.lastResults = payload.recomendaciones || [];
    state.visibleResults = 3;
    $("#resultsMessage").textContent = payload.mensaje;
    $("#resultSummary").innerHTML = `
      <span>👤 ${query.edad} años</span><span>🤝 ${query.relacion}</span>
      <span>🎉 ${query.ocasion}</span><span>💰 ${money(query.presupuesto)}</span>
      <span>✨ ${query.personalidad}</span>`;
    renderResultCards();
    showView("results");
  }

  function renderResultCards() {
    const grid = $("#resultsGrid");
    grid.innerHTML = "";
    const visible = state.lastResults.slice(0, state.visibleResults);
    if (!visible.length) {
      grid.innerHTML = `<article class="result-card"><div class="result-icon">🔎</div><span class="rank">Sin coincidencias</span><h2>Ajusta algunos criterios</h2><p>Prueba aumentando el presupuesto o eliminando alguna restricción.</p></article>`;
      $("#showMore").classList.add("hidden");
      return;
    }
    visible.forEach((gift, index) => {
      const card = document.createElement("article");
      card.className = "result-card";
      card.innerHTML = `
        <div class="result-top"><div class="result-icon">${gift.imagen}</div>
        <div class="result-score" style="--score:${gift.porcentaje}"><strong>${gift.porcentaje}%</strong></div></div>
        <span class="rank">Opción ${index + 1} · ${gift.categoria}</span>
        <h2>${gift.nombre}</h2><p>${gift.descripcion}</p>
        <div class="price">${money(gift.precio)}</div>
        <div class="match-tags">${gift.coincidencias.slice(0, 5).map(tag => `<span>${tag}</span>`).join("")}</div>
        <div class="why-box"><strong>¿Por qué se recomienda?</strong><br>${gift.explicacion}</div>`;
      grid.appendChild(card);
    });
    $("#showMore").classList.toggle("hidden", state.visibleResults >= state.lastResults.length);
  }

  async function loadHistory(filter = "") {
    try {
      const payload = await api("/api/historial");
      state.history = payload.historial || [];
      renderHistory(filter, payload.estadisticas || {});
    } catch (error) {
      showToast(error.message);
    }
  }

  function renderHistory(filter = "", stats = {}) {
    const term = filter.trim().toLowerCase();
    const filtered = term ? state.history.filter(item => JSON.stringify(item).toLowerCase().includes(term)) : state.history;
    $("#statQueries").textContent = stats.consultas ?? state.history.length;
    $("#statAverage").textContent = `${stats.afinidad_promedio || 0}%`;
    $("#statTop").textContent = stats.regalo_mas_recomendado || "—";
    $("#statGifts").textContent = stats.regalos_disponibles ?? state.catalog?.total_regalos ?? 0;
    const body = $("#historyBody");
    body.innerHTML = "";
    filtered.forEach(item => {
      const best = item.resultado?.recomendaciones?.[0];
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" }).format(new Date(item.fecha))}</td>
        <td>${item.consulta.edad} años · ${item.consulta.relacion}</td><td>${item.consulta.ocasion}</td>
        <td>${money(item.consulta.presupuesto)}</td><td>${best ? `${best.imagen} ${best.nombre}` : "Sin resultado"}</td>
        <td><span class="affinity-badge">${best?.porcentaje || 0}%</span></td>`;
      body.appendChild(row);
    });
    $("#emptyHistory").classList.toggle("hidden", filtered.length > 0);
    $(".history-table-wrap").classList.toggle("hidden", filtered.length === 0);
  }

  function resetForm() {
    $("#giftForm").reset();
    $("#presupuesto").value = 250000;
    state.ocasion = "";
    state.intereses.clear();
    $$(".occasion-option, .interest-option").forEach(el => el.classList.remove("selected"));
    $$(".budget-buttons button").forEach(btn => btn.classList.toggle("selected", btn.dataset.budget === "250000"));
    $$(".field-error, .standalone-error").forEach(el => el.textContent = "");
    $("#formAlert").classList.add("hidden");
    goToStep(1);
  }

  function startQuery(reset = true) {
    if (!requireBackend()) return;
    if (reset) resetForm();
    showView("wizard");
  }

  function loadDemo() {
    if (!requireBackend()) return;
    resetForm();
    $("#edad").value = 27;
    $("#relacion").value = "Amigo/a";
    state.ocasion = "Cumpleaños";
    $$(".occasion-option").find(btn => btn.dataset.value === "Cumpleaños")?.classList.add("selected");
    ["Tecnología", "Música", "Viajes"].forEach(name => {
      state.intereses.add(name);
      $$(".interest-option").find(btn => btn.dataset.value === name)?.classList.add("selected");
    });
    $("#personalidad").value = "Tecnológica";
    $("#tipoRegalo").value = "Tecnología";
    $("#presupuesto").value = 350000;
    goToStep(5);
    showView("wizard");
    showToast("Demostración cargada. Pulsa “Obtener recomendación”.");
  }

  function bindEvents() {
    $("#nextButton").addEventListener("click", () => { if (validateStep(state.step)) goToStep(state.step + 1); });
    $("#prevButton").addEventListener("click", () => goToStep(state.step - 1));
    $("#giftForm").addEventListener("submit", async event => {
      event.preventDefault();
      if (!validateStep(5)) return;
      const button = $("#submitButton");
      button.disabled = true;
      button.innerHTML = "<span>Python está analizando...</span> ⏳";
      $("#formAlert").classList.add("hidden");
      try {
        const query = collectForm();
        const payload = await api("/api/recomendar", { method: "POST", body: JSON.stringify(query) });
        renderResults(query, payload);
      } catch (error) {
        $("#formAlert").textContent = error.message;
        $("#formAlert").classList.remove("hidden");
      } finally {
        button.disabled = false;
        button.innerHTML = "<span>Obtener recomendación</span> ✨";
      }
    });
    $$(".budget-buttons button").forEach(button => button.addEventListener("click", () => {
      $("#presupuesto").value = button.dataset.budget;
      $$(".budget-buttons button").forEach(btn => btn.classList.remove("selected"));
      button.classList.add("selected");
      updateSummary();
    }));
    $("#presupuesto").addEventListener("input", updateSummary);
    $("#showMore").addEventListener("click", () => { state.visibleResults = state.lastResults.length; renderResultCards(); });
    $("#historySearch").addEventListener("input", event => renderHistory(event.target.value, {
      consultas: state.history.length,
      afinidad_promedio: state.history.length ? Math.round(state.history.reduce((sum, x) => sum + (x.resultado?.recomendaciones?.[0]?.porcentaje || 0), 0) / state.history.length) : 0,
      regalo_mas_recomendado: $("#statTop").textContent,
      regalos_disponibles: state.catalog?.total_regalos || 0
    }));
    $("#clearHistory").addEventListener("click", async () => {
      if (!confirm("¿Deseas eliminar todo el historial guardado por la aplicación?")) return;
      try { await api("/api/historial", { method: "DELETE" }); await loadHistory(); showToast("Historial eliminado."); }
      catch (error) { showToast(error.message); }
    });
    $("#reloadKnowledge").addEventListener("click", async () => {
      try {
        const result = await api("/api/base-conocimiento/recargar", { method: "POST", body: "{}" });
        showToast(`${result.mensaje} ${result.regalos} regalos y ${result.reglas} reglas.`);
        await loadCatalog(true);
        await loadHistory();
      } catch (error) { showToast(error.message); }
    });
    $("#themeToggle").addEventListener("click", () => {
      document.body.classList.toggle("dark");
      const dark = document.body.classList.contains("dark");
      $("#themeToggle").textContent = dark ? "☀️" : "🌙";
      localStorage.setItem("giftExpertTheme", dark ? "dark" : "light");
    });
    $$(".nav-link, [data-view]").forEach(button => button.addEventListener("click", () => showView(button.dataset.view)));
    ["#heroStart", "#navStart", "#ethicsStart", "#newQuery", "#anotherQuery", "#emptyStart"].forEach(selector => $(selector)?.addEventListener("click", () => startQuery(true)));
    $("#changeBudget").addEventListener("click", () => {
      if (!requireBackend()) return;
      showView("wizard"); goToStep(5);
    });
    $("#closeConnectionModal").addEventListener("click", () => $("#connectionModal").classList.add("hidden"));
    $("#connectionModal").addEventListener("click", event => {
      if (event.target.id === "connectionModal") $("#connectionModal").classList.add("hidden");
    });
    $("#demoButton").addEventListener("click", loadDemo);
  }

  async function loadCatalog(reload = false) {
    const payload = await api("/api/catalogo");
    state.catalog = payload;
    if (!reload) buildOptions();
  }

  async function init() {
    if (localStorage.getItem("giftExpertTheme") === "dark") {
      document.body.classList.add("dark");
      $("#themeToggle").textContent = "☀️";
    }
    bindEvents();
    try {
      const status = await api("/api/estado");
      await loadCatalog();
      goToStep(1);
      setBackendStatus(true);
      console.info(`Gift Expert operativo: ${status.motor} + ${status.servidor}`);
    } catch (error) {
      setBackendStatus(false, "Ejecuta EJECUTAR_GIFT_EXPERT.bat y vuelve a abrir la aplicación.");
      showToast("La interfaz está lista, pero falta iniciar Python + Flask.");
      console.error(error);
    }
  }

  init();
})();
