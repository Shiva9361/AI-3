# AI Assignment 3

### S Shivadharshan : CS22B057 `Shiva9361` 
### P Akilesh : CS22B040 `Akileshdash` 
---

# ♟️ Chess Env with Minimax and Alpha-Beta Pruning

This project implements a chess-playing AI using the `minimax` and `alpha-beta pruning` algorithms on top of the [gym-chess](https://github.com/iamlu-coding/gym-chess) environment. The AI evaluates positions using a custom heuristic function based on material count, mobility, and pawn structure.

---

## Features

-  **Minimax** algorithm with depth-based evaluation  
-  **Alpha-Beta Pruning** for faster move search  
-  **Custom Heuristic Function** to evaluate positions  
-  **Timeout Control** to avoid long computations  
-  **SVG Visualization** of gameplay

---


## Clone the Repository

```bash
git clone --recurse-submodules https://github.com/Shiva9361/AI-3.git
cd AI-3
```

---

## Setup Instructions

1. **Create a Virtual Environment (Python ≥ 3.10)**

```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. **Install Dependencies**

```bash
pip3 install -r requirements.txt
```

3. **Run the AI**:
   ```bash
   python chess_.py --algorithm minimax
   ```
   Or use:
   ```bash
   python chess_.py --algorithm alphabeta
   ```

---

## Heuristic Evaluation

The AI scores each chess board position based on:

- **Material Value**:
  Assigns standard values to pieces (Pawn=100, Knight=320, etc.).

- **Mobility**:
  Rewards positions with more legal moves (weighted by 10).

- **Pawn Structure**:
  Penalizes:
  - **Doubled Pawns**: -20 (White), +20 (Black)
  - **Isolated Pawns**: -15 (White), +15 (Black)

Positive scores favor White; negative scores favor Black.

---

## Algorithms

- **Minimax**: Recursively explores moves up to a given depth and chooses the best score assuming optimal opponent play.
- **Alpha-Beta Pruning**: Optimized version of minimax that skips unnecessary branches in the search tree.

---

## Timeout Feature

To prevent long or infinite evaluations, the code uses `func_timeout` to enforce a time limit (default 600 seconds) on move evaluation.

---

## Output

- SVG files of each move step are saved to `gameplay_frames/`  
- Each frame visualizes the board after the corresponding move.

---

## Arguments

| Argument     | Description                            | Default    |
|--------------|----------------------------------------|------------|
| `--algorithm`| Select between `minimax` and `alphabeta`| `minimax`  |

---

## Acknowledgements

- [gym-chess](https://github.com/iamlu-coding/gym-chess)
- [python-chess](https://github.com/niklasf/python-chess)

---

### Slide Deck  : Access [here](https://docs.google.com/presentation/d/1D8ZQTIRZ715QmdwBinPVTuOWpxJJOafepQp6NCMuwbA/edit?usp=sharing)


---

## Requirements

- Python **3.10 or higher**
- GYM no longer works in python 3.12, tested to work with 3.10
- See `requirements.txt` for all package dependencies


