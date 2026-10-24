# WorkBuddy 开发对话上下文

> 用于核验本项目在腾讯 WorkBuddy 中完成构思与实现，符合联动活动「使用 WorkBuddy 开发」条件。  
> 开发日期：2026-10-24 ｜ 环境：WorkBuddy（Agent / Skill）  
> **本文件不含 MCP Token、账号密码或其他凭证。**

## 轮次 1 · 选题避让

**用户**：已配置麦当劳 MCP，希望做用餐赛道 / 麦当劳大赛作品，避开 GitHub 上高重复的省钱凑单方向。

**WorkBuddy**：排查公开报名与竞品后，确认「反凑单 / 优惠组合优化」等方向拥挤；建议改走更窄的点餐沟通类：餐品替代解释、门店决策卡、点餐风险检查等。

## 轮次 2 · 定题「麦麦点餐质检员」

**用户**：做只读点餐质检，不推荐、不领券、不下单。

**WorkBuddy**：立项 `mcd-order-lint` Skill：宿主只读拉取菜单/详情 → 映射适配器 JSON → 标准库脚本确定性核验 → 通过/不通过/未知三态。

## 轮次 3 · 实现与打包

**用户**：按比赛文件要求落地。

**WorkBuddy 产出**：

- `scripts/lint_order.py`：无网络、无 Token 的质检引擎
- `tests/test_lint_order.py`：18 项 unittest
- `references/input-contract.md`、`assets/demo-*`
- `README.md` / `CONTEST_DECLARATION.md`（官方原文）/ `MCP_INTEGRATION.md` / `mcp-config.example.json` / `SKILL.md`
- 用户级 Skill 目录与 `outputs/mcd-order-lint.zip`

## 轮次 4 · 真实只读联调

**用户**：用真实 MCP 验证，不要下单。

**WorkBuddy**：

- 门店 `3350075`：`query-meals`、`query-meal-detail`（麦辣鸡腿汉堡三件套）成功
- 确认套餐必选组、默认项与特调字段
- **未**调用下单 / 支付 / 领券类工具

## 轮次 5 · 三场景回放

基于真实返回的人工摘取子集，构造：

1. 正常三选项组 → 通过为主，单位未知  
2. 缺少饮料组 → 不通过  
3. 「保持温热」未出现在返回中 → 未知  

并生成 `examples/live-lint-20261024/`（含 HTML 报告）；原 18 项回归仍通过。

## 轮次 6 · 参赛仓库脱敏与文档补全

**用户**：准备上传公开 GitHub，检查明文密钥与文档缺口。

**处理**：

- 确认参赛材料不含真实 Token；Token 仅存于本机 WorkBuddy `mcp.json`，禁止入库
- 修正 `verify.py` 绝对本机路径
- 补全 README / MCP_INTEGRATION / workbuddy 过程说明，根目录放置脱敏 `mcp-config.example.json`

## 边界声明

- 脚本本身永不联网、不读 Token  
- 真实联调仅只读；支付与下单由用户在官方渠道自行完成  
- 演示数据为构造餐单，不代表实际购买意图  
