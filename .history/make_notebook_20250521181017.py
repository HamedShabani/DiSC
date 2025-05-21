import nbformat as nbf
## Key Formulas

**Lever arm** per pin:

$$
r_i \;=\; R \,\sin\!\Bigl(\frac{\theta_i}{2}\Bigr)
$$

**Slip torque** per pin:

$$
\tau_i \;=\; \mu\,F_i\,r_i
$$

**Reference torque** (ideal symmetric 120° layout):

$$
\tau_{\mathrm{ref}}
\;=\;
\mu\,F_{\mathrm{ref}}\,R\,\sin(60^\circ)
$$

**Stability index**:

$$
S_i \;=\; \frac{\tau_i}{\tau_{\mathrm{ref}}}
$$

**Classification**  
- \(S_i > 1.2\): **stable**  
- \(0.8 \le S_i \le 1.2\): **marginal**  
- \(S_i < 0.8\): **critical**  

# Create a new notebook
nb = nbf.v4.new_notebook()

# Define cells
nb.cells = [
    # Title and introduction
    nbf.v4.new_markdown_cell(
        "# DiSC Stability Analysis Notebook\n"
        "\n"
        "This Jupyter notebook provides a **comprehensive analysis** of the Digital Skull Clamp (DiSC) stability criteria. "
        "It includes:\n"
        "1. Mathematical model and key formulas\n"
        "2. Python functions for geometry, stability index, classification, and visualization\n"
        "3. Example runs over multiple configurations\n"
        "4. Sensitivity analysis and plots\n"
        "\n"
        "Use the toolbar to run each cell in order."
    ),
    # Formulas cell
    nbf.v4.new_markdown_cell(
        "## Key Formulas\n"
        "\n"
        "**Lever arm** per pin:\n"
        "\\[\n"
        "r_i = R \\sin\\left(\\frac{\\theta_i}{2}\\right)\n"
        "\\]\n"
        "\n"
        "**Slip torque** per pin:\n"
        "\\[\n"
        "\\tau_i = \\mu F_i r_i\n"
        "\\]\n"
        "\n"
        "**Reference torque** (ideal symmetric 120° layout):\n"
        "\\[\n"
        "\\tau_{\\mathrm{ref}} = \\mu F_{\\mathrm{ref}} R \\sin\\left(60°\\right)\n"
        "\\]\n"
        "\n"
        "**Stability index**:\n"
        "\\[\n"
        "S_i = \\frac{\\tau_i}{\\tau_{\\mathrm{ref}}}\n"
        "\\]\n"
        "\n"
        "**Classification**:\n"
        "- $S_i > 1.2$: stable\n"
        "- $0.8 \\le S_i \\le 1.2$: marginal\n"
        "- $S_i < 0.8$: critical\n"
    ),
    # Imports and function definitions
    nbf.v4.new_code_cell(
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n\n"
        "def geometry_from_markers(skull_center, pin_markers):\n"
        "    vs = [np.array(p) - np.array(skull_center) for p in pin_markers]\n"
        "    norms = [np.linalg.norm(v) for v in vs]\n"
        "    R_est = float(np.mean(norms))\n"
        "    thetas = []\n"
        "    for i in range(3):\n"
        "        j = (i + 1) % 3\n"
        "        cos_theta = np.dot(vs[i], vs[j]) / (norms[i] * norms[j])\n"
        "        theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))\n"
        "        thetas.append(np.rad2deg(theta))\n"
        "    return R_est, thetas, norms\n\n"
        "def compute_stability_index(R, mu, forces, thetas_deg):\n"
        "    thetas = np.deg2rad(thetas_deg)\n"
        "    lever_arms = R * np.sin(thetas / 2)\n"
        "    torques = mu * np.array(forces) * lever_arms\n"
        "    theta_ref = np.deg2rad(120)\n"
        "    F_ref = np.mean(forces)\n"
        "    r_ref = R * np.sin(theta_ref / 2)\n"
        "    tau_ref = mu * F_ref * r_ref\n"
        "    S = torques / tau_ref\n"
        "    return torques, S\n\n"
        "def classify_stability(S, thresholds=(0.8, 1.2)):\n"
        "    labels = []\n"
        "    for s in S:\n"
        "        if s > thresholds[1]: labels.append(\"stable\")\n"
        "        elif s >= thresholds[0]: labels.append(\"marginal\")\n"
        "        else: labels.append(\"critical\")\n"
        "    return labels\n\n"
        "def visualize_stability(R, thetas_deg, S, thresholds=(0.8, 1.2)):\n"
        "    # Compute cumulative angles\n"
        "    acc = 0.0\n"
        "    angles = [0.0]\n"
        "    for theta in thetas_deg[:-1]:\n"
        "        acc += theta\n"
        "        angles.append(acc)\n"
        "    angles_rad = np.deg2rad(angles)\n"
        "    xs = R * np.cos(angles_rad)\n"
        "    ys = R * np.sin(angles_rad)\n"
        "    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))\n"
        "    circle = plt.Circle((0, 0), R, fill=False)\n"
        "    ax1.add_artist(circle)\n"
        "    ax1.scatter(xs, ys)\n"
        "    for i, (x, y) in enumerate(zip(xs, ys), start=1): ax1.text(x, y, str(i))\n"
        "    ax1.set_aspect('equal'); ax1.set_title('Pin positions (top view)')\n"
        "    ax2.bar(np.arange(1, len(S)+1), S)\n"
        "    ax2.axhline(thresholds[0], linestyle='--')\n"
        "    ax2.axhline(thresholds[1], linestyle='--')\n"
        "    ax2.set_xlabel('Pin'); ax2.set_ylabel('Stability index S_i')\n"
        "    plt.tight_layout()\n"
    ),
    # Example runs over multiple conditions
    nbf.v4.new_code_cell(
        "R = 0.1  # 100 mm\n"
        "mu = 0.3\n"
        "cases = {\n"
        "    'Symmetric (120°/120°/120°, 100 N)': ([120, 120, 120], [100, 100, 100]),\n"
        "    'Low Force (120°/120°/120°, 60 N)': ([120, 120, 120], [60, 60, 60]),\n"
        "    'Asymmetric (100°/130°/130°, 100 N)': ([100, 130, 130], [100, 100, 100]),\n"
        "}\n"
        "for name, (thetas, forces) in cases.items():\n"
        "    print(f\"## {name}\")\n"
        "    R_est, th, r = geometry_from_markers([0,0,0], [[R,0,0],[0,R,0],[ -R,0,0]])\n"
        "    torques, S = compute_stability_index(R_est, mu, forces, thetas)\n"
        "    labels = classify_stability(S)\n"
        "    for i, (s, lab) in enumerate(zip(S, labels), start=1):\n"
        "        print(f\"Pin {i}: S={s:.2f} → {lab}\")\n"
        "    visualize_stability(R_est, thetas, S)\n"
    ),
]

# … earlier cells definition …

# Write notebook to file in the local folder
notebook_path = 'DiSC_stability_notebook.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at: {notebook_path}")

