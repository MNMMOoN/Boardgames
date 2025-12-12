(() => {
  const qs = (sel, scope = document) => scope.querySelector(sel);
  const qsa = (sel, scope = document) => Array.from(scope.querySelectorAll(sel));
  const state = {
    token: localStorage.getItem("morghi_token"),
    name: localStorage.getItem("morghi_name"),
    gameId: localStorage.getItem("morghi_game_id"),
    eventSource: null,
  };

  function setCurrentPlayer(name) {
    const el = qs("#current-player");
    if (el) el.textContent = name ? `Player: ${name}` : "";
  }

  function setSseStatus(text) {
    const el = qs("#sse-status");
    if (el) el.textContent = `SSE: ${text}`;
  }

  function appendChatMessage({ text, from = "System", system = false }) {
    const log = qs("#chat-log");
    if (!log) return;
    const item = document.createElement("div");
    item.className = `chat-message ${system ? "system" : ""}`;
    const label = document.createElement("p");
    label.className = "text-[11px] uppercase tracking-wide text-slate-400 mb-1";
    label.textContent = system ? "System" : from || "Player";
    const body = document.createElement("p");
    body.textContent = text;
    item.append(label, body);
    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
  }

  function connectSse() {
    try {
      const es = new EventSource("/events");
      state.eventSource = es;
      setSseStatus("connecting...");

      es.addEventListener("open", () => setSseStatus("connected"));
      es.addEventListener("error", () => setSseStatus("disconnected"));

      es.addEventListener("message", (ev) => {
        try {
          const payload = JSON.parse(ev.data);
          appendChatMessage({ text: payload.text || "Event received", system: payload.system });
        } catch {
          appendChatMessage({ text: "Incoming message", system: true });
        }
      });

      es.addEventListener("game_started", () => {
        appendChatMessage({ text: "All players ready. Moving to game...", system: true });
        setTimeout(() => (window.location.href = "/game.html"), 600);
      });

      es.addEventListener("hand_changed", (ev) => {
        const data = safeParse(ev.data);
        updateHand(data?.cards || []);
      });

      es.addEventListener("scores_changed", (ev) => {
        const data = safeParse(ev.data);
        updateScores(data?.eggs ?? 0, data?.chickens ?? 0);
      });

      es.addEventListener("fox_incoming", () => {
        appendChatMessage({ text: "A fox is coming for your egg! Decide to defend.", system: true });
        alert("Fox incoming! If you have two Roosters you may defend.");
      });
    } catch (e) {
      console.warn("SSE unavailable", e);
      setSseStatus("unavailable");
    }
  }

  function safeParse(raw) {
    try {
      return JSON.parse(raw || "{}");
    } catch {
      return {};
    }
  }

  /* ---------- Login page ---------- */
  function initLoginPage() {
    const form = qs("#login-form");
    const createForm = qs("#create-game-form");
    const refreshBtn = qs("#refresh-games");
    setCurrentPlayer(state.name);

    form?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const name = formData.get("name");
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (!res.ok) return alert("Enter a name to continue.");
      const data = await res.json();
      state.token = data.token;
      state.name = data.name;
      localStorage.setItem("morghi_token", data.token);
      localStorage.setItem("morghi_name", data.name);
      setCurrentPlayer(data.name);
      window.location.href = "/lobby.html";
    });

    createForm?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(createForm);
      const payload = Object.fromEntries(fd.entries());
      const res = await fetch("/games", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const game = await res.json();
      state.gameId = game.id;
      localStorage.setItem("morghi_game_id", game.id);
      window.location.href = "/lobby.html";
    });

    refreshBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      loadGames();
    });

    loadGames();
  }

  async function loadGames() {
    const list = qs("#game-list");
    if (!list) return;
    list.innerHTML = `<p class="text-slate-400">Loading...</p>`;
    try {
      const res = await fetch("/games");
      const data = await res.json();
      if (!data.games?.length) {
        list.innerHTML = `<p class="text-slate-400">No games yet. Create one!</p>`;
        return;
      }
      list.innerHTML = "";
      data.games.forEach((g) => {
        const btn = document.createElement("button");
        btn.className =
          "w-full text-left px-4 py-3 rounded-xl border border-slate-700 hover:border-amber-300 hover:bg-slate-800/70";
        btn.innerHTML = `
          <div class="flex items-center justify-between">
            <div>
              <p class="font-semibold text-slate-100">${g.name}</p>
              <p class="text-xs text-slate-400">${g.players.length}/${g.slots} players • ${g.status}</p>
            </div>
            <span class="badge">Join</span>
          </div>
        `;
        btn.addEventListener("click", () => {
          state.gameId = g.id;
          localStorage.setItem("morghi_game_id", g.id);
          window.location.href = "/lobby.html";
        });
        list.appendChild(btn);
      });
    } catch (err) {
      list.innerHTML = `<p class="text-red-300">Failed to load games.</p>`;
      console.error(err);
    }
  }

  /* ---------- Lobby page ---------- */
  function initLobbyPage() {
    setCurrentPlayer(state.name);
    connectSse();
    const readyBtn = qs("#ready-toggle");
    const statusPill = qs("#status-pill");
    const gamePill = qs("#game-id-pill");
    const playerList = qs("#player-list");
    const playerCount = qs("#player-count");

    if (state.gameId) gamePill.textContent = `Game: ${state.gameId}`;

    readyBtn?.addEventListener("click", async () => {
      if (!state.gameId) return alert("Pick or create a game first.");
      const nextReady = !readyBtn.dataset.ready;
      readyBtn.dataset.ready = nextReady ? "1" : "";
      readyBtn.textContent = nextReady ? "I'm not ready" : "I'm ready";
      statusPill.textContent = nextReady ? "Ready" : "Idle";
      await fetch(`/game/${state.gameId}/ready`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ready: nextReady }),
      });
      loadGame(state.gameId, playerList, playerCount);
    });

    if (state.gameId) loadGame(state.gameId, playerList, playerCount);
  }

  async function loadGame(gameId, playerList, playerCount) {
    if (!playerList) return;
    playerList.innerHTML = `<li class="text-slate-400">Loading game...</li>`;
    try {
      const res = await fetch(`/game/${gameId}`);
      const data = await res.json();
      const players = data.players || [];
      playerList.innerHTML = "";
      players.forEach((p) => {
        const li = document.createElement("li");
        li.className = "flex items-center justify-between rounded-lg bg-slate-800/70 px-3 py-2";
        li.innerHTML = `
          <span class="text-slate-100">${p.name}</span>
          <span class="badge ${p.ready ? "bg-emerald-500/20 border-emerald-400/40 text-emerald-200" : ""}">${p.ready ? "Ready" : "Not ready"}</span>
        `;
        playerList.appendChild(li);
      });
      if (playerCount) playerCount.textContent = `${players.length}/${data.slots} players`;
    } catch (err) {
      playerList.innerHTML = `<li class="text-red-300">Unable to load players.</li>`;
      console.error(err);
    }
  }

  /* ---------- Game page ---------- */
  function initGamePage() {
    setCurrentPlayer(state.name);
    connectSse();
    qsa(".action-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.dataset.action;
        appendChatMessage({ text: `Requested action: ${action}`, system: true });
      });
    });
  }

  function updateHand(cards = []) {
    const slots = qsa("#hand-cards .card-slot");
    cards.slice(0, 4).forEach((card, idx) => {
      if (slots[idx]) slots[idx].textContent = card || "?";
    });
  }

  function updateScores(eggs, chickens) {
    const eggsEl = qs("#score-eggs");
    const chickEl = qs("#score-chickens");
    if (eggsEl) eggsEl.textContent = eggs;
    if (chickEl) chickEl.textContent = chickens;
  }

  /* ---------- Chat shared ---------- */
  function initChat() {
    const chatForm = qs("#chat-form");
    chatForm?.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(chatForm);
      const message = (fd.get("message") || "").toString().trim();
      if (!message) return;
      appendChatMessage({ text: message, from: state.name || "You" });
      chatForm.reset();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initChat();
    const page = document.body.dataset.page;
    switch (page) {
      case "login":
        initLoginPage();
        break;
      case "lobby":
        initLobbyPage();
        break;
      case "game":
        initGamePage();
        break;
      default:
        connectSse();
        break;
    }
  });
})();
