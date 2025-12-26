import { GameState, Message } from '../../core/state';
import type { Game } from './Game.svelte';
import type { SSE } from 'sse.js';
import api from '../../core/api';
import auth from '../../services/auth.svelte';

export class GameEventsListener {
    private game: Game;
    private stream: SSE | null;
    constructor(game: Game) {
        this.game = game;
        this.stream = null;
    }
    public openStream() {
        this.stream = api.stream(
            `/games/${this.game.id}`,
            {
                state: this.onSseState.bind(this),
                message: this.onSseMessage.bind(this),
                player_ready: this.onSsePlayerReady.bind(this),
                game_start: this.onSseGameStart.bind(this),
                turn: this.onSseTurn.bind(this),
                hand_changed: this.onSseHandChanged.bind(this),
                scores_changed: this.onSseScoresChanged.bind(this),
            },
            auth.token,
        );
    }
    public closeStream() {
        this.stream?.close();
        this.stream = null;
    }
    public onSseState(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseState: ", data);
        console.log("GEL: this=", this);
        let state = GameState.from_json(data);
        this.game.players.clear();
        for (let p of state.players) {
            this.game.players.set(p.id, p);
            if (p.id == auth.playerId) {
                this.game.playerEggs = p.eggs;
                this.game.playerChickens = p.chickens;
                this.game.playerReady = p.ready;
                this.game.playerHand = p.hand ?? [];
            }
        }
        this.game.messages = state.messages;
    }
    public onSseMessage(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseMessage: ", data);
        let message = Message.from_json(data);
        this.game.messages = this.game.messages.concat(message);
    }
    public onSsePlayerReady(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSsePlayerReady: ", data);
        let playerId = data["player_id"];
        let player = this.game.players.get(playerId);
        if (player) {
            player.ready = true;
            this.game.players.set(playerId, player);
        }
        if (playerId == auth.playerId) {
            this.game.playerReady = true;
        }
    }
    public onSseGameStart(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseGameStart: ", data);
    }
    public onSseTurn(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseTurn: ", data);
    }
    public onSseHandChanged(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseHandChanged: ", data);
    }
    public onSseScoresChanged(data: any): void {
        data = JSON.parse(data["data"]);
        console.log("GEL: onSseScoresChanged: ", data);
    }
}
