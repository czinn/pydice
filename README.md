# pydice
An implementation of the game Liar's Dice in Python using an almost-P2P protocol.

pydice uses a concept called Mental Poker. It allows a game with hidden information and randomness to be played without a central authority (e.g. a server) keeping track of information.

# The Commitment Schema

The commitment schema (or protocol) goes something like this (with `Hash(x)` being some hash function):

1. Each player picks a secret number `K` and computes `C = Hash(K)` and `D = Hash(C)`
2. Each player reveals `D` to all other players.
3. Each player reveals `C` to all other players, who can verify that `D = Hash(C)`. This ensures that players didn't change their `C` in response to other players revealing their values.
4. All revealed `C`s are added together in some commutative way to get `S`.
5. Each player calculates `Hash(C + S)` (all players can do this for all other players) to obtain the turn ordering for the round.
6. Each player privately calculates `R = Hash(K + S)`. `R` is the player's private value; in Liar's Dice, it's used to generate their set of dice.
7. After the round, each player reveals `K` and `R`, and other players can verify that this matches their commitment `C`.
