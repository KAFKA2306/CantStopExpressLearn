import random

class CantStopExpress:
    def __init__(self):
        self.scores = [0, 0, 0]  # Scores for each "5th die" number
        self.chart = [[0] * 10 for _ in range(3)]  # Chart to keep track of filled boxes
        self.turn = 1  # Turn counter

    def roll_dice(self):
        """Roll five six-sided dice and return the results as a list."""
        return [random.randint(1, 6) for _ in range(5)]

    def play_turn(self):
        print(f"=== Turn {self.turn} ===")
        dice = self.roll_dice()
        print(f"Dice: {dice}")

        # Choose 4 dice for two pairs and 1 die as the "5th die"
        pairs = []
        fifth_die = None

        # TODO: Implement your strategy for choosing pairs and the "5th die"
        # You can access the current state of the chart and scores.

        print(f"Pairs: {pairs}")
        print(f"5th Die: {fifth_die}")

        # Update the chart and scores based on the chosen pairs and "5th die"
        # TODO: Implement the logic to update the chart and scores

        self.turn += 1

    def game_over(self):
        """Check if the game is over."""
        return any(sum(row) >= 8 for row in self.chart)

    def print_chart(self):
        """Print the current state of the chart."""
        print("Chart:")
        for row in self.chart:
            print(row)

    def print_scores(self):
        """Print the current scores."""
        print("Scores:")
        for i, score in enumerate(self.scores):
            print(f"Player {i+1}: {score}")

    def play_game(self):
        while not self.game_over():
            self.play_turn()
            self.print_chart()
            self.print_scores()

        # Calculate the final scores
        final_scores = [sum(row) for row in self.chart]
        winner = final_scores.index(max(final_scores))

        print("Game over!")
        print(f"Final Scores:")
        for i, score in enumerate(final_scores):
            print(f"Player {i+1}: {score}")

        print(f"Winner: Player {winner+1}")

# Create and play the game
game = CantStopExpress()
game.play_game()
