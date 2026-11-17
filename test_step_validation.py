"""Regression checks for state safety when the next dice are invalid."""

import unittest

from cant_stop_express_env import CantStopExpressEnv


class StepValidationTests(unittest.TestCase):
    def test_invalid_next_dice_does_not_change_state(self):
        env = CantStopExpressEnv(seed=1)
        env.reset(dice=(1, 2, 3, 4, 5))
        before = env.state()
        with self.assertRaises(ValueError):
            env.step(before.legal_actions[0], next_dice=(0, 2, 3, 4, 5))
        self.assertEqual(env.state(), before)

    def test_valid_next_dice_advances_turn(self):
        env = CantStopExpressEnv(seed=1)
        env.reset(dice=(1, 2, 3, 4, 5))
        before = env.state()
        after, _, _, _, _ = env.step(before.legal_actions[0], next_dice=(2, 2, 3, 3, 4))
        self.assertEqual(after.turn, before.turn + 1)
        self.assertEqual(after.dice, (2, 2, 3, 3, 4))


if __name__ == "__main__":
    unittest.main()
