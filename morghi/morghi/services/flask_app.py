import flask
import flask_jwt_extended as jwt
import json
import random
import typing as T
from .morghi_game import Game
from morghi.core import Injector, MorghiConfig


class MorghiApp:
    _app_: flask.Flask
    _games_: dict[int, Game]
    _injector_: Injector

    def __init__(self, root_module_name: str, injector: Injector) -> None:
        self._injector_ = injector
        self._games_ = {}
        self._app_ = flask.Flask(root_module_name)
        self._jwt_ = jwt.JWTManager(self._app_)
        config: MorghiConfig = injector.get_service(MorghiConfig)
        self._app_.config["JWT_SECRET_KEY"] = config["jwt_secret"]
        self._register_routes_()

    def run(self) -> None:
        config: MorghiConfig = self._injector_.get_service(MorghiConfig)
        self._app_.run(host="0.0.0.0", port=config["port"])

    def _register_routes_(self) -> None:
        self._app_.add_url_rule(
            "/",
            endpoint="/main.html",
            view_func=lambda: self._app_.send_static_file("main.html"),
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/main.css",
            endpoint="/main.css",
            view_func=lambda: self._app_.send_static_file("main.css"),
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/main.js",
            endpoint="/main.js",
            view_func=lambda: self._app_.send_static_file("main.js"),
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/login",
            view_func=self._login__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games",
            view_func=self._games__get_,
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/games",
            view_func=self._games__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>",
            view_func=self._games__by_id__get_,
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/ready",
            view_func=self._games__by_id__ready__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/listen",
            view_func=self._games__by_id__listen__get_,
            methods=["GET"],
        )

    # EndPoints
    def _login__post_(self) -> tuple[flask.Response, int]:
        payload = flask.request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        if not name:
            return flask.jsonify({"error": "Name is required"}), 400
        id = random.randint(0, 10000)
        token = jwt.create_access_token(identity=name, additional_claims={"id": id})
        return flask.jsonify(
            {
                "token": token,
                "player": {"id": id, "name": name},
            }
        ), 200

    def _games__get_(self) -> tuple[flask.Response, int]:
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        games = [g.get_info() for g in self._games_.values()]
        return flask.jsonify({"games": games}), 200

    def _games__post_(self) -> tuple[flask.Response, int]:
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        payload = flask.request.get_json(silent=True) or {}
        title = payload.get("name") or "New Game"
        game = Game(id=random.randint(0, 10000), name=title)
        self._games_[game.id] = game
        return flask.jsonify(game.get_info()), 201

    def _games__by_id__get_(self, game_id: int) -> tuple[flask.Response, int]:
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        state = self._games_.get(game_id)
        if state is None:
            return flask.jsonify({"error": "Game not found"}), 404
        return flask.jsonify(state), 200

    def _games__by_id__ready__post_(self, game_id: int) -> tuple[flask.Response, int]:
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        payload = flask.request.get_json(silent=True) or {}
        return flask.jsonify(
            {
                "game_id": game_id,
                "ready": bool(payload.get("ready")),
                "ack": True,
            }
        ), 200

    def _games__by_id__listen__get_(self, game_id: int) -> tuple[flask.Response, int]:
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        game = self._games_.get(game_id)
        if game is None:
            return flask.jsonify({"error": "Game not found"}), 404
        return flask.Response(
            self._event_stream_(game, user_id), mimetype="text/event-stream"
        ), 200

    # Methods
    def _event_stream_(self, game: Game, user_id: int) -> T.Generator[str, None, None]:
        queue = game.announcer.add_listener()
        # Immediately send current state on connection
        yield json.dumps({"event": "init", "data": game.get_state_for(user_id)})
        # Send updates
        while True:
            msg = queue.get(timeout=10)
            yield json.dumps(msg)

    def _get_auth_(self) -> tuple[int, str]:
        jwt.verify_jwt_in_request()
        payload = jwt.get_jwt()
        return payload["id"], payload["sub"]
