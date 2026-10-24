# 麦麦点餐质检

总评：待确认
门店：3350075
检查时间：2026-10-24T14:39:28.262027+08:00

- [通过 / info] L1 · quantity：数量须为正整数（布尔值无效）
- [通过 / info] L1 · identity：名称与餐品 ID 对应
  - 证据：{"excerpt": "9900005456 麦辣鸡腿汉堡三件套", "path": "data.code/data.name", "queried_at": "2026-10-24T14:23:26+08:00", "response_ref": "f6f7d6afdfab3babd7c649029c805788", "source": "query-meal-detail", "store_id": "3350075"}
- [未知 / warning] L1 · unit：数量单位未明确或无单位证据
- [通过 / info] L1 · groups：套餐组选择数量与允许 ID 符合
  - 证据：{"excerpt": "3组均min=1,max=1", "path": "data.rounds[].minQuantity/maxQuantity/choices[].code", "queried_at": "2026-10-24T14:23:26+08:00", "response_ref": "f6f7d6afdfab3babd7c649029c805788", "source": "query-meal-detail", "store_id": "3350075"}
- [未知 / warning] L1 · modifier：保持温热：支持情况未知

仅核对当前结构化输入；证据未获独立真实性认证，30分钟时效仅为本地检查策略，不保证菜单仍有效。不承诺食品安全、过敏原或过敏交叉接触安全。
