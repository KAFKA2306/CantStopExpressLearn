# CantStopExpressLearn

[![Test rules environment](https://github.com/KAFKA2306/CantStopExpressLearn/actions/workflows/test.yml/badge.svg)](https://github.com/KAFKA2306/CantStopExpressLearn/actions/workflows/test.yml)

**学習器を強くする前に、まずゲームを間違えていないことを証明する。**

Can’t Stop Express のルール環境とQ学習器を分離し、ゲーム規則を回帰テストしたうえで方策比較を行う実験リポジトリです。

## Authority

ゲーム規則の一次資料は Eagle-Gryphon Games の [Can't Stop Express](https://www.eagle-gryphon.com/products/cant-stop-express) 製品ページと、同ページの **Rulebooks & Downloads** から提供される公式Rulebookです。リポジトリ内には公式ルールの転記コピーを持ちません。

現在の実行可能な挙動は実装とテストを正準とします。

- `cant_stop_express_env.py`: ゲーム規則・状態遷移・得点
- `q_learning.py`: Q学習と方策比較
- `tests/test_env.py`: 規則と学習器の回帰テスト

## Model

`CantStopExpressEnv` は1プレイヤー分のscore sheetをモデル化します。状態はpair count、5th-die count、turn、dice、合法行動、score、終了状態を保持します。

- 同値なpair順序・dice indexは同一行動へ正規化
- pair countは10で上限
- 5th dieのいずれかが8回に達すると終了
- 規則上扱えない状態は推測で補わずtruncatedとして停止
- `reward`は規則上の総得点差分。学習用shape rewardは別に扱う
- 同点判定は`winners()`が最高得点者をすべて返す

複数プレイヤーが同じ投擲を同時利用するUIや対戦進行は対象外です。

## Q-learning

設定は`TrainingConfig`に集約しています。終了・truncated遷移では次状態のQ値をbootstrapしません。`compare_policies()`は同じseed集合でrandom / fixed / Q-learningを比較します。

```bash
python q_learning.py
```

## Test

外部サービスや実ネットワークは不要です。

```bash
python -m unittest discover -s tests -v
```

主な回帰条件は、合法行動の決定性、重複排除、状態更新、不正actionのfail-closed、seed固定trajectory、得点境界、terminal Q transition、import時の副作用不在、同一seedでの方策比較です。
