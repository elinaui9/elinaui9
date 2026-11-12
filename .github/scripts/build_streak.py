"""Fetch the GitHub streak card in the profile palette and add a looping flame animation.

Writes assets/streak.svg. Leaves the existing file alone if the fetch fails,
so a service hiccup never replaces the card with an error image.
"""
import re
import sys
import urllib.request
from pathlib import Path

USER = "elinaui9"
PARAMS = (
    "background=11100E&border=2A2723&stroke=2A2723&ring=D8CBB7&fire=D8CBB7"
    "&currStreakNum=F4F2ED&sideNums=F4F2ED&currStreakLabel=D8CBB7"
    "&sideLabels=9C8E7B&dates=9C8E7B&border_radius=16"
)
URL = f"https://streak-stats.demolab.com/?user={USER}&{PARAMS}"
OUT = Path(__file__).resolve().parents[2] / "assets" / "streak.svg"

FLAME_CSS = """
            @keyframes flicker {
                0%   { transform: scale(1, 1)      rotate(0deg);  opacity: 1; }
                20%  { transform: scale(.94, 1.08) rotate(-3deg); opacity: .92; }
                40%  { transform: scale(1.04, .95) rotate(2deg);  opacity: 1; }
                60%  { transform: scale(.97, 1.06) rotate(-1deg); opacity: .88; }
                80%  { transform: scale(1.02, .98) rotate(3deg);  opacity: .97; }
                100% { transform: scale(1, 1)      rotate(0deg);  opacity: 1; }
            }
            @keyframes glow {
                0%, 100% { opacity: .10; transform: scale(.9); }
                50%      { opacity: .28; transform: scale(1.15); }
            }
            .flame {
                transform-box: fill-box;
                transform-origin: 50% 100%;
                animation: flicker 1.4s ease-in-out infinite;
            }
            .flame-glow {
                transform-box: fill-box;
                transform-origin: 50% 50%;
                animation: glow 1.4s ease-in-out infinite;
            }
"""

GLOW = "<circle class='flame-glow' cx='0' cy='14' r='13' fill='#d8cbb7'/>\n                    "


def main() -> int:
    req = urllib.request.Request(URL, headers={"User-Agent": "profile-readme-streak"})
    try:
        svg = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    except Exception as exc:  # network error, timeout, 5xx
        print(f"fetch failed: {exc}")
        return 0

    if "Current Streak" not in svg:
        print("unexpected response, keeping existing card")
        return 0

    svg = svg.replace("</style>", FLAME_CSS + "        </style>", 1)

    # The flame is the filled path inside the "Fire icon" group.
    pattern = re.compile(
        r"(<!-- Fire icon -->\s*<g[^>]*>\s*<path[^>]*fill='none'/>\s*)(<path )"
    )
    svg, n = pattern.subn(lambda m: m.group(1) + GLOW + "<path class='flame' ", svg, count=1)
    if n != 1:
        print("flame not found, card layout may have changed")
        return 1

    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
