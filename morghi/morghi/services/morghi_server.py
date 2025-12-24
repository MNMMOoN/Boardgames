import datetime
import flask
import flask_jwt_extended as jwt
import json
import queue
import random
import traceback
import typing as T
from .game import Game
from .event_update import EventUpdate
from morghi.core import Injector, MorghiConfig, actions


class MorghiServer:
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
            view_func=self._game__get_,
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/listen",
            view_func=self._game__listen__get_,
            methods=["GET"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/join",
            view_func=self._game__join__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/ready",
            view_func=self._game__ready__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/leave",
            view_func=self._game__leave__post_,
            methods=["POST"],
        )
        self._app_.add_url_rule(
            "/games/<game_id>/action",
            view_func=self._game__action__post_,
            methods=["POST"],
        )

    # EndPoints
    def _login__post_(self) -> tuple[flask.Response, int]:
        try:
            name: str = str(flask.request.get_json()["name"])
        except Exception as x:
            traceback.print_exception(x)
            return flask.jsonify({"error": "Name is required"}), 400
        id = random.randint(0, 10000)
        token = jwt.create_access_token(
            identity=name,
            expires_delta=datetime.timedelta(days=7),
            additional_claims={"id": id},
        )
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

        try:
            name: str = str(flask.request.get_json()["name"])
        except Exception as x:
            traceback.print_exception(x)
            return flask.jsonify({"error": "Name is required"}), 400
        game = Game(id=random.randint(0, 10000), name=name)
        self._games_[game.id] = game
        return flask.jsonify(game.get_info()), 201

    def _game__get_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}, {game_id=}, {type(game_id)=}")

        state = self._games_.get(game_id)
        if state is None:
            return flask.jsonify({"error": "Game not found"}), 404
        return flask.jsonify(state), 200

    def _game__listen__get_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        game = self._games_.get(game_id)
        if game is None:
            return flask.jsonify({"error": "Game not found"}), 404
        return flask.Response(
            self._event_stream_(game, user_id), mimetype="text/event-stream"
        ), 200

    def _game__join__post_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}, {game_id=}, {type(game_id)=}")

        game = self._games_.get(game_id)
        if game is None:
            return flask.jsonify({"error": "Game not found"}), 404
        error = game.on_player_join(user_id)
        if error:
            return flask.jsonify({"error": error}), 400
        else:
            return flask.Response(None), 204

    def _game__ready__post_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")
        if game_id not in self._games_:
            return flask.jsonify({"error": "Game not found"}), 404
        error = self._games_[game_id].on_player_ready(user_id)
        if error:
            return flask.jsonify({"error": error}), 400
        else:
            return flask.Response(None), 204

    def _game__leave__post_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")
        if game_id not in self._games_:
            return flask.jsonify({"error": "Game not found"}), 404
        error = self._games_[game_id].on_player_leave(user_id)
        if error:
            return flask.jsonify({"error": error}), 400
        else:
            return flask.Response(None), 204

    def _game__action__post_(self, game_id: str | int) -> tuple[flask.Response, int]:
        game_id = int(game_id)
        user_id, user_name = self._get_auth_()
        print(f"{user_id=}, {user_name=}")

        if game_id not in self._games_:
            return flask.jsonify({"error": "Game not found"}), 404
        try:
            payload = dict(flask.request.get_json())
        except Exception as x:
            traceback.print_exception(x)
            return flask.jsonify({"error": "Invalid payload"}), 400
        try:
            action_name: str = str(payload.get("name"))
        except Exception as x:
            traceback.print_exception(x)
            return flask.jsonify({"error": "Action name is required"}), 400
        try:
            action_request: actions.Action = actions.Action.create_from_dict(
                name=action_name,
                data=payload,
            )
        except Exception as x:
            traceback.print_exception(x)
            return flask.jsonify(
                {"error": f"Failed to parse action '{action_name}'; {x}"}
            ), 400
        # areates Action
        error = self._games_[game_id].on_action(player=user_id, action=action_request)
        if error:
            return flask.jsonify({"error": error}), 400
        else:
            return flask.Response(None), 204

    # Methods
    def _event_stream_(
        self, game: Game, player_id: int
    ) -> T.Generator[str, None, None]:
        lq = game.on_player_listen(player_id)
        try:
            # Immediately send current state on connection
            eu = EventUpdate(event="state", data=game.get_state(player_id))
            yield json.dumps(eu.to_dict())
            # Send updates
            while True:
                try:
                    eu = lq.get(timeout=10.0)
                except queue.Empty:
                    eu = EventUpdate(event="ping", data=None)
                yield json.dumps(eu.to_dict())
        except Exception as x:
            print(x)
        finally:
            game._announcer_.remove_listener(lq)

    def _get_auth_(self) -> tuple[int, str]:
        jwt.verify_jwt_in_request()
        payload = jwt.get_jwt()
        return payload["id"], payload["sub"]
