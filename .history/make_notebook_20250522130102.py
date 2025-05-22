#!/usr/bin/env python3
"""
make_notebook.py

Creates "DiSC_stability_notebook.ipynb" with:
  • Clear intro
  • Key formulas (lever arm = R·sin(θ/2))
  • Functions: geometry_from_markers, compute_stability_index, classify, visualize
  • Example runs: symmetric vs. asymmetric vs. low-force
Run:
  pip install nbformat
  python make_notebook.py
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells = [

    # ─────────────────────────  TITLE  ─────────────────────────
    nbf.v4.new_markdown_cell(
        "# DiSC Stability Analysis Notebook\n\n"
        "This notebook analyses how stable a three-pin skull clamp is when you vary\n"
        "• **Pin forces** (from sensors) and\n"
        "• **Pin-to-pin angles** θ (from tracker).\n\n"
        "All maths, code, and example plots are self-contained—just run each cell."
    ),

    # ────────────────────────  KEY FORMULAS  ────────────────────
    nbf.v4.new_markdown_cell(
        "## Key Formulas\n\n"
        "**1. Lever arm for each pin pair**  \n"
        "$$\n"
        "r_i \\;=\\; R\\,\\sin\\!\\Bigl(\\dfrac{\\theta_i}{2}\\Bigr)\n"
        "$$\n"
        "where $\\theta_i$ is the central angle between neighbouring pins.\n\n"
        "**2. Slip torque for that pair**  \n"
        "$$\n"
        "\\tau_i \\;=\\; \\mu\\,F_i\\,r_i\n"
        "$$\n"
        "**3. Reference torque** (ideal 120 ° spacing, same mean force)  \n"
        "$$\n"
        "\\tau_{\\mathrm{ref}} = \\mu\\,F_{\\mathrm{ref}}\\,R\\,\\sin(60^{\\circ})\n"
        "$$\n"
        "**4. Stability index**  \n"
        "$$\n"
        "S_i = \\dfrac{\\tau_i}{\\tau_{\\mathrm{ref}}}\n"
        "$$\n"
        "**Classification**  \n"
        "- $S_i > 1.2$ → **stable**  \n"
        "- $0.8 \\le S_i \\le 1.2$ → **marginal**  \n"
        "- $S_i < 0.8$ → **critical**"
    ),

    # ────────────────────  FUNCTION DEFINITIONS  ───────────────
    nbf.v4.new_code_cell(
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n\n"
        "def geometry_from_markers(skull_center, pin_markers):\n"
        "    \"\"\"Return estimated skull radius, three θ (deg), and each pin distance.\"\"\"\n"
        "    vs    = [np.array(p) - np.array(skull_center) for p in pin_markers]\n"
        "    norms = [np.linalg.norm(v) for v in vs]\n"
        "    R_est = float(np.mean(norms))\n"
        "    thetas = []\n"
        "    for i in range(3):\n"
        "        j = (i + 1) % 3\n"
        "        cosθ = np.dot(vs[i], vs[j]) / (norms[i] * norms[j])\n"
        "        theta = np.arccos(np.clip(cosθ, -1, 1))\n"
        "        thetas.append(np.rad2deg(theta))\n"
        "    return R_est, thetas, norms\n\n"
        "def compute_stability_index(R, mu, forces, thetas_deg):\n"
        "    \"\"\"Return per-pair torques and normalised stability S.\"\"\"\n"
        "    thetas = np.deg2rad(thetas_deg)\n"
        "    r      = R * np.sin(thetas / 2)           # lever arms\n"
        "    torq   = mu * np.array(forces) * r        # slip torques\n"
        "    # reference torque for ideal 120 ° at same mean force\n"
        "    tau_ref = mu * np.mean(forces) * R * np.sin(np.deg2rad(60))\n"
        "    S = torq / tau_ref\n"
        "    return torq, S\n\n"
        "def classify_stability(S, thr=(0.8, 1.2)):\n"
        "    out = []\n"
        "    for s in S:\n"
        "        out.append('stable'   if s > thr[1] else\n"
        "                    'marginal' if s >= thr[0] else\n"
        "                    'critical')\n"
        "    return out\n\n"
        "def visualize_stability(R, thetas_deg, S, thr=(0.8,1.2)):\n"
        "    \"\"\"Plot pin layout and bar chart of S.\"\"\"\n"
        "    # pin positions for picture\n"
        "    acc = 0.0\n"
        "    cum = [0.0]\n"
        "    for θ in thetas_deg[:-1]:\n"
        "        acc += θ\n"
        "        cum.append(acc)\n"
        "    ang = np.deg2rad(cum)\n"
        "    xs, ys = R*np.cos(ang), R*np.sin(ang)\n"
        "    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9,4))\n"
        "    ax1.add_artist(plt.Circle((0,0),R,fill=False))\n"
        "    ax1.scatter(xs,ys)\n"
        "    for i,(x,y) in enumerate(zip(xs,ys),1): ax1.text(x,y,str(i))\n"
        "    ax1.set_aspect('equal'); ax1.set_title('Pin layout')\n"
        "    ax2.bar(range(1,4),S)\n"
        "    ax2.axhline(thr[0],ls='--'); ax2.axhline(thr[1],ls='--')\n"
        "    ax2.set_xlabel('Pin pair'); ax2.set_ylabel('S')\n"
        "    ax2.set_title('Stability index'); plt.tight_layout()\n"
    ),

    # ───────────────────  EXAMPLE RUNS  ────────────────────────
    nbf.v4.new_markdown_cell(
        "## Example Configurations\n"
        "We compare three cases:\n"
        "- *Symmetric*: all θ=120 °, forces=100 N  \n"
        "- *Low force*: θ still 120 °, forces=60 N  \n"
        "- *Asymmetric*: θ=100/130/130 °, forces=100 N"
    ),
    nbf.v4.new_code_cell(
        "R=0.1              # 100 mm skull in metres for plots\n"
        "mu=0.3\n"
        "cases={\n"
        "  'Symmetric (120°,100 N)' : ([120,120,120],[100,100,100]),\n"
        "  'Low-force (120°,60 N)' : ([120,120,120],[60,60,60]),\n"
        "  'Asymmetric (100/130/130°,100 N)':([100,130,130],[100,100,100])\n"
        "}\n"
        "for title,(θs,Fs) in cases.items():\n"
        "    print(f'\\n## {title}')\n"
        "    torq,S=compute_stability_index(R,mu,Fs,θs)\n"
        "    for i,(s) in enumerate(S,1): print(f'  Pair {i}: S={s:.2f}')\n"
        "    visualize_stability(R,θs,S)\n"
    ),
]

with open('DiSC_stability_notebook.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print('Notebook created: DiSC_stability_notebook.ipynb')
