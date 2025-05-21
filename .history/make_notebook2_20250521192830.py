import nbformat as nbf

# Create a new notebook
nb = nbf.v4.new_notebook()

# Define cells
nb.cells = [
    nbf.v4.new_markdown_cell("# Advanced DiSC Stability Analysis Notebook\n"
                             "\n"
                             "This notebook extends the basic stability model with a more realistic evaluation function\n"
                             "`evaluate_clamp_basic`, which computes a **Stability Index (SI)** based on:\n"
                             "- Resultant moment (Mz) caused by pin forces\n"
                             "- Penetration depth differences (Δd)\n"
                             "- Exponential decay terms to combine both effects\n"
                             "\n"
                             "We will explore advantages of this model, run examples, and visualize the SI surface."),
    nbf.v4.new_markdown_cell("## Mathematical Model\n"
                             "\n"
                             "1. **Moment about z-axis**\n"
                             "\\[\n"
                             "M_z = \\sum_{i=1}^3 (\\mathbf{r}_i \\times \\mathbf{F}_i)_z\n"
                             "\\]\n"
                             "\n"
                             "2. **Penetration depth** per pin:\n"
                             "\\[\n"
                             "d_i = k_{depth} \\; |F_{i}|,\n"
                             "\\quad Δd = \\max_i d_i - \\min_i d_i\n"
                             "\\]\n"
                             "\n"
                             "3. **Stability Index (SI)**:\n"
                             "\\[\n"
                             "SI = \\exp\\bigl(-|M_z|/M_{crit}\\bigr) \\; \\times \\; \\exp\\bigl(-Δd / d_{crit}\\bigr)\n"
                             "\\]"),
    nbf.v4.new_code_cell("import numpy as np\n"
                         "import matplotlib.pyplot as plt\n"
                         "from mpl_toolkits.mplot3d import Axes3D  # registers the 3D projection\n\n"
                         "def evaluate_clamp_basic(forces_N, phis_deg,\n"
                         "                         skull_R=85.0,\n"
                         "                         k_depth=0.04,\n"
                         "                         Mcrit=50.0,\n"
                         "                         dcrit=1.0):\n"
                         "    \"\"\"\n"
                         "    Compute the Stability Index (SI) for a three-pin clamp\n"
                         "    forces_N : list of 3 normal forces [N]\n"
                         "    phis_deg : list of 3 pin angles [deg]\n"
                         "    skull_R   : radius of skull [mm]\n"
                         "    k_depth   : depth coefficient [mm/N]\n"
                         "    Mcrit     : moment scaling constant [N·mm]\n"
                         "    dcrit     : depth scaling constant [mm]\n"
                         "    Returns\n"
                         "    -------\n"
                         "    SI        : stability index (dimensionless)\n"
                         "    \"\"\"\n"
                         "    phis = np.deg2rad(phis_deg)\n"
                         "    # pin position vectors\n"
                         "    r = np.stack([\n"
                         "        skull_R * np.cos(phis),\n"
                         "        skull_R * np.sin(phis),\n"
                         "        np.zeros_like(phis)\n"
                         "    ], axis=1)\n"
                         "    r_hat = r / np.linalg.norm(r, axis=1)[:, None]\n"
                         "    forces = np.asarray(forces_N, float)\n"
                         "    F_vec = np.array([-forces[i] * r_hat[i] for i in range(3)])\n"
                         "    Mz = np.cross(r, F_vec)[:, 2].sum()\n"
                         "    depths = k_depth * np.abs((F_vec * r_hat).sum(axis=1))\n"
                         "    delta_d = depths.ptp()\n"
                         "    SI = np.exp(-abs(Mz) / Mcrit) * np.exp(-delta_d / dcrit)\n"
                         "    return SI\n"),
    nbf.v4.new_markdown_cell("## Example Single Case\n"
                             "\n"
                             "Compute the SI for a symmetric clamp and an asymmetric clamp:"),
    nbf.v4.new_code_cell("# Symmetric configuration\n"
                         "SI_sym = evaluate_clamp_basic([100, 100, 100], [0, 120, 240])\n"
                         "print(f\"Symmetric SI = {SI_sym:.3f}\")\n\n"
                         "# Asymmetric configuration\n"
                         "SI_asym = evaluate_clamp_basic([100, 100, 100], [0, 100, 260])\n"
                         "print(f\"Asymmetric SI = {SI_asym:.3f}\")"),
    nbf.v4.new_markdown_cell("## Surface Visualization over Force Grid (Pin C fixed)\n"
                             "\n"
                             "Explore SI as forces on pins A and B vary."),
    nbf.v4.new_code_cell(
        "# 3D surface for SI over (F_A, F_B)\n"
        "force_min, force_max, N = 20, 200, 60\n"
        "fA = np.linspace(force_min, force_max, N)\n"
        "fB = np.linspace(force_min, force_max, N)\n"
        "FA, FB = np.meshgrid(fA, fB)\n"
        "FC = 120.0\n"
        "Z = np.zeros_like(FA)\n"
        "for i in range(N):\n"
        "    for j in range(N):\n"
        "        Z[i, j] = evaluate_clamp_basic([FA[i, j], FB[i, j], FC], [0, 120, 240])\n"
        "norm_Z = (Z - Z.min()) / (Z.max() - Z.min())\n"
        "colors = plt.cm.plasma(norm_Z)\n"
        "fig = plt.figure(figsize=(8, 6))\n"
        "ax = fig.add_subplot(111, projection='3d')\n"
        "surf = ax.plot_surface(FA, FB, Z, facecolors=colors, rstride=1, cstride=1,\n"
        "                        edgecolor='k', linewidth=0.2, antialiased=True)\n"
        "ax.set_xlabel('Force A [N]')\n"
        "ax.set_ylabel('Force B [N]')\n"
        "ax.set_zlabel('SI')\n"
        "ax.set_title('SI Surface (Pin C = 120 N)')\n"
        "plt.show()"
    )
]

# Write notebook to file
notebook_path = 'DiSC_advanced_stability_notebook.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at: {notebook_path}")
