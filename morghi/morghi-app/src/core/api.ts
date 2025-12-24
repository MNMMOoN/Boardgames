import config from "./config";
class Api {
    private url: string;
    constructor() {
        this.url = config.api.url;
        if (this.url.endsWith('/')) {
            this.url = this.url.slice(0, -1);
        }
    }
    public async fetchPost(endpoint: string, auth: string | null = null, body: object | null = null): Promise<any> {
        const headers = new Headers();
        headers.append('Content-Type', 'application/json');
        if (auth != null) { headers.append('Authorization', auth); }
        const response = await fetch(this.url + endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body)
        });
        const ret = await response.json();
        if (!response.ok) {
            throw Error(ret.error);
        }
        return ret;
    }
}
export const api = new Api();