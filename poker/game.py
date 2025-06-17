from typing import List

from .cards import Deck, Card
from .eval import evaluate_best


class Player:
    def __init__(self, name: str, stack: int = 100):
        self.name = name
        self.cards: List[Card] = []
        self.stack = stack

    def bet(self, amount: int) -> int:
        if amount > self.stack:
            amount = self.stack
        self.stack -= amount
        return amount

    def reset(self):
        self.cards = []


class HeadsUpGame:
    def __init__(self, player1: str = "Player 1", player2: str = "Player 2",
                 starting_stack: int = 100, small_blind: int = 5, big_blind: int = 10):
        self.players = [Player(player1, starting_stack), Player(player2, starting_stack)]
        self.deck: Deck = Deck()
        self.board: List[Card] = []
        self.pot: int = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.button = 0  # index of dealer; small blind pre-flop

    def reset(self):
        """Prepare for a new hand."""
        for p in self.players:
            p.reset()
        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.button = 1 - self.button  # rotate dealer
        for p in self.players:
            p.cards.extend(self.deck.draw(2))

    def deal_flop(self):
        self.board.extend(self.deck.draw(3))

    def deal_turn(self):
        self.board.append(self.deck.draw(1))

    def deal_river(self):
        self.board.append(self.deck.draw(1))

    def showdown(self):
        evaluations = []
        for p in self.players:
            hand = p.cards + self.board
            name, rank, score = evaluate_best(hand)
            evaluations.append((p, name, rank, score))
        evaluations.sort(key=lambda x: x[2], reverse=True)
        best_rank = evaluations[0][2]
        winners = [p for p, _, r, _ in evaluations if r == best_rank]
        return winners, evaluations

    def post_blinds(self):
        """Collect blinds and set up initial pot."""
        sb_player = self.players[self.button]
        bb_player = self.players[1 - self.button]
        sb = sb_player.bet(self.small_blind)
        bb = bb_player.bet(self.big_blind)
        self.pot = sb + bb
        print(
            f"{sb_player.name} posts small blind {sb}. Stack: {sb_player.stack}"
        )
        print(
            f"{bb_player.name} posts big blind {bb}. Stack: {bb_player.stack}"
        )

    # --- Betting logic ---
    def _parse_action(self, s: str):
        """Parse a player input string.

        Parameters
        ----------
        s : str
            Raw input from the user such as ``"y 25"``.

        Returns
        -------
        tuple[str, int]
            The action character (``"y"`` or ``"n"``) and the numeric amount. If
            parsing fails, the amount defaults to 0 so the caller will fold.
        """
        parts = s.strip().lower().split()
        if not parts:
            return 'n', 0
        action = parts[0]
        try:
            amount = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            amount = 0
        return action, amount

    def betting_round(self, stage: str, first_to_act: int, input_fn=input) -> bool:
        """Return True if the hand ended due to a fold."""
        print(f"\n== {stage} Betting ==")

        bets = [0, 0]
        current_bet = 0
        to_act = first_to_act
        checked = [False, False]

        while True:
            player = self.players[to_act]
            to_call = current_bet - bets[to_act]

            if to_call <= 0:
                # Player can check or bet
                response = input_fn(f"{player.name} bet? (y/n amount) ")
                action, amount = self._parse_action(response)
                if action == 'y' and amount > 0:
                    bet_amt = player.bet(amount)
                    bets[to_act] += bet_amt
                    current_bet = bets[to_act]
                    self.pot += bet_amt
                    checked[to_act] = False
                    print(f"{player.name} bets {bet_amt}. Stack: {player.stack}")
                    to_act = 1 - to_act
                else:
                    checked[to_act] = True
                    print(f"{player.name} checks.")
                    if checked[0] and checked[1]:
                        break
                    to_act = 1 - to_act
            else:
                # Player must decide to call, raise, or fold
                response = input_fn(f"{player.name} call {to_call}? (y/n amount) ")
                action, amount = self._parse_action(response)
                if action == 'y':
                    if amount < to_call:
                        amount = to_call
                    call_amt = player.bet(to_call)
                    bets[to_act] += call_amt
                    self.pot += call_amt
                    if call_amt < to_call:
                        print(
                            f"{player.name} calls all-in for {call_amt}. Stack: {player.stack}"
                        )
                        break
                    else:
                        print(
                            f"{player.name} calls {call_amt}. Stack: {player.stack}"
                        )
                    if amount > to_call and player.stack > 0:
                        # Raise only if player still has chips
                        raise_amt = amount - to_call
                        if raise_amt > player.stack:
                            raise_amt = player.stack
                        extra = player.bet(raise_amt)
                        bets[to_act] += extra
                        current_bet = bets[to_act]
                        self.pot += extra
                        print(
                            f"{player.name} raises {extra}. Stack: {player.stack}"
                        )
                        checked[0] = checked[1] = False
                        to_act = 1 - to_act
                    else:
                        break
                else:
                    # Fold
                    print(f"{player.name} folds. {self.players[1 - to_act].name} wins {self.pot}")
                    self.players[1 - to_act].stack += self.pot
                    return True

        print(f"Pot is now {self.pot}")
        return False

    def play_hand(self, input_fn=input):
        self.reset()
        self.post_blinds()
        print("\n-- Hole Cards --")
        for p in self.players:
            print(f"{p.name} ({p.stack}): " + ' '.join(str(c) for c in p.cards))

        if self.betting_round('Pre-Flop', self.button, input_fn):
            return

        self.deal_flop()
        print("\n-- Flop --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('Flop', 1 - self.button, input_fn):
            return

        self.deal_turn()
        print("\n-- Turn --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('Turn', 1 - self.button, input_fn):
            return

        self.deal_river()
        print("\n-- River --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('River', 1 - self.button, input_fn):
            return

        winners, evals = self.showdown()
        print("\n-- Showdown --")
        for p, name, rank, score in evals:
            print(
                f"{p.name}: {name} ({' '.join(str(c) for c in p.cards)}) - {score:.2f}"
            )
        if len(winners) == 1:
            winner = winners[0]
            winner.stack += self.pot
            print(f"\nWinner: {winner.name} wins {self.pot}")
        else:
            split = self.pot // len(winners)
            for w in winners:
                w.stack += split
            print("\nIt's a tie between: " + ', '.join(p.name for p in winners))
