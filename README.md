# ml-pokerbot

This project provides a simple heads-up Texas Hold'em implementation in Python. The
logic uses a proper 52-card deck and includes hand evaluation for determining the
winner. A command-line interface plays out a single hand with basic betting.

## Running a Game

Run the following command:

```bash
python play_heads_up.py
```

The script will walk through betting on the pre-flop, flop, turn and river rounds.
Each hand begins with automatic posting of the small and big blinds so the pot is
seeded before any action. Blinds rotate each hand.
When prompted, reply with `y` or `n` followed by the amount (e.g. `y 25`).
Facing a bet you may:

1. Enter `n` or an amount smaller than the required call to fold.
2. Enter `y` or `y` with the exact call amount to call. If no amount is given, the
   required call will automatically be wagered for you.
3. Enter `y` with a higher amount to raise, after which betting continues until a call or fold.

A player that cannot fully cover the required call will automatically go all-in for
their remaining chips. Further raises are not permitted in that case since side pots
are not implemented.

If a non-numeric amount is entered it is treated as zero which effectively folds the hand.

Stacks and the pot update after each action and the winner of the pot is announced at the end of the hand. This implementation can serve as a starting point for machine-learning experiments or further game logic.
Each showdown also prints a numeric score from **0.00** to **0.99** indicating the relative strength of every hand.
