# ml-pokerbot

This project provides a simple heads-up Texas Hold'em implementation in Python. The
logic uses a proper 52-card deck and includes hand evaluation for determining the
winner. A command-line interface plays out a single hand with basic betting.

## Running a Game

Run the following command:

```bash
python play_heads_up.py
```

The script will walk through betting on the pre-flop, flop, turn and river rounds,
pot are updated after each action and the winner of the pot is announced at the
end of the hand. This implementation can serve as a starting point for
machine-learning experiments or further game logic.
Input: (y/n) amount