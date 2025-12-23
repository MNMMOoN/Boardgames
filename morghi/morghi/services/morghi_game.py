import time
import queue
import random
from morghi.core import actions, Cards, Rules, GameState, GameInfo, Message
from .event_update import EventUpdate
from .event_announcer import EventAnnouncer
from .morghi_deck import Deck
from .morghi_player import Player


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
        self._deck_ = Deck(Cards.all())
        self._turn_: int = 0
        self._current_player_: int = -1
        self._expected_reaction_: actions.Action | None = None
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
            player.hand = self._deck_.take(Rules.NUM_CARDS_IN_HAND)
            self._announcer_.announce(
                update=EventUpdate.hand_changed(
                    player_id=player.id,
                    hand=player.hand,
                ),
                targets=[player.id],
            )
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

    def get_info(self) -> GameInfo:
        return GameInfo(
            id=self.id,
            name=self.name,
            status="Playing" if self.is_started else "Waiting",
            players=list(self._players_.keys()),
            capacity=Rules.MAX_PLAYERS_COUNT,
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
        if player in self._players_:
            return None
        if self.is_started:
            return "The game has already started"
        self._players_[player] = Player(id=player, name=f"Player {player}")
        for p_id in self._players_.keys():
            self._announcer_.announce(EventUpdate.state(self.get_state(player=p_id)))
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
        for p_id in self._players_.keys():
            self._announcer_.announce(EventUpdate.state(self.get_state(player=p_id)))
        return None

    def _validate_action_(self, player: int, action_name: str) -> str | Player:
        if not self.is_started:
            return "The game has not started yet"
        if player != self._current_player_:
            return "It is not your turn"
        p = self._players_.get(player)
        if p is None:
            return f"Player '{player}' not found"
        if (
            self._expected_reaction_ is not None
            and self._expected_reaction_.name != action_name
        ):
            return f"Expected reaction '{self._expected_reaction_.name}', Found '{action_name}'"
        return p

    def on_action(self, player: int, action: actions.Action) -> str | None:
        p = self._validate_action_(player, action.name)
        if isinstance(p, str):
            # It's an error, return it
            return p
        if isinstance(action, actions.SkipTurn):
            return self._exec_skip_turn_(p, action)
        elif isinstance(action, actions.LayEgg):
            return self._exec_lay_egg_(p, action)
        elif isinstance(action, actions.StealEgg):
            return self._exec_steal_egg_(p, action)
        elif isinstance(action, actions.DefendEgg):
            return self._exec_defend_egg_(p, action)
        elif isinstance(action, actions.BreakEgg):
            return self._exec_break_egg_(p, action)
        else:
            return f"Unknown action '{action.name}'"

    def _exec_skip_turn_(self, player: Player, action: actions.SkipTurn) -> str | None:
        if len(action.card_indices) != 1:
            return "Invalid number of cards"
        ci = action.card_indices.pop()
        if ci < 0 or ci >= len(player.hand):
            return f"Invalid card index '{ci}'"
        card = player.hand.pop(ci)
        self._deck_.put([card])
        player.hand.extend(self._deck_.take(1))
        self._announcer_.announce(
            update=EventUpdate.hand_changed(
                player_id=player.id,
                hand=player.hand,
            ),
            targets=[player.id],
        )
        self._announcer_.announce(
            EventUpdate.message(
                message=self._create_message_(
                    text=f"{player.name} dropped a {card}",
                )
            )
        )
        self._next_player_()
        return None

    def _exec_lay_egg_(self, player: Player, action: actions.LayEgg) -> str | None:
        cards = player.take_cards(
            indices=action.card_indices,
            names=Rules.CARDS_TO_LAY_EGG,
        )
        if cards is None:
            return "Invalid cards"
        self._deck_.put(cards)
        player.hand.extend(self._deck_.take(len(cards)))
        player.num_of_tokhms += 1
        self._announcer_.announce(
            update=EventUpdate.scores_changed(
                player=player.id,
                eggs=player.num_of_tokhms,
                chickens=player.num_of_jojos,
            )
        )
        self._announcer_.announce(
            update=EventUpdate.hand_changed(
                player_id=player.id,
                hand=player.hand,
            ),
            targets=[player.id],
        )
        self._announcer_.announce(
            update=EventUpdate.message(
                message=self._create_message_(
                    text=f"{player.name} laid an egg",
                )
            )
        )
        self._next_player_()
        return None

    def _exec_steal_egg_(self, player: Player, action: actions.StealEgg) -> str | None:
        cards = player.take_cards(action.card_indices, Rules.CARDS_TO_STEAL_EGG)
        if cards is None:
            return "Invalid card"
        self._deck_.put(cards)
        player.hand.extend(self._deck_.take(len(cards)))
        self._announcer_.announce(
            update=EventUpdate.hand_changed(
                player_id=player.id,
                hand=player.hand,
            ),
            targets=[player.id],
        )
        self._expected_reaction_ = actions.DefendEgg(
            defender=action.target,
            does_defend=False,
            card_indices=set(),
        )
        return None

    def _exec_defend_egg_(
        self, player: Player, action: actions.DefendEgg
    ) -> str | None:
        if not isinstance(self._expected_reaction_, actions.DefendEgg):
            return "Invalid action"
        if self._expected_reaction_.defender != player.id:
            return "Invalid action; You are not the defender"
        cards = player.take_cards(action.card_indices, Rules.CARDS_TO_DEFEND_EGG)
        if cards is None:
            return "Invalid cards"
        self._deck_.put(cards)
        player.hand.extend(self._deck_.take(len(cards)))
        self._expected_reaction_ = None
        self._announcer_.announce(
            update=EventUpdate.hand_changed(
                player_id=player.id,
                hand=player.hand,
            ),
            targets=[player.id],
        )
        self._announcer_.announce(
            update=EventUpdate.message(
                message=self._create_message_(
                    text=f"{player.name} defended the egg",
                )
            )
        )
        self._next_player_()
        return None

    def _exec_break_egg_(self, player: Player, action: actions.BreakEgg) -> str | None:
        target = self._players_.get(action.target)
        if target is None:
            return f"Player '{action.target}' not found"
        count = min(target.num_of_tokhms, Rules.MAX_EGGS_TO_BREAK)
        if count == 0:
            return "No eggs to break"
        cards = player.take_cards(action.card_indices, Rules.CARDS_TO_BREAK_EGG)
        if cards is None:
            return "Invalid cards"
        self._deck_.put(cards)
        player.hand.extend(self._deck_.take(len(cards)))
        target.num_of_tokhms -= count
        self._announcer_.announce(
            update=EventUpdate.scores_changed(
                player=target.id,
                eggs=target.num_of_tokhms,
                chickens=target.num_of_jojos,
            )
        )
        self._announcer_.announce(
            update=EventUpdate.hand_changed(
                player_id=player.id,
                hand=player.hand,
            ),
            targets=[player.id],
        )
        self._announcer_.announce(
            update=EventUpdate.message(
                message=self._create_message_(
                    text=f"{player.name} broke the {count} egg(s) from {target.name}",
                )
            )
        )
        self._next_player_()
        return None
