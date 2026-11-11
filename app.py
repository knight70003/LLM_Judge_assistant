import json
from pathlib import Path
import subprocess
import sys
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LLM Judge Dashboard")

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEST_SUITE_PATH = BASE_DIR / "test_suite.json"
REPORT_PATH = BASE_DIR / "reports" / "report.json"

# Simple User Request Schema (No manual ID/Model Output needed)
class QuickTestCaseRequest(BaseModel):
    input: str
    system_prompt: str = "Answer accurately."


# NOTE: HTML is a *raw* string (r"""...""") so JavaScript backslashes and
# template literals (${...}) are passed to the browser untouched. It is NOT an
# f-string, so braces in CSS/JS need no escaping.
HTML = r"""
<!DOCTYPE html>
<html lang="en" data-theme="dark">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark light">
<title>LLM Judge | AI Evaluation &amp; Quality Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

<script>
/* Apply the saved theme before first paint to avoid a flash. */
(function () {
    var t = null;
    try { t = localStorage.getItem("llmjudge-theme"); } catch (e) {}
    if (t !== "light" && t !== "dark") {
        t = (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) ? "light" : "dark";
    }
    document.documentElement.setAttribute("data-theme", t);
})();
</script>

<style>
/* ---------- Design tokens ---------- */
:root {
    --font-ui: 'Plus Jakarta Sans', Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

    --blue: #4F8BFF;
    --violet: #8B6CFF;
    --cyan: #22D3EE;
    --green: #34D399;
    --amber: #FBBF24;
    --red: #F87171;

    --r-lg: 22px;
    --r-md: 14px;
    --r-sm: 10px;
    --ease: cubic-bezier(.2, .8, .2, 1);
}

[data-theme="dark"] {
    --bg: #070B16;
    --bg-2: #0B1224;
    --panel: rgba(16, 23, 42, .62);
    --panel-solid: #0F172A;
    --panel-hover: rgba(22, 32, 58, .8);
    --field: rgba(4, 8, 18, .72);
    --line: rgba(148, 163, 255, .14);
    --line-strong: rgba(148, 163, 255, .28);
    --text: #E8ECF8;
    --text-2: #9AA6C4;
    --text-3: #66718F;
    --shadow: 0 10px 40px -12px rgba(0, 0, 0, .6);
    --shadow-hover: 0 22px 50px -14px rgba(79, 139, 255, .35);
    --g1: rgba(79, 139, 255, .75);
    --g2: rgba(139, 108, 255, .65);
    --glow-a: rgba(79, 139, 255, .22);
    --glow-b: rgba(139, 108, 255, .2);
    --glow-c: rgba(34, 211, 238, .14);
    --term-bg: #050810;
    --term-text: #C7D2FE;
    --term-bar: rgba(255, 255, 255, .04);
    --ok: #34D399; --warn: #FBBF24; --err: #F87171;
    --key: #7DD3FC; --str: #A5B4FC; --num: #FCA5A5; --bool: #C4B5FD;
}

[data-theme="light"] {
    --bg: #F3F5FB;
    --bg-2: #E9EDF8;
    --panel: rgba(255, 255, 255, .72);
    --panel-solid: #FFFFFF;
    --panel-hover: rgba(255, 255, 255, .95);
    --field: rgba(255, 255, 255, .9);
    --line: rgba(60, 80, 150, .14);
    --line-strong: rgba(60, 80, 150, .3);
    --text: #12172B;
    --text-2: #4A5578;
    --text-3: #7A85A6;
    --shadow: 0 10px 30px -14px rgba(40, 60, 130, .25);
    --shadow-hover: 0 20px 44px -16px rgba(60, 90, 220, .35);
    --g1: rgba(59, 110, 240, .55);
    --g2: rgba(124, 92, 240, .5);
    --glow-a: rgba(79, 139, 255, .18);
    --glow-b: rgba(139, 108, 255, .14);
    --glow-c: rgba(34, 211, 238, .12);
    --term-bg: #0E1326;
    --term-text: #C7D2FE;
    --term-bar: rgba(255, 255, 255, .05);
    --ok: #34D399; --warn: #FBBF24; --err: #F87171;
    --key: #7DD3FC; --str: #A5B4FC; --num: #FCA5A5; --bool: #C4B5FD;
}

/* ---------- Base ---------- */
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 96px; }
body {
    font-family: var(--font-ui);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
}
.theme-anim, .theme-anim * {
    transition: background-color .4s ease, color .4s ease, border-color .4s ease, box-shadow .4s ease !important;
}
button { font-family: inherit; color: inherit; }
i[data-lucide], svg.lucide { width: 18px; height: 18px; flex: none; stroke-width: 2; }
:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }

/* ---------- Ambient background ---------- */
.ambient { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; }
.ambient::after {
    content: ""; position: absolute; inset: 0;
    background-image: radial-gradient(circle at 1px 1px, var(--line) 1px, transparent 0);
    background-size: 36px 36px;
    mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
    opacity: .7;
}
.orb { position: absolute; border-radius: 50%; filter: blur(90px); will-change: transform; }
.orb.a { width: 520px; height: 520px; background: var(--glow-a); top: -160px; left: -120px; animation: drift 22s ease-in-out infinite alternate; }
.orb.b { width: 460px; height: 460px; background: var(--glow-b); bottom: -140px; right: -100px; animation: drift 26s ease-in-out infinite alternate-reverse; }
.orb.c { width: 340px; height: 340px; background: var(--glow-c); top: 40%; left: 55%; animation: drift 30s ease-in-out infinite alternate; }
@keyframes drift { from { transform: translate3d(0, 0, 0) scale(1); } to { transform: translate3d(60px, 40px, 0) scale(1.15); } }

/* ---------- Layout ---------- */
.shell { position: relative; z-index: 1; width: 92%; max-width: 1360px; margin: 0 auto; padding: 0 0 56px; }
section { margin-top: 28px; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.section-head h2 { font-size: 15px; font-weight: 700; letter-spacing: .01em; display: flex; align-items: center; gap: 10px; }
.section-head p { font-size: 13px; color: var(--text-2); }

/* ---------- Glass + gradient border ---------- */
.glass {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--r-lg);
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    box-shadow: var(--shadow);
}
.glass::before {
    content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1px;
    background: linear-gradient(135deg, var(--g1), transparent 38%, transparent 62%, var(--g2));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    pointer-events: none; opacity: .55; transition: opacity .3s ease;
}
.glass:hover::before { opacity: 1; }

/* ---------- Header ---------- */
.topbar {
    position: sticky; top: 0; z-index: 50;
    margin: 0 -4vw; padding: 14px 4vw 12px;
    background: linear-gradient(to bottom, var(--bg) 40%, transparent);
}
.topbar-inner {
    display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
    padding: 12px 16px; border-radius: 18px;
}
.brand { display: flex; align-items: center; gap: 14px; min-width: 0; }
.logo-mark {
    width: 44px; height: 44px; border-radius: 13px; flex: none;
    display: grid; place-items: center; color: #fff;
    background: linear-gradient(135deg, var(--blue), var(--violet) 60%, var(--cyan));
    box-shadow: 0 8px 24px -6px rgba(99, 102, 241, .7), inset 0 1px 0 rgba(255, 255, 255, .35);
}
.logo-mark i, .logo-mark svg { width: 24px; height: 24px; }
.brand-name { font-size: 20px; font-weight: 800; letter-spacing: -.02em; }
.brand-name span { background: linear-gradient(120deg, var(--cyan), var(--blue) 45%, var(--violet)); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { font-size: 12.5px; color: var(--text-2); font-weight: 500; }

.nav { display: flex; gap: 4px; padding: 4px; border-radius: 12px; background: var(--field); border: 1px solid var(--line); }
.nav a {
    display: flex; align-items: center; gap: 7px; padding: 7px 12px; border-radius: 9px;
    font-size: 13px; font-weight: 600; color: var(--text-2); text-decoration: none; transition: all .2s ease; white-space: nowrap;
}
.nav a i, .nav a svg { width: 15px; height: 15px; }
.nav a:hover { color: var(--text); background: var(--panel-hover); }

.top-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.pill {
    display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px;
    font-size: 12px; font-weight: 600; color: var(--text-2);
    background: var(--field); border: 1px solid var(--line); white-space: nowrap;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-3); flex: none; }
.dot.ok { background: var(--green); box-shadow: 0 0 0 0 rgba(52, 211, 153, .6); animation: ping 2.2s infinite; }
.dot.bad { background: var(--red); }
.dot.run { background: var(--cyan); animation: ping-c 1.1s infinite; }
.dot.done { background: var(--green); }
@keyframes ping { 70% { box-shadow: 0 0 0 7px rgba(52, 211, 153, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); } }
@keyframes ping-c { 0% { box-shadow: 0 0 0 0 rgba(34, 211, 238, .7); } 70% { box-shadow: 0 0 0 7px rgba(34, 211, 238, 0); } 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); } }

.icon-btn {
    width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; cursor: pointer;
    background: var(--field); border: 1px solid var(--line); color: var(--text-2); transition: all .2s ease;
}
.icon-btn:hover { color: var(--text); border-color: var(--line-strong); transform: translateY(-1px); }
.icon-btn:active { transform: scale(.94); }
.theme-toggle .moon { display: none; }
[data-theme="light"] .theme-toggle .sun { display: none; }
[data-theme="light"] .theme-toggle .moon { display: block; }
.theme-toggle .sun, .theme-toggle .moon { width: 18px; height: 18px; }

/* ---------- Metric cards ---------- */
.cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.card {
    padding: 22px; transition: transform .3s var(--ease), box-shadow .3s ease, background .3s ease; overflow: hidden;
}
.card:hover { transform: translateY(-5px); box-shadow: var(--shadow-hover); background: var(--panel-hover); }
.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.card-label { font-size: 13px; font-weight: 600; color: var(--text-2); }
.card-icon { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; color: var(--c); background: color-mix(in srgb, var(--c) 15%, transparent); border: 1px solid color-mix(in srgb, var(--c) 30%, transparent); }
.card[data-c="blue"] { --c: var(--blue); }
.card[data-c="green"] { --c: var(--green); }
.card[data-c="violet"] { --c: var(--violet); }
.card[data-c="cyan"] { --c: var(--cyan); }
.metric { font-size: 38px; font-weight: 800; letter-spacing: -.03em; line-height: 1.1; font-variant-numeric: tabular-nums; }
.metric-sub { font-size: 12px; color: var(--text-3); margin-top: 6px; min-height: 18px; }
.meter { margin-top: 16px; height: 6px; border-radius: 99px; background: var(--line); overflow: hidden; position: relative; }
.meter > i { display: block; height: 100%; width: 0; border-radius: inherit; background: linear-gradient(90deg, var(--c), color-mix(in srgb, var(--c) 40%, #fff)); transition: width .9s var(--ease); }
.meter.indeterminate > i { width: 40%; animation: slide 1.2s ease-in-out infinite; }
@keyframes slide { 0% { transform: translateX(-110%); } 100% { transform: translateX(280%); } }
#status.is-error { color: var(--red); }
#status.is-done { color: var(--green); }
#status.is-run { color: var(--cyan); }

/* ---------- Control center ---------- */
.actions { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.btn {
    --c1: var(--blue); --c2: var(--violet);
    position: relative; overflow: hidden; isolation: isolate;
    display: flex; align-items: center; gap: 14px; text-align: left; width: 100%;
    padding: 16px 18px; border-radius: var(--r-md); cursor: pointer; border: 1px solid rgba(255, 255, 255, .16);
    color: #fff; background: linear-gradient(135deg, var(--c1), var(--c2));
    box-shadow: 0 12px 28px -14px var(--c1), inset 0 1px 0 rgba(255, 255, 255, .25);
    transition: transform .25s var(--ease), box-shadow .25s ease, filter .25s ease, opacity .2s ease;
}
.btn::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(120deg, transparent 30%, rgba(255, 255, 255, .22) 50%, transparent 70%); transform: translateX(-120%); transition: transform .7s ease; }
.btn:hover:not(:disabled)::after { transform: translateX(120%); }
.btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 18px 34px -12px var(--c1), inset 0 1px 0 rgba(255, 255, 255, .3); }
.btn:active:not(:disabled) { transform: translateY(0) scale(.97); }
.btn:disabled { cursor: not-allowed; opacity: .5; filter: saturate(.6); }
.btn.is-loading:disabled { opacity: 1; filter: none; cursor: progress; }
.btn.eval { --c1: #2F6BFF; --c2: #5B7CFF; }
.btn.pair { --c1: #0891B2; --c2: #22D3EE; }
.btn.analysis { --c1: #7C3AED; --c2: #A78BFA; }
.btn.report { --c1: #334155; --c2: #64748B; }
[data-theme="dark"] .btn.report { --c1: #1E293B; --c2: #475569; }
.btn-ico { width: 42px; height: 42px; border-radius: 12px; display: grid; place-items: center; flex: none; background: rgba(255, 255, 255, .18); }
.btn-ico i, .btn-ico svg { width: 20px; height: 20px; }
.btn-text { display: flex; flex-direction: column; min-width: 0; }
.btn-title { font-weight: 700; font-size: 14.5px; }
.btn-desc { font-size: 12px; opacity: .8; }
.spinner { width: 20px; height: 20px; border-radius: 50%; border: 2.5px solid rgba(255, 255, 255, .35); border-top-color: #fff; animation: spin .7s linear infinite; display: none; }
.btn.is-loading .spinner { display: block; }
.btn.is-loading .btn-ico > i, .btn.is-loading .btn-ico > svg { display: none; }
@keyframes spin { to { transform: rotate(360deg); } }
.ripple { position: absolute; border-radius: 50%; background: rgba(255, 255, 255, .4); transform: scale(0); animation: ripple .6s ease-out forwards; pointer-events: none; }
@keyframes ripple { to { transform: scale(4); opacity: 0; } }

.btn-submit { justify-content: center; padding: 14px 20px; font-weight: 700; font-size: 14px; --c1: #2F6BFF; --c2: #8B6CFF; }
.btn-submit .spinner { width: 18px; height: 18px; }
.btn-submit.is-loading i, .btn-submit.is-loading svg { display: none; }

/* ---------- Workspace ---------- */
.workspace { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr); gap: 22px; align-items: stretch; }
.panel { padding: 24px; display: flex; flex-direction: column; min-width: 0; }
.panel-title { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.panel-desc { font-size: 13px; color: var(--text-2); margin: 4px 0 18px; }
.field { margin-bottom: 16px; }
.field-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 7px; gap: 8px; }
.field label { font-size: 13px; font-weight: 600; }
.counter { font-size: 11.5px; color: var(--text-3); font-variant-numeric: tabular-nums; }
.counter.warn { color: var(--amber); }
.counter.max { color: var(--red); }
.control {
    width: 100%; padding: 13px 14px; border-radius: var(--r-sm); font: inherit; font-size: 14px; color: var(--text);
    background: var(--field); border: 1px solid var(--line); resize: vertical; transition: border-color .2s ease, box-shadow .2s ease;
}
.control::placeholder { color: var(--text-3); }
.control:hover { border-color: var(--line-strong); }
.control:focus { outline: none; border-color: var(--blue); box-shadow: 0 0 0 4px color-mix(in srgb, var(--blue) 22%, transparent); }
.control.invalid { border-color: var(--red); box-shadow: 0 0 0 4px color-mix(in srgb, var(--red) 18%, transparent); }
textarea.control { min-height: 130px; line-height: 1.55; }
textarea.control.sys { min-height: 76px; font-family: var(--font-mono); font-size: 12.5px; }
.help { font-size: 12px; color: var(--text-3); margin-top: 6px; }
.help.error { color: var(--red); }
.kbd { font-family: var(--font-mono); font-size: 11px; padding: 1px 6px; border-radius: 5px; background: var(--field); border: 1px solid var(--line); }

/* ---------- Terminal ---------- */
.terminal { display: flex; flex-direction: column; flex: 1; min-height: 420px; border-radius: var(--r-md); overflow: hidden; background: var(--term-bg); border: 1px solid rgba(148, 163, 255, .16); box-shadow: inset 0 0 60px rgba(79, 139, 255, .05); }
.term-bar { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: var(--term-bar); border-bottom: 1px solid rgba(148, 163, 255, .12); flex-wrap: wrap; }
.lights { display: flex; gap: 6px; }
.lights span { width: 11px; height: 11px; border-radius: 50%; }
.lights span:nth-child(1) { background: #FF5F57; } .lights span:nth-child(2) { background: #FEBC2E; } .lights span:nth-child(3) { background: #28C840; }
.term-title { font-family: var(--font-mono); font-size: 12px; color: #8E9ABF; flex: 1; min-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.term-tools { display: flex; gap: 6px; }
.term-btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; font-size: 12px; font-weight: 600; border-radius: 8px; cursor: pointer; color: #AAB4D6; background: rgba(255, 255, 255, .05); border: 1px solid rgba(148, 163, 255, .16); transition: all .2s ease; }
.term-btn i, .term-btn svg { width: 14px; height: 14px; }
.term-btn:hover { color: #fff; background: rgba(255, 255, 255, .1); }
.term-btn:active { transform: scale(.95); }
.console { flex: 1; min-height: 0; max-height: 440px; overflow: auto; padding: 16px 18px; font-family: var(--font-mono); font-size: 12.5px; line-height: 1.7; color: var(--term-text); white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; }
.console .ln { display: block; }
.console .ln.ok { color: var(--ok); } .console .ln.warn { color: var(--warn); } .console .ln.err { color: var(--err); }
.console .ln.sys { color: #6B7699; }
.console .j-key { color: var(--key); } .console .j-str { color: var(--str); } .console .j-num { color: var(--num); } .console .j-bool { color: var(--bool); }
.console .cursor { display: inline-block; width: 8px; height: 15px; background: var(--cyan); vertical-align: -2px; margin-left: 4px; animation: blink 1s steps(2) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.empty-term { height: 100%; min-height: 220px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; text-align: center; color: #6B7699; white-space: normal; font-family: var(--font-ui); }
.empty-term i, .empty-term svg { width: 30px; height: 30px; opacity: .7; }
.empty-term b { color: #AAB4D6; font-size: 14px; }
.empty-term span { font-size: 12.5px; max-width: 280px; }
.term-foot { display: flex; align-items: center; gap: 10px; padding: 9px 14px; font-family: var(--font-mono); font-size: 11.5px; color: #8E9ABF; border-top: 1px solid rgba(148, 163, 255, .12); background: var(--term-bar); }
.term-foot .grow { flex: 1; }

/* ---------- Test suite ---------- */
.suite-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); gap: 14px; max-height: 520px; overflow-y: auto; padding: 4px 6px 6px 2px; align-items: start; }
.tc { background: var(--field); border: 1px solid var(--line); border-radius: var(--r-md); padding: 14px; transition: border-color .25s ease, transform .25s var(--ease), box-shadow .25s ease; }
.tc:hover { border-color: var(--line-strong); transform: translateY(-2px); box-shadow: var(--shadow); }
.tc-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 10px; }
.badge { font-family: var(--font-mono); font-size: 12px; font-weight: 600; padding: 3px 9px; border-radius: 7px; color: var(--cyan); background: color-mix(in srgb, var(--cyan) 13%, transparent); border: 1px solid color-mix(in srgb, var(--cyan) 28%, transparent); }
.tag { font-size: 11px; font-weight: 600; color: var(--green); display: inline-flex; align-items: center; gap: 5px; }
.tc-label { font-size: 11.5px; font-weight: 700; color: var(--text-3); margin: 8px 0 3px; }
.tc-text { font-size: 13px; color: var(--text-2); overflow-wrap: anywhere; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.tc.open .tc-text { display: block; -webkit-line-clamp: unset; }
.tc-extra { display: none; }
.tc.open .tc-extra { display: block; animation: reveal .3s var(--ease); }
@keyframes reveal { from { opacity: 0; transform: translateY(-4px); } }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.chip { font-size: 11px; padding: 2px 8px; border-radius: 99px; color: var(--text-2); border: 1px solid var(--line); background: var(--panel); }
.tc-toggle { margin-top: 12px; display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: var(--blue); background: none; border: none; cursor: pointer; padding: 2px 0; }
.tc-toggle i, .tc-toggle svg { width: 14px; height: 14px; transition: transform .25s ease; }
.tc.open .tc-toggle i, .tc.open .tc-toggle svg { transform: rotate(180deg); }
.empty { grid-column: 1 / -1; text-align: center; padding: 40px 16px; color: var(--text-2); display: flex; flex-direction: column; align-items: center; gap: 8px; border: 1px dashed var(--line-strong); border-radius: var(--r-md); }
.empty i, .empty svg { width: 32px; height: 32px; color: var(--text-3); }
.empty b { color: var(--text); font-size: 14px; }
.empty span { font-size: 13px; }

.skeleton { border-radius: var(--r-md); height: 120px; background: linear-gradient(100deg, var(--field) 30%, var(--line) 50%, var(--field) 70%); background-size: 220% 100%; animation: shimmer 1.4s linear infinite; border: 1px solid var(--line); }
@keyframes shimmer { to { background-position: -220% 0; } }

/* ---------- Toasts ---------- */
.toasts { position: fixed; z-index: 100; right: 20px; bottom: 20px; display: flex; flex-direction: column; gap: 10px; width: min(380px, calc(100vw - 32px)); }
.toast {
    display: flex; gap: 12px; align-items: flex-start; padding: 13px 14px; border-radius: 14px; font-size: 13px;
    background: var(--panel-solid); border: 1px solid var(--line-strong); box-shadow: 0 18px 40px -12px rgba(0, 0, 0, .5);
    border-left: 3px solid var(--c, var(--blue)); animation: toast-in .35s var(--ease);
}
.toast.success { --c: var(--green); } .toast.error { --c: var(--red); } .toast.info { --c: var(--blue); }
.toast i, .toast svg { color: var(--c); margin-top: 1px; }
.toast .t-body { flex: 1; overflow-wrap: anywhere; }
.toast .t-body b { display: block; font-size: 13px; }
.toast .t-body span { color: var(--text-2); }
.toast.leaving { animation: toast-out .3s ease forwards; }
@keyframes toast-in { from { opacity: 0; transform: translateX(24px) scale(.96); } }
@keyframes toast-out { to { opacity: 0; transform: translateX(24px) scale(.96); } }

/* ---------- Scrollbars ---------- */
* { scrollbar-width: thin; scrollbar-color: var(--line-strong) transparent; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 99px; border: 2px solid transparent; background-clip: content-box; }
::-webkit-scrollbar-thumb:hover { background: var(--blue); background-clip: content-box; }

/* ---------- Entrance (single orchestrated moment) ---------- */
.enter { animation: enter .7s var(--ease) both; animation-delay: calc(var(--i, 0) * 70ms); }
@keyframes enter { from { opacity: 0; transform: translateY(14px); } }

/* ---------- Responsive ---------- */
@media (max-width: 1180px) {
    .cards, .actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 992px) {
    .workspace { grid-template-columns: minmax(0, 1fr); }
    .nav { order: 3; width: 100%; overflow-x: auto; }
    .topbar-inner { gap: 12px; }
}
@media (max-width: 600px) {
    .shell { width: 94%; }
    .cards, .actions { grid-template-columns: minmax(0, 1fr); }
    .metric { font-size: 32px; }
    .subtitle { font-size: 11.5px; }
    .top-actions { width: 100%; justify-content: space-between; }
    .panel { padding: 18px; }
    .term-title { display: none; }
    .toasts { right: 16px; bottom: 16px; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .001ms !important; animation-iteration-count: 1 !important; transition-duration: .001ms !important; scroll-behavior: auto !important; }
    .orb { display: none; }
    .spinner { animation-duration: 1.2s !important; animation-iteration-count: infinite !important; }
}
</style>
</head>

<body>

<div class="ambient" aria-hidden="true"><div class="orb a"></div><div class="orb b"></div><div class="orb c"></div></div>

<div class="shell">

<!-- ===== Header ===== -->
<header class="topbar">
    <div class="topbar-inner glass enter" style="--i:0">
        <div class="brand">
            <div class="logo-mark"><i data-lucide="scale"></i></div>
            <div>
                <div class="brand-name">LLM <span>Judge</span></div>
                <div class="subtitle">AI Evaluation &amp; Quality Intelligence Platform</div>
            </div>
        </div>

        <nav class="nav" aria-label="Sections">
            <a href="#overview"><i data-lucide="layout-dashboard"></i>Overview</a>
            <a href="#control"><i data-lucide="sliders-horizontal"></i>Control</a>
            <a href="#workspace"><i data-lucide="flask-conical"></i>Workspace</a>
            <a href="#suite"><i data-lucide="list-checks"></i>Test suite</a>
        </nav>

        <div class="top-actions">
            <span class="pill" id="connPill" title="Backend health (GET /health)"><span class="dot" id="connDot"></span><span id="connText">Checking…</span></span>
            <span class="pill" title="Current evaluation status"><span class="dot" id="runDot"></span><span id="runText">Idle</span></span>
            <button class="icon-btn theme-toggle" id="themeBtn" type="button" aria-label="Toggle light and dark theme" title="Toggle theme">
                <i data-lucide="sun" class="sun"></i><i data-lucide="moon" class="moon"></i>
            </button>
        </div>
    </div>
</header>

<!-- ===== Analytics overview ===== -->
<section id="overview" aria-labelledby="h-overview">
    <div class="section-head enter" style="--i:1">
        <h2 id="h-overview"><i data-lucide="bar-chart-3"></i>Analytics overview</h2>
        <p>Live metrics from the latest evaluation report.</p>
    </div>
    <div class="cards">
        <article class="card glass enter" data-c="blue" style="--i:2">
            <div class="card-top"><span class="card-label">Total Test Cases</span><span class="card-icon"><i data-lucide="layers"></i></span></div>
            <div class="metric" id="cases">0</div>
            <div class="metric-sub">Cases in your test suite</div>
            <div class="meter"><i id="casesBar"></i></div>
        </article>
        <article class="card glass enter" data-c="green" style="--i:3">
            <div class="card-top"><span class="card-label">Pass Rate</span><span class="card-icon"><i data-lucide="shield-check"></i></span></div>
            <div class="metric" id="passrate">0%</div>
            <div class="metric-sub">Cases that met the judge criteria</div>
            <div class="meter"><i id="passBar"></i></div>
        </article>
        <article class="card glass enter" data-c="violet" style="--i:4">
            <div class="card-top"><span class="card-label">Mean Evaluation Score</span><span class="card-icon"><i data-lucide="gauge"></i></span></div>
            <div class="metric" id="meanscore">0</div>
            <div class="metric-sub">Average judge score across cases</div>
            <div class="meter"><i id="scoreBar"></i></div>
        </article>
        <article class="card glass enter" data-c="cyan" style="--i:5">
            <div class="card-top"><span class="card-label">Execution Status</span><span class="card-icon"><i data-lucide="activity"></i></span></div>
            <div class="metric" id="status" style="font-size:30px">Idle</div>
            <div class="metric-sub" id="statusSub">Ready for the next run</div>
            <div class="meter" id="statusMeter"><i></i></div>
        </article>
    </div>
</section>

<!-- ===== Evaluation control center ===== -->
<section id="control" aria-labelledby="h-control">
    <div class="section-head enter" style="--i:6">
        <h2 id="h-control"><i data-lucide="rocket"></i>Evaluation control center</h2>
        <p>One operation runs at a time. Controls unlock when it finishes.</p>
    </div>
    <div class="actions">
        <button class="btn eval enter" style="--i:7" type="button" id="btnEval" data-op="evaluation">
            <span class="btn-ico"><i data-lucide="play"></i><span class="spinner"></span></span>
            <span class="btn-text"><span class="btn-title">Run Evaluation</span><span class="btn-desc">Score every case with the judge</span></span>
        </button>
        <button class="btn pair enter" style="--i:8" type="button" id="btnPair" data-op="pairwise">
            <span class="btn-ico"><i data-lucide="git-compare"></i><span class="spinner"></span></span>
            <span class="btn-text"><span class="btn-title">Run Pairwise Evaluation</span><span class="btn-desc">Compare responses head to head</span></span>
        </button>
        <button class="btn analysis enter" style="--i:9" type="button" id="btnAnalysis" data-op="analysis">
            <span class="btn-ico"><i data-lucide="line-chart"></i><span class="spinner"></span></span>
            <span class="btn-text"><span class="btn-title">Run Analysis</span><span class="btn-desc">Summarise results and trends</span></span>
        </button>
        <button class="btn report enter" style="--i:10" type="button" id="btnReport" data-op="report">
            <span class="btn-ico"><i data-lucide="file-text"></i><span class="spinner"></span></span>
            <span class="btn-text"><span class="btn-title">View Report</span><span class="btn-desc">Load report.json into the console</span></span>
        </button>
    </div>
</section>

<!-- ===== Workspace: create test case + console ===== -->
<section id="workspace" aria-labelledby="h-workspace">
    <div class="section-head enter" style="--i:11">
        <h2 id="h-workspace"><i data-lucide="flask-conical"></i>Workspace</h2>
    </div>
    <div class="workspace">
        <div class="panel glass enter" style="--i:12">
            <div class="panel-title"><i data-lucide="plus-circle"></i>Add prompt to test suite</div>
            <p class="panel-desc">Write the prompt you want to evaluate. An ID and a starter model output are generated for you.</p>

            <form id="tcForm" novalidate>
                <div class="field">
                    <div class="field-head"><label for="tc_input">User prompt</label><span class="counter" id="inputCount">0 / 2000</span></div>
                    <textarea id="tc_input" class="control" maxlength="2000" required placeholder="e.g. What is data drift in machine learning, and how do you detect it?"></textarea>
                    <div class="help" id="inputHelp">The question or task the model will answer. <span class="kbd">Ctrl</span> + <span class="kbd">Enter</span> saves.</div>
                </div>
                <div class="field">
                    <div class="field-head"><label for="tc_sys">System prompt</label><span class="counter" id="sysCount">0 / 500</span></div>
                    <textarea id="tc_sys" class="control sys" maxlength="500" placeholder="Answer accurately.">Answer accurately.</textarea>
                    <div class="help">Instructions that set the model&rsquo;s role and tone. Leave blank to use &ldquo;Answer accurately.&rdquo;</div>
                </div>
                <button class="btn btn-submit" type="submit" id="btnSave">
                    <i data-lucide="sparkles"></i><span class="spinner"></span><span id="btnSaveText">Generate &amp; Save Test Case</span>
                </button>
            </form>
        </div>

        <div class="panel glass enter" style="--i:13">
            <div class="panel-title" style="margin-bottom:14px"><i data-lucide="terminal-square"></i>Developer console</div>
            <div class="terminal">
                <div class="term-bar">
                    <div class="lights" aria-hidden="true"><span></span><span></span><span></span></div>
                    <div class="term-title" id="termTitle">llm-judge ~ console</div>
                    <div class="term-tools">
                        <button class="term-btn" type="button" id="btnCopy" title="Copy output"><i data-lucide="copy"></i>Copy</button>
                        <button class="term-btn" type="button" id="btnClear" title="Clear console"><i data-lucide="trash-2"></i>Clear</button>
                    </div>
                </div>
                <div class="console" id="output" role="log" aria-live="polite" tabindex="0"></div>
                <div class="term-foot">
                    <span class="dot" id="termDot"></span><span id="console-status">System Ready</span>
                    <span class="grow"></span><span id="termMeta"></span>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- ===== Test suite ===== -->
<section id="suite" aria-labelledby="h-suite">
    <div class="panel glass enter" style="--i:14">
        <div class="section-head" style="margin-bottom:16px">
            <h2 id="h-suite"><i data-lucide="list-checks"></i>Test suite <span class="badge" id="suiteCount">0</span></h2>
            <button class="term-btn" type="button" id="btnRefresh" style="color:var(--text-2);border-color:var(--line);background:var(--field)"><i data-lucide="refresh-cw"></i>Refresh</button>
        </div>
        <div class="suite-list" id="testSuiteList" aria-live="polite"></div>
    </div>
</section>

</div>

<div class="toasts" id="toasts" role="status" aria-live="polite"></div>

<!-- Icons: Lucide from CDN. If it fails to load, labels remain and the UI is fully usable. -->
<script src="https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js" onerror="window.__noLucide = true"></script>

<script>
"use strict";

/* ============ Helpers ============ */
const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const reduceMotion = () => window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Escape every user/model-provided string before it touches innerHTML. */
function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function refreshIcons() {
    try { if (window.lucide && typeof window.lucide.createIcons === "function") window.lucide.createIcons(); } catch (e) { /* icons are optional */ }
}

/* ============ Centralised API layer ============ */
class ApiError extends Error {
    constructor(message, status) { super(message); this.name = "ApiError"; this.status = status; }
}

async function api(path, options = {}) {
    let res;
    try {
        res = await fetch(path, options);
    } catch (err) {
        setConnection(false);
        throw new ApiError("Cannot reach the server. Check that the FastAPI app is running.", 0);
    }
    const raw = await res.text();
    let body = null;
    try { body = raw ? JSON.parse(raw) : null; } catch (e) { body = raw; }
    if (!res.ok) {
        const detail = body && typeof body === "object" ? body.detail : null;
        const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join("; ") : (detail || ("Request failed with HTTP " + res.status));
        throw new ApiError(String(msg), res.status);
    }
    setConnection(true);
    return body;
}

/* ============ Toasts ============ */
const TOAST_ICON = { success: "check-circle-2", error: "alert-triangle", info: "info" };
function toast(type, title, message, ttl = 4500) {
    const el = document.createElement("div");
    el.className = "toast " + type;
    el.innerHTML = '<i data-lucide="' + (TOAST_ICON[type] || "info") + '"></i><div class="t-body"><b>' + esc(title) + "</b>" + (message ? "<span>" + esc(message) + "</span>" : "") + "</div>";
    el.addEventListener("click", () => dismiss(el));
    $("toasts").appendChild(el);
    refreshIcons();
    setTimeout(() => dismiss(el), ttl);
}
function dismiss(el) {
    if (!el.parentNode || el.classList.contains("leaving")) return;
    el.classList.add("leaving");
    setTimeout(() => el.remove(), 300);
}

/* ============ Theme ============ */
function applyTheme(t) { document.documentElement.setAttribute("data-theme", t); }
function toggleTheme() {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.classList.add("theme-anim");
    applyTheme(next);
    try { localStorage.setItem("llmjudge-theme", next); } catch (e) { /* storage may be blocked */ }
    setTimeout(() => document.documentElement.classList.remove("theme-anim"), 500);
}

/* ============ Connection + status ============ */
function setConnection(ok) {
    $("connDot").className = "dot " + (ok ? "ok" : "bad");
    $("connText").textContent = ok ? "Connected" : "Offline";
}
async function checkHealth() {
    try {
        const res = await fetch("/health", { cache: "no-store" });
        setConnection(res.ok);
    } catch (e) { setConnection(false); }
}

const STATUS_TONE = { "Idle": "", "Running...": "run", "Generating...": "run", "Completed": "done", "Failed": "error" };
function setStatus(label, sub) {
    const tone = STATUS_TONE[label] ?? "";
    const s = $("status");
    s.textContent = label;
    s.className = "metric" + (tone ? " is-" + tone : "");
    $("statusSub").textContent = sub || "";
    $("statusMeter").classList.toggle("indeterminate", tone === "run");
    $("statusMeter").firstElementChild.style.width = tone === "done" ? "100%" : (tone === "error" ? "100%" : "0");
    $("runText").textContent = label.replace("...", "");
    $("runDot").className = "dot" + (tone === "run" ? " run" : tone === "done" ? " done" : tone === "error" ? " bad" : "");
}

/* ============ Animated numbers ============ */
function animateNumber(el, to, { decimals = 0, suffix = "" } = {}) {
    const target = Number(to);
    if (!Number.isFinite(target)) { el.textContent = String(to) + suffix; return; }
    const from = Number(el.dataset.val ?? 0);
    el.dataset.val = String(target);
    if (reduceMotion() || from === target) { el.textContent = target.toFixed(decimals) + suffix; return; }
    const t0 = performance.now(), dur = 700;
    const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (from + (target - from) * eased).toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}
function setBar(id, pct) { $(id).style.width = Math.max(0, Math.min(100, pct)) + "%"; }
function scoreToPct(score) {
    const s = Number(score) || 0;
    if (s <= 1) return s * 100;
    if (s <= 5) return (s / 5) * 100;
    if (s <= 10) return (s / 10) * 100;
    return s;
}

function updateMetrics(data) {
    if (data.total_cases !== undefined) { animateNumber($("cases"), data.total_cases ?? 0); setBar("casesBar", Math.min(100, (data.total_cases ?? 0) * 10)); }
    const pass = Number(data.pass_rate ?? 0);
    const mean = Number(data.mean_score ?? 0);
    animateNumber($("passrate"), pass, { decimals: Number.isInteger(pass) ? 0 : 1, suffix: "%" });
    animateNumber($("meanscore"), mean, { decimals: Number.isInteger(mean) ? 0 : 2 });
    setBar("passBar", pass);
    setBar("scoreBar", scoreToPct(mean));
}

/* ============ Console ============ */
const consoleState = { text: "" };

function emptyConsole() {
    consoleState.text = "";
    $("output").innerHTML = '<div class="empty-term"><i data-lucide="terminal"></i><b>Waiting for execution</b><span>Run an evaluation, pairwise comparison, analysis or open the report. Output appears here.</span></div>';
    $("termMeta").textContent = "";
    refreshIcons();
}

function classifyLine(line) {
    const l = line.toLowerCase();
    if (/(error|traceback|exception|failed|fatal)/.test(l)) return "err";
    if (/warn/.test(l)) return "warn";
    if (/(success|passed|completed|saved|done|✓)/.test(l)) return "ok";
    return "";
}

function highlightJson(escaped) {
    return escaped.replace(/(&quot;(?:[^&]|&(?!quot;))*?&quot;)(\s*:)?|\b(true|false|null)\b|(-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)/g, (m, str, colon, bool, num) => {
        if (str) return '<span class="' + (colon ? "j-key" : "j-str") + '">' + str + "</span>" + (colon || "");
        if (bool) return '<span class="j-bool">' + bool + "</span>";
        if (num) return '<span class="j-num">' + num + "</span>";
        return m;
    });
}

function renderConsole(text, { json = false, tone = "" } = {}) {
    const out = $("output");
    const plain = String(text ?? "");
    consoleState.text = plain;
    if (!plain.trim()) { out.innerHTML = '<span class="ln sys">(no output)</span>'; return; }
    if (json) {
        out.innerHTML = highlightJson(esc(plain));
    } else {
        let inErr = false;
        out.innerHTML = plain.split("\n").map((line) => {
            if (line.trim() === "ERROR:") inErr = true;
            const cls = tone === "err" || inErr ? "err" : classifyLine(line);
            return '<span class="ln ' + cls + '">' + (esc(line) || " ") + "</span>";
        }).join("");
    }
    $("termMeta").textContent = plain.split("\n").length + " lines";
    out.scrollTop = out.scrollHeight;
}

function consoleRunning(message) {
    consoleState.text = message;
    $("output").innerHTML = '<span class="ln sys">$ ' + esc(message) + '<span class="cursor"></span></span>';
    $("termMeta").textContent = "";
}

function setTerm(state, text) {
    $("termDot").className = "dot" + (state === "run" ? " run" : state === "ok" ? " done" : state === "err" ? " bad" : "");
    $("console-status").textContent = text;
}

async function copyConsole() {
    if (!consoleState.text.trim()) { toast("info", "Nothing to copy", "The console is empty."); return; }
    try {
        await navigator.clipboard.writeText(consoleState.text);
    } catch (e) {
        const ta = document.createElement("textarea");
        ta.value = consoleState.text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); } catch (e2) { toast("error", "Copy failed", "Select the text and copy manually."); ta.remove(); return; }
        ta.remove();
    }
    toast("success", "Copied", "Console output copied to clipboard.", 2200);
}

/* ============ Operations (evaluation / pairwise / analysis / report) ============ */
const OPS = {
    evaluation: { btn: "btnEval", path: "/run-evaluation", label: "Evaluation", title: "llm-judge ~ run_evaluation.py", after: () => loadReport() },
    pairwise:   { btn: "btnPair", path: "/run-pairwise",   label: "Pairwise Evaluation", title: "llm-judge ~ run_pairwise.py" },
    analysis:   { btn: "btnAnalysis", path: "/run-analysis", label: "Analysis", title: "llm-judge ~ run_analysis.py" },
    report:     { btn: "btnReport", path: "/report", label: "Report", title: "llm-judge ~ report.json", json: true }
};
const state = { busy: false, timer: null };

function lockControls(activeKey) {
    state.busy = !!activeKey;
    Object.entries(OPS).forEach(([key, op]) => {
        const b = $(op.btn);
        b.disabled = state.busy;
        b.classList.toggle("is-loading", key === activeKey);
        b.setAttribute("aria-busy", key === activeKey ? "true" : "false");
    });
}

async function runOperation(key) {
    if (state.busy) { toast("info", "Please wait", "Another operation is still running."); return; }
    const op = OPS[key];
    lockControls(key);
    $("termTitle").textContent = op.title;
    const started = performance.now();
    const tick = () => setTerm("run", "Executing " + op.label + "… " + Math.floor((performance.now() - started) / 1000) + "s");
    tick();
    state.timer = setInterval(tick, 1000);
    setStatus("Running...", op.label + " in progress");
    consoleRunning(key === "report" ? "Loading report.json" : "Running " + op.label + " on current test suite");

    try {
        const data = await api(op.path);
        const secs = ((performance.now() - started) / 1000).toFixed(1);
        if (key === "report") {
            if (data && data.error) throw new ApiError(String(data.error), 500);
            updateMetrics(data || {});
            renderConsole(JSON.stringify(data, null, 4), { json: true });
        } else {
            const ok = data && data.success !== false;
            renderConsole(data && data.output !== undefined ? data.output : JSON.stringify(data, null, 2), { tone: ok ? "" : "err" });
            if (!ok) throw new ApiError("The script reported a failure. See console output.", 500);
        }
        setStatus("Completed", op.label + " finished in " + secs + "s");
        setTerm("ok", "Finished in " + secs + "s");
        toast("success", op.label + " complete", key === "report" ? "Metrics refreshed from report.json." : "Finished in " + secs + "s.");
        if (op.after) await op.after();
    } catch (err) {
        const msg = err instanceof ApiError ? err.message : "Unexpected error: " + err;
        if (!consoleState.text.trim() || $("output").querySelector(".cursor")) renderConsole("ERROR: " + msg, { tone: "err" });
        setStatus("Failed", msg);
        setTerm("err", "Failed");
        toast("error", op.label + " failed", msg, 7000);
    } finally {
        clearInterval(state.timer);
        lockControls(null);
    }
}

/* ============ Report (silent refresh) ============ */
async function loadReport() {
    try {
        const data = await api("/report");
        if (data && !data.error) updateMetrics(data);
    } catch (err) { console.warn("Report not loaded:", err.message); }
}

/* ============ Test suite ============ */
let suiteData = [];

function skeletons(n = 3) { return Array.from({ length: n }, () => '<div class="skeleton"></div>').join(""); }

function tcCard(item, idx) {
    const criteria = Array.isArray(item.criteria) ? item.criteria : [];
    return (
        '<article class="tc" data-idx="' + idx + '">' +
        '<div class="tc-head"><span class="badge">' + esc(item.id ?? "TC") + '</span><span class="tag"><i data-lucide="wand-2" style="width:13px;height:13px"></i>Auto generated</span></div>' +
        '<div class="tc-label">Prompt</div><div class="tc-text">' + esc(item.input) + "</div>" +
        '<div class="tc-label">Model output</div><div class="tc-text">' + esc(item.model_output || "Pending evaluation...") + "</div>" +
        '<div class="tc-extra">' +
            '<div class="tc-label">System prompt</div><div class="tc-text">' + esc(item.system_prompt || "n/a") + "</div>" +
            '<div class="tc-label">Expected output</div><div class="tc-text">' + esc(item.expected_output || "n/a") + "</div>" +
            (criteria.length ? '<div class="tc-label">Criteria</div><div class="chips">' + criteria.map((c) => '<span class="chip">' + esc(c) + "</span>").join("") + "</div>" : "") +
        "</div>" +
        '<button class="tc-toggle" type="button" aria-expanded="false"><span>Show details</span><i data-lucide="chevron-down"></i></button>' +
        "</article>"
    );
}

async function loadTestSuite() {
    const list = $("testSuiteList");
    list.innerHTML = skeletons();
    try {
        const data = await api("/test-suite");
        suiteData = Array.isArray(data) ? data : [];
        animateNumber($("cases"), suiteData.length);
        setBar("casesBar", Math.min(100, suiteData.length * 10));
        $("suiteCount").textContent = suiteData.length;
        if (suiteData.length === 0) {
            list.innerHTML = '<div class="empty"><i data-lucide="inbox"></i><b>No test cases yet</b><span>Add a prompt above and it will appear here, saved to test_suite.json.</span></div>';
        } else {
            list.innerHTML = suiteData.map(tcCard).join("");
        }
    } catch (err) {
        list.innerHTML = '<div class="empty"><i data-lucide="alert-triangle"></i><b>Could not load the test suite</b><span>' + esc(err.message) + "</span></div>";
    }
    refreshIcons();
}

function toggleCard(card) {
    const open = card.classList.toggle("open");
    const btn = card.querySelector(".tc-toggle");
    btn.setAttribute("aria-expanded", String(open));
    btn.querySelector("span").textContent = open ? "Hide details" : "Show details";
}

/* ============ Test case form ============ */
function updateCounter(inputId, counterId, max) {
    const len = $(inputId).value.length, c = $(counterId);
    c.textContent = len + " / " + max;
    c.className = "counter" + (len >= max ? " max" : len >= max * 0.9 ? " warn" : "");
}

function setFieldError(msg) {
    const input = $("tc_input"), help = $("inputHelp");
    input.classList.toggle("invalid", !!msg);
    help.classList.toggle("error", !!msg);
    if (msg) help.textContent = msg;
    else help.innerHTML = 'The question or task the model will answer. <span class="kbd">Ctrl</span> + <span class="kbd">Enter</span> saves.';
}

function setSaving(on) {
    const b = $("btnSave");
    b.disabled = on || state.busy;
    b.classList.toggle("is-loading", on);
    $("btnSaveText").textContent = on ? "Generating test case…" : "Generate & Save Test Case";
}

async function saveTestCase(ev) {
    if (ev) ev.preventDefault();
    if (state.busy || $("btnSave").classList.contains("is-loading")) return;

    const userInput = $("tc_input").value.trim();
    if (userInput.length < 3) {
        setFieldError(userInput ? "Prompt is too short. Add a little more detail." : "Enter a user prompt before saving.");
        $("tc_input").focus();
        return;
    }
    setFieldError("");

    const payload = { input: userInput, system_prompt: $("tc_sys").value.trim() || "Answer accurately." };
    setSaving(true);
    setStatus("Generating...", "Creating test case");
    try {
        const data = await api("/test-suite/add-quick", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        toast("success", "Test case saved", (data && data.message) || "Saved to test_suite.json.");
        $("tc_input").value = "";
        $("tc_sys").value = "Answer accurately.";
        updateCounter("tc_input", "inputCount", 2000);
        updateCounter("tc_sys", "sysCount", 500);
        setStatus("Idle", "Ready for the next run");
        await loadTestSuite();
    } catch (err) {
        setStatus("Idle", "Ready for the next run");
        toast("error", "Could not save test case", err.message, 7000);
    } finally {
        setSaving(false);
    }
}

/* ============ Ripple ============ */
function addRipple(ev) {
    const btn = ev.currentTarget;
    if (btn.disabled || reduceMotion()) return;
    const r = btn.getBoundingClientRect(), size = Math.max(r.width, r.height) / 2;
    const el = document.createElement("span");
    el.className = "ripple";
    el.style.cssText = "width:" + size + "px;height:" + size + "px;left:" + (ev.clientX - r.left - size / 2) + "px;top:" + (ev.clientY - r.top - size / 2) + "px";
    btn.appendChild(el);
    setTimeout(() => el.remove(), 650);
}

/* ============ Boot ============ */
function init() {
    $("themeBtn").addEventListener("click", toggleTheme);
    Object.entries(OPS).forEach(([key, op]) => $(op.btn).addEventListener("click", () => runOperation(key)));
    document.querySelectorAll(".btn").forEach((b) => b.addEventListener("pointerdown", addRipple));

    $("tcForm").addEventListener("submit", saveTestCase);
    $("tc_input").addEventListener("input", () => { updateCounter("tc_input", "inputCount", 2000); if ($("tc_input").value.trim()) setFieldError(""); });
    $("tc_sys").addEventListener("input", () => updateCounter("tc_sys", "sysCount", 500));
    $("tc_input").addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") saveTestCase(e); });
    updateCounter("tc_sys", "sysCount", 500);

    $("btnCopy").addEventListener("click", copyConsole);
    $("btnClear").addEventListener("click", () => { emptyConsole(); setTerm("", "System Ready"); $("termTitle").textContent = "llm-judge ~ console"; });
    $("btnRefresh").addEventListener("click", loadTestSuite);
    $("testSuiteList").addEventListener("click", (e) => {
        const btn = e.target.closest(".tc-toggle");
        if (btn) toggleCard(btn.closest(".tc"));
    });

    emptyConsole();
    setStatus("Idle", "Ready for the next run");
    setTerm("", "System Ready");
    refreshIcons();
    if (window.__noLucide) console.info("Lucide icons unavailable; running with text labels only.");

    checkHealth();
    setInterval(checkHealth, 20000);
    loadReport();
    loadTestSuite();
}

document.addEventListener("DOMContentLoaded", init);
window.addEventListener("load", refreshIcons);
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.get("/test-suite")
async def get_test_suite():
    if not TEST_SUITE_PATH.exists():
        return []
    try:
        with open(TEST_SUITE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# Smart Route: ID auto-generates & outputs auto-fill
@app.post("/test-suite/add-quick")
async def add_quick_test_case(req: QuickTestCaseRequest):
    suite = []
    if TEST_SUITE_PATH.exists():
        try:
            with open(TEST_SUITE_PATH, "r", encoding="utf-8") as f:
                suite = json.load(f)
        except Exception:
            suite = []

    # Auto generate ID (TC001, TC002, TC003...)
    next_id_num = len(suite) + 1
    generated_id = f"TC{next_id_num:03d}"

    # Auto-generate model outputs based on input (Realistic behavior)
    new_case = {
        "id": generated_id,
        "input": req.input,
        "system_prompt": req.system_prompt,
        "model_output": f"Automated response for '{req.input}': Evaluated concepts based on provided context.",
        "expected_output": f"Concise ground truth explanation covering core principles of '{req.input}'.",
        "criteria": [
            "correctness",
            "faithfulness",
            "completeness",
            "instruction_following",
            "tone",
        ],
    }

    suite.append(new_case)

    with open(TEST_SUITE_PATH, "w", encoding="utf-8") as f:
        json.dump(suite, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "message": f"Test case '{generated_id}' created and saved to test_suite.json!",
    }


@app.get("/run-evaluation")
async def run_evaluation():
    try:
        result = subprocess.run(
            [sys.executable, "run_evaluation.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/run-pairwise")
async def run_pairwise():
    try:
        result = subprocess.run(
            [sys.executable, "run_pairwise.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/run-analysis")
async def run_analysis():
    try:
        result = subprocess.run(
            [sys.executable, "run_analysis.py"],
            capture_output=True,
            text=True,
        )
        output = result.stdout
        if result.stderr:
            output += "\n\nERROR:\n" + result.stderr
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "output": str(e)}


@app.get("/report")
async def report():
    try:
        if not REPORT_PATH.exists():
            return {
                "total_cases": 0,
                "pass_rate": 0,
                "mean_score": 0,
                "results": [],
            }
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "LLM Judge Dashboard"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)