# 实验记录本同步规则

本目录中的 Markdown 记录、模板、`index.html`、`实验记录本.html`、`data.js`、`db-data.json` 或同步脚本发生变更后，必须同步到 GitHub Pages。

## 必须执行的流程

1. 修改记录或界面文件。
2. 运行 `实验记录本\scripts\sync-data.py` 生成最新 `data.js` 和 `db-data.json`。
3. 确保 `实验记录本\index.html` 与 `实验记录本\实验记录本.html` 保持一致。
4. 提交并推送到 `origin master`。
5. 验证线上地址 `https://a917695138-lgtm.github.io/electrochromic-notebook/?t=2` 或对应 `data.js` 已更新。

## 推荐命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\Users\ao\Documents\电致变色\实验记录本\scripts\push-to-github.ps1" -NoPause
```

如果 GitHub 访问失败，优先检查本仓库 Git 代理是否为 `http://127.0.0.1:7897`。
