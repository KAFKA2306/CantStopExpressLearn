import random

score_table = {
    (1, 1): 200, (2, 2): 200, (3, 3): 200, (4, 4): 200, (5, 5): 200, (6, 6): 200,
    (1, 2): 0, (1, 3): 0, (1, 4): 0, (1, 5): 0, (1, 6): 0,
    (2, 3): 0, (2, 4): 0, (2, 5): 0, (2, 6): 0,
    (3, 4): 0, (3, 5): 0, (3, 6): 0,
    (4, 5): 0, (4, 6): 0,
    (5, 6): 0
}

def calculate_probabilities(dice):
    pairs = []
    for i in range(4):
        for j in range(i + 1, 5):
            pairs.append((dice[i], dice[j]))
    
    counts = {pair: pairs.count(pair) for pair in set(pairs)}
    total_count = sum(counts.values())
    
    probabilities = {pair: count / total_count for pair, count in counts.items()}
    return probabilities

def calculate_expected_scores(probabilities, fifth_die):
    expected_scores = {}
    for pair in probabilities:
        score = score_table.get(pair, -200)
        fifth_die_score = score_table.get((pair[0], fifth_die), 0) + score_table.get((pair[1], fifth_die), 0)
        expected_scores[pair] = probabilities[pair] * (score + fifth_die_score)
    
    return expected_scores

def choose_best_pair(dice, fifth_die):
    probabilities = calculate_probabilities(dice)
    expected_scores = calculate_expected_scores(probabilities, fifth_die)
    best_pair = max(expected_scores, key=expected_scores.get)
    return best_pair

def play_cant_stop_express():
    player_score = 0
    chosen_fifth_die = set()
    
    play_results = []
    
    while len(chosen_fifth_die) < 3:
        dice = [random.randint(1, 6) for _ in range(5)]
        expected_scores = get_expected_scores(dice)
        best_fifth_die = max(expected_scores, key=expected_scores.get)
        
        best_pair = choose_best_pair(dice, best_fifth_die)
        
        if best_fifth_die not in chosen_fifth_die:
            chosen_fifth_die.add(best_fifth_die)
        
        score = score_table.get(best_pair, -200)
        fifth_die_score = score_table.get((best_pair[0], best_fifth_die), 0) + score_table.get((best_pair[1], best_fifth_die), 0)
        player_score += score + fifth_die_score
        
        play_results.append((dice, best_pair, best_fifth_die, score + fifth_die_score, player_score))
    
    return player_score, play_results

def get_expected_scores(dice):
    expected_scores = {}
    for fifth_die in dice:
        probabilities = calculate_probabilities(dice)
        expected_scores[fifth_die] = sum(probabilities[pair] * (score_table.get(pair, -200) +
                                              score_table.get((pair[0], fifth_die), 0) +
                                              score_table.get((pair[1], fifth_die), 0))
                                        for pair in probabilities)
    return expected_scores

# ゲームを100回プレイして、最高スコアと最高スコアを達成したプレイ、期待値の高いプレイを表示する
best_score = 0
best_play_results = []
expected_score_plays = []

for _ in range(100):
    score, play_results = play_cant_stop_express()
    if score > best_score:
        best_score = score
        best_play_results = play_results
    
    expected_score_plays.append((score, play_results))

# 最高スコアを達成したプレイを表示
print("Best Score:", best_score)
print("Best Play Results:")
for dice, pair, fifth_die, turn_score, total_score in best_play_results:
    print("Dice:", dice)
    print("Pair:", pair)
    print("5th Die:", fifth_die)
    print("Turn Score:", turn_score)
    print("Total Score:", total_score)
    print("---")

# 期待値の高いプレイを表示
expected_score_plays.sort(reverse=True)
print("Top 5 Expected Score Plays:")
for i in range(5):
    score, play_results = expected_score_plays[i]
    print("Play", i+1)
    print("Score:", score)
    print("Play Results:")
    for dice, pair, fifth_die, turn_score, total_score in play_results:
        print("Dice:", dice)
        print("Pair:", pair)
        print("5th Die:", fifth_die)
        print("Turn Score:", turn_score)
        print("Total Score:", total_score)
        print("---")

---
#5th Dieは、各ゲームで３回出てくるはずです。
#それぞれのペアが何点だったのかすべて出力してその和が得点です。
#ルールについてご不明な点があれば、これ（https://github.com/KAFKA2306/CantStopExpressLearn/blob/main/GameRule.md）を参照してください。
#ルールに従うように、全体的にコードを修正してください。
