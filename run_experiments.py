"""
Sorting Algorithm Experiment Runner
Algorithms: Insertion Sort (3), Merge Sort (4), Quick Sort (5)
Pure stdlib – no external dependencies required.
"""

import argparse
import random
import time
import statistics
import struct
import zlib


# ── Sorting Algorithms ────────────────────────────────────────────────────────

def insertion_sort(arr):
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def _merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr):
    a = arr[:]
    _qs(a, 0, len(a) - 1)
    return a

def _qs(a, lo, hi):
    if lo < hi:
        p = _partition(a, lo, hi)
        _qs(a, lo, p - 1)
        _qs(a, p + 1, hi)

def _partition(a, lo, hi):
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1


# ── Algorithm registry ────────────────────────────────────────────────────────

ALGORITHMS = {
    3: ("Insertion Sort", insertion_sort),
    4: ("Merge Sort",     merge_sort),
    5: ("Quick Sort",     quick_sort),
}

COLORS = {
    3: (214,  39,  40),   # red
    4: ( 31, 119, 180),   # blue
    5: ( 44, 160,  44),   # green
}


# ── Array generators ──────────────────────────────────────────────────────────

def random_array(n):
    return [random.randint(0, 10 * n) for _ in range(n)]

def nearly_sorted_array(n, noise_frac):
    a = list(range(n))
    for _ in range(int(n * noise_frac)):
        i, j = random.randrange(n), random.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a


# ── Timing ────────────────────────────────────────────────────────────────────

def measure(fn, arr, reps):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn(arr)
        times.append(time.perf_counter() - t0)
    return statistics.mean(times), (statistics.stdev(times) if len(times) > 1 else 0.0)


# ── Pure-Python PNG writer ────────────────────────────────────────────────────

def _png_chunk(tag, data):
    c = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", c)

def save_png(pixels, width, height, path):
    """pixels: list of (R,G,B) tuples, row-major."""
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw += bytes([r, g, b])
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)


# ── Minimal bitmap font (printable ASCII 32-126, 6×8) ────────────────────────
# Each char is 8 rows × 6 cols stored as 6 bytes (one per column, LSB=top).

_FONT6X8 = {
    ' ': [0,0,0,0,0,0],
    '!': [0,0,95,0,0,0], '"': [0,7,0,7,0,0], '#': [20,127,20,127,20,0],
    '$': [36,42,127,42,18,0], '%': [35,19,8,100,98,0], '&': [54,73,85,34,80,0],
    "'": [0,0,7,0,0,0], '(': [0,28,34,65,0,0], ')': [0,65,34,28,0,0],
    '*': [42,28,127,28,42,0], '+': [8,8,62,8,8,0], ',': [0,80,48,0,0,0],
    '-': [8,8,8,8,8,0], '.': [0,96,96,0,0,0], '/': [32,16,8,4,2,0],
    '0': [62,81,73,69,62,0], '1': [0,66,127,64,0,0], '2': [66,97,81,73,70,0],
    '3': [33,65,73,77,51,0], '4': [24,20,18,127,16,0], '5': [39,69,69,69,57,0],
    '6': [60,74,73,73,48,0], '7': [1,113,9,5,3,0], '8': [54,73,73,73,54,0],
    '9': [6,73,73,41,30,0], ':': [0,54,54,0,0,0], ';': [0,86,54,0,0,0],
    '<': [8,20,34,65,0,0], '=': [20,20,20,20,20,0], '>': [0,65,34,20,8,0],
    '?': [2,1,81,9,6,0], '@': [62,65,93,89,78,0],
    'A': [124,18,17,18,124,0], 'B': [127,73,73,73,54,0], 'C': [62,65,65,65,34,0],
    'D': [127,65,65,34,28,0], 'E': [127,73,73,73,65,0], 'F': [127,9,9,9,1,0],
    'G': [62,65,65,81,115,0], 'H': [127,8,8,8,127,0], 'I': [0,65,127,65,0,0],
    'J': [32,64,65,63,1,0], 'K': [127,8,20,34,65,0], 'L': [127,64,64,64,64,0],
    'M': [127,2,12,2,127,0], 'N': [127,4,8,16,127,0], 'O': [62,65,65,65,62,0],
    'P': [127,9,9,9,6,0], 'Q': [62,65,81,33,94,0], 'R': [127,9,25,41,70,0],
    'S': [38,73,73,73,50,0], 'T': [1,1,127,1,1,0], 'U': [63,64,64,64,63,0],
    'V': [31,32,64,32,31,0], 'W': [63,64,56,64,63,0], 'X': [99,20,8,20,99,0],
    'Y': [3,4,120,4,3,0], 'Z': [97,81,73,69,67,0],
    'a': [32,84,84,84,120,0], 'b': [127,72,68,68,56,0], 'c': [56,68,68,68,32,0],
    'd': [56,68,68,72,127,0], 'e': [56,84,84,84,24,0], 'f': [8,126,9,1,2,0],
    'g': [12,82,82,82,62,0], 'h': [127,8,4,4,120,0], 'i': [0,68,125,64,0,0],
    'j': [32,64,68,61,0,0], 'k': [127,16,40,68,0,0], 'l': [0,65,127,64,0,0],
    'm': [124,4,24,4,120,0], 'n': [124,8,4,4,120,0], 'o': [56,68,68,68,56,0],
    'p': [124,18,18,18,12,0], 'q': [12,18,18,20,124,0], 'r': [124,8,4,4,8,0],
    's': [72,84,84,84,36,0], 't': [4,63,68,64,32,0], 'u': [60,64,64,32,124,0],
    'v': [28,32,64,32,28,0], 'w': [60,64,48,64,60,0], 'x': [68,40,16,40,68,0],
    'y': [12,80,80,80,60,0], 'z': [68,100,84,76,68,0],
    '(': [0,28,34,65,0,0], ')': [0,65,34,28,0,0], '[': [0,127,65,65,0,0],
    ']': [0,65,65,127,0,0], '%': [35,19,8,100,98,0], '.': [0,96,96,0,0,0],
    '0': [62,81,73,69,62,0],
}
_FONT6X8_FALLBACK = [0,62,65,65,62,0]  # 'O' shape for unknown chars

