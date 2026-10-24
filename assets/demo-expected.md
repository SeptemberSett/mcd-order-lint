# 麦麦点餐质检

总评：当前检查范围通过
门店：store-demo
检查时间：2026-10-24T10:00:00+08:00

- [通过 / info] L1 · quantity：数量须为正整数（布尔值无效）
- [通过 / info] L1 · identity：名称与餐品 ID 对应
  - 证据：{"excerpt": "示例汉堡", "path": "products[0]", "queried_at": "2026-10-24T09:55:00+08:00", "response_ref": "demo-1", "source": "query-meals", "store_id": "store-demo"}
- [通过 / info] L1 · unit：数量单位匹配
  - 证据：{"excerpt": "份", "path": "unit", "queried_at": "2026-10-24T09:55:00+08:00", "response_ref": "demo-2", "source": "query-meal-detail", "store_id": "store-demo"}
- [通过 / info] L1 · groups：套餐组选择数量与允许 ID 符合
  - 证据：{"excerpt": "模拟单品无套餐组", "path": "groups", "queried_at": "2026-10-24T09:55:00+08:00", "response_ref": "demo-2", "source": "query-meal-detail", "store_id": "store-demo"}
- [通过 / info] L1 · modifier：去洋葱：明确支持
  - 证据：{"excerpt": "去洋葱支持", "path": "modifiers", "queried_at": "2026-10-24T09:55:00+08:00", "response_ref": "demo-2", "source": "query-meal-detail", "store_id": "store-demo"}

仅核对当前结构化输入；证据未获独立真实性认证，30分钟时效仅为本地检查策略，不保证菜单仍有效。不承诺食品安全、过敏原或过敏交叉接触安全。
