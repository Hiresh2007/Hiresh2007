"""Generate assets/terminal.svg: an animated Kali-style terminal session.

Commands type out character by character (SMIL, so it animates inside a
GitHub README <img>), output lines fade in, and the cursor keeps blinking.
Edit SESSION below and re-run:  python scripts/terminal_svg.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"

W = 880
PAD_X = 24
TOP = 64  # first text baseline
LINE_H = 22
FONT = 14
CHAR_W = 8.4  # monospace advance at 14px (0.6em)
TYPE_SPEED = 0.04  # seconds per character
PAUSE_AFTER_CMD = 0.3
PAUSE_AFTER_OUT = 0.4

C = {
    "bg": "#0d1117",
    "bar": "#161b22",
    "border": "#30363d",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "blue": "#58a6ff",
    "green": "#3fb950",
    "red": "#ff7b72",
    "yellow": "#d29922",
    "purple": "#d2a8ff",
    "cyan": "#39c5cf",
}

# Each step: a command (typed) followed by output lines.
# Output line = list of (text, colour) segments.
SESSION: list[tuple[str, list[list[tuple[str, str]]]]] = [
    ("whoami", [[("Hiresh Yadav", "text"), ("  ·  CS student  ·  aspiring SOC Analyst", "muted")]]),
    (
        "cat focus.txt",
        [[("network traffic analysis · intrusion detection · SOC workflows · linux", "cyan")]],
    ),
    (
        "pcap-triage analyze lab_scan.pcap",
        [
            [("[MEDIUM]", "yellow"), (" TCP vertical port scan ", "text"), ("[T1046]", "purple"),
             ("  192.0.2.66 -> 102 ports in 0.5s", "muted")],
            [("[MEDIUM]", "yellow"), (" TCP horizontal sweep :445 ", "text"), ("[T1046]", "purple"),
             ("  192.0.2.66 -> 30 hosts in 0.6s", "muted")],
        ],
    ),
    (
        "cat learning.txt",
        [[("TryHackMe · HTB Academy (CJCA) · Cisco NetAcad · CompTIA Security+", "text")]],
    ),
    (
        "./status --internship",
        [[("[+]", "green"), (" open to security internships from summer 2027", "text")]],
    ),
]


def prompt(y: float, begin: float) -> str:
    """Two-line Kali prompt; returns SVG that fades in at `begin`."""
    top = (
        f'<tspan fill="{C["blue"]}">┌──(</tspan><tspan fill="{C["red"]}">hiresh@kali</tspan>'
        f'<tspan fill="{C["blue"]}">)-[</tspan><tspan fill="{C["text"]}">~</tspan>'
        f'<tspan fill="{C["blue"]}">]</tspan>'
    )
    return (
        f'<g opacity="0">{fade(begin, 0.15)}'
        f'<text x="{PAD_X}" y="{y}">{top}</text>'
        f'<text x="{PAD_X}" y="{y + LINE_H}" fill="{C["blue"]}">└─<tspan fill="{C["red"]}">$</tspan></text>'
        "</g>"
    )


def fade(begin: float, dur: float = 0.3) -> str:
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
        f'dur="{dur}s" fill="freeze"/>'
    )


def typed(text: str, x: float, y: float, begin: float, idx: int) -> tuple[str, float]:
    """Command text revealed one character at a time through a clip rect."""
    n = len(text)
    width = n * CHAR_W
    dur = max(n * TYPE_SPEED, 0.1)
    steps = ";".join(f"{i * CHAR_W:.1f}" for i in range(n + 1))
    times = ";".join(f"{i / n:.4f}" for i in range(n + 1))
    svg = (
        f'<clipPath id="c{idx}"><rect x="{x}" y="{y - FONT - 2}" width="0" height="{LINE_H}">'
        f'<animate attributeName="width" values="{steps}" keyTimes="{times}" calcMode="discrete" '
        f'begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
        f'<text x="{x}" y="{y}" fill="{C["green"]}" clip-path="url(#c{idx})" '
        f'textLength="{width:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>'
        # typing cursor that rides the clip edge, then disappears
        f'<rect x="{x}" y="{y - FONT + 1}" width="{CHAR_W:.1f}" height="{FONT + 2}" '
        f'fill="{C["text"]}" opacity="0">'
        f'<set attributeName="opacity" to="0.8" begin="{begin:.2f}s"/>'
        f'<animate attributeName="x" values="{";".join(f"{x + i * CHAR_W:.1f}" for i in range(n + 1))}" '
        f'keyTimes="{times}" calcMode="discrete" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0" begin="{begin + dur + PAUSE_AFTER_CMD:.2f}s"/>'
        "</rect>"
    )
    return svg, dur


def build() -> str:
    body: list[str] = []
    t = 0.4
    y = TOP
    cmd_x = PAD_X + 4 * CHAR_W  # after "└─$ "
    for i, (cmd, outputs) in enumerate(SESSION):
        body.append(prompt(y, t))
        y += LINE_H
        svg, dur = typed(cmd, cmd_x, y, t + 0.25, i)
        body.append(svg)
        t += 0.25 + dur + PAUSE_AFTER_CMD
        for line in outputs:
            y += LINE_H
            spans = "".join(f'<tspan fill="{C[c]}">{escape(s)}</tspan>' for s, c in line)
            body.append(f'<text x="{PAD_X}" y="{y}" opacity="0">{fade(t)}{spans}</text>')
            t += 0.12
        t += PAUSE_AFTER_OUT
        y += LINE_H + 6
    # final prompt with blinking block cursor
    body.append(prompt(y, t))
    y += LINE_H
    body.append(
        f'<rect x="{cmd_x}" y="{y - FONT + 1}" width="{CHAR_W:.1f}" height="{FONT + 2}" '
        f'fill="{C["text"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.5;0.6" dur="1.1s" '
        f'begin="{t + 0.2:.2f}s" repeatCount="indefinite"/></rect>'
    )
    height = y + 30

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-labelledby="title desc">
<title id="title">Hiresh Yadav - terminal</title>
<desc id="desc">Animated terminal: whoami Hiresh Yadav, CS student and aspiring SOC Analyst. Focus: network traffic analysis, intrusion detection, SOC workflows, Linux. pcap-triage detects a TCP port scan and an SMB sweep (MITRE T1046). Learning: TryHackMe, HTB Academy, Cisco NetAcad, CompTIA Security+. Open to security internships from summer 2027.</desc>
<defs>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{C["blue"]}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{C["blue"]}" stop-opacity="0.07"/>
    <stop offset="1" stop-color="{C["blue"]}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="win"><rect width="{W}" height="{height}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#win)">
  <rect width="{W}" height="{height}" fill="{C["bg"]}"/>
  <rect width="{W}" height="36" fill="{C["bar"]}"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>
  <text x="{W / 2}" y="23" text-anchor="middle" fill="{C["muted"]}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace" font-size="12">hiresh@kali: ~</text>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace" font-size="{FONT}" xml:space="preserve">
    {"".join(body)}
  </g>
  <rect width="{W}" height="90" y="-90" fill="url(#scan)">
    <animate attributeName="y" from="-90" to="{height}" dur="6s" repeatCount="indefinite"/>
  </rect>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="12" fill="none" stroke="{C["border"]}"/>
</svg>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}")
