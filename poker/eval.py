from collections import Counter
from itertools import combinations
from typing import List, Tuple

from .cards import Card

HAND_RANKS = [
    "High Card",
    "One Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
]

# Category index in HAND_RANKS list is used for comparison


def _is_straight(ranks: List[int]) -> Tuple[bool, int]:
    """Return (is_straight, high_card). ranks should be sorted ascending."""
    if ranks == [2, 3, 4, 5, 14]:
        return True, 5  # Wheel straight (A-2-3-4-5)
    for i in range(4):
        if ranks[i] + 1 != ranks[i + 1]:
            return False, 0
    return True, ranks[-1]


def _rank_five(cards: List[Card]) -> Tuple:
    ranks = sorted([c.rank for c in cards])
    suits = [c.suit for c in cards]
    rank_counts = Counter(ranks)
    counts = sorted(rank_counts.values(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight, high_straight = _is_straight(sorted(ranks))

    if is_straight and is_flush:
        return (8, high_straight)
    if counts[0] == 4:
        four = [r for r, c in rank_counts.items() if c == 4][0]
        kicker = max(r for r in ranks if r != four)
        return (7, four, kicker)
    if counts[0] == 3 and counts[1] == 2:
        three = [r for r, c in rank_counts.items() if c == 3][0]
        pair = [r for r, c in rank_counts.items() if c == 2][0]
        return (6, three, pair)
    if is_flush:
        return (5,) + tuple(sorted(ranks, reverse=True))
    if is_straight:
        return (4, high_straight)
    if counts[0] == 3:
        three = [r for r, c in rank_counts.items() if c == 3][0]
        kickers = sorted([r for r in ranks if r != three], reverse=True)
        return (3, three) + tuple(kickers)
    if counts[0] == 2 and counts[1] == 2:
        pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
        kicker = [r for r, c in rank_counts.items() if c == 1][0]
        return (2, pairs[0], pairs[1], kicker)
    if counts[0] == 2:
        pair = [r for r, c in rank_counts.items() if c == 2][0]
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (1, pair) + tuple(kickers)
    return (0,) + tuple(sorted(ranks, reverse=True))


def evaluate_best(seven: List[Card]) -> Tuple[int, Tuple]:
    best = (-1, ())
    for combo in combinations(seven, 5):
        rank = _rank_five(list(combo))
        if rank > best[1]:
            best = (HAND_RANKS[rank[0]], rank)
    return best
