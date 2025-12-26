import { writable, type Writable } from 'svelte/store';

export class AuthState {
    public readonly token: string;
    public readonly playerId: number;
    public readonly playerName: string;
    constructor(token: string, userId: number, userName: string) {
        this.token = token;
        this.playerId = userId;
        this.playerName = userName;
    }
    public static from_json(json: any): AuthState {
        if (typeof json === 'string') { json = JSON.parse(json); }
        if (json == null) { throw new Error('Invalid json, Parsed item is null'); }
        if (typeof json !== 'object') { throw new Error('Invalid json, Parsed item not an object') }
        if (typeof json['token'] !== 'string') { throw new Error("'token' not found or invalid in parsed json object") }
        if (typeof json['playerId'] !== 'number') { throw new Error("'playerId' not found or invalid in parsed json object") }
        if (typeof json['playerName'] !== 'string') { throw new Error("'playerName' not found or invalid in parsed json object") }
        return new AuthState(json['token'], json['playerId'], json['playerName']);
    }
}
export class AuthService {
    private _auth: AuthState | null;
    public get auth(): AuthState | null { return this._auth; }
    private _isLoggedIn: boolean;
    public get isLoggedIn(): boolean { return this._isLoggedIn; }
    private _token: string | null;
    public get token(): string | null { return this._token; }
    private _playerId: number | null;
    public get playerId(): number | null { return this._playerId; }
    private _playerName: string | null;
    public get playerName(): string | null { return this._playerName; }
    public constructor() {
        this._auth = $state(AuthService.load_state());
        this._isLoggedIn = $derived(this._auth !== null);
        this._token = $derived(this._auth?.token ?? null);
        this._playerId = $derived(this._auth?.playerId ?? null);
        this._playerName = $derived(this._auth?.playerName ?? null);
    }
    private update(auth: AuthState | null) {
        this._auth = auth;
        if (this._auth == null) {
            localStorage.removeItem('auth');
        } else {
            localStorage.setItem('auth', JSON.stringify(this._auth));
        }
    }
    public logout() {
        this.update(null);
    }
    public login_from_json(json: any) {
        this.update(AuthState.from_json(json));
    }
    private static load_state(): AuthState | null {
        let item = localStorage.getItem('auth');
        if (item == null) { return null; }
        try {
            return AuthState.from_json(item);
        } catch (x) {
            console.error(x);
            localStorage.removeItem('auth');
            return null;
        }
    }
}
let service = $state(new AuthService());
export default service;