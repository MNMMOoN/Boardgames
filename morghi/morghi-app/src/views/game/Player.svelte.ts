export class Player {
    public id: number = $state(0);
    public name: string = $state("");
    public ready: boolean = $state(false);
    public eggs: number = $state(0);
    public chickens: number = $state(0);
}
