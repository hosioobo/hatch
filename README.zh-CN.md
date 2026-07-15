# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## 自由构建，干净发布。

Hatch 为独立创作者提供用于探索的私有 workbench 和用于分享的整洁 product
空间。它明确两者之间的边界，因此每次公开发布时都不必重新梳理同一套要求。

## 快速开始

安装 Hatch 后，使用 `$hatch` 启动项目。它会为 workbench、product 和评估
证据分别创建独立的本地 Git 仓库。

当 product 版本准备好后，再次使用 `$hatch` 进行提升。Hatch 会确认范围，
记录版本和变更日志，审查准确的提交，并判断它是否已准备好推送。

## 工作区结构

`$hatch init` 会创建如下本地容器。三个同级目录都是相互独立的 Git 仓库。

```text
my-project/
├── hatch.toml                  # 描述三个边界的配置
├── my-project-workbench/       # 私有草稿、实验和 brief
├── my-project-product/         # 可安全公开的 product 源码
└── my-project-evals/           # 私有人类或自动评估证据
```

## 命令

Hatch 只有两个面向用户的命令。后续步骤是 `promote` 中审慎进行的环节，
不是需要记住的额外命令。

### `init`

开始新项目时使用 `$hatch init`。

1. 确定父目录、项目名称和公开 Git 身份。
2. 使用 `--dry-run` 时，只输出容器和三个仓库的路径。
3. 否则创建容器，并将 `workbench`、`product`、`evals` 初始化为独立、以
   `main` 为默认分支的 Git 仓库。
4. 写入 `hatch.toml`、私有 workbench 审查策略、仓库说明、忽略文件，以及
   product 的初始 `VERSION`（`0.0.0`）和 `CHANGELOG.md`。
5. 为 product 仓库配置公开 Git 身份。

它绝不会自行创建远程仓库、提交、推送、打标签、发布版本或部署。

### `promote`

当选定工作准备成为 product 快照时，使用 `$hatch promote`。

1. 在不修改 product 的情况下检查候选内容、当前 product 状态和已有 evidence。
2. 创建固定 source 的 Promotion Brief，记录意图、包含与排除的工作、公开安全
   决策、验收标准、evidence 和下一个稳定版本。
3. 展示 brief，并在修改 product 前获得确认。
4. 只将已确认的范围应用到 product；绝不自动同步整个 workbench。
5. 写入 `VERSION` 与对应的 `CHANGELOG.md` 条目，运行相关 product 检查，并创建
   一个准确的 product 提交。
6. 按私有策略审查该准确提交可达的历史、提交消息、Git 身份、路径和文件内容。
7. 为同一提交记录人工、自动或混合的评估 evidence。
8. 运行 ready check。它验证 brief、版本日志、审查和 evidence 是否都指向同一
   提交，然后报告 `READY TO PUSH`、`NOT READY` 或 `NEEDS EVIDENCE`。

`promote` 不会自行推送、打标签、创建发布版本或部署。

## Hatch 为什么存在

### workbench 不是 product

**问题。** 项目需要容纳草稿、实验、笔记和未完成工作的空间。公共仓库则需要
一个聚焦且安全的快照。把两者混在一起，会让每次发布都变成一次清理工程。

**解决方案。** 将它们保留在独立的 Git 仓库中。在 workbench 中自由开发，
只将适合公开的工作提升到 product。

### 提升应当可重复

**问题。** 每次提升都会出现相同的问题：包含什么？可以安全公开吗？这是哪个
版本？它真的经过测试吗？

**解决方案。** Hatch 将 brief、版本、审查、评估证据和就绪决定组成一个流程，
并将它们全部关联到一个准确的 product 提交。

### 总结

Hatch 将私有探索与公开 product 工作分开，让两者之间的移动保持小巧、慎重且
可验证。
