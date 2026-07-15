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
