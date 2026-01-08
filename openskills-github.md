• 用到的 skill：github-to-usage-md（从 GitHub 仓库提取 README/结构来快速总结用途与用法）。

  https://github.com/numman-ali/openskills 是一个 Node.js CLI 工具，目标是把 Claude Code 的 “skills” 体系
  用同样的格式带到更多 AI 编程代理（Claude Code / Cursor / Windsurf / Aider 等）：从 Anthropic
  marketplace 或任意 GitHub 仓库安装 skills，并把可用 skills 清单同步到 AGENTS.md，让代理按需加载
  SKILL.md。

  常用用法（来自仓库 README）：

  - 安装：npm i -g openskills
  - 安装 skills（marketplace 或任意仓库）：openskills install anthropics/skills 或 openskills install
    your-org/custom-skills
  - 同步到 AGENTS.md：openskills sync
  - 给代理加载某个 skill：openskills read <name>
  - 查看已安装：openskills list