import numpy as np
import random

# サイコロを5つ振る関数
def roll_dice():
    return [random.randint(1, 6) for _ in range(5)]

# 5つのサイコロから2つのペアと5th Dieを選ぶ関数
def choose_pair_and_fifth_die(dice):
    pairs = []
    for i in range(len(dice)):
        for j in range(i + 1, len(dice)):
            pairs.append((dice[i], dice[j]))
    pair = random.choice(pairs)
    remaining_dice = dice.copy()
    remaining_dice.remove(pair[0])
    remaining_dice.remove(pair[1])
    fifth_die = random.choice(remaining_dice)
    return pair, fifth_die

# ゲームをシミュレーションする関数
def simulate_game():
    total_score = 0
    play_results = []
    fifth_die_counts = {}

    for turn in range(25):
        dice = roll_dice()
        pair, fifth_die = choose_pair_and_fifth_die(dice)

        pair_sum = sum(pair)
        turn_score = pair_sum

        if fifth_die not in fifth_die_counts:
            fifth_die_counts[fifth_die] = 0
        fifth_die_counts[fifth_die] += 1

        total_score += turn_score
        play_results.append((dice, pair, fifth_die, turn_score, total_score))

        if any(count >= 8 for count in fifth_die_counts.values()):
            break

    return total_score, play_results

# モンテカルロシミュレーションを実行
num_simulations = 10000
simulation_results = []

for _ in range(num_simulations):
    total_score, play_results = simulate_game()
    simulation_results.append((total_score, play_results))

# スコアの統計量を計算
total_scores = [result[0] for result in simulation_results]
mean_score = np.mean(total_scores)
std_score = np.std(total_scores)
max_score = np.max(total_scores)
min_score = np.min(total_scores)

print("Mean Score:", mean_score)
print("Standard Deviation of Score:", std_score)
print("Max Score:", max_score)
print("Min Score:", min_score)

# 高得点のプレイを表示
high_score_plays = sorted(simulation_results, reverse=True)[:5]
print("Top 5 High Score Plays:")
for i, (score, play_results) in enumerate(high_score_plays, 1):
    print("Play", i)
    print("Score:", score)
    print("Play Results:")
    for dice, pair, fifth_die, turn_score, total_score in play_results:
        print("Dice:", dice)
        print("Pair:", pair)
        print("5th Die:", fifth_die)
        print("Turn Score:", turn_score)
        print("Total Score:", total_score)
        print("---")

# 期待値の高いプレイを表示
expected_score_plays = sorted(simulation_results, reverse=True)
print("Top 5 Expected Score Plays:")
for i in range(5):
    score, play_results = expected_score_plays[i]
    print("Play", i + 1)
    print("Score:", score)
    print("Play Results:")
    for dice, pair, fifth_die, turn_score, total_score in play_results:
        print("Dice:", dice)
        print("Pair:", pair)
        print("5th Die:", fifth_die)
        print("Turn Score:", turn_score)
        print("Total Score:", total_score)
        print("---")

# 5th Dieは各ゲームで追跡し、ルールの正準実装は cant_stop_express_env.py を使用します。
