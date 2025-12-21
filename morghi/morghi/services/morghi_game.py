import time
import queue
import random
from morghi.core import rules, GameState, GameInfo, Message
from .event_update import EventUpdate
from .event_announcer import EventAnnouncer
from .morghi_deck import DeckOfCards
from .morghi_player import Player


REACTION_CAUSE_FOX_DEFENSE = "fox_defense"


class ReactionExpectation:
    def __init__(self, cause: str, reacting_player: int, acting_player: int):
        self.cause: str = cause
        self.reacting_player: int = reacting_player
        self.acting_player: int = acting_player

    @classmethod
    def make_fox_defense(cls, reacting_player: int, acting_player: int):
        return cls(REACTION_CAUSE_FOX_DEFENSE, reacting_player, acting_player)


class PlayResult:
    next_player: bool
    error: str | None

    def __init__(self, next_player: bool, error: str | None):
        self.next_player = next_player
        self.error = error

    @classmethod
    def err(cls, error: str) -> PlayResult:
        return PlayResult(next_player=False, error=error)


class Game:
    def __init__(self, id: int, name: str) -> None:
        self.id: int = id
        self.name: str = name
        self._announcer_: EventAnnouncer = EventAnnouncer()
        self.is_started: bool = False
        self._players_ready_: list[int] = []
        self._players_: dict[int, Player] = {}
        self._deck_ = DeckOfCards()
        self._turn_: int = 0
        self._current_player_: int = -1
        self._expected_reaction_: ReactionExpectation | None = None
        self._messages_: dict[str, Message] = {}

    def _create_message_(self, text: str, sender: str = "system"):
        return Message(
            id=str(len(self._messages_)),
            sender=sender,
            text=text,
            time_ms=time.time() * 1000.0,
        )

    def _start_game_(self) -> None:
        for player in self._players_.values():
            player.hand = self._deck_.take(rules.STARTING_NUM_OF_CARDS_IN_HAND)
            self._announcer_.announce(EventUpdate.hand_changed(player.id, player.hand))
        self._announcer_.announce(EventUpdate.game_start())
        self.is_started = True
        msg = self._create_message_("Game Started")
        self._messages_[msg["id"]] = msg
        self._announcer_.announce(EventUpdate.message(msg))
        self._next_player_()

    def _next_player_(self) -> None:
        p = self._players_.get(self._current_player_)
        pl: list[int] = list(self._players_.keys())
        if self._current_player_ in pl:
            i = pl.index(self._current_player_) + 1
            i %= len(pl)
            self._current_player_ = pl[i]
            if i == 0:
                self._turn_ += 1
        else:
            self._turn_ = 1
            self._current_player_ = random.choice(pl)
        p = self._players_[self._current_player_]
        self._expected_reaction_ = None
        self._announcer_.announce(EventUpdate.turn(p.id, p.name))

    def _play_cards_(
        self, player: int, cards: list[str], args: dict | None
    ) -> PlayResult:
        cc = len(cards)
        if cc == 1:
            # Single-Card Rules
            if cards[0] == rules.CARD_ROBAH:
                return self._play_tokhm_bedozd_(player, args)
            raise NotImplementedError()
        elif cc == 2:
            # Double-Card Rules
            raise NotImplementedError()
        elif cc == 3:
            # Triple-Card Rules
            raise NotImplementedError()
        elif cc == 4:
            # Quad-Card Rules
            raise NotImplementedError()
        else:
            return PlayResult.err("Invalid cards")

    def _play_reaction_(
        self, reaction: ReactionExpectation, args: dict | None
    ) -> PlayResult:
        reacting_player = self._players_.get(reaction.reacting_player)
        if reacting_player is None:
            return PlayResult.err(
                f"Reacting player ({reaction.reacting_player}) not found"
            )
        acting_player = self._players_.get(reaction.acting_player)
        if acting_player is None:
            return PlayResult.err(f"Acting player ({reaction.acting_player}) not found")
        # Find the cause and execute reaction
        if reaction.cause == REACTION_CAUSE_FOX_DEFENSE:
            return self._play_reaction__fox_defense_(
                reacting_player, acting_player, args
            )
        else:
            raise Exception(f"Unexpected reaction cause '{reaction.cause}'")

    def _play_reaction__fox_defense_(
        self, reacting_player: Player, acting_player: Player, args: dict | None
    ) -> PlayResult:
        if args is None or "defend" not in args:
            return PlayResult.err("Missing required reaction argument 'defend'")
        if bool(args["defend"]):
            num_roosters: int = reacting_player.hand.count(rules.CARD_KHOROS)
            if num_roosters < 2:
                return PlayResult.err(
                    f"Not enough roosters; Expected >= 2, Found = {num_roosters}"
                )
            self._deck_.put([rules.CARD_KHOROS] * 2)
            new_cards = self._deck_.take(2)
            i = reacting_player.hand.index(rules.CARD_KHOROS)
            reacting_player.hand[i] = new_cards[0]
            i = reacting_player.hand.index(rules.CARD_KHOROS)
            reacting_player.hand[i] = new_cards[1]
            self._announcer_.announce(
                EventUpdate.hand_changed(reacting_player.id, reacting_player.hand)
            )
            return PlayResult(next_player=True, error=None)
        else:
            return self._play_tokhm_bedozd__execute_(
                attacker=acting_player, defender=reacting_player
            )

    def _play_tokhm_bedozd_(self, player_id: int, args: dict | None) -> PlayResult:
        if args is None or "target" not in args:
            return PlayResult(next_player=False, error="Undefined target")
        player = self._players_.get(player_id)
        if player is None:
            return PlayResult(next_player=False, error="Player not found")
        try:
            target = self._players_.get(int(args["target"]))
        except Exception as x:
            print(x)
            target = None
        if target is None:
            return PlayResult(
                next_player=False, error="Target not found / Invalid target Id"
            )
        if target.num_of_tokhms < 1:
            return PlayResult(next_player=False, error="Target has no tokhms to steal")
        if target.hand.count(rules.CARD_KHOROS) >= 2:
            self._expected_reaction_ = ReactionExpectation.make_fox_defense(
                reacting_player=target.id, acting_player=player_id
            )
            self._announcer_.announce(
                EventUpdate.reaction_expectation(
                    self._expected_reaction_.cause,
                    self._expected_reaction_.acting_player,
                    self._expected_reaction_.reacting_player,
                )
            )
            return PlayResult(next_player=False, error=None)
        else:
            return self._play_tokhm_bedozd__execute_(player, target)

    def _play_tokhm_bedozd__execute_(self, attacker: Player, defender: Player):
        defender.num_of_tokhms -= 1
        self._announcer_.announce(
            EventUpdate.scores_changed(
                player=defender.id,
                eggs=defender.num_of_tokhms,
                chickens=defender.num_of_jojos,
            )
        )
        attacker.num_of_tokhms += 1
        self._announcer_.announce(
            EventUpdate.scores_changed(
                player=attacker.id,
                eggs=attacker.num_of_tokhms,
                chickens=attacker.num_of_jojos,
            )
        )
        return PlayResult(next_player=True, error=None)

    def get_info(self) -> GameInfo:
        return GameInfo(
            id=self.id,
            name=self.name,
            status="Playing" if self.is_started else "Waiting",
            players=len(self._players_),
            capacity=4,
        )

    def get_state(self, player: int | None = None) -> GameState:
        return GameState(
            id=self.id,
            name=self.name,
            status="Playing" if self.is_started else "Waiting",
            players=[
                p.get_private_state(is_ready=p in self._players_ready_)
                if p.id == player
                else p.get_state(is_ready=p in self._players_ready_)
                for p in self._players_.values()
            ],
            chat=list(self._messages_.values()),
        )

    def on_player_listen(self, player: int) -> queue.Queue[EventUpdate]:
        ret = self._announcer_.add_listener(player)
        return ret

    def on_player_join(self, player: int) -> str | None:
        if self.is_started:
            return "The game has already started"
        if player in self._players_:
            return "Player already joined"
        self._players_[player] = Player(id=player, name=f"Player {player}")
        return None

    def on_player_ready(self, player: int) -> str | None:
        if self.is_started:
            return "The game has already started"
        p = self._players_.get(player)
        if p is None:
            return "Player not found"
        if p.id not in self._players_ready_:
            self._players_ready_.append(p.id)
            msg = self._create_message_(f"{p.name} is ready")
            self._messages_[msg["id"]] = msg
            self._announcer_.announce(EventUpdate.message(msg))
        if len(self._players_ready_) == len(self._players_):
            self._start_game_()
        return None

    def on_player_leave(self, player: int) -> str | None:
        p = self._players_.get(player)
        if p is None:
            return "Player not found"
        self._players_.pop(player)
        return None

    def on_player_draw_cards(
        self, player: int, card_indices: set[int], args: dict | None
    ) -> str | None:
        if not self.is_started:
            return "The game has not started yet"
        if player != self._current_player_:
            return "It is not your turn"
        if self._expected_reaction_ is not None:
            return "Cannot draw cards while waiting for a reaction"
        p = self._players_.get(player)
        if p is None:
            return "Player not found"
        for i in card_indices:
            if i < 0 or i >= len(p.hand):
                return f"Invalid card index '{i}'"
        cards = [p.hand[i] for i in card_indices]
        result = self._play_cards_(player, cards, args)
        if result.error is None:
            self._announcer_.announce(EventUpdate.cards_drawn(p.id, cards, args))
            self._deck_.put(cards)
            new_cards = self._deck_.take(len(cards))
            for i in card_indices:
                p.hand[i] = new_cards[i]
            self._announcer_.announce(EventUpdate.hand_changed(p.id, p.hand))
            if result.next_player:
                self._next_player_()
        return result.error

    def on_player_react(self, player: int, cause: str, args: dict) -> str | None:
        if not self.is_started:
            return "The game has not started yet"
        if self._expected_reaction_ is None:
            return "No reaction expected"
        if player != self._expected_reaction_.reacting_player:
            return "You are not expected to react"
        if self._expected_reaction_.cause != cause:
            return f"Invalid reaction, expected '{self._expected_reaction_.cause}', found '{cause}'"
        ret = self._play_reaction_(self._expected_reaction_, args)
        if ret.error is None:
            self._expected_reaction_ = None
            if ret.next_player:
                self._next_player_()
        return ret.error
