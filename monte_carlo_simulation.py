import random

def roll_dice(n=5):
    """Roll n six-sided dice and return the results as a list."""
    return [random.randint(1, 6) for _ in range(n)]

def calculate_score(turns=1):
    """Simulate a game of Can't Stop Express."""
    total_score = 0
    for _ in range(turns):
        turn_score = 0
        # three unique "5th die" numbers
        unique_5th_numbers = []
        for i in range(3):
            roll = roll_dice()
            unique_5th_numbers.append(sum(roll) - min(roll))
            turn_score -= 200  # penalty for the first four times of a value
            print(f"Turn {i+1}, score: {turn_score}")
        # continue the game
        while len(unique_5th_numbers) != 0:
            roll = roll_dice()
            roll_sum = sum(roll)
            if roll_sum in unique_5th_numbers:
                unique_5th_numbers.remove(roll_sum)
            # calculate score based on the rules
            if roll_sum < 5 or roll_sum > 10:
                turn_score -= 200  # penalty for the first four times of a value
            elif roll_sum == 5:
                turn_score = 0  # no score for exactly five times of a value
            else:
                # plus points for at least six times of a value
                turn_score += (roll_sum - 5) * 40
            print(f"Turn {3 + len(unique_5th_numbers) + 1}, score: {turn_score}")
        total_score += turn_score
    return total_score

def monte_carlo_simulation(num_trials=100):
    """Estimate the expected value of a game of Can't Stop Express."""
    total_score = 0
    for _ in range(num_trials):
        total_score += calculate_score()
        print(f"End of game {_ + 1}, total score: {total_score}")
    return total_score / num_trials

expected_value = monte_carlo_simulation()
print(f"Expected value: {expected_value}")