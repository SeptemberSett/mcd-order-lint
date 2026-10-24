"""Replay a manually extracted real MCP response subset; never connects or orders."""
import html
import importlib.util
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
ENGINE = REPO / "scripts" / "lint_order.py"
TESTS = REPO / "tests"

spec = importlib.util.spec_from_file_location("lint_order", ENGINE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Keep captured fixtures unchanged. Freshness is evaluated at the actual replay time.
checked_at = datetime.now().astimezone().isoformat()
results = []
for stem, title in [
    ("normal", "正常选择"),
    ("missing-drink", "缺少必选饮料"),
    ("unknown-modifier", "特殊要求未知"),
]:
    data = json.loads((ROOT / (stem + ".json")).read_text(encoding="utf-8"))
    data["checked_at"] = checked_at
    report = module.lint(data)
    (ROOT / (stem + "-result.json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / (stem + ".md")).write_text(module.markdown(report), encoding="utf-8")
    group = next(f for f in report["findings"] if f["code"] == "groups")
    age = (
        datetime.fromisoformat(checked_at)
        - datetime.fromisoformat("2026-10-24T14:23:26+08:00")
    ).total_seconds()
    fresh = 0 <= age <= 1800
    expected_group = ("fail" if stem == "missing-drink" else "pass") if fresh else "unknown"
    assert group["state"] == expected_group, (stem, group)
    assert next(f for f in report["findings"] if f["code"] == "unit")["state"] == "unknown"
    if stem == "unknown-modifier":
        assert next(f for f in report["findings"] if f["code"] == "modifier")["state"] == "unknown"
    results.append((title, report))
    print(title, report["summary"], "groups=" + group["state"])

regression = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS), "-v"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
(ROOT / "regression-tests.txt").write_text(
    regression.stdout + regression.stderr, encoding="utf-8"
)
assert regression.returncode == 0, regression.stderr

cards = ""
for title, report in results:
    findings = "".join(
        "<li><strong>"
        + html.escape(f["state"])
        + "</strong> · "
        + html.escape(f["code"] + "：" + f["message"])
        + "</li>"
        for f in report["findings"]
    )
    cards += (
        "<section><h2>"
        + title
        + "</h2><p>总评：<b>"
        + report["summary"]
        + "</b></p><ul>"
        + findings
        + "</ul></section>"
    )

page = (
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
    "<title>麦麦点餐质检员 · 真实数据回放测试</title>"
    '<style>body{background:#f5f7fa;color:#243047;font:16px/1.8 "Microsoft YaHei",sans-serif;'
    "max-width:960px;margin:36px auto;padding:0 24px}"
    "section{background:white;border:1px solid #dce3eb;border-radius:12px;padding:20px 28px;margin:20px 0}"
    "h1{font-size:28px}h2{font-size:21px}li{margin:8px 0}"
    ".note{background:#fff5d9;padding:18px;border-radius:10px}</style>"
    "<h1>麦麦点餐质检员 · 真实数据回放测试</h1>"
    "<p>门店：青岛城阳利群得来速餐厅（3350075）<br>"
    "对象：麦辣鸡腿汉堡三件套（9900005456）<br>"
    "真实查询时间：2026-10-24 14:23:26 +08:00<br>"
    "本地执行时间：" + html.escape(checked_at) + "</p>"
    '<p class="note">全程只读，无下单、支付、领券。菜单证据来自本会话真实接口返回的人工摘取子集，'
    "并非完整原始响应；三份餐单由测试构造，不是实际购买意图。当前验证的是人工适配后进入质检脚本的链路，"
    "尚非全自动适配。本示例不含任何 MCP Token。</p>"
    + cards
    + "<section><h2>结论与边界</h2>"
    "<p>三个场景的断言均符合预期；原有18项单元测试通过。"
    "接口没有明确的数量包装单位字段，因此单位检查保持未知。"
    "缺少饮料被识别为套餐组不全；“保持温热”不被擅自判为支持或不支持。</p>"
    "<p>来源：query-meal-detail；字段：data.code、data.name、data.rounds[].minQuantity/maxQuantity/choices[].code。"
    "未认证或过期证据不会被当作实时保证。"
    "若查询距回放超过30分钟，脚本应输出证据时效未知，请重新只读查询，而不是修改原始查询时间。</p>"
    "<p>不承诺食品安全、过敏原或交叉接触安全。</p></section></html>"
)
(ROOT / "report.html").write_text(page, encoding="utf-8")
print("场景断言通过；18项回归通过；报告已更新。")
