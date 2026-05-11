# Product Spec

## Primary Input

- Markdown essay
- Plain text essay

## Primary Outputs

- Knowledge unit candidates
- Relation candidates
- KnowledgePatch
- Review report
- Blog draft
- Blog quality report

## Main Flow

1. 用户把随笔放入 `00-inbox/`
2. 系统读取随笔
3. 系统抽取知识单元候选
4. 系统推荐链接关系
5. 系统生成 patch
6. 系统展示 review report
7. 用户接受或拒绝 patch
8. 接受后写入正式 vault
9. 系统基于已接受内容生成博客草稿
10. 系统生成质量报告

## Local Trial Flow

Before real provider calls are introduced, the local trial flow accepts:

- one Markdown essay
- one structured extraction JSON file

The local trial writes inspectable AI working artifacts:

- AI run log
- review package
- candidate Markdown notes
- patch review report
- blog draft package
- blog quality report

Rules:

- The local trial must not call an LLM provider.
- The local trial must not write formal vault files.
- The local trial may simulate patch acceptance only to generate downstream draft artifacts.
- Simulated acceptance must not imply user acceptance for formal vault apply.

## Human Review Points

必须人工确认：

- 正式写入知识库
- 合并已有笔记
- 删除或覆盖文件
- 标记内容为 evergreen
- 发布博客

## Failure Cases

系统必须能处理：

- 随笔太短
- 随笔没有明确知识点
- AI 生成无来源 claim
- 关系推荐置信度低
- patch validation 失败
- 目标路径冲突
