#!/usr/bin/env python3
"""预售落地页上线前自检。

用法：
    python3 check_landing.py <page.html> [--demo-brand AutoBrief]

检查两类问题：
  1. 硬伤（FAIL）：没填的占位符、装了支付链接却没写交付日、没有退款承诺、没有 CTA 收款入口
  2. 建议（WARN）：缺少微证、FAQ 太少、CTA 文案无信息量、首屏 H1 过长

退出码：0 = 可上线（可能有 warning）；1 = 存在硬伤。
"""

import argparse
import re
import sys
from pathlib import Path

# 占位符与示例残留
PLACEHOLDERS = [
    "REPLACE_ME",
    "YOUR_",
    "your-domain.com",
    "example.com",
    "TODO",
    "Lorem ipsum",
    "换成你的照片",
    "产品名",
]

# 表示"还没想清楚交付时间"的说法，预售页里出现就是硬伤
VAGUE_DATE = ["即将推出", "敬请期待", "Coming Soon", "coming soon", "马上上线", "不日上线"]

# 无信息量的 CTA 文案
WEAK_CTA = ["了解更多", "Learn more", "点击这里", "Click here", "提交", "Submit"]

PAY_HOSTS = [
    "buy.stripe.com",
    "checkout.stripe.com",
    "gumroad.com",
    "lemonsqueezy.com",
    "paddle.com",
    "paypal.me",
    "checkout.",
]


def strip_tags(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    return html


def text_of(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", strip_tags(html))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--demo-brand", default="AutoBrief",
                    help="模板自带示例品牌名，用于检测漏改")
    args = ap.parse_args()

    p = Path(args.page)
    if not p.exists():
        print(f"FAIL  文件不存在: {p}")
        return 1
    src = p.read_text(encoding="utf-8")
    body = strip_tags(src)
    text = text_of(src)

    fails: list[str] = []
    warns: list[str] = []
    oks: list[str] = []

    # ---------- 硬伤 ----------
    leftovers = [w for w in PLACEHOLDERS if w in src]
    if leftovers:
        fails.append(f"占位符未替换: {', '.join(leftovers)}")
    if args.demo_brand and args.demo_brand in src:
        fails.append(f"示例品牌名 '{args.demo_brand}' 还在页面里，未替换成真实产品名")

    pay_hit = [h for h in PAY_HOSTS if h in src]
    if not pay_hit:
        fails.append("没有找到收款链接（Stripe / Gumroad / Lemon Squeezy / Paddle 任一）——"
                     "不收真钱就验不出付费意愿")
    else:
        oks.append(f"收款通道: {pay_hit[0]}")

    has_date = bool(re.search(r"20\d{2}\s*年\s*\d{1,2}\s*月", src)) \
        or bool(re.search(r"20\d{2}-\d{1,2}-\d{1,2}", src)) \
        or bool(re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+20\d{2}", src))
    if not has_date:
        fails.append("没有写死的交付日期。预售页必须出现具体年月，不能靠'即将上线'")

    for v in VAGUE_DATE:
        if v in src:
            fails.append(f"出现模糊交付表述「{v}」——改成具体日期")
            break

    has_refund = ("退" in text and ("全额" in text or "无条件" in text)) or "refund" in text.lower()
    if not has_refund:
        fails.append("没有无条件退款承诺。这一句对预售转化的影响最大")

    if not re.search(r"<h1[\s>]", src, re.I):
        fails.append("缺少 <h1>。首屏主标题是唯一的'三秒说服位'")

    if not re.search(r'name="viewport"', src, re.I):
        fails.append("缺少 viewport meta，移动端会按桌面宽度渲染")

    # ---------- 建议 ----------
    if len(re.findall(r"<details", src, re.I)) < 3:
        warns.append("FAQ 少于 3 条。FAQ 的作用是拆掉付款前最后一道犹豫")

    if not re.search(r"(已有\s*\d|人预订|人在等|waitlist|已加入)", text):
        warns.append("缺少微证（已有 N 人预订 / 有人在等）。没有社会证明时可用名额进度代替")

    if not re.search(r"(track\(|dataLayer|plausible|umami|gtag)", src):
        warns.append("没有埋点。至少需要：滚动深度、CTA 点击、价格区曝光")

    if not re.search(r"<img", src, re.I):
        warns.append("页面里没有 <img>。若首屏产品图是 CSS 画的示意，上线前建议换成真实截图或设计稿")

    # CTA 文案只看 <a> / <button> 的可见文字，避免正文里出现同词导致误报
    cta_texts = []
    for tag in re.findall(r"<(?:a|button)\b[^>]*>(.*?)</(?:a|button)>", body, re.S | re.I):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", tag)).strip()
        if t:
            cta_texts.append(t)
    for w in WEAK_CTA:
        if any(w == t or (len(t) <= 6 and w in t) for t in cta_texts):
            warns.append(f"CTA 文案「{w}」没有信息量，改成动词 + 明确结果（如「预订创始名额 · $49」）")
            break
    if cta_texts:
        oks.append(f"CTA 文案 {len(cta_texts)} 处，示例：「{cta_texts[0][:22]}」")

    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S | re.I)
    if m:
        h1 = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if len(h1) > 40:
            warns.append(f"H1 偏长（{len(h1)} 字）：「{h1[:30]}…」——建议压到 20 字内，只留'给谁+解决什么+变成什么'")
        else:
            oks.append(f"H1: {h1}")

    # ---------- 输出 ----------
    print(f"\n自检：{p.name}\n" + "=" * 52)
    for o in oks:
        print(f"  OK    {o}")
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    print("=" * 52)
    print(f"结果：{len(oks)} 通过 / {len(warns)} 建议 / {len(fails)} 硬伤\n")
    if fails:
        print("存在硬伤，先改完再上线。其余模块规范见 references/framework.md 第六、七节。")
        return 1
    print("可上线。上线后按本次会话定下的样本门槛（单版 ≥500 独立访客）再下结论。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
