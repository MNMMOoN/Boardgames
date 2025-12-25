export class AuthState {
    public readonly token: string;
    public readonly playerId: number;
    public readonly playerName: string;
    constructor(token: string, userId: number, userName: string) {
        this.token = token;
        this.playerId = userId;
        this.playerName = userName;
    }
    public save() {
        localStorage.setItem('auth', JSON.stringify(this));
    }
    public static load(): AuthState | null {
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
export class GameInfo {
    public id: number
    public name: string
    public status: string
    public players: number[]
    public capacity: number
    constructor(id: number, name: string, status: string, players: number[], capacity: number) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.players = players;
        this.capacity = capacity;
    }
    public static from_json(json: any): GameInfo {
        if (typeof json === 'string') { json = JSON.parse(json); }
        if (json == null) { throw new Error('Invalid json, Parsed item is null'); }
        if (typeof json !== 'object') { throw new Error('Invalid json; Parsed item not an object'); }
        if (typeof json['id'] !== 'number') { throw new Error("'id' not found or invalid in parsed json object") }
        if (typeof json['name'] !== 'string') { throw new Error("'name' not found or invalid in parsed json object") }
        if (typeof json['status'] !== 'string') { throw new Error("'status' not found or invalid in parsed json object") }
        if (typeof json['players'] !== 'object') { throw new Error("'players' not found or invalid in parsed json object") }
        if (typeof json['capacity'] !== 'number') { throw new Error("'capacity' not found or invalid in parsed json object") }
        return new GameInfo(json.id, json.name, json.status, json.players, json.capacity);
    }
}
export class Message {
    public id: number
    public sender: string
    public text: string
    public time_ms: number
    constructor(id: number, sender: string, text: string, time_ms: number) {
        this.id = id;
        this.sender = sender;
        this.text = text;
        this.time_ms = time_ms;
    }
    public static from_json(json: any): Message {
        if (typeof json === 'string') { json = JSON.parse(json); }
        if (json == null) { throw new Error('Invalid json, Parsed item is null'); }
        if (typeof json !== 'object') { throw new Error('Invalid json; Parsed item not an object'); }
        if (typeof json['id'] !== 'number') { throw new Error("'id' not found or invalid in parsed json object") }
        if (typeof json['sender'] !== 'string') { throw new Error("'sender' not found or invalid in parsed json object") }
        if (typeof json['text'] !== 'string') { throw new Error("'text' not found or invalid in parsed json object") }
        if (typeof json['time_ms'] !== 'number') { throw new Error("'time_ms' not found or invalid in parsed json object") }
        return new Message(json.id, json.sender, json.text, json.time_ms);
    }
}
export class PlayerState {
    public id: number
    public name: string
    public ready: boolean
    public eggs: number
    public chickens: number
    public hand: string[] | undefined
    constructor(id: number, name: string, ready: boolean, eggs: number, chickens: number, hand: string[] | undefined) {
        this.id = id;
        this.name = name;
        this.ready = ready;
        this.eggs = eggs;
        this.chickens = chickens;
        this.hand = hand;
    }
    public static from_json(json: any): PlayerState {
        if (typeof json === 'string') { json = JSON.parse(json); }
        if (json == null) { throw new Error('Invalid json, Parsed item is null'); }
        if (typeof json !== 'object') { throw new Error('Invalid json; Parsed item not an object'); }
        if (typeof json['id'] !== 'number') { throw new Error("'id' not found or invalid in parsed json object") }
        if (typeof json['name'] !== 'string') { throw new Error("'name' not found or invalid in parsed json object") }
        if (typeof json['ready'] !== 'boolean') { throw new Error("'ready' not found or invalid in parsed json object") }
        if (typeof json['eggs'] !== 'number') { throw new Error("'eggs' not found or invalid in parsed json object") }
        if (typeof json['chickens'] !== 'number') { throw new Error("'chickens' not found or invalid in parsed json object") }
        let hand: string[] | undefined = json['hand'];
        if (hand !== undefined && typeof hand !== 'object') { throw new Error("'hand' not found or invalid in parsed json object") }
        return new PlayerState(json.id, json.name, json.ready, json.eggs, json.chickens, hand);
    }
}
export class GameState {
    public id: number
    public name: string
    public status: string
    public players: PlayerState[]
    public messages: Message[]
    constructor(id: number, name: string, status: string, players: PlayerState[], messages: Message[]) {
        this.id = id;
        this.name = name;
        this.status = status;
        this.players = players;
        this.messages = messages;
    }
    public static from_json(json: any): GameState {
        if (typeof json === 'string') { json = JSON.parse(json); }
        if (json == null) { throw new Error('Invalid json, Parsed item is null'); }
        if (typeof json !== 'object') { throw new Error('Invalid json; Parsed item not an object'); }
        if (typeof json['id'] !== 'number') { throw new Error("'id' not found or invalid in parsed json object") }
        if (typeof json['name'] !== 'string') { throw new Error("'name' not found or invalid in parsed json object") }
        if (typeof json['status'] !== 'string') { throw new Error("'status' not found or invalid in parsed json object") }
        if (typeof json['players'] !== 'object') { throw new Error("'players' not found or invalid in parsed json object") }
        if (typeof json['messages'] !== 'object') { throw new Error("'messages' not found or invalid in parsed json object") }
        let players: PlayerState[] = [];
        for (let i = 0; i < json['players'].length; i++) {
            players.push(PlayerState.from_json(json['players'][i]));
        }
        let messages: Message[] = [];
        for (let i = 0; i < json['messages'].length; i++) {
            messages.push(Message.from_json(json['messages'][i]));
        }
        return new GameState(json.id, json.name, json.status, players, messages);
    }
}