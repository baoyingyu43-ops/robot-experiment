[README.md](https://github.com/user-attachments/files/27097882/README.md)
# 🤖 机器人声音外观匹配实验程序

## 文件夹结构（必须按这个放）

```
robot_experiment/
├── app.py
├── requirements.txt
├── images/
│   ├── A01.png ~ A06.png
└── audio/
    ├── cognitive.wav   ← 高认知型声音
    ├── emotional.wav   ← 高情感型声音
    └── balanced.wav    ← 平衡型声音
```

## 部署到网上（3步）

**Step 1** 注册 GitHub：https://github.com

**Step 2** 新建仓库 robot-experiment → 上传所有文件（包括images和audio文件夹）

**Step 3** 去 https://share.streamlit.io → 用GitHub登录 → New app → 选你的仓库 → Deploy

部署完成后得到一个链接，直接发给被试即可。

## 被试完成后

每个被试填完会下载一个CSV文件，发给你后用以下代码合并：

```python
import pandas as pd, glob
df = pd.concat([pd.read_csv(f) for f in glob.glob("收到的数据/*.csv")])
df.to_csv("全部数据.csv", index=False, encoding="utf-8-sig")
```
