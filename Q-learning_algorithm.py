from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable

from cant_stop_express_env import Action, CantStopExpressEnv, GameState


@dataclass(frozen=True)
class TrainingConfig:
    episodes: int = 1000
    alpha: float = 0.5
    gamma: float = 0.95
    epsilon: float = 0.1
    seed: int = 0


def state_key(state: GameState):
    return (state.pair_counts, state.fifth_counts, state.dice)


class QLearningAgent:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self._rng = random.Random(config.seed)
        self.q: dict[tuple[object, Action], float] = {}

    def value(self, state, action):
        return self.q.get((state_key(state), action), 0.0)

    def choose_action(self, state: GameState) -> Action:
        if not state.legal_actions:
            raise ValueError("state has no legal actions")
        if self._rng.random() < self.config.epsilon:
            return self._rng.choice(state.legal_actions)
        return max(
            state.legal_actions,
            key=lambda action: (
                self.value(state, action),
                tuple(-value for value in action.pair_sums),
                -(action.fifth_value or 0),
            ),
        )

    def update(self, state, action, reward, next_state, terminated):
        current = self.value(state, action)
        bootstrap = (
            0.0
            if terminated or not next_state.legal_actions
            else max(self.value(next_state, candidate) for candidate in next_state.legal_actions)
        )
        target = reward + self.config.gamma * bootstrap
        self.q[(state_key(state), action)] = current + self.config.alpha * (target - current)


def run_episode(
    env: CantStopExpressEnv,
    policy: Callable[[GameState], Action],
    *,
    learn: QLearningAgent | None = None,
):
    state = env.reset()
    total = 0.0
    while True:
        action = policy(state)
        next_state, reward, terminated, truncated, _ = env.step(action)
        if learn:
            learn.update(state, action, reward, next_state, terminated or truncated)
        total += reward
        state = next_state
        if terminated or truncated:
            return total


def compare_policies(seeds, q_agent: QLearningAgent):
    results = {"random": [], "fixed": [], "q": []}
    for seed in seeds:
        rng = random.Random(seed)
        env = CantStopExpressEnv(seed=seed)
        results["random"].append(run_episode(env, lambda state, rr=rng: rr.choice(state.legal_actions)))
        env = CantStopExpressEnv(seed=seed)
        results["fixed"].append(run_episode(env, lambda state: state.legal_actions[0]))
        env = CantStopExpressEnv(seed=seed)
        results["q"].append(run_episode(env, q_agent.choose_action))
    return results


def main():
    config = TrainingConfig()
    agent = QLearningAgent(config)
    for episode in range(config.episodes):
        env = CantStopExpressEnv(seed=config.seed + episode)
        run_episode(env, agent.choose_action, learn=agent)
    print(compare_policies(range(10), agent))


if __name__ == "__main__":
    main()
