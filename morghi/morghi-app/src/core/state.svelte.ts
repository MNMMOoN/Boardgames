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
    public static from_json(item: any): AuthState {
        if (typeof item === 'string') {
            item = JSON.parse(item);
        }
        if (!item) { throw new Error('Invalid auth state'); }
        if (typeof item !== 'object') { throw new Error('Parsed auth state is not an object') }
        if (typeof item['token'] !== 'string') { throw new Error("'token' not found in auth state") }
        if (typeof item['playerId'] !== 'number') { throw new Error("'playerId' not found in auth state") }
        if (typeof item['playerName'] !== 'string') { throw new Error("'playerName' not found in auth state") }
        return new AuthState(item['token'], item['playerId'], item['playerName']);
    }
}