def _draw_char(pixels, width, height, x0, y0, ch, color):
    cols = _FONT6X8.get(ch, _FONT6X8_FALLBACK)
    for col_idx, col_bits in enumerate(cols):
        for row_idx in range(8):
            if col_bits & (1 << row_idx):
                px = x0 + col_idx
                py = y0 + row_idx
                if 0 <= px < width and 0 <= py < height:
                    pixels[py * width + px] = color

def draw_text(pixels, width, height, x, y, text, color):
    cx = x
    for ch in text:
        _draw_char(pixels, width, height, cx, y, ch, color)
        cx += 6

def draw_text_centered(pixels, width, height, y, text, color):
    draw_text(pixels, width, height, (width - len(text) * 6) // 2, y, text, color)

def blend(base, color, alpha):
    return tuple(int(b * (1 - alpha) + c * alpha) for b, c in zip(base, color))

def draw_line_aa(pixels, width, height, x0, y0, x1, y1, color, thick=2):
    """Bresenham line with thickness."""
    dx = abs(x1 - x0); dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        for tx in range(-thick // 2, thick // 2 + 1):
            for ty in range(-thick // 2, thick // 2 + 1):
                px, py = x + tx, y + ty
                if 0 <= px < width and 0 <= py < height:
                    pixels[py * width + px] = color
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x += sx
        if e2 < dx:
            err += dx; y += sy

def draw_filled_band(pixels, width, height, xs, y_lo, y_hi, color):
    """Shade between two polylines (same x coords)."""
    for i in range(len(xs) - 1):
        x_a, x_b = xs[i], xs[i + 1]
        ya_lo, ya_hi = y_lo[i], y_hi[i]
        yb_lo, yb_hi = y_lo[i + 1], y_hi[i + 1]
        for x in range(x_a, x_b + 1):
            t = (x - x_a) / max(1, x_b - x_a)
            yl = int(ya_lo + t * (yb_lo - ya_lo))
            yh = int(ya_hi + t * (yb_hi - ya_hi))
            for y in range(min(yl, yh), max(yl, yh) + 1):
                if 0 <= x < width and 0 <= y < height:
                    base = pixels[y * width + x]
                    pixels[y * width + x] = blend(base, color, 0.25)


# ── Chart renderer ────────────────────────────────────────────────────────────

W, H = 900, 580
MARGIN = dict(left=90, right=40, top=50, bottom=70)

def make_chart(sizes, results, algo_ids, title, path):
    pixels = [(255, 255, 255)] * (W * H)

    # Plot area
    px_l = MARGIN['left'];  px_r = W - MARGIN['right']
    py_t = MARGIN['top'];   py_b = H - MARGIN['bottom']
    pw = px_r - px_l;       ph = py_b - py_t

    # Draw axes (dark grey)
    GREY = (80, 80, 80); BLACK = (0, 0, 0); LGREY = (200, 200, 200)
    draw_line_aa(pixels, W, H, px_l, py_t, px_l, py_b, GREY, 1)
    draw_line_aa(pixels, W, H, px_l, py_b, px_r, py_b, GREY, 1)

    # Determine data range
    all_means = [v for aid in algo_ids for v in results[aid]['mean']]
    all_stds  = [v for aid in algo_ids for v in results[aid]['std']]
    y_max = max(m + s for m, s in zip(all_means, all_stds)) * 1.1 or 1.0
    y_min = 0.0
    x_min = sizes[0]; x_max = sizes[-1]

    def to_px(xi, yi):
        px = px_l + int((xi - x_min) / max(1, x_max - x_min) * pw)
        py = py_b - int((yi - y_min) / (y_max - y_min) * ph)
        return px, py

    # Grid lines + y-tick labels
    n_yticks = 5
    for i in range(n_yticks + 1):
        yv = y_min + (y_max - y_min) * i / n_yticks
        _, gy = to_px(x_min, yv)
        draw_line_aa(pixels, W, H, px_l, gy, px_r, gy, LGREY, 1)
        label = f"{yv:.3f}"
        draw_text(pixels, W, H, px_l - len(label) * 6 - 4, gy - 4, label, BLACK)

    # X-tick labels
    for s in sizes:
        gx, _ = to_px(s, y_min)
        draw_line_aa(pixels, W, H, gx, py_b, gx, py_b + 4, GREY, 1)
        label = str(s)
        draw_text(pixels, W, H, gx - len(label) * 3, py_b + 8, label, BLACK)

    # Title
    draw_text_centered(pixels, W, H, 16, title, BLACK)

    # Axis labels
    draw_text_centered(pixels, W, H, py_b + 30, "Array size (n)", BLACK)
    # Y label (rotated manually – just print vertically)
    ylabel = "Runtime (s)"
    for i, ch in enumerate(ylabel):
        draw_text(pixels, W, H, 4, py_t + i * 9, ch, BLACK)

    # Plot each algorithm
    for aid in algo_ids:
        color = COLORS[aid]
        means = results[aid]['mean']
        stds  = results[aid]['std']

        # Shade ± std band
        xs_px = [to_px(s, 0)[0] for s in sizes]
        y_lo_px = [to_px(s, max(0, m - sd))[1] for s, m, sd in zip(sizes, means, stds)]
        y_hi_px = [to_px(s, m + sd)[1]          for s, m, sd in zip(sizes, means, stds)]
        draw_filled_band(pixels, W, H, xs_px, y_hi_px, y_lo_px, color)

        # Mean line
        pts = [to_px(s, m) for s, m in zip(sizes, means)]
        for i in range(len(pts) - 1):
            draw_line_aa(pixels, W, H, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color, 2)

        # Dots
        for px_i, py_i in pts:
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    if dx*dx + dy*dy <= 16:
                        nx, ny = px_i + dx, py_i + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            pixels[ny * W + nx] = color

    # Legend
    lx = px_r - 160; ly = py_t + 10
    for idx, aid in enumerate(algo_ids):
        color = COLORS[aid]
        name  = ALGORITHMS[aid][0]
        yy = ly + idx * 20
        for dx in range(20):
            for dy in range(3):
                if 0 <= lx + dx < W and 0 <= yy + 4 + dy < H:
                    pixels[(yy + 4 + dy) * W + lx + dx] = color
        draw_text(pixels, W, H, lx + 24, yy, name, BLACK)

    save_png(pixels, W, H, path)
    print(f"Saved {path}")


# ── Experiments ───────────────────────────────────────────────────────────────

def run_experiment(algo_ids, sizes, gen_fn, reps):
    results = {aid: {'mean': [], 'std': []} for aid in algo_ids}
    for n in sizes:
        print(f"  n={n}")
        for aid in algo_ids:
            name, fn = ALGORITHMS[aid]
            arr = gen_fn(n)
            mean, std = measure(fn, arr, reps)
            results[aid]['mean'].append(mean)
            results[aid]['std'].append(std)
            print(f"    {name}: {mean:.4f}s ± {std:.4f}s")
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Sorting experiment runner")
    p.add_argument("-a", nargs="+", type=int, required=True,
                   help="Algorithm IDs: 3=Insertion 4=Merge 5=Quick")
    p.add_argument("-s", nargs="+", type=int, required=True,
                   help="Array sizes")
    p.add_argument("-e", type=int, choices=[1, 2], default=1,
                   help="Noise level: 1=5%% 2=20%%")
    p.add_argument("-r", type=int, default=5,
                   help="Repetitions per experiment")
    return p.parse_args()


def main():
    args = parse_args()
    algo_ids = args.a
    sizes    = sorted(args.s)
    noise    = 0.05 if args.e == 1 else 0.20
    reps     = args.r

    for aid in algo_ids:
        if aid not in ALGORITHMS:
            print(f"Unknown algorithm ID {aid}. Valid: 3, 4, 5"); return

    import sys
    sys.setrecursionlimit(10_000_000)

    print(f"\n=== Part B: Random Arrays (reps={reps}) ===")
    r1 = run_experiment(algo_ids, sizes, random_array, reps)
    make_chart(sizes, r1, algo_ids, "Runtime Comparison (Random Arrays)", "result1.png")

    print(f"\n=== Part C: Nearly Sorted Arrays (noise={int(noise*100)}%, reps={reps}) ===")
    r2 = run_experiment(algo_ids, sizes, lambda n: nearly_sorted_array(n, noise), reps)
    make_chart(sizes, r2, algo_ids,
               f"Runtime Comparison (Nearly Sorted, noise={int(noise*100)}%)", "result2.png")


if __name__ == "__main__":
    main()

