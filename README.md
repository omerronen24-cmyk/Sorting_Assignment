# Sorting_Assignment

**Students:** Omer Ronen and Rotem Ben Yaish  

**Algorithms:** Insertion Sort (3), Merge Sort (4), Quick Sort (5) — *this repo implements IDs **3–5** only* (other IDs from the PDF will error).

| Deliverable | Contents |
|-------------|----------|
| `run_experiments.py` | Sorts, timing, CLI (`-a`, `-s`, `-e`, `-r`), plots |
| `result1.png` | Part B — random arrays |
| `result2.png` | Part C — nearly sorted, 5% vs 20% swap noise |
| `requirements.txt` | `matplotlib` |

**Run:** `pip install -r requirements.txt`  

**Figures used in this submission** (reproducible with `--seed 0` if needed):

```bash
python run_experiments.py -a 3 4 5 -s 100 500 1000 2500 5000 -e 0   -r 20 --seed 0   # → result1.png
python run_experiments.py -a 3 4 5 -s 100 500 1000 2500 5000 -e 1 2 -r 20 --seed 0   # → result2.png
```

*Sizes above 50,000 are skipped for Insertion Sort (quadratic); Merge/Quick can go up to 1,000,000. Each point is the mean of `-r` runs; shaded band = ±1 stdev.*

---

## Part B — `result1.png` (random arrays)

![result1](result1.png)

Insertion Sort curves upward much faster than Merge and Quick, matching **O(n²)** vs **O(n log n)**. Merge and Quick stay low on this scale; their gap is small here. Shading shows run-to-run deviation (random input).

---

## Part C — `result2.png` (nearly sorted + noise)

![result2](result2.png)

Compared to Part B, **Insertion Sort is much faster** when the array is almost sorted: few inversions mean cheap inner-loop work, especially at **5%** noise; at **20%** noise it slows as more elements are far from place. **Merge** and **Quick** stay similar to Part B (order affects them little with this setup); their 5% vs 20% lines overlap. **Why:** insertion benefits from locality of order; divide-and-conquer routines still scan/partition the whole structure each level.
