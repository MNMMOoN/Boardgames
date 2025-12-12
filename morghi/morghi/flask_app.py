from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
    Response,
)


@dataclass
class LobbyPlayer:
    id: str
    name: str
    ready: bool = False


@dataclass
class LobbyGame:
    id: str
    name: str
    slots: int = 4
    status: str = "Waiting"
    players: List[LobbyPlayer] = None  # type: ignore

    def to_dict(self) -> Dict:
        payload = asdict(self)
        payload["players"] = [asdict(p) for p in self.players or []]
        return payload


class MorghiApp:
    """
    Minimal mock Flask app to serve the UI without backend logic.
    All endpoints are lightweight stubs that return predictable data
    so the front-end can be exercised without game rules implemented.
    """

    def __init__(self) -> None:
        self.app = Flask(
            __name__, static_folder="static", template_folder="templates"
        )
        self.app.secret_key = "dev-secret"  # Replace for production
        self.games: Dict[str, LobbyGame] = {}
        self._bootstrap_data()
        self._register_routes()

    def _bootstrap_data(self) -> None:
        # Seed a couple of fake lobby games for the UI to render.
        g1 = LobbyGame(
            id=str(uuid.uuid4())[:8],
            name="Sunrise Coop",
            slots=4,
            status="Waiting",
            players=[
                LobbyPlayer(id="p1", name="Alex", ready=True),
                LobbyPlayer(id="p2", name="Sam", ready=False),
            ],
        )
        g2 = LobbyGame(
            id=str(uuid.uuid4())[:8],
            name="Night Watch",
            slots=5,
            status="Waiting",
            players=[LobbyPlayer(id="p3", name="Kai", ready=False)],
        )
        self.games[g1.id] = g1
        self.games[g2.id] = g2

    def _register_routes(self) -> None:
        app = self.app

        @app.route("/")
        def index():
            username = session.get("username")
            status = session.get("status", "login")
            if not username:
                return redirect(url_for("login_page"))
            if status == "playing":
                return redirect(url_for("game_page"))
            return redirect(url_for("lobby_page"))

        @app.route("/login.html")
        def login_page():
            return render_template("login.html")

        @app.route("/lobby.html")
        def lobby_page():
            return render_template("lobby.html")

        @app.route("/game.html")
        def game_page():
            return render_template("game.html")

        @app.route("/main.css")
        def main_css():
            return send_from_directory(app.static_folder, "main.css")

        @app.route("/main.js")
        def main_js():
            return send_from_directory(app.static_folder, "main.js")

        @app.post("/login")
        def login():
            data = request.get_json(silent=True) or request.form
            username = (data.get("name") or "").strip()
            if not username:
                return jsonify({"error": "name is required"}), 400

            token = str(uuid.uuid4())
            session["username"] = username
            session["token"] = token
            session["status"] = "lobby"
            session["game_id"] = None
            return jsonify({"token": token, "name": username})

        @app.get("/games")
        def list_games():
            payload = [g.to_dict() for g in self.games.values()]
            return jsonify({"games": payload})

        @app.post("/games")
        def create_game():
            data = request.get_json(silent=True) or request.form
            name = (data.get("name") or "New Game").strip()
            slots = int(data.get("slots") or 4)
            gid = str(uuid.uuid4())[:8]
            game = LobbyGame(id=gid, name=name, slots=slots, players=[])
            self.games[gid] = game
            return jsonify(game.to_dict()), 201

        @app.get("/game/<gid>")
        def get_game(gid: str):
            game = self.games.get(gid)
            if not game:
                return jsonify({"error": "not found"}), 404
            return jsonify(game.to_dict())

        @app.post("/game/<gid>/ready")
        def set_ready(gid: str):
            game = self.games.get(gid)
            if not game:
                return jsonify({"error": "not found"}), 404

            data = request.get_json(silent=True) or request.form
            ready = str(data.get("ready", "")).lower() in {"1", "true", "yes", "on"}
            username = session.get("username", "Guest")

            # Simple upsert for the requesting player in the lobby.
            existing: Optional[LobbyPlayer] = next(
                (p for p in game.players if p.name == username), None
            )
            if existing:
                existing.ready = ready
            else:
                game.players.append(
                    LobbyPlayer(id=str(uuid.uuid4())[:8], name=username, ready=ready)
                )
            session["status"] = "playing" if ready else "lobby"
            session["game_id"] = gid
            return jsonify(game.to_dict())

        @app.route("/events")
        def events():
            def stream():
                yield "event: message\ndata: {\"text\": \"Connected to lobby\", \"system\": true}\n\n"
                # Periodic ping to keep connection open for demo purposes.
                while True:
                    time.sleep(15)
                    yield "event: ping\ndata: {}\n\n"

            return Response(stream(), mimetype="text/event-stream")

    def get_app(self) -> Flask:
        return self.app


def create_app() -> Flask:
    return MorghiApp().get_app()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
