#!/usr/bin/env python3
"""Generate an RmlUi theme folder for sven-n/MuMain from a tokens.json design file.

Usage, from the MuMain root (tokens.json is read from beside this script):
    python tools/kryon_theme/generate_theme.py
or from anywhere:
    python generate_theme.py --tokens tokens.json --mumain path/to/MuMain

It writes src/bin/Data/Interface/RmlUi/themes/<name>/ inside the MuMain checkout:
    theme.ini   - inherits the base theme (modern), loads the fonts
    tokens.ini  - every token of the base theme, with this design's values
    *.rcss      - the base theme's stylesheets with their literal colors retinted to this palette
    base.rcss   - the same, plus this design's components (frames, buttons, tabs, inputs...)
    README.md   - what was generated and from what

Re-run it after updating MuMain (to pick up changes in the base theme) or after editing tokens.json.
Only the Python standard library is needed.
"""
import argparse
import colorsys
import json
import re
import shutil
import sys
from pathlib import Path

THEMES_DIR = Path("src/bin/Data/Interface/RmlUi/themes")
HEX_RE = re.compile(r"(?<=[\s:,(])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(r"\brgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)")


# ---------------------------------------------------------------- tokens.json helpers

def lookup(data, ref):
    """Resolve 'a.b.c' against the json, or return ref itself when it is a literal."""
    if not isinstance(ref, str) or ref.startswith("#") or "." not in ref:
        return ref
    for root in (data, data.get("semantic", {})):  # "text.warm" is short for "semantic.text.warm"
        node = root
        for part in ref.split("."):
            if not isinstance(node, dict) or part not in node:
                node = None
                break
            node = node[part]
        if node is not None:
            return node
    return ref  # a literal that merely contains a dot (e.g. a font name)


def parse_hex(value):
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(h[6:8], 16) if len(h) == 8 else 255
    return r, g, b, a


def rml_color(value):
    """#RRGGBB(AA) -> RmlUi notation (rgba alpha is 0-255 in this engine)."""
    if not isinstance(value, str) or not value.startswith("#"):
        return str(value)
    r, g, b, a = parse_hex(value)
    if a == 255:
        return "#%02x%02x%02x" % (r, g, b)
    return "rgba(%d, %d, %d, %d)" % (r, g, b, a)


def gradient(data, ref):
    g = lookup(data, ref) if isinstance(ref, str) else ref
    stops = ", ".join("%s %s%%" % (rml_color(c), p) for c, p in g["stops"])
    return "linear-gradient(%sdeg, %s)" % (g["angle"], stops)


def inverted(data, ref):
    g = dict(lookup(data, ref))
    g["angle"] = (g["angle"] + 180) % 360
    return gradient(data, g)


# ---------------------------------------------------------------- recoloring

