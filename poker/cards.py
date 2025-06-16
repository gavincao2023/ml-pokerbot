from dataclasses import dataclass
import random

SUITS = ['\u2660', '\u2665', '\u2666', '\u2663']  # Spades, Hearts, Diamonds, Clubs
RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # 11=J,12=Q,13=K,14=A

RANK_STR = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    def __str__(self):
        r = RANK_STR.get(self.rank, str(self.rank))
        return f"{r}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        assert len(self.cards) >= n, "Not enough cards to draw"
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn if n > 1 else drawn[0]
