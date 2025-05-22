# Digital Skull Clamp (DiSC) — Stability Toolkit

This is a lightweight, self-contained Python toolkit and Jupyter notebook that helps you:

- Read pin forces (from sensors) and pin angles (from tracker)
- Compute a **Stability Index (SI)** for each pin pair
- Classify each gap as **stable / marginal / critical**
- Visualize stability results with simple 2D and 3D plots
- Use a refined model that incorporates pin geometry and angle-dependent torque

---

## 📁 Project Structure

```
📦 disc-stability/
 ├─ notebooks/
 │   ├─ DiSC_stability_notebook.ipynb          ← basic lever-arm model
 │   └─ DiSC_advanced_stability_notebook.ipynb ← refined model (no shear)
 ├─ src/
 │   ├─ simple_model.py        ← basic torque model
 │   └─ advanced_model.py      ← improved geometry-based model
 ├─ make_notebook.py           ← creates notebooks from source
 ├─ examples/                  ← test CSV files
 ├─ requirements.txt
 └─ LICENSE
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/HamedShabani/DiSC
cd DiSC

python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
jupyter notebook notebooks/DiSC_advanced_stability_notebook.ipynb
```

The functions are already in the Notebooks for simplicity. They can be transfered to antoher file later
---

## 🧠 Stability Model: Core Math

| Symbol | Meaning                             | Units              |
|--------|-------------------------------------|--------------------|
| `R`    | Skull radius                        | meters (e.g. 0.1)  |
| `θᵢ`   | Angle between pins _i_ and _i+1_    | degrees            |
| `Fᵢ`   | Clamping force at pin _i_           | N                  |
| `μ`    | Friction coefficient (typ. ≈ 0.3)   | –                  |

### Equations:
- Lever arm:   `rᵢ = R · sin(θᵢ / 2)`
- Grip force:   `F_grip = μ · Fᵢ`
- Torque:     `τᵢ = F_grip · rᵢ`
- Reference torque (ideal 120° layout):  
  `τ_ref = μ · F_avg · R · sin(60°)`
- Stability Index: `Sᵢ = τᵢ / τ_ref`

### Classification:
- `Sᵢ > 1.2` → ✅ **Stable**  
- `0.8 ≤ Sᵢ ≤ 1.2` → ⚠️ **Marginal**  
- `Sᵢ < 0.8` → ❌ **Critical**

---

## 🔍 Code Example

```python


R = 0.10
mu = 0.3
forces = [100, 100, 100]
angles = [120, 120, 120]

_, S = compute_stability_index(R, mu, forces, angles)
print(S)  # Output: [1.0, 1.0, 1.0]
```

---

## 📦 Requirements

- Python ≥ 3.8  
- numpy  
- matplotlib  
- nbformat  

Install with:
```bash
pip install -r requirements.txt
```

---

## 📄 License

MIT License — see the `LICENSE` file.

---


