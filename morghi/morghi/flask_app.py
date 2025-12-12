from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Generator

from flask import Flask, Response, jsonify, request, send_from_directory


class MorghiApp:
    """
    Minimal mock Flask application that serves the SPA assets and exposes
    placeholder endpoints for the front-end to call. Business logic will be
    implemented later; for now we only return static or mocked payloads so
    the UI can render and navigate without errors.
    """

    def __init__(self) -> None:
        static_root = Path(__file__).parent / "static"
        self.app = Flask(__name__, static_folder=str(static_root), static_url_path="")
        self._static_root = static_root
        self._register_routes()

    # Public API ---------------------------------------------------------
    def run(self, **kwargs: Any) -> None:
        """Run the underlying Flask app."""
        self.app.run(**kwargs)

    # Internal helpers ---------------------------------------------------
    def _register_routes(self) -> None:
        app = self.app

        # Static assets
        @app.get("/")
        def serve_index() -> Response:
            return send_from_directory(self._static_root, "main.html")

        @app.get("/main.css")
        def serve_css() -> Response:
            return send_from_directory(self._static_root, "main.css")

        @app.get("/main.js")
        def serve_js() -> Response:
            return send_from_directory(self._static_root, "main.js")

        # Auth / session (mocked)
        @app.post("/login")
        def login() -> tuple[Response, int]:
            payload = request.get_json(silent=True) or {}
            name = (payload.get("name") or "").strip()
            if not name:
                return jsonify({"error": "Name is required"}), 400

            token = f"token-{name.lower().replace(' ', '-')}"
            return jsonify(
                {
                    "token": token,
                    "player": {"id": hash(token) % 10_000, "name": name},
                }
            ), 200

        # Games listing and creation (mocked)
        @app.get("/games")
        def list_games() -> tuple[Response, int]:
            games = [
                {
                    "id": "G-1234",
                    "name": "Sunny Barn",
                    "status": "Waiting",
                    "players": 2,
                    "capacity": 4,
                },
                {
                    "id": "G-5678",
                    "name": "Fox & Feathers",
                    "status": "Waiting",
                    "players": 3,
                    "capacity": 4,
                },
            ]
            return jsonify({"games": games}), 200

        @app.post("/games")
        def create_game() -> tuple[Response, int]:
            payload = request.get_json(silent=True) or {}
            title = payload.get("name") or "New Game"
            mock_game = {
                "id": f"G-{int(time.time())}",
                "name": title,
                "status": "Waiting",
                "players": 1,
                "capacity": 4,
            }
            return jsonify(mock_game), 201

        # Single game info (mocked)
        @app.get("/game/<game_id>")
        def get_game(game_id: str) -> tuple[Response, int]:
            mock_state = self._mock_game_state(game_id)
            return jsonify(mock_state), 200

        # Ready toggle (mocked)
        @app.post("/game/<game_id>/ready")
        def set_ready(game_id: str) -> tuple[Response, int]:
            payload = request.get_json(silent=True) or {}
            return jsonify(
                {
                    "game_id": game_id,
                    "ready": bool(payload.get("ready")),
                    "ack": True,
                }
            ), 200

        # Server-Sent Events stream (mocked)
        @app.get("/game/<game_id>/listen")
        def listen(game_id: str) -> tuple[Response, int]:
            def event_stream() -> Generator[str, None, None]:
                state = self._mock_game_state(game_id)
                yield self._format_sse("state", state)
                # Periodic heartbeat to keep the connection open
                while True:
                    time.sleep(15)
                    yield ": ping\n\n"

            return Response(event_stream(), mimetype="text/event-stream"), 200

    # Mock data helpers --------------------------------------------------
    def _mock_game_state(self, game_id: str) -> Dict[str, Any]:
        return {
            "id": game_id,
            "name": "Mock Match",
            "status": "Waiting",
            "players": [
                {"id": 1, "name": "Alice", "ready": True, "scores": {"eggs": 1, "chickens": 0}},
                {"id": 2, "name": "Bob", "ready": True, "scores": {"eggs": 0, "chickens": 0}},
            ],
            "you": {
                "id": 1,
                "hand": ["Hen", "Rooster", "Nest", "Fox"],
                "scores": {"eggs": 1, "chickens": 0},
            },
            "chat": [
                {"id": "m1", "sender": "system", "text": "Welcome to the coop!", "ts": int(time.time())}
            ],
        }

    @staticmethod
    def _format_sse(event: str, data: Dict[str, Any]) -> str:
        payload = json.dumps(data)
        return f"event: {event}\ndata: {payload}\n\n"

if __name__ == '__main__':
    app = MorghiApp().app
    app.run()