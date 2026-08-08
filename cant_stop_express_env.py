from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import random
from typing import Iterable, Optional

PAIR_POINTS = {2: 100, 3: 70, 4: 60, 5: 50, 6: 40, 7: 30, 8: 40, 9: 50, 10: 60, 11: 70, 12: 100}


@dataclass(frozen=True, order=True)
class Action:
    pair_sums: tuple[int, int]
    fifth_value: Optional[int]
    fifth_index: int


@dataclass(frozen=True)
class GameState:
    pair_counts: tuple[int, ...]  # sums 2..12
    fifth_counts: tuple[tuple[int, int], ...]
    turn: int
    dice: tuple[int, ...]
    legal_actions: tuple[Action, ...]
    score: int
    terminated: bool


def score_pair_count(pair_sum: int, count: int) -> int:
    if not 2 <= pair_sum <= 12:
        raise ValueError("pair_sum must be in 2..12")
    if not 0 <= count <= 10:
        raise ValueError("pair count must be in 0..10")
    if count == 0 or count == 5:
        return 0
    if 1 <= count <= 4:
        return -200
    return (count - 5) * PAIR_POINTS[pair_sum]


def winners(scores: Iterable[int]) -> tuple[int, ...]:
    values = tuple(scores)
    if not values:
        raise ValueError("scores must not be empty")
    best = max(values)
    return tuple(i for i, score in enumerate(values) if score == best)


def total_score(pair_counts: Iterable[int]) -> int:
    counts = tuple(pair_counts)
    if len(counts) != 11:
        raise ValueError("pair_counts must have 11 entries for sums 2..12")
    return sum(score_pair_count(pair_sum, count) for pair_sum, count in zip(range(2, 13), counts))


def _pairings(indices: tuple[int, int, int, int]):
    a, b, c, d = indices
    return (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c)))


def enumerate_actions(dice: Iterable[int], fifth_values: Iterable[int] = ()) -> tuple[Action, ...]:
    dice = tuple(int(value) for value in dice)
    if len(dice) != 5 or any(value < 1 or value > 6 for value in dice):
        raise ValueError("dice must contain exactly five values in 1..6")
    chosen = tuple(dict.fromkeys(int(value) for value in fifth_values))
    if len(chosen) > 3 or any(value < 1 or value > 6 for value in chosen):
        raise ValueError("fifth_values must contain at most three unique values in 1..6")

    mark_fifth = True
    if len(chosen) < 3:
        allowed_indices = [i for i, value in enumerate(dice) if value not in chosen]
    else:
        matches = [i for i, value in enumerate(dice) if value in chosen]
        if matches:
            allowed_indices = matches
        else:
            # Free throw: the unused die is ignored and no 5th-die track is marked.
            allowed_indices = list(range(5))
            mark_fifth = False

    by_value_key: dict[tuple[tuple[int, int], Optional[int]], Action] = {}
    for fifth_idx in allowed_indices:
        remaining = tuple(i for i in range(5) if i != fifth_idx)
        for pairing in _pairings(remaining):
            sums = tuple(
                sorted(
                    (
                        dice[pairing[0][0]] + dice[pairing[0][1]],
                        dice[pairing[1][0]] + dice[pairing[1][1]],
                    )
                )
            )
            fifth_value = dice[fifth_idx] if mark_fifth else None
            key = (sums, fifth_value)
            candidate = Action(sums, fifth_value, fifth_idx)
            prior = by_value_key.get(key)
            if prior is None or candidate.fifth_index < prior.fifth_index:
                by_value_key[key] = candidate
    return tuple(
        sorted(
            by_value_key.values(),
            key=lambda action: (
                action.pair_sums,
                -1 if action.fifth_value is None else action.fifth_value,
                action.fifth_index,
            ),
        )
    )


class CantStopExpressEnv:
    def __init__(self, seed: int | None = None, max_turns: int = 100):
        self._rng = random.Random(seed)
        self.max_turns = max_turns
        self._pair_counts = [0] * 11
        self._fifth_counts: dict[int, int] = {}
        self.turn = 0
        self.dice = (1, 1, 1, 1, 1)
        self.terminated = False
        self.truncated = False

    def _roll(self) -> tuple[int, ...]:
        return tuple(self._rng.randint(1, 6) for _ in range(5))

    def reset(self, *, seed: int | None = None, dice: Iterable[int] | None = None) -> GameState:
        if seed is not None:
            self._rng.seed(seed)
        self._pair_counts = [0] * 11
        self._fifth_counts = {}
        self.turn = 1
        self.terminated = False
        self.truncated = False
        self.dice = tuple(dice) if dice is not None else self._roll()
        self._validate_dice(self.dice)
        return self.state()

    @staticmethod
    def _validate_dice(dice):
        if len(dice) != 5 or any(not isinstance(value, int) or value < 1 or value > 6 for value in dice):
            raise ValueError("dice must contain exactly five integer values in 1..6")

    def legal_actions(self) -> tuple[Action, ...]:
        if self.terminated or self.truncated:
            return ()
        return enumerate_actions(self.dice, self._fifth_counts.keys())

    def state(self) -> GameState:
        return GameState(
            tuple(self._pair_counts),
            tuple(sorted(self._fifth_counts.items())),
            self.turn,
            tuple(self.dice),
            self.legal_actions(),
            total_score(self._pair_counts),
            self.terminated,
        )

    def step(self, action: Action, *, next_dice: Iterable[int] | None = None):
        if self.terminated or self.truncated:
            raise RuntimeError("cannot step a finished episode")
        legal = self.legal_actions()
        if action not in legal:
            raise ValueError("action is not legal for the current dice/state")
        previous_score = total_score(self._pair_counts)
        for pair_sum in action.pair_sums:
            idx = pair_sum - 2
            if self._pair_counts[idx] < 10:
                self._pair_counts[idx] += 1
        if action.fifth_value is not None:
            self._fifth_counts[action.fifth_value] = self._fifth_counts.get(action.fifth_value, 0) + 1
            self.terminated = self._fifth_counts[action.fifth_value] >= 8

        reward = total_score(self._pair_counts) - previous_score
        info = {"rule_reward": reward, "score": total_score(self._pair_counts)}
        if not self.terminated:
            self.turn += 1
            if self.turn > self.max_turns:
                self.truncated = True
            else:
                self.dice = tuple(next_dice) if next_dice is not None else self._roll()
                self._validate_dice(self.dice)
                if not enumerate_actions(self.dice, self._fifth_counts.keys()):
                    self.truncated = True
                    info["truncation_reason"] = "no_legal_fifth_die"
        next_state = self.state()
        return next_state, reward, self.terminated, self.truncated, info

    def shaped_reward(self, rule_reward: float, *, shaping: float = 0.0) -> float:
        return float(rule_reward) + float(shaping)
