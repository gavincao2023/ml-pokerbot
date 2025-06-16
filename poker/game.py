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
        parts = s.strip().lower().split()
        if not parts:
            return 'n', 0
        action = parts[0]
        amount = int(parts[1]) if len(parts) > 1 else 0
        return action, amount

    def betting_round(self, stage: str, input_fn=input) -> bool:
        """Return True if the hand ended due to a fold."""
        print(f"\n== {stage} Betting ==")
        bettor, caller = self.players

        response = input_fn(f"{bettor.name} bet? (y/n amount) ")
        action, amount = self._parse_action(response)
        if action == 'y' and amount > 0:
            bet = bettor.bet(amount)
            self.pot += bet
            print(f"{bettor.name} bets {bet}. Stack: {bettor.stack}")
            response = input_fn(f"{caller.name} call? (y/n amount) ")
            action, amount = self._parse_action(response)
            if action == 'y':
                call = caller.bet(amount)
                self.pot += call
                print(f"{caller.name} calls {call}. Stack: {caller.stack}")
            else:
                print(f"{caller.name} folds. {bettor.name} wins {self.pot}")
                bettor.stack += self.pot
                return True
        else:
            response = input_fn(f"{caller.name} bet? (y/n amount) ")
            action, amount = self._parse_action(response)
            if action == 'y' and amount > 0:
                bet = caller.bet(amount)
                self.pot += bet
                print(f"{caller.name} bets {bet}. Stack: {caller.stack}")
                response = input_fn(f"{bettor.name} call? (y/n amount) ")
                action, amount = self._parse_action(response)
                if action == 'y':
                    call = bettor.bet(amount)
                    self.pot += call
                    print(f"{bettor.name} calls {call}. Stack: {bettor.stack}")
                else:
                    print(f"{bettor.name} folds. {caller.name} wins {self.pot}")
                    caller.stack += self.pot
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
