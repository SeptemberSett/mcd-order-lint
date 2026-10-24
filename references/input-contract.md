# 适配器输入契约

`lint_order.py` 读取 JSON：`schema_version` 必须为 `1.0`，顶层含 `store_id`、带时区的 `checked_at`、`menu.products` 和非空 `order`。产品至少有 `id`、`name`，可有 `aliases`、`units`、`groups`、`modifiers`、`evidence`；订单行至少有 `line_id`，可有 `product_id`、`name`、`quantity`、`unit`、`selections`、`modifiers`。

`quantity` 必须是严格正整数，布尔值、负数、零和小数均不通过。`groups` 使用 `min/max/allowed_ids`；修饰状态只能是 `supported`、`unsupported`、`unknown`。`evidence` 每项应带 `store_id`、`queried_at`、`source`、`path`、`excerpt`、`response_ref`。

这是宿主适配器 schema，不是麦当劳 MCP 原始 schema。字段映射须由宿主依据当前工具响应完成，不得猜测字段路径。缺证据默认 `unknown`。
