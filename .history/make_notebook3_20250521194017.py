import nbformat as nbf

# Create a new notebook object
nb = nbf.v4.new_notebook()

# Define the notebook cells
nb.cells = [
    # Title
    nbf.v4.new_markdown_cell(
        "# Advanced DiSC Stability Analysis Notebook\n\n"
        "This notebook implements a more realistic **Stability Index (SI)** model for the\n"
        "Digital Skull Clamp (DiSC), combining both twisting moments and uneven pin depths."
    ),
    # Key formulas
    nbf.v4.new_markdown_cell(
        "## Mathematical Model & Key Formulas\n\n"
        "1. **Moment about z-axis**  \n"
        "$$\n"
        "M_z = \\sum_{i=1}^3 \\bigl(\\mathbf{r}_i \\times \\mathbf{F}_i\\bigr)_z\n"
        "$$\n\n"
        "2. **Penetration depth** per pin and range:  \n"
        "$$\n"
        "d_i = k_{\\rm depth} \\; |F_i|,\n"
        "\\quad \\Delta d = \\max_i d_i - \\min_i d_i\n"
        "$$\n\n"
        "3. **Stability Index (SI)**:  \n"
        "$$\n"
        "SI = \\exp\\biggl(-\\frac{|M_z|}{M_{\\rm crit}}\\biggr) \\times "
        "\\exp\\biggl(-\\frac{\\Delta d}{d_{\\rm crit}}\\biggr)\n"
        "$$\n"
    ),
    # Function definition
    nbf.v4.new_code_cell(
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "from mpl_toolkits.mplot3d import Axes3D\n\n"
        "def evaluate_clamp_basic(forces_N, phis_deg,\n"
        "                         skull_R=85.0,\n"
        "                         k_depth=0.04,\n"
        "                         Mcrit=50.0,\n"
        "                         dcrit=1.0):\n"
        "    \"\"\"\n"
        "    Compute the Stability Index (SI) for a three-pin clamp.\n"
        "    Inputs:\n"
        "      - forces_N: [F1, F2, F3] forces from sensors (N)\n"
        "      - phis_deg: [ϕ1, ϕ2, ϕ3] pin angles from tracker (deg)\n"
        "      - skull_R: radius of skull (mm)\n"
        "      - k_depth: mm of penetration per N of force\n"
        "      - Mcrit: moment scaling constant\n"
        "      - dcrit: depth-range scaling constant\n"
        "    Returns:\n"
        "      - SI: stability index (0–1)\n"
        "    \"\"\"\n"
        "    phis = np.deg2rad(phis_deg)\n"
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
        "    return SI\n"
    ),
    # Why this model
    nbf.v4.new_markdown_cell(
        "### Why this model?\n"
        "- **Twisting force (moment)**: captures how pins can twist the clamp off if forces are unbalanced.\n"
        "- **Penetration depth**: ensures all pins sink equally; uneven depths let the clamp wobble.\n"
        "- **Combined index**: SI goes down if either twisting or depth imbalance grows."
    ),
    # Simple explanation for depth
    nbf.v4.new_markdown_cell(
        "### What is penetration depth?\n"
        "- When you push a pin in with some force, it sinks a bit into the skull (or phantom).\n"
        "- We **estimate** that sink amount by:  \n"
        "  $$d_i = k_{\\rm depth}\\times F_i$$  \n"
        "  where **k_depth** (e.g. 0.04 mm/N) converts force to millimeters of penetration.\n"
        "- The difference $$\\Delta d = \\max_i d_i - \\min_i d_i$$ shows how unevenly the pins sit.\n"
        "- **Data source**: all from your **force sensors**—the tracker only gives pin angles."
    ),
    # Single-case examples
    nbf.v4.new_code_cell(
        "# Single-case examples\n"
        "SI_sym = evaluate_clamp_basic([100,100,100], [0,120,240])\n"
        "SI_asym = evaluate_clamp_basic([100,100,100], [0,100,260])\n"
        "print(f\"Symmetric SI  = {SI_sym:.3f}\")\n"
        "print(f\"Asymmetric SI = {SI_asym:.3f}\")"
    ),
    # Surface visualization intro
    nbf.v4.new_markdown_cell(
        "## 3D Stability Surface\n"
        "Fix Pin C = 120 N, vary forces on A/B, and see SI change."
    ),
    # 3D surface code
    nbf.v4.new_code_cell(
        "force_min, force_max, N = 20, 200, 60\n"
        "fA = np.linspace(force_min, force_max, N)\n"
        "fB = np.linspace(force_min, force_max, N)\n"
        "FA, FB = np.meshgrid(fA, fB)\n"
        "FC = 120.0\n"
        "Z = np.zeros_like(FA)\n"
        "for i in range(N):\n"
        "    for j in range(N):\n"
        "        Z[i,j] = evaluate_clamp_basic([FA[i,j], FB[i,j], FC], [0,120,240])\n"
        "norm_Z = (Z - Z.min())/(Z.max()-Z.min())\n"
        "colors = plt.cm.plasma(norm_Z)\n"
        "fig = plt.figure(figsize=(8,6))\n"
        "ax = fig.add_subplot(111, projection='3d')\n"
        "ax.plot_surface(FA, FB, Z, facecolors=colors, rstride=1, cstride=1, edgecolor='k')\n"
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
