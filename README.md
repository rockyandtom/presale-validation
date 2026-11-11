# presale-validation

A Skill for deciding whether a product idea should be validated by preselling: put up a landing page while the product does not exist, see whether anyone actually pays, and only then decide whether to build it.

This repository holds the decision framework, a single-file HTML landing-page template, and a dependency-free self-check script. `SKILL.md` — the rule source — is kept in its original Chinese; this README is the English guide to the package.

## Background

The question "should we build this?" is usually answered by opinion, enthusiasm, or a waitlist that costs the subscriber nothing. This Skill replaces that with a signal someone paid for. The core action is deliberately narrow: open a page that collects money before the product exists, and observe what happens.

Two confusions make most pre-sale attempts worthless, and the methodology is built around separating them. The first is treating three different questions as one: whether anyone needs it (demand), whether anyone will pay for it (willingness to pay), and whether anyone keeps using it (retention). Only the first two can be tested before launch; retention has no shortcut and requires two or three months with a real product. A waitlist cannot prove willingness to pay, and asking people whether they would buy is not evidence either.

The second confusion is about whether preselling is even appropriate. A presale page contains only text, images and maybe a thirty-second recording, so the visitor has to complete the value judgement in their imagination. Every criterion in the framework reduces to that single question: **can the value be perceived without the product?** Ideas whose value only appears during use, that need network effects, that require trust endorsements, or that depend on accumulated data will produce misleading results no matter how good the page is.

The Skill also exists because "we got some sign-ups" is not a decision rule. It defines both the pass threshold and the kill process in advance, so the result of the test cannot be reinterpreted after the fact.

## What it does

1. Splits validation into three tiers — demand, willingness to pay, retention — and forbids building a presale page for the wrong tier.
2. Provides nine fit criteria derived from one principle (perceived value without the product), covering a one-sentence value proposition, a known and actively described problem, a reachable audience, a short decision chain, an appropriate price band, asynchronous delivery with a two-to-eight-week buffer, an existing paid alternative, imaginable and comparable outcomes, and a single payment that covers the cost of the test.
3. Lists eight red flags, including value that exists only in use, network effects, required trust endorsements, large procurement, dependence on accumulated data, no distribution channel, low-priced one-off tools, and platforms that disallow preselling.
4. Grades four ways to collect payment and defines an eleven-section page structure.
5. Ships a single dependency-free HTML template that can be edited directly.
6. Ships a checker that separates hard failures from suggestions, plus a sample-size threshold and a kill process.

## When to use it

Use it when someone has a product idea and wants to know whether it deserves development, when building a presale / waitlist / coming-soon page, when asked how to validate demand, when diagnosing a page that converts poorly, or when evaluating whether someone else's case study can be copied.

It is not for a finished product about to launch, for a pure marketing page, or for optimising pricing on a product that already has paying users.

## Repository contents

- `SKILL.md` — the workflow (Chinese): tier separation, fit criteria, red flags, payment methods, page structure, thresholds and the kill process.
- `references/framework.md` — the full decision framework, including the nine criteria, eight red flags, payment grading and the eleven page modules.
- `assets/landing-presale-template.html` — one standalone HTML file with eleven sections, no build step and no external dependencies.
- `scripts/check_landing.py` — pre-publication self-check.

## How to use

1. Decide which tier is actually being validated. If the question is only "does anyone need this", build a waitlist or a fake-door button instead of a presale page; do not spend the test on the wrong signal.
2. Run the fit judgement in `references/framework.md`. Apply the single principle first, then the nine criteria, then the eight red flags. If a red flag is present, stop — a page cannot fix it.
3. Copy the template into your project and fill every placeholder:

```bash
cp assets/landing-presale-template.html ./index.html
```

4. Before publishing, run the self-check:

```bash
python3 scripts/check_landing.py index.html
python3 scripts/check_landing.py index.html --demo-brand AutoBrief
```

Hard failures include unfilled placeholders, a payment link without a stated delivery date, no refund promise and no CTA that leads to payment. Warnings cover missing micro-evidence, too few FAQ entries, an uninformative CTA and an overlong H1.

Exit code `0` means publishable (possibly with warnings); `1` means hard failures must be fixed first. The checker's closing output also reminds you to apply a pre-agreed sample threshold before drawing any conclusion from the live test; the example it prints is 500 unique visitors per variant.

5. Choose and wire a real payment method yourself. The workflow grades the options but does not bundle a provider.

## Requirements

- Python 3, standard library only, for `scripts/check_landing.py`.
- The HTML template needs no framework, CDN, build step or backend to be edited.

## Scope and limitations

- `SKILL.md` and `references/framework.md` are in Chinese. This README is the English entry point, not a translation.
- No external API, payment account or credential is bundled. Collecting real money is a decision the workflow deliberately leaves to the user.
- The checker validates page structure, not market demand. A clean report is a prerequisite for publishing, not evidence that the idea is good.

## Origin

Extracted from a personal WorkBuddy skill library and cleaned for public release: machine-specific absolute paths were replaced with portable ones, backup and build artifacts were excluded, and no credentials are included.
