# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## 自由に作り、きれいに公開する。

Hatch は、ひとりで作る人のために、試行錯誤用の非公開 workbench と共有用の
整理された product 空間を用意します。両者の境界を明確にするため、公開の
たびに同じ要件を整理し直す必要がありません。

## クイックスタート

Hatch をインストールしたら、`$hatch` でプロジェクトを始めます。workbench、
product、評価エビデンス用に、それぞれ独立したローカル Git リポジトリを
作成します。

product のバージョンが準備できたら、もう一度 `$hatch` を使って昇格します。
Hatch は対象範囲を確認し、バージョンと変更履歴を記録し、対象のコミットを
監査して、push の準備ができたかを判断します。

## ワークスペース構成

`$hatch init` は次のローカルコンテナを作成します。3 つの兄弟ディレクトリは
それぞれ独立した Git リポジトリです。

```text
my-project/
├── hatch.toml                  # 3 つの境界を示す設定
├── my-project-workbench/       # 非公開の下書き、実験、brief
├── my-project-product/         # 安全に公開できる product ソース
└── my-project-evals/           # 非公開の人間または自動評価エビデンス
```

## コマンド

Hatch の利用者向けコマンドは 2 つだけです。以降の手順は覚える追加コマンド
ではなく、`promote` の中で慎重に実行される段階です。

### `init`

新しいプロジェクトを始めるときは `$hatch init` を使います。

1. 親ディレクトリ、プロジェクト名、公開 Git ID を決めます。
2. `--dry-run` ではコンテナと 3 つのリポジトリのパスだけを表示します。
3. それ以外ではコンテナを作成し、`workbench`、`product`、`evals` をそれぞれ
   `main` ブランチの独立した Git リポジトリとして初期化します。
4. `hatch.toml`、非公開 workbench の監査ポリシー、リポジトリ案内、ignore
   ファイル、product の初期 `VERSION`（`0.0.0`）と `CHANGELOG.md` を書きます。
5. product リポジトリに公開 Git ID を設定します。

リモートの作成、コミット、push、タグ、リリース作成、デプロイは決して行いません。

### `promote`

選んだ作業を product スナップショットにする準備ができたら `$hatch promote`
を使います。

1. product を変更せずに候補、現在の product 状態、既存の evidence を調べます。
2. 意図、含める・除外する作業、公開安全性の判断、受け入れ基準、evidence、次の
   安定バージョンを記録する source-pinned Promotion Brief を作成します。
3. brief を提示し、product を変更する前に確認を得ます。
4. 確認済みの範囲だけを product に反映します。workbench 全体を自動同期しません。
5. `VERSION` と対応する `CHANGELOG.md` の項目を書き、関連する product チェックを
   実行して、一つの正確な product コミットを作成します。
6. 非公開ポリシーに照らし、その正確なコミットの到達可能な履歴、コミット
   メッセージ、Git ID、パス、ファイル内容を監査します。
7. 同じコミットに対する人間・自動・混合の評価 evidence を記録します。
8. ready check を実行します。brief、バージョンログ、監査、evidence がすべて同じ
   コミットを指すことを確認し、`READY TO PUSH`、`NOT READY`、`NEEDS EVIDENCE`
   のいずれかを報告します。

`promote` 自身が push、タグ、リリース作成、デプロイを行うことはありません。

## Hatch が必要な理由

### workbench と product は別物です

**問題。** プロジェクトには、下書き、実験、メモ、未完成の作業のための場所が
必要です。公開リポジトリには、焦点が絞られた安全なスナップショットが必要
です。両者を混ぜると、リリースのたびに片付けが必要になります。

**解決策。** それぞれを独立した Git リポジトリに保ちます。workbench では
自由に開発し、公開に適した作業だけを product へ昇格します。

### 昇格は繰り返せるべきです

**問題。** 昇格のたびに、同じ問いが生まれます。何が含まれるのか。安全に
公開できるのか。どのバージョンなのか。本当にテストされたのか。

**解決策。** Hatch は brief、バージョン、監査、評価エビデンス、準備状態の
判断を一つの流れにし、すべてを一つの正確な product コミットに結び付けます。

### まとめ

Hatch は非公開の探索と公開 product 作業を分け、その間の移動を小さく、
慎重で、検証可能なものにします。
