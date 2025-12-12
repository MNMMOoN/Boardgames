(() => {
  const views = ["login", "game-select", "lobby", "game"];
  const state = {
    view: "login",
    player: null,
    token: null,
    games: [],
    currentGame: null,
    lobby: { players: [], status: "Waiting" },
    chat: [],
    hand: [],
    scores: { eggs: 0, chickens: 0 },
    eventSource: null,
  };

  // Helpers --------------------------------------------------------------
  const el = (id) => document.getElementById(id);
  const setStatus = (text) => (el("status-label").textContent = text);
  const saveSession = () =>
    localStorage.setItem(
      "morghi-session",
      JSON.stringify({ token: state.token, player: state.player })
    );
  const loadSession = () => {
    try {
      return JSON.parse(localStorage.getItem("morghi-session") || "{}");
    } catch {
      return {};
    }
  };

  const api = async (path, options = {}) => {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    const res = await fetch(path, { headers, ...options });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  };

  const showView = (name) => {
    views.forEach((v) => {
      el(`view-${v}`)?.classList.toggle("hidden", v !== name);
    });
    state.view = name;
    el("breadcrumb").textContent = name.replace("-", " ").toUpperCase();
    el("logout-btn").classList.toggle("hidden", name === "login");
  };

  const renderGames = (targetId) => {
    const container = el(targetId);
    container.innerHTML = "";
    if (!state.games.length) {
      container.innerHTML =
        '<p class="text-sm text-slate-400">No games yet. Create one!</p>';
      return;
    }
    state.games.forEach((g) => {
      const btn = document.createElement("button");
      btn.className =
        "flex w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900 px-3 py-3 text-left text-sm transition hover:border-amber-400 hover:bg-slate-800/70";
      btn.innerHTML = `
        <div>
          <p class="text-base font-semibold text-white">${g.name}</p>
          <p class="text-xs text-slate-400">${g.players}/${g.capacity} players • ${g.status}</p>
        </div>
        <span class="pill">Join</span>
      `;
      btn.addEventListener("click", () => enterLobby(g.id));
      container.appendChild(btn);
    });
  };

  const renderLobbyPlayers = () => {
    const target = el("lobby-players");
    target.innerHTML = "";
    state.lobby.players.forEach((p) => {
      const card = document.createElement("div");
      card.className =
        "flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2";
      card.innerHTML = `
        <div>
          <p class="font-semibold text-white">${p.name}</p>
          <p class="text-xs text-slate-400">Eggs ${p.scores.eggs} • Chickens ${p.scores.chickens}</p>
        </div>
        <span class="chip" style="background:${p.ready ? "#22c55e33" : "#334155"}; color:${p.ready ? "#bbf7d0" : "#e2e8f0"};">
          ${p.ready ? "Ready" : "Not ready"}
        </span>
      `;
      target.appendChild(card);
    });
  };

  const addChat = (msg) => {
    state.chat.push(msg);
    [el("chat-log"), el("chat-log-game")].forEach((box) => {
      if (!box) return;
      const line = document.createElement("div");
      line.className = `chat-line ${msg.sender === "system" ? "system" : ""}`;
      line.innerHTML = `
        <span class="text-xs text-slate-500">${new Date(msg.ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
        <strong>${msg.sender}</strong>
        <span class="flex-1">${msg.text}</span>
      `;
      box.appendChild(line);
      box.scrollTop = box.scrollHeight;
    });
  };

  const renderHand = () => {
    const grid = el("hand-grid");
    grid.innerHTML = "";
    state.hand.forEach((c) => {
      const tile = document.createElement("div");
      tile.className = "card-tile";
      tile.innerHTML = `
        <div class="card-icon">${c.type}</div>
        <div class="card-title">${c.name}</div>
        <div class="text-xs text-slate-400">${c.desc}</div>
      `;
      grid.appendChild(tile);
    });
  };

  const renderScores = () => {
    el("score-eggs").textContent = state.scores.eggs ?? 0;
    el("score-chickens").textContent = state.scores.chickens ?? 0;
    const board = el("scoreboard");
    board.innerHTML = "";
    state.lobby.players.forEach((p) => {
      const row = document.createElement("div");
      row.className =
        "flex items-center justify-between rounded-lg bg-slate-950/50 px-3 py-2 text-sm";
      row.innerHTML = `
        <div class="flex items-center gap-2">
          <div class="h-2 w-2 rounded-full" style="background:${p.ready ? "#22c55e" : "#eab308"}"></div>
          <span class="font-semibold text-white">${p.name}</span>
        </div>
        <div class="flex gap-3 text-xs text-slate-300">
          <span>🥚 ${p.scores.eggs}</span>
          <span>🐔 ${p.scores.chickens}</span>
        </div>
      `;
      board.appendChild(row);
    });
  };

  const deriveActions = () => {
    const counts = state.hand.reduce((acc, c) => {
      acc[c.name] = (acc[c.name] || 0) + 1;
      return acc;
    }, {});
    const canLay =
      counts.Hen >= 1 && counts.Rooster >= 1 && counts.Nest >= 1;
    const canHatch = (state.scores.eggs || 0) >= 1 && counts.Hen >= 2;
    const canFox = counts.Fox >= 1;
    const canSnake = counts.Snake >= 1;
    const canTrap = counts.Trap >= 1;
    return [
      { key: "lay-egg", label: "Lay an egg", enabled: canLay },
      { key: "hatch-egg", label: "Hatch egg → chicken", enabled: canHatch },
      { key: "fox", label: "Use Fox (steal)", enabled: canFox },
      { key: "snake", label: "Use Snake (break eggs)", enabled: canSnake },
      { key: "trap", label: "Use Trap (peek hand)", enabled: canTrap },
      { key: "replace", label: "Replace a card", enabled: true },
    ];
  };

  const renderActions = () => {
    const container = el("actions");
    container.innerHTML = "";
    deriveActions().forEach((action) => {
      const btn = document.createElement("button");
      btn.className = "action-btn";
      btn.disabled = !action.enabled;
      btn.innerHTML = `
        <span>${action.label}</span>
        <span class="pill">${action.enabled ? "Ready" : "Need cards"}</span>
      `;
      btn.addEventListener("click", () =>
        addChat({
          id: crypto.randomUUID(),
          sender: "you",
          text: `Action queued: ${action.label}`,
          ts: Math.floor(Date.now() / 1000),
        })
      );
      container.appendChild(btn);
    });
  };

  // EventSource handling -------------------------------------------------
  const closeStream = () => {
    if (state.eventSource) {
      state.eventSource.close();
      state.eventSource = null;
    }
  };

  const openStream = (gameId) => {
    closeStream();
    const es = new EventSource(`/game/${gameId}/listen`);
    state.eventSource = es;
    setStatus("Connected");

    es.addEventListener("state", (ev) => {
      const payload = JSON.parse(ev.data);
      applyStateFromServer(payload);
    });

    es.addEventListener("game_started", () => {
      addChat({
        id: crypto.randomUUID(),
        sender: "system",
        text: "Game started!",
        ts: Math.floor(Date.now() / 1000),
      });
      showView("game");
    });

    es.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      addChat(msg);
    });

    es.addEventListener("hand_changed", (ev) => {
      state.hand = JSON.parse(ev.data).hand || state.hand;
      renderHand();
      renderActions();
    });

    es.addEventListener("scores_changed", (ev) => {
      const scores = JSON.parse(ev.data);
      state.scores = scores.you || state.scores;
      state.lobby.players = scores.players || state.lobby.players;
      renderScores();
    });

    es.addEventListener("fox_incoming", () => {
      addChat({
        id: crypto.randomUUID(),
        sender: "system",
        text: "Fox incoming! You may defend with 2 Roosters.",
        ts: Math.floor(Date.now() / 1000),
      });
    });

    es.onerror = () => setStatus("Reconnecting…");
  };

  // State application ----------------------------------------------------
  const applyStateFromServer = (payload) => {
    state.currentGame = payload.id;
    state.lobby.players = payload.players || [];
    state.hand = (payload.you && payload.you.hand || []).map((name) => ({
      name,
      type: ["Hen", "Rooster", "Fox", "Snake", "Trap"].includes(name)
        ? "Animal"
        : "Nest",
      desc: "Card in your hand",
    }));
    state.scores = payload.you?.scores || state.scores;
    payload.chat?.forEach(addChat);
    renderLobbyPlayers();
    renderHand();
    renderActions();
    renderScores();
    el("lobby-title").textContent = payload.name || "Lobby";
  };

  // Actions --------------------------------------------------------------
  const enterLobby = async (gameId) => {
    const data = await api(`/game/${gameId}`);
    applyStateFromServer(data);
    showView("lobby");
    openStream(gameId);
  };

  const loadGames = async () => {
    const data = await api("/games");
    state.games = data.games || [];
    renderGames("game-list");
  };

  // Event wiring ---------------------------------------------------------
  const setupEvents = () => {
    el("login-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = el("name-input").value.trim();
      if (!name) return;
      const res = await api("/login", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      state.player = res.player;
      state.token = res.token;
      saveSession();
      setStatus(`Logged in as ${res.player.name}`);
      await loadGames();
      showView("game-select");
    });

    el("reload-lobby-games").addEventListener("click", loadGames);

    el("create-game-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = el("game-name-input").value.trim() || "New Game";
      const res = await api("/games", {
        method: "POST",
        body: JSON.stringify({ name }),
      });
      state.games.unshift(res);
      renderGames("game-list");
      await enterLobby(res.id);
    });

    el("ready-btn").addEventListener("click", async () => {
      const desired = !state.lobby.players.find(
        (p) => p.id === state.player?.id
      )?.ready;
      await api(`/game/${state.currentGame}/ready`, {
        method: "POST",
        body: JSON.stringify({ ready: desired }),
      });
      addChat({
        id: crypto.randomUUID(),
        sender: "system",
        text: desired ? "You are ready" : "You are not ready",
        ts: Math.floor(Date.now() / 1000),
      });
    });

    const chatSubmit = (inputId) => async (e) => {
      e.preventDefault();
      const input = el(inputId);
      const text = input.value.trim();
      if (!text) return;
      addChat({
        id: crypto.randomUUID(),
        sender: state.player?.name || "you",
        text,
        ts: Math.floor(Date.now() / 1000),
      });
      input.value = "";
      // Placeholder: would POST to server here
    };

    el("chat-form").addEventListener("submit", chatSubmit("chat-input"));
    el("chat-form-game").addEventListener(
      "submit",
      chatSubmit("chat-input-game")
    );

    el("logout-btn").addEventListener("click", () => {
      closeStream();
      state.player = null;
      state.token = null;
      localStorage.removeItem("morghi-session");
      setStatus("Offline");
      showView("login");
    });
  };

  // Boot ---------------------------------------------------------------
  const boot = async () => {
    setupEvents();
    const session = loadSession();
    if (session?.token && session?.player) {
      state.token = session.token;
      state.player = session.player;
      setStatus(`Logged in as ${session.player.name}`);
      await loadGames();
      showView("game-select");
    } else {
      showView("login");
      await loadGames();
    }
  };

  document.addEventListener("DOMContentLoaded", boot);
})();
