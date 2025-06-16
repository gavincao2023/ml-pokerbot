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
When prompted, reply with `y` or `n` followed by the amount (e.g. `y 25`).
Facing a bet you may:

1. Enter `n` or an amount smaller than the required call to fold.
2. Enter `y` with the exact call amount to call.
3. Enter `y` with a higher amount to raise, after which betting continues until a call or fold.

Stacks and the pot update after each action and the winner of the pot is announced at the end of the hand. This implementation can serve as a starting point for machine-learning experiments or further game logic.
