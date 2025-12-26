import { SvelteMap } from 'svelte/reactivity';
import type { GameInfo, Message } from '../../core/state';
import type { Player } from './Player.svelte';

export class Game {
    public id: number;
    constructor(info: GameInfo) {
        this.id = info.id;
    }
    public isPlaying: boolean = $state(false);
    public players = new SvelteMap<number, Player>();
    public messages: Message[] = $state([]);
    public playerEggs: number = $state(0);
    public playerChickens: number = $state(0);
    public playerReady: boolean = $state(false);
    public playerHand: string[] = $state([]);
}
