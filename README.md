---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'c025538c-c0f8-4a27-a6ee-61b27545ec59'
  PropagateID: 'c025538c-c0f8-4a27-a6ee-61b27545ec59'
  ReservedCode1: '54a6b8ff-15af-4f5e-9f94-8dd6a0fbe586'
  ReservedCode2: '54a6b8ff-15af-4f5e-9f94-8dd6a0fbe586'
---

# 《我的成长世界》家庭积分激励系统

面向家庭场景的小朋友成长激励系统。通过游戏化方式，将「日常行为 → 积分奖励 → 角色成长 → 等级升级 → 成就解锁 → 奖励兑换」形成完整成长闭环，打造一款"孩子愿意每天打开查看，家长愿意长期记录"的家庭成长游戏化系统。

## 项目定位

- **家庭私有部署**，单家庭、单孩子优先（数据结构预留多孩扩展）
- 家长负责管理记录，小朋友只读查看自己的成长成果
- 原创像素幻想冒险风格，规避 Minecraft 版权风险
- 移动端优先的响应式 Web 应用

## 技术栈

| 端 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + TypeScript + TailwindCSS |
| 后端 | FastAPI (Python) |
| 数据库 | SQLite（优先），预留 PostgreSQL 兼容 |
| 部署 | Docker Compose |

## 核心功能

- **成长大厅**：角色头像、等级、魔法宝石（积分）、成长进度条、徽章、任务、奖励
- **积分系统**：加/减分，全程可追溯（时间/类型/分值/原因/操作人）
- **任务规则**：学习/家务/习惯/品德/临时，正向奖励、负向惩罚
- **等级系统**：按累计积分升级，只升不降
- **成就系统**：自动检测解锁
- **奖励商城**：兑换商店，扣减宝石，生成兑换记录
- **成长日志**：文字+照片，形成家庭成长档案
- **数据统计**：每日/每周/每月积分趋势、正负行为比例、成长曲线

## 目录结构

```
my-growth-world/
├── backend/           # FastAPI 后端
│   └── app/
│       ├── api/       # 路由
│       ├── core/      # 配置、安全、数据库
│       ├── models/    # SQLAlchemy 模型
│       ├── schemas/   # Pydantic 校验
│       ├── services/  # 业务逻辑
│       └── seed/      # 预置数据
├── frontend/          # Vue3 前端
│   └── src/
│       ├── api/       # API 封装
│       ├── components/
│       ├── router/
│       ├── stores/
│       └── views/     # auth/parent/child/game
├── docs/              # 设计文档
├── deploy/            # 部署配置
└── docker-compose.yml
```

## 开发与部署

见 `docs/` 下的设计与部署文档。

> 本系统为 AIGC 辅助生成，仅供家庭个人使用。

> AI生成