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
    def __init__(self, player1: str = "Player 1", player2: str = "Player 2", starting_stack: int = 100):
        self.players = [Player(player1, starting_stack), Player(player2, starting_stack)]
        self.deck: Deck = Deck()
        self.board: List[Card] = []
        self.pot: int = 0

    def reset(self):
        for p in self.players:
            p.reset()
        self.deck = Deck()
        self.board = []
        self.pot = 0
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
            result = evaluate_best(hand)
            evaluations.append((p, result))
        evaluations.sort(key=lambda x: x[1][1], reverse=True)
        best_rank = evaluations[0][1][1]
        winners = [p for p, res in evaluations if res[1] == best_rank]
        return winners, evaluations

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

    def betting_round(self, stage: str, input_fn=input) -> bool:
        """Return True if the hand ended due to a fold."""
        print(f"\n== {stage} Betting ==")

        bets = [0, 0]
        current_bet = 0
        to_act = 0
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
                if action == 'y' and amount >= to_call:
                    call_amt = player.bet(to_call)
                    bets[to_act] += call_amt
                    self.pot += call_amt
                    print(f"{player.name} calls {call_amt}. Stack: {player.stack}")
                    if amount > to_call:
                        # Raise
                        raise_amt = amount - to_call
                        extra = player.bet(raise_amt)
                        bets[to_act] += extra
                        current_bet = bets[to_act]
                        self.pot += extra
                        print(f"{player.name} raises {extra}. Stack: {player.stack}")
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
        print("\n-- Hole Cards --")
        for p in self.players:
            print(f"{p.name} ({p.stack}): " + ' '.join(str(c) for c in p.cards))

        if self.betting_round('Pre-Flop', input_fn):
            return

        self.deal_flop()
        print("\n-- Flop --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('Flop', input_fn):
            return

        self.deal_turn()
        print("\n-- Turn --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('Turn', input_fn):
            return

        self.deal_river()
        print("\n-- River --")
        print(' '.join(str(c) for c in self.board))
        if self.betting_round('River', input_fn):
            return

        winners, evals = self.showdown()
        print("\n-- Showdown --")
        for p, res in evals:
            hand_name, rank = res
            print(f"{p.name}: {hand_name} ({' '.join(str(c) for c in p.cards)})")
        if len(winners) == 1:
            winner = winners[0]
            winner.stack += self.pot
            print(f"\nWinner: {winner.name} wins {self.pot}")
        else:
            split = self.pot // len(winners)
            for w in winners:
                w.stack += split
            print("\nIt's a tie between: " + ', '.join(p.name for p in winners))
