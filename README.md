# mcd-order-lint · 麦麦点餐质检员

基于麦当劳中国 MCP **只读**能力的 WorkBuddy Skill：在真正下单前，核对点餐草稿是否漏选套餐组、名称/ID 是否对得上、特调是否有证据支持。

> 本项目为个人开源工具，**非麦当劳官方产品**。餐品、价格、供应状态以官方渠道实时结果为准。

## 目标用户

- 用 WorkBuddy / AI 助手点麦当劳、容易漏选饮料或写错特调的人
- 想确认「草稿能不能下」但不想让 AI 擅自推荐、领券、下单的人

## 能做什么 / 不能做什么

| 能做 | 不能做 |
|---|---|
| 只读查询门店菜单与餐品详情 | 领券、下单、取消订单、支付、抽奖 |
| 核验数量、身份、套餐组、特调归属 | 推荐套餐、比价、凑单优化 |
| 输出通过 / 不通过 / 未知三态 | 承诺过敏原或食品安全 |

## 快速开始（离线演示，无需 Token）

需要 Python 3.9+，仅标准库：

```bash
python scripts/lint_order.py assets/demo-input.json --format markdown
python scripts/lint_order.py assets/demo-input.json --format json
python -m unittest discover -s tests -v
```

## 真实 MCP 联调（可选）

1. 在 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 申请 MCP Token  
2. 参考根目录 `mcp-config.example.json`，在 WorkBuddy 自定义连接器中配置（**不要把真实 Token 写入本仓库**）  
3. 启用 `mcd-mcp` 后，对助手说：「用麦麦点餐质检员核对我的点餐草稿」  
4. Skill 仅允许宿主调用只读工具 `query-meals`、`query-meal-detail`

配置示例见 `mcp-config.example.json`（占位符 `${MCD_MCP_TOKEN}`）。

## 真实数据回放示例

`examples/live-lint-20261024/` 基于 2026-10-24 对门店 `3350075`、餐品「麦辣鸡腿汉堡三件套」的只读查询人工摘取子集，回放三个场景：

- 正常选择 → 待确认（单位字段未知）
- 缺少必选饮料 → 需修正
- 「保持温热」特调 → 未知

打开 `examples/live-lint-20261024/report.html` 可浏览摘要。重新回放：

```bash
python examples/live-lint-20261024/verify.py
```

## 项目结构

```text
README.md
CONTEST_DECLARATION.md      # 官方参赛声明（内容不可改）
MCP_INTEGRATION.md          # MCP 工具与调用说明
mcp-config.example.json     # 脱敏配置示例
workbuddy.md                # WorkBuddy 开发过程记录
SKILL.md                    # Skill 说明
scripts/lint_order.py       # 确定性质检引擎（不联网）
tests/                      # 18 项 unittest
assets/                     # 模拟输入输出
references/input-contract.md
examples/live-lint-20261024/
```

## 许可与边界

脚本不联网、不读取 Token、不执行交易。证据有本地时效策略（约 30 分钟），过期应重新只读查询，不得伪造查询时间。
