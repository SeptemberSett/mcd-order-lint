# 麦当劳 MCP 集成说明

## Server

| 项 | 值 |
|---|---|
| 接入地址 | `https://mcp.mcd.cn` |
| 协议 | Streamable HTTP |
| 鉴权 | 请求头 `Authorization: Bearer <MCP_TOKEN>`（仅宿主本地配置，本仓库不含真实 Token） |
| 配置示例 | 根目录 `mcp-config.example.json`（占位符 `${MCD_MCP_TOKEN}`） |

参考：[麦当劳 MCP 文档](https://open.mcd.cn/mcp/doc)、官方相关仓库 `M-China/mcd-mcp-server`。

## 实际使用的 Tool（仅只读）

| Tool | 用途 | 本项目如何用 |
|---|---|---|
| `query-meals` | 查询门店当前可售餐品列表 | 确认门店侧是否能找到目标餐品名称/编码 |
| `query-meal-detail` | 查询餐品详情、套餐组成与替换/特调选项 | 映射套餐组 `min/max/allowed_ids`、特调是否返回 |

**明确禁止**由本 Skill 触发：`create-order`、`cancel-order`、`calculate-price`、`auto-bind-coupons`、`draw-lottery`、积分商城下单等写操作或交易工具。

## 调用流程

1. 用户给出门店标识与点餐草稿（不索取账号、地址、Token）。
2. 宿主（WorkBuddy）只读调用 `query-meals` / `query-meal-detail`。
3. 将响应中明确字段映射为 `references/input-contract.md` 约定的适配器 JSON（不是 MCP 原始 schema）。
4. 运行 `python scripts/lint_order.py <input.json> --format markdown|json`。
5. 按「通过 / 不通过 / 未知」输出；缺字段保持未知，不把无结果当成下架，不把缺特调字段当成不支持。

## 业务价值

下单前做轻量「点餐质检」：抓漏选饮料、ID/名称不一致、无证据的特调要求，减少无效沟通与点错单，同时不替代推荐、优惠或支付。

## 已验证的只读联调（摘要）

- 时间：2026-10-24（北京时间）
- 门店：`3350075`（青岛城阳利群得来速餐厅）
- 餐品：麦辣鸡腿汉堡三件套（`9900005456`）
- 工具：`query-meals`、`query-meal-detail` 均成功；**未**调用下单/支付/领券
- 回放材料：`examples/live-lint-20261024/`（人工摘取子集，非完整原始响应）

映射时记录：`store_id`、`queried_at`、工具名、字段路径、excerpt、`response_ref`。菜单无结果 ≠ 下架；缺字段 ≠ 不支持。
