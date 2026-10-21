# 实验记录本同步规则

本目录中的 Markdown 记录、模板、`index.html`、`实验记录本.html`、`data.js`、`db-data.json` 或同步脚本发生变更后，必须同步到 GitHub Pages。

## 必须执行的流程

1. 修改记录或界面文件。
2. 运行 `实验记录本\scripts\sync-data.py` 生成最新 `data.js` 和 `db-data.json`。
3. 提交并推送到 `origin master`。
4. 验证线上地址 `https://a917695138-lgtm.github.io/electrochromic-notebook/?t=2` 或对应 `data.js` 已更新。

结构说明（2026-10-21）：`index.html` 是壳（约 78 KB，纯界面），数据全部在 `data.js`；
网页为只读视图（新建/编辑/删除/导入入口已移除），修改一律改 md 后跑 sync。
`实验记录本.html` 副本已退役删除。frontmatter 受控词表见 skill
`nature-experiment-log/references/notebook-metadata-schema.md`，改完跑
`scripts\check-metadata.py` 校验。

## 推荐命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Users\ao\Documents\电致变色\实验记录本\scripts\push-to-github.ps1" -NoPause
```

如果 GitHub 访问失败，优先检查本仓库 Git 代理是否为 `http://127.0.0.1:7897`。