class Recolor:
    def __init__(self, cfg):
        self.cfg = cfg

    def rgb(self, r, g, b):
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        hue = h * 360
        c = self.cfg
        if l <= 0.02 or l >= 0.98:
            return r, g, b  # black / white: outlines, world text, masks
        if s <= c["neutralMaxSaturation"]:
            if l <= c["surface"]["maxLightness"]:
                return self._hls(c["surface"]["hue"], l * c["surface"]["lightnessScale"], c["surface"]["saturation"])
            if l <= c["metal"]["maxLightness"]:
                return self._hls(c["metal"]["hue"], l * c["metal"]["lightnessScale"], c["metal"]["saturation"])
            return self._hls(c["text"]["hue"], l * c["text"]["lightnessScale"], c["text"]["saturation"])
        w = c["warm"]
        if w["minHue"] <= hue <= w["maxHue"]:
            return self._hls(w["hue"], l, s * w["saturationScale"])
        cr = c["crimson"]
        if (hue < cr["maxHueBelow"] or hue > cr["minHueAbove"]) and l <= cr["maxLightness"]:
            return self._hls(cr["hue"], l * cr["lightnessScale"], min(s, cr["maxSaturation"]))
        return r, g, b  # saturated non-warm colors carry game meaning (mana blue, poison green...)

    @staticmethod
    def _hls(hue, l, s):
        r, g, b = colorsys.hls_to_rgb(hue / 360, min(max(l, 0), 1), min(max(s, 0), 1))
        return round(r * 255), round(g * 255), round(b * 255)

    def text(self, css):
        out, depth, i = [], 0, 0
        # only touch declaration blocks, never selectors (#ids look like hex colors)
        for chunk in re.split(r"([{}])", css):
            if chunk == "{":
                depth += 1
            elif chunk == "}":
                depth -= 1
            elif depth > 0:
                chunk = HEX_RE.sub(self._hex_sub, chunk)
                chunk = RGB_RE.sub(self._rgb_sub, chunk)
            out.append(chunk)
        return "".join(out)

    def _hex_sub(self, m):
        r, g, b, a = parse_hex(m.group(0))
        r, g, b = self.rgb(r, g, b)
        if len(m.group(1)) == 8:
            return "#%02x%02x%02x%02x" % (r, g, b, a)
        return "#%02x%02x%02x" % (r, g, b)

    def _rgb_sub(self, m):
        r, g, b = self.rgb(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if m.group(4) is not None:
            return "rgba(%d, %d, %d, %s)" % (r, g, b, m.group(4))
        return "rgb(%d, %d, %d)" % (r, g, b)


# ---------------------------------------------------------------- output files

def write_theme_ini(data, dest):
    lines = [
        "; Generated by generate_theme.py from tokens.json -- edit tokens.json and re-run instead.",
        "[Theme]",
        "Base=%s" % data["baseTheme"],
        "",
        "[Fonts]",
    ]
    lines += ["%s=%s" % (k, v) for k, v in data["typography"]["fontFiles"].items()]
    lines += ["", "[Meta]", "DisplayName=%s" % data["displayName"], ""]
    (dest / "theme.ini").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def read_ini_tokens(path):
    tokens = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith((";", "[")) and "=" in line:
            k, v = line.split("=", 1)
            tokens[k.strip()] = v.strip()
    return tokens


def write_tokens_ini(data, base_dir, dest):
    base_tokens = read_ini_tokens(base_dir / "tokens.ini")
    mapping = {k: v for k, v in data["clientTokens"].items() if not k.startswith("_")}
    unknown = sorted(set(mapping) - set(base_tokens))
    if unknown:
        print("warning: tokens not in the base theme (still written): %s" % ", ".join(unknown))
    lines = [
        "; Generated by generate_theme.py from tokens.json -- edit tokens.json and re-run instead.",
        "; Tokens not listed here keep the %s theme's value (inherited key by key)." % data["baseTheme"],
        "[Tokens]",
    ]
    for key, ref in mapping.items():
        lines.append("%s=%s" % (key, rml_color(lookup(data, ref))))
    (dest / "tokens.ini").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(mapping)


def shadow(spec, inset_default=False):
    kind = spec.get("kind", "inset" if inset_default else "outset")
    parts = ["inset"] if kind == "inset" else []
    parts += ["%sdp" % spec.get("x", 0), "%sdp" % spec.get("y", 0), "%sdp" % spec.get("blur", 0),
              "%sdp" % spec.get("spread", 0), rml_color(spec["color"])]
    return " ".join(parts)


def components_css(d):
    L = lambda ref: rml_color(lookup(d, ref))  # noqa: E731
    c = d["components"]
    e = d["effects"]
    sem = d["semantic"]
    win = c["window"]
    rings = [s for s in e["windowRings"] if s["kind"] == "outset"]
    win_shadow = ", ".join([shadow(s) for s in rings] + [shadow(e["windowShadow"])])
    btn, tab, inp = c["button"], c["tab"], c["input"]
    glow = e["topGlow"]
    brushed = e["brushedLines"]
    brushed_css = "repeating-linear-gradient(%ddeg, %s 0dp 1dp, transparent 1dp %ddp)" % (
        brushed["angle"], rml_color(brushed["color"]), brushed["period"])
    glow_css = "radial-gradient(circle at %s, %s, transparent %d%%)" % (
        glow["at"], rml_color(glow["color"]), int(glow["reach"] * 100))
    btn_rings = ", ".join(shadow(s, True) for s in btn["rings"]) + ", " + shadow(btn["shadow"])
    sec = c["buttonSecondary"]
    css = f"""

/* =====================================================================================
   KRYON COMPONENTS -- generated from tokens.json (components / effects / variants).
   Appended after the retinted base rules so these recipes win by source order.
   ===================================================================================== */

/* Window: gold border, dark outer ring + aged-gold ring, deep drop shadow, warm top glow. */
.modern-frame,
.modern-frame-crimson {{
	background-color: {L(sem["surface"]["panelEnd"])};
	decorator: {glow_css}, {brushed_css}, {gradient(d, win["background"])};
	border-width: {win["border"]["width"]}dp;
	border-color: {L(win["border"]["color"])};
	border-radius: {d["radius"]["sm"]}dp;
	box-shadow: {win_shadow};
}}
/* The content plate keeps the frame visible: no own fill, only the inner gold line. */
.modern-panel,
.modern-panel-crimson {{
	background-color: transparent;
	decorator: none;
	border-width: 1dp;
	border-color: {rml_color(e["windowRings"][-1]["color"])};
	border-radius: 0dp;
}}
.modern-frame-accent-crimson {{
	border-color: {L(sem["border"]["divider"])};
}}
.modern-header,
.modern-header-rail {{
	background-color: {L(sem["surface"]["raisedEnd"])};
	decorator: radial-gradient(circle at 50% 0%, {L(c["header"]["glow"])}, transparent 70%), {gradient(d, c["header"]["background"])};
	border-width: 0dp;
	border-bottom-width: 1dp;
	border-bottom-color: {L(c["header"]["borderBottom"]["color"])};
}}
.modern-header-accent {{
	opacity: 0.6;
}}
.modern-title-plate {{
	background-color: {L(sem["surface"]["raisedEnd"])};
	decorator: radial-gradient(circle at 50% 0%, {L(c["header"]["glow"])}, transparent 70%), {gradient(d, c["header"]["background"])};
	border-color: {L(sem["border"]["title"])};
	box-shadow: inset 0dp 1dp 0dp {rml_color("#DBB87630")}, inset 0dp -1dp 0dp #000000, 0dp 2dp 5dp rgba(0, 0, 0, 140);
}}
.modern-header-title {{
	color: {L(sem["text"]["warm"])};
	font-family: "token(font-title)";
	letter-spacing: 1.6dp;
	text-transform: uppercase;
	font-effect: shadow(0dp 1dp #000000);
}}
.title-glow {{
	decorator: radial-gradient(ellipse, {rml_color("#EFD39860")}, {rml_color("#8D693740")} 55%, transparent 88%);
}}

/* Primary forged-bronze button (web: SIGN IN). Plain .btn gets the same metal; .btn-ok is brighter. */
.btn,
.btn-ok {{
	color: {L(sem["text"]["onButton"])};
	background-color: {L("primitives.gold.900")};
	decorator: {gradient(d, btn["background"])};
	border-width: {btn["border"]["width"]}dp;
	border-color: {L("primitives.gold.550")};
	border-radius: {d["radius"]["sm"]}dp;
	letter-spacing: 0.4dp;
	font-family: "token(font-title)";
	font-effect: shadow(0dp 1dp #000000);
	box-shadow: {btn_rings};
}}
/* The window's one primary action keeps the web's uppercase, spaced lettering. */
.btn-ok {{
	border-color: {L(btn["border"]["color"])};
	text-transform: uppercase;
	letter-spacing: 1.2dp;
}}
.btn:hover,
.btn-ok:hover {{
	color: {rml_color(btn["hover"]["text"])};
	border-color: {L(btn["hover"]["border"])};
	decorator: {gradient(d, btn["hover"]["background"])};
}}
.btn:active,
.btn-ok:active {{
	transform: translateY(1dp);
	decorator: {inverted(d, btn["background"])};
	box-shadow: inset 0dp 1dp 3dp rgba(0, 0, 0, 184);
}}
.btn.disabled,
.btn-ok.disabled {{
	decorator: none;
	box-shadow: none;
	background-color: {L("primitives.ink.800")};
	border-color: {L(sem["border"]["idle"])};
	color: {L(sem["text"]["disabled"])};
	opacity: {btn["disabled"]["opacity"]};
}}

/* Icon buttons: secondary metal; the primary one uses the forged bronze. */
.btn-icon {{
	color: {rml_color(sec["text"]["color"])};
	decorator: {gradient(d, sec["background"])};
	border-color: {rml_color(sec["border"]["color"])};
	box-shadow: {", ".join(shadow(s, True) for s in sec["rings"])}, 0dp 2dp 5dp rgba(0, 0, 0, 133);
}}
.btn-icon:hover {{
	color: {rml_color(sec["hover"]["text"])};
	border-color: {L(sec["hover"]["border"])};
	decorator: {gradient(d, btn["background"])};
}}
.btn-icon-primary {{
	color: {L(sem["text"]["onButton"])};
	decorator: {gradient(d, btn["background"])};
	border-color: {L(btn["border"]["color"])};
}}
.btn-icon-primary:hover {{
	border-color: {L(btn["hover"]["border"])};
	decorator: {gradient(d, btn["hover"]["background"])};
}}
.btn-icon-label,
.btn-icon-primary .btn-icon-label {{
	color: {L(sem["text"]["onButton"])};
}}

/* Inputs: near-black well, bronze edge; gold edge while focused. */
.text-field {{
	color: {rml_color(inp["text"]["color"])};
	background-color: {L(sem["surface"]["inputTop"])};
	decorator: {gradient(d, inp["background"])};
	border-color: {L(inp["border"]["color"])};
	box-shadow: inset 0dp 1dp 4dp #000000;
}}
.text-field:focus {{
	border-color: {L(inp["focus"]["border"])};
	box-shadow: inset 0dp 1dp 4dp #000000, 0dp 0dp 0dp 2dp {rml_color(e["focusHalo"]["color"])};
}}
.text-field selection {{
	color: {rml_color(inp["selection"]["text"])};
	background-color: {rml_color(inp["selection"]["background"])};
}}

/* Checkbox and slots. */
.checkbox-box {{
	background-color: {rml_color(c["checkbox"]["background"])};
	border-color: {L(c["checkbox"]["border"])};
}}
.checkbox-box.checked {{
	decorator: {gradient(d, c["checkbox"]["checked"]["background"])};
	border-color: {L(c["checkbox"]["checked"]["border"])};
}}
.slot {{
	border-color: {rml_color(c["slot"]["border"])};
}}
.slot--selected {{
	border-color: {L(c["slot"]["selected"]["border"])};
	background-color: {rml_color(c["slot"]["selected"]["wash"])};
}}

/* Scrollbar: gold thumb on a steel rail. */
.scroll-pane scrollbarvertical slidertrack {{
	background-color: {rml_color(c["scrollbar"]["track"])};
}}
.scroll-pane scrollbarvertical sliderbar {{
	background-color: {rml_color(c["scrollbar"]["thumb"])};
}}
.scroll-pane scrollbarvertical sliderbar:hover,
.scroll-pane scrollbarvertical sliderbar:active {{
	background-color: {rml_color(c["scrollbar"]["thumbHover"])};
}}

/* ---- Opt-in helpers for forked .rml files (not used by the shared markup) ---- */

/* Tabs / segmented selectors (web: ES/EN/PT, shop tabs, ranking periods). */
.kryon-tab {{
	pointer-events: auto;
	cursor: pointer;
	text-align: center;
	font-family: "token(font-body)";
	font-size: 7dp;
	text-transform: uppercase;
	letter-spacing: {tab["text"]["letterSpacing"]}dp;
	color: {rml_color(tab["text"]["color"])};
	background-color: {rml_color(tab["background"])};
	border: 1dp {rml_color(tab["border"]["color"])};
	border-radius: {d["radius"]["sm"]}dp;
}}
.kryon-tab:hover {{
	border-color: {L(sem["border"]["hover"])};
	color: {L(sem["text"]["primary"])};
}}
.kryon-tab.active {{
	color: {rml_color(tab["active"]["text"])};
	decorator: {gradient(d, tab["active"]["background"])};
	border-color: {rml_color(tab["active"]["border"])};
	box-shadow: {", ".join(shadow(s, True) for s in tab["active"]["rings"])};
}}
/* Golden progress bar (web: loaders). Put .kryon-progress-fill inside with width = percent. */
.kryon-progress {{
	background-color: {rml_color(c["progressBar"]["track"])};
	border: 1dp {rml_color(c["progressBar"]["border"]["color"])};
	box-shadow: 0dp 0dp 0dp 1dp {L("primitives.ink.850")}, inset 0dp 1dp 4dp #000000;
}}
.kryon-progress-fill {{
	height: 100%;
	decorator: {gradient(d, c["progressBar"]["fill"])};
	box-shadow: 0dp 0dp 10dp {rml_color(c["progressBar"]["glow"])};
}}
/* Gold "L" corner ornaments (web: login card). Two empty divs as the frame's last children. */
.kryon-corner-tl, .kryon-corner-tr {{
	position: absolute;
	top: {e["cornerOrnament"]["inset"]}dp;
	width: {e["cornerOrnament"]["size"]}dp;
	height: {e["cornerOrnament"]["size"]}dp;
	pointer-events: none;
	border-top: {e["cornerOrnament"]["thickness"]}dp {rml_color(e["cornerOrnament"]["color"])};
}}
.kryon-corner-tl {{ left: {e["cornerOrnament"]["inset"]}dp; border-left: {e["cornerOrnament"]["thickness"]}dp {rml_color(e["cornerOrnament"]["color"])}; }}
.kryon-corner-tr {{ right: {e["cornerOrnament"]["inset"]}dp; border-right: {e["cornerOrnament"]["thickness"]}dp {rml_color(e["cornerOrnament"]["color"])}; }}
/* Bright gold call-to-action (web: welcome "claim"). */
.kryon-cta {{
	color: {rml_color(c["buttonCta"]["text"]["color"])};
	decorator: {gradient(d, c["buttonCta"]["background"])};
	border: 1dp {rml_color(c["buttonCta"]["border"]["color"])};
	box-shadow: {shadow(c["buttonCta"]["shadow"])};
	text-transform: uppercase;
	font-weight: bold;
}}
/* Ranking / list rows. */
.kryon-row {{
	color: {rml_color(c["row"]["text"]["color"])};
	border-bottom: 1dp {rml_color(c["row"]["divider"])};
}}
.kryon-row:hover {{
	background-color: {rml_color(c["row"]["hover"])};
}}
"""
    for name, v in d["variants"].items():
        if name == "gold":
            continue
        extra = ""
        if "glow" in v:
            extra = "radial-gradient(circle at 50%% 0%%, %s, transparent 45%%), " % rml_color(v["glow"])
        rings = v.get("rings")
        ring_css = ""
        if rings:
            ring_css = "\n\tbox-shadow: %s, %s;" % (", ".join(shadow(s) for s in rings), shadow(e["windowShadow"]))
        css += f"""
/* Variant "{name}": {v["use"]}. Use as class="modern-frame kryon-frame-{name}". */
.kryon-frame-{name} {{
	decorator: {extra}{gradient(d, v["panel"])};
	border-color: {rml_color(v["border"])};{ring_css}
}}
.kryon-frame-{name} .modern-header-title {{ color: {rml_color(v["title"])}; }}
.kryon-frame-{name} .slot--selected {{ border-color: {rml_color(v["accent"])}; }}
"""
    return css


def write_readme(data, dest, files, n_tokens):
    text = f"""# {data["displayName"]} theme

Generated by `generate_theme.py` from `tokens.json`. Do not edit these files by hand: change
`tokens.json` and run the generator again (also after pulling a new MuMain, so the theme picks up
changes to the `{data["baseTheme"]}` stylesheets).

- `theme.ini`: inherits `{data["baseTheme"]}` (its .rml forks and any stylesheet not copied here) and loads Georgia/Trebuchet from Windows.
- `tokens.ini`: {n_tokens} tokens with this palette.
- {len(files)} `.rcss` files: the `{data["baseTheme"]}` stylesheets with their literal colors retinted
  (dark neutrals -> blue steel, iron edges -> aged gold, crimson -> forged bronze; black, white and
  game-meaning colors such as mana blue or poison green are kept).
- `base.rcss` ends with the shared components: window frame with rings, forged buttons, inputs,
  tabs, progress bar, corner ornaments and the palette variants
  ({", ".join("kryon-frame-" + k for k in data["variants"] if k != "gold")}).

Select it with `$theme {data["name"]}` in chat, in Options > UI > Theme, or `[UI] RmlTheme={data["name"]}` in config.ini.
"""
    (dest / "README.md").write_text(text, encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent
    ap.add_argument("--tokens", type=Path, default=here / "tokens.json")
    ap.add_argument("--mumain", type=Path, default=Path("."), help="root of the sven-n/MuMain checkout (default: current folder)")
    ap.add_argument("--out", type=Path, help="output folder (default: the themes folder inside --mumain)")
    args = ap.parse_args()

    data = json.loads(args.tokens.read_text(encoding="utf-8"))
    if data.get("formatVersion") != 1:
        sys.exit("unsupported tokens.json formatVersion")
    themes = args.mumain / THEMES_DIR
    base_dir = themes / data["baseTheme"]
    if not (base_dir / "base.rcss").is_file():
        sys.exit("base theme not found: %s" % base_dir)
    dest = (args.out or themes) / data["name"]
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    write_theme_ini(data, dest)
    n_tokens = write_tokens_ini(data, base_dir, dest)

    recolor = Recolor(data["recolor"])
    skip = set(data["recolor"]["skipFiles"])
    written = []
    for src in sorted(base_dir.glob("*.rcss")):
        if src.name in skip:
            continue
        css = recolor.text(src.read_text(encoding="utf-8"))
        header = "/* Generated by generate_theme.py: %s/%s retinted with tokens.json. */\n" % (data["baseTheme"], src.name)
        if src.name == "base.rcss":
            css += components_css(data)
        (dest / src.name).write_text(header + css, encoding="utf-8", newline="\n")
        written.append(src.name)

    write_readme(data, dest, written, n_tokens)
    print("theme '%s' written to %s (%d stylesheets, %d tokens)" % (data["name"], dest, len(written), n_tokens))


if __name__ == "__main__":
    main()
