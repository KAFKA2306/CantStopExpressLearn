# CantStopExpressLearn

Can’t Stop Express のルール環境と学習器を分離し、ゲーム規則の正しさをテストしてから方策比較を行う実験リポジトリです。

## 正準ルール

実装は次を根拠にしています。

- Eagle-Gryphon Games（現行出版社）: https://www.eagle-gryphon.com/products/cant-stop-express
- 同ページから案内される公式 Rulebook: https://drive.google.com/drive/folders/1_zUKoVAgsMXVtQnHJLVlp4qiIyIK__A1?usp=sharing
- リポジトリ内転記: `GameRule.md`

出版社の説明どおり、各ターンは5個の6面ダイスから4個を2ペアにして2つの合計を記録し、残り1個を5th dieとして扱います。5th dieのいずれかが8回に達すると、そのプレイヤーのゲームは終了します。

## 環境

`cant_stop_express_env.py` の `CantStopExpressEnv` がゲーム規則だけを担当します。Q学習器は環境内部を書き換えません。

`GameState` は以下を機械可読に保持します。

- `pair_counts`: 2〜12の各ペア合計の記入数（各0〜10）
- `fifth_counts`: 選択済み5th dieと使用回数
- `turn`
- `dice`: 現在の5 dice
- `legal_actions`
- `score`
- `terminated`

`Action` は2つのペア合計、5th die値、代表となる5th die indexを保持します。同じ値のダイスが複数ある場合、値として同一の行動は1つへ正規化します。2ペアの左右順序も別行動にしません。

### 5th die

最初の3回は異なる5th die値を選択します。3値確定後は、そのいずれかが出目に存在すれば必ずその値を5th dieにします。3値がどれも存在しない投擲はfree throwとして、2ペアだけ記録し5th die trackは進めません。

規則上選べる5th dieが存在しない未定義ケースは推測で補完せず、episodeを`truncated`として停止します。

## 得点

各ペア合計の記入数について、0回と5回は0点、1〜4回は-200点、6〜10回はscore padの基礎点×`(count - 5)`です。ペア合計別基礎点はscore padの配列を固定値として保持します。pair countは10を超えて増えません。

環境が返す`reward`はその手による**規則上の総得点差分**です。学習用のshape rewardは`shaped_reward()`で別に加算し、規則得点と混在させません。

## Q学習

`Q-learning_algorithm.py` はimport時に学習を開始しません。設定は`TrainingConfig`へ集約しています。

Q更新は終了遷移（またはtruncated遷移）では次状態の最大Q値をbootstrapしません。`compare_policies()`は同じseed集合に対してrandom / fixed / Q-learning方策を比較できます。

```bash
python Q-learning_algorithm.py
```

## テスト

外部サービスや実ネットワークは不要です。

```bash
python -m unittest discover -s tests -v
```

主な回帰条件:

- `[1,2,3,4,5]`の合法行動を決定論的に列挙
- 同値pair順序・同値dice indexの重複排除
- chart / score / turn / 5th die更新
- 不正action・終了後stepのfail-closed
- seed固定trajectory
- 得点境界と同点winner
- terminal Q transitionでbootstrapしない
- module import時にstdout・学習・無限loopを発生させない
- 同じseed集合で3方策を比較

## 対象外

この環境は1プレイヤー分のscore sheetをモデル化します。複数プレイヤーが同じ投擲を同時利用するUIや対戦進行は学習環境の責務に含めません。同点判定は`winners()`が最高得点者を全員返します。
