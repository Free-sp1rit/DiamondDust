# MVP Scope

## P0 Must Have

1. 读取一篇 Markdown 随笔
2. 抽取候选 KnowledgeUnit
3. 生成候选 Relation
4. 生成 KnowledgePatch
5. 验证 KnowledgePatch
6. 输出 review report
7. 用户接受 patch 后写入 Markdown vault
8. 基于已接受知识单元生成博客草稿
9. 生成博客质量报告

## P0 Must Not Have

- 不做 Obsidian 插件
- 不做 Notion 同步
- 不做 MCP server
- 不做 PDF / 图片 / LaTeX / 代码项目解析
- 不做图谱可视化
- 不做自动发布
- 不做模型训练
- 不做复杂 agent autonomy

## MVP Done When

给定 5 篇真实或半真实 Markdown 随笔，系统可以稳定产出：

- extraction JSON
- valid KnowledgePatch
- candidate Markdown notes
- blog draft
- blog review report

并且：

- schema tests pass
- patch validation tests pass
- no direct formal write from LLM output