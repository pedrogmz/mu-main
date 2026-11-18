"""Builds the Kryon theme's ornate window kit (themes/kryon-nousar/ui/ornate_*.OZT) from the Season 6 party
UI asset pack (MU_S6_Party_UI_Assets). The party window is the first user of the kit; any window can
take the same pieces (see "Kryon ornate window kit" in themes/kryon-nousar/base.rcss).

  ornate_frame.OZT        The party window's whole frame: the claw corners, the gold side rails and
                          the title band, with the plate cut out (the window paints its own fill),
                          the title, the gems and the close button removed. The right half is the
                          left half mirrored, so the close button's corner gets the claw back. It is
                          compacted to its corners plus a short stretch slice in each direction.
  ornate_gem.OZT          The diamond gem on the title band's top rail.
  ornate_gem_small.OZT    The small gem under the title band.
  ornate_gem_bottom.OZT   The ruby on the frame's bottom rail.
  ornate_close.OZT        The round crimson close button, and its lit variant.
  ornate_close_hover.OZT
  ornate_list.OZT         The member list's thin gold box, hollow.
  ornate_card.OZT         A member card's bevelled edge, hollow.
  ornate_portrait.OZT     A card's portrait frame, hollow.
  ornate_crown.OZT        The leader's crown (from the first sample card's portrait).
  ornate_danger.OZT       The crimson plate of "Abandonar", its lettering removed, and lit.
  ornate_danger_hover.OZT
  ornate_bar.OZT          The empty health bar and its red fill.
  ornate_bar_fill.OZT
  ornate_dot.OZT          The round green status gem.

Every piece prints its outer and inner rect for the ninepatch declarations in base.rcss.

Usage: python tools/kryon_theme/make_kryon_ornate_textures.py PATH_TO_PARTY_PACK [--preview DIR]
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage

import make_kryon_hud_textures as hud
from make_kryon_hud_textures import resize, write_ozt

OUT = pathlib.Path(__file__).resolve().parents[2] / "src/bin/Data/Interface/RmlUi/themes/kryon-nousar/ui"

# The full window (00_party_window_full, 680x855), in its own pixels.
WINDOW_MID_X = 340          # the art is symmetric about this column
FRAME_KEEP_X = 230          # the left part kept (corner, rail, the title band's left end)
FRAME_STRETCH_X = (232, 248)  # a plain slice of the title band, stretched across the middle
FRAME_TOP = 262             # rows kept above the stretch slice (title band, claw)
FRAME_STRETCH_Y = (430, 446)  # a plain slice of the side rails
FRAME_BOTTOM = 640          # rows kept from here down (bottom claws and rail)
# The plate inside the rails (cut out) and the claws that reach over it (kept where bright).
PLATE = (47, 117, 633, 799)
CLAW_ZONES = [(30, 100, 82, 215), (25, 680, 98, 815)]
# The title band's lettering and gems: the band between them is replaced by its plain columns.
TITLE_BAND = (150, 26, 530, 102)
TITLE_PLAIN_X = (232, 248)


def load(pack, name):
    return np.asarray(Image.open(pack / f"{name}.png").convert("RGBA")).astype(np.float32)


def crop(pixels, box):
    x0, y0, x1, y1 = box
    return pixels[y0:y1, x0:x1].copy()


def luminance(pixels):
    return pixels[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)


def soft(mask, sigma=0.8):
    return ndimage.gaussian_filter(mask.astype(np.float32), sigma)


def cut_rect(pixels, box, keep_bright_zones=(), threshold=70):
    """Makes box transparent, except the bright texels (ornaments) inside keep_bright_zones."""
    height, width = pixels.shape[:2]
    hole = np.zeros((height, width), dtype=bool)
    x0, y0, x1, y1 = box
    hole[y0:y1, x0:x1] = True
    bright = luminance(pixels) > threshold
    for zx0, zy0, zx1, zy1 in keep_bright_zones:
        zone = np.zeros_like(hole)
        zone[zy0:zy1, zx0:zx1] = True
        hole &= ~(zone & ndimage.binary_opening(bright, iterations=1))
    out = pixels.copy()
    out[..., 3] *= 1 - soft(hole)
    return out


def stretch_columns(pixels, box, source_x):
    """Fills box with the plain columns source_x repeated (removes lettering, gems)."""
    x0, y0, x1, y1 = box
    s0, s1 = source_x
    tile = pixels[y0:y1, s0:s1]
    reps = -(-(x1 - x0) // (s1 - s0))
    pixels[y0:y1, x0:x1] = np.tile(tile, (1, reps, 1))[:, :x1 - x0]


def compact(pixels, keep_x, stretch_x, top, stretch_y, bottom):
    """Left part + stretch slice + the left part mirrored; then top + stretch slice + bottom.
    Returns the texture and its ninepatch inner rect."""
    left = pixels[:, :keep_x]
    mid = pixels[:, stretch_x[0]:stretch_x[1]]
    row = np.concatenate([left, mid, left[:, ::-1]], axis=1)
    out = np.concatenate([row[:top], row[stretch_y[0]:stretch_y[1]], row[bottom:]], axis=0)
    inner = (keep_x, top, keep_x + (stretch_x[1] - stretch_x[0]), top + (stretch_y[1] - stretch_y[0]))
    return out, inner


def hollow_ring(pixels, inset, radius=0):
    """A bevelled frame with its well cut out: the rect inset from each side becomes transparent."""
    height, width = pixels.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]
    x0, y0, x1, y1 = inset, inset, width - inset, height - inset
    dx = np.maximum(np.maximum(x0 + radius - xx, xx - (x1 - radius)), 0)
    dy = np.maximum(np.maximum(y0 + radius - yy, yy - (y1 - radius)), 0)
    hole = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1) & (dx * dx + dy * dy <= radius * radius)
    out = pixels.copy()
    out[..., 3] *= 1 - soft(hole)
    return out


def three_slice(pixels, left, right, mid_width=8):
    """Left cap + a plain column repeated + right cap: drops what lies between (lettering)."""
    col = pixels[:, left:left + 1]
    return np.concatenate([pixels[:, :left], np.repeat(col, mid_width, axis=1), pixels[:, right:]], axis=1)


def masked_circle(pixels, cx, cy, r):
    height, width = pixels.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]
    inside = np.clip(r - np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) + 0.5, 0, 1)
    out = pixels.copy()
    out[..., 3] *= inside
    return out


def diamond(pixels, cx, cy, hx, hy):
    """A gem on its diamond, cut out with a soft edge."""
    x0, y0 = int(cx - hx) - 1, max(int(cy - hy) - 1, 0)
    x1, y1 = int(cx + hx) + 2, min(int(cy + hy) + 2, pixels.shape[0])
    cut = pixels[y0:y1, x0:x1].copy()
    yy, xx = np.mgrid[y0:y1, x0:x1]
    distance = np.abs(xx + 0.5 - cx) / hx + np.abs(yy + 0.5 - cy) / hy
    cut[..., 3] *= np.clip((1.0 - distance) * hx / 1.5, 0, 1)
    return cut


def lit(pixels, gain=1.25):
    out = pixels.copy()
    out[..., :3] = np.clip(out[..., :3] * gain, 0, 255)
    return out


def emit(name, pixels, inner=None, scale=1.0):
    if scale != 1.0:
        pixels = resize(pixels, scale)
        if inner:
            inner = tuple(int(round(v * scale)) for v in inner)
    hud.OUT = OUT
    write_ozt(name, pixels)
    h, w = pixels.shape[:2]
    if inner:
        x0, y0, x1, y1 = inner
        print(f"  {name}: outer 0px 0px {w}px {h}px; inner {x0}px {y0}px {x1 - x0}px {y1 - y0}px")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pack", type=pathlib.Path)
    parser.add_argument("--preview", type=pathlib.Path)
    args = parser.parse_args()
    pack = args.pack

    window = load(pack, "00_party_window_full")

    # Gems first, from the untouched art.
    emit("ornate_gem", diamond(window, 344, 16, 14, 17), scale=0.75)
    emit("ornate_gem_small", diamond(window, 344, 106, 11, 15), scale=0.75)
    emit("ornate_gem_bottom", diamond(window, 343.5, 808, 23, 25), scale=0.75)

    # The frame: the title band cleaned, the plate cut out, compacted and mirrored.
    frame = window.copy()
    stretch_columns(frame, TITLE_BAND, TITLE_PLAIN_X)
    stretch_columns(frame, (300, 0, 380, 26), (260, 300))     # the top gem's rail
    stretch_columns(frame, (300, 102, 380, 128), (260, 300))  # the small gem under the band
    frame = cut_rect(frame, PLATE, CLAW_ZONES)
    frame, inner = compact(frame, FRAME_KEEP_X, FRAME_STRETCH_X, FRAME_TOP, FRAME_STRETCH_Y, FRAME_BOTTOM)
    emit("ornate_frame", frame, inner, scale=0.75)

    # The member list's box (x 66..614, y 203..632): its left part, a slice and the mirror.
    box = crop(window, (64, 200, 616, 636))
    box = hollow_ring(box, 9, 4)
    left = box[:, :40]
    box = np.concatenate([left, box[:, 140:156], left[:, ::-1]], axis=1)
    box = np.concatenate([box[:40], box[200:216], box[-40:]], axis=0)
    emit("ornate_list", box, (40, 40, 56, 56), scale=0.5)

    card = load(pack, "03_party_member_card_3_sample")
    # The card's edge, the whole plate cut out (the row paints its own fill).
    edge = hollow_ring(crop(card, (14, 11, 627, 137)), 8, 4)
    edge = np.concatenate([edge[:, :30], edge[:, 300:316], edge[:, -30:]], axis=1)
    emit("ornate_card", edge, (30, 30, 46, edge.shape[0] - 30), scale=0.5)
    # The portrait frame of the third card (no crown on it), its picture cut out.
    portrait = hollow_ring(crop(card, (21, 17, 134, 124)), 9, 3)
    emit("ornate_portrait", portrait, (24, 24, portrait.shape[1] - 24, portrait.shape[0] - 24), scale=0.5)

    # The crown on the first card's portrait: its bright gold texels.
    crown = crop(load(pack, "01_party_member_card_1_sample"), (26, 22, 60, 50))
    rgb = crown[..., :3]
    gold = (rgb[..., 0] > 120) & (rgb[..., 0] > rgb[..., 2] * 1.6)
    labels, _ = ndimage.label(gold)
    biggest = np.argmax(np.bincount(labels.ravel())[1:]) + 1
    keep = ndimage.binary_dilation(labels == biggest, iterations=1)
    crown[..., 3] *= soft(keep, 0.6)
    emit("ornate_crown", crown, scale=0.75)

    close = masked_circle(crop(load(pack, "04_close_button"), (14, 10, 136, 132)), 61, 62, 60)
    emit("ornate_close", close, scale=0.5)
    emit("ornate_close_hover", lit(close), scale=0.5)

    danger = three_slice(crop(load(pack, "07_abandon_button"), (14, 14, 237, 98)), 28, 196)
    inner = (24, 22, danger.shape[1] - 24, danger.shape[0] - 22)
    emit("ornate_danger", danger, inner, scale=0.5)
    emit("ornate_danger_hover", lit(danger), inner, scale=0.5)

    bar = crop(load(pack, "11_hp_bar_empty"), (12, 12, 280, 58))
    bar = np.concatenate([bar[:, :24], bar[:, 120:136], bar[:, -24:]], axis=1)
    emit("ornate_bar", bar, (24, 14, bar.shape[1] - 24, bar.shape[0] - 14), scale=0.5)
    fill = crop(load(pack, "10_hp_bar_filled"), (12, 12, 266, 58))
    fill = np.concatenate([fill[:, :24], fill[:, 120:136], fill[:, -24:]], axis=1)
    emit("ornate_bar_fill", fill, (24, 14, fill.shape[1] - 24, fill.shape[0] - 14), scale=0.5)

    dot = masked_circle(crop(load(pack, "12_status_indicators"), (16, 12, 84, 80)), 34, 34, 33)
    emit("ornate_dot", dot, scale=0.5)

    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for path in OUT.glob("ornate_*.OZT"):
            data = path.read_bytes()[4:]
            width, height = int.from_bytes(data[12:14], "little"), int.from_bytes(data[14:16], "little")
            pixels = np.frombuffer(data[18:18 + width * height * 4], np.uint8).reshape(height, width, 4)
            Image.fromarray(pixels[::-1, :, [2, 1, 0, 3]].copy(), "RGBA").save(args.preview / f"{path.stem}.png")


if __name__ == "__main__":
    main()
