# Project Charter

## Mission

DiamondDust is a local-first semantic knowledge compiler that turns scattered essays into structured knowledge dust, then recomposes them into durable knowledge artifacts such as blog drafts, maps, and reviewable knowledge patches.

DiamondDust 是一个本地优先的语义知识编译器：它将零散随笔拆解为更小粒度的结构化知识单元，再将这些知识单元重组为可审阅、可维护、可发布的知识产物。

## Target User

希望将个人随笔、学习笔记和项目经验转化为结构化知识库，并进一步生成知识博客草稿的个人知识工作者。

## Core Problem

用户在入门新知识领域时，随笔零散、结构不稳定、难以持续维护，也难以转化为高质量知识博客。

## Product Promise

用户输入一篇 Markdown 随笔，系统可以半自动生成：

1. 候选知识单元
2. 候选链接关系
3. 可审阅知识库 patch
4. 博客草稿
5. 质量检查报告

## Success Criteria

MVP 成功标准：

- 能处理真实 Markdown 随笔
- 能生成结构化 KnowledgeUnit
- 能生成可审阅 patch
- 不直接污染正式知识库
- 能生成一篇可修改的博客草稿
- 有基础测试覆盖核心 schema 和 patch 流程

## Non-goals

- 不做完整笔记编辑器
- 不做全自动博客发布
- 不训练专用模型
- 不做人生建议系统
- 不把 Notion 或任何向量数据库作为唯一真实数据源
- 不允许 AI 直接覆盖正式知识库

## Invariants

- 原始随笔永远保留
- AI 输出必须先成为 proposal / patch
- 正式写入必须可追溯、可审阅、可回滚
- 主数据必须可迁移
- 模型和 AI 厂商必须可替换