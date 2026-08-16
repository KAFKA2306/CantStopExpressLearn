import contextlib
import importlib.util
import io
import pathlib
import sys
import unittest

from cant_stop_express_env import Action, CantStopExpressEnv, enumerate_actions, total_score, winners

ROOT = pathlib.Path(__file__).resolve().parents[1]


class EnvTests(unittest.TestCase):
    def test_actions_are_deterministic_and_pair_order_deduplicated(self):
        actions = enumerate_actions([1, 2, 3, 4, 5])
        self.assertEqual(actions, enumerate_actions([1, 2, 3, 4, 5]))
        keys = [(action.pair_sums, action.fifth_value) for action in actions]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn(((3, 7), 5), keys)

    def test_duplicate_die_values_normalize_equivalent_actions(self):
        actions = enumerate_actions([1, 1, 2, 2, 3])
        keys = [(action.pair_sums, action.fifth_value) for action in actions]
        self.assertEqual(len(keys), len(set(keys)))

    def test_step_updates_pairs_fifth_turn(self):
        env = CantStopExpressEnv(seed=1)
        state = env.reset(dice=[1, 2, 3, 4, 5])
        action = next(
            candidate
            for candidate in state.legal_actions
            if candidate.pair_sums == (3, 7) and candidate.fifth_value == 5
        )
        next_state, reward, terminated, truncated, info = env.step(
            action, next_dice=[1, 2, 3, 4, 6]
        )
        self.assertEqual(next_state.pair_counts[1], 1)  # sum 3
        self.assertEqual(next_state.pair_counts[5], 1)  # sum 7
        self.assertEqual(next_state.fifth_counts, ((5, 1),))
        self.assertEqual(next_state.turn, 2)
        self.assertEqual(reward, -400)
        self.assertFalse(terminated)
        self.assertFalse(truncated)
        self.assertEqual(info["score"], total_score(next_state.pair_counts))

    def test_invalid_and_post_terminal_fail_closed(self):
        env = CantStopExpressEnv()
        state = env.reset(dice=[1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            env.step(Action((2, 2), 6, 0))

        for index in range(8):
            if index:
                env.dice = (1, 2, 3, 4, 5)
            matching = [action for action in env.legal_actions() if action.fifth_value == 1]
            action = matching[0] if matching else env.legal_actions()[0]
            env.step(action, next_dice=[1, 2, 3, 4, 5])
            if env.terminated:
                break
        while not env.terminated:
            env.dice = (1, 2, 3, 4, 5)
            action = next(action for action in env.legal_actions() if action.fifth_value == 1)
            env.step(action, next_dice=[1, 2, 3, 4, 5])
        with self.assertRaises(RuntimeError):
            env.step(action)

    def test_seed_reproduces_trajectory(self):
        def trajectory(seed):
            env = CantStopExpressEnv(seed=seed)
            state = env.reset()
            result = []
            for _ in range(12):
                result.append(state.dice)
                action = state.legal_actions[0]
                state, _, done, truncated, _ = env.step(action)
                if done or truncated:
                    break
            return result

        self.assertEqual(trajectory(42), trajectory(42))

    def test_ties_share_victory(self):
        self.assertEqual(winners([100, 50, 100]), (0, 2))

    def test_scoring_boundaries(self):
        counts = [0] * 11
        counts[0] = 4
        counts[6] = 5
        counts[8] = 6
        self.assertEqual(total_score(counts), -140)


class QLearningTests(unittest.TestCase):
    def _load(self):
        spec = importlib.util.spec_from_file_location("qlearning", ROOT / "Q-learning_algorithm.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_import_is_silent(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self._load()
        self.assertEqual(buffer.getvalue(), "")

    def test_terminal_transition_does_not_bootstrap(self):
        module = self._load()
        agent = module.QLearningAgent(
            module.TrainingConfig(alpha=1.0, gamma=0.9, epsilon=0, seed=1)
        )
        env = CantStopExpressEnv()
        state = env.reset(dice=[1, 2, 3, 4, 5])
        action = state.legal_actions[0]
        next_state, _, _, _, _ = env.step(action, next_dice=[1, 2, 3, 4, 6])
        for candidate in next_state.legal_actions:
            agent.q[(module.state_key(next_state), candidate)] = 100.0
        agent.update(state, action, 7.0, next_state, True)
        self.assertEqual(agent.value(state, action), 7.0)

    def test_policy_comparison_uses_same_seed_set(self):
        module = self._load()
        agent = module.QLearningAgent(module.TrainingConfig(epsilon=0, seed=1))
        results = module.compare_policies([1, 2], agent)
        self.assertEqual(set(results), {"random", "fixed", "q"})
        self.assertTrue(all(len(values) == 2 for values in results.values()))


if __name__ == "__main__":
    unittest.main()
