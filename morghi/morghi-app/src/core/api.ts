import config from "./config";
import { SSE } from "sse.js";
import type { SSEHeaders } from "sse.js"
class Api {
    private url: string;
    constructor() {
        this.url = config.api.url;
        if (this.url.endsWith('/')) {
            this.url = this.url.slice(0, -1);
        }
    }
    public async get(endpoint: string, auth: string | null = null): Promise<any> {
        const headers = new Headers();
        if (auth != null) { headers.append('Authorization', `Bearer ${auth}`); }
        const response = await fetch(this.url + endpoint, {
            method: 'GET',
            headers: headers
        });
        const ret = await response.json();
        if (!response.ok) {
            throw Error(ret.error);
        }
        return ret;
    }
    public async post(endpoint: string, auth: string | null = null, body: object | null = null): Promise<any> {
        const headers = new Headers();
        headers.append('Content-Type', 'application/json');
        if (auth != null) { headers.append('Authorization', `Bearer ${auth}`); }
        const response = await fetch(this.url + endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body)
        });
        const ret = response.status == 204 ? {} : await response.json();
        if (!response.ok) {
            throw Error(ret.error);
        }
        return ret;
    }
    public stream(endpoint: string, handlers: { [key: string]: Function }, auth: string | null = null, method: string = 'GET'): SSE {
        const headers: SSEHeaders = {};
        if (auth != null) { headers['Authorization'] = `Bearer ${auth}`; }
        const ret: SSE = new SSE(this.url + endpoint, {
            start: false,
            method: method,
            headers: headers,
        });
        ret.onmessage = (e) => console.log('SSE; OnMessage: ', e);
        ret.addEventListener('open', (e: any) => console.log('SSE; CONNECTION OPENED: ', e));
        ret.addEventListener('message', (e: any) => console.log('SSE; MESSAGE: ', e));
        ret.addEventListener('error', (e: any) => console.log('SSE; ERROR: ', e));
        for (const [event, handler] of Object.entries(handlers)) {
            ret.addEventListener(event, handler);
        }
        ret.stream();
        return ret;
    }
}
const api = new Api();
export default api;