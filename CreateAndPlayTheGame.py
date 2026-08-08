"""Small, import-safe demonstration client for CantStopExpressEnv."""

from cant_stop_express_env import CantStopExpressEnv


def play_game(seed: int = 0) -> int:
    env = CantStopExpressEnv(seed=seed)
    state = env.reset()
    while not state.terminated:
        if not state.legal_actions:
            break
        action = state.legal_actions[0]
        state, _, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break
    return state.score


def main() -> None:
    print(f"Final score: {play_game()}")


if __name__ == "__main__":
    main()
