#!/usr/bin/env python3
"""
make_notebook.py

Generates a Jupyter notebook "DiSC_advanced_stability_notebook.ipynb" that:
  - Introduces the advanced Stability Index model
  - Shows all key formulas in LaTeX ($$ … $$) so they render correctly
  - Includes the `evaluate_clamp_basic` function
  - Runs single-case examples and a 3D surface visualization
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells = [
    # Title cell
    nbf.v4.new_markdown_cell(
        "# Advanced DiSC Stability Analysis Notebook\n"
        "\n"
        "This notebook implements a more realistic **Stability Index (SI)** model for the\n"
        "Digital Skull Clamp (DiSC), combining both moment-based and penetration-depth effects."
    ),

    # Formulas cell with proper $$ delimiters
    nbf.v4.new_markdown_cell(
        "## Mathematical Model & Key Formulas\n"
        "\n"
        "1. **Moment about z-axis**\n"
        "$$\n"
        "M_z = \\sum_{i=1}^3 \\bigl(\\mathbf{r}_i \\times \\mathbf{F}_i\\bigr)_z\n"
        "$$\n"
        "\n"
        "2. **Penetration depth** per pin and range:\n"
        "$$\n"
        "d_i = k_{\\rm depth} \\; |F_i|,\n"
        "\\quad \\Delta d = \\max_i d_i - \\min_i d_i\n"
        "$$\n"
        "\n"
        "3. **Stability Index (SI)** (product of two exponential decays):\n"
        "$$\n"
        "SI = \\exp\\biggl(-\\frac{|M_z|}{M_{\\rm crit}}\\biggr) \\times "
        "\\exp\\biggl(-\\frac{\\Delta d}{d_{\\rm crit}}\\biggr)\n"
        "$$\n"
    ),

    # Code cell: function definition
    nbf.v4.new_code_cell(
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "from mpl_toolkits.mplot3d import Axes3D  # for 3D plotting\n\n"
        "def evaluate_clamp_basic(forces_N, phis_deg,\n"
        "                         skull_R=85.0,\n"
        "                         k_depth=0.04,\n"
        "                         Mcrit=50.0,\n"
        "                         dcrit=1.0):\n"
        "    \"\"\"\n"
        "    Compute the Stability Index (SI) for a three-pin clamp.\n"
        "    - forces_N : [F1, F2, F3] normal forces in N\n"
        "    - phis_deg : [ϕ1, ϕ2, ϕ3] pin angles in degrees\n"
        "    - skull_R   : skull radius (same units as depth, default 85 mm)\n"
        "    - k_depth   : coefficient converting force to penetration depth (depth per N)\n"
        "    - Mcrit     : characteristic moment scaling (same units as M_z)\n"
        "    - dcrit     : characteristic depth scaling (same units as depth)\n"
        "    Returns\n"
        "    -------\n"
        "    SI : float\n"
        "        Dimensionless stability index\n"
        "    \"\"\"\n"
        "    # --- compute pin vectors ---\n"
        "    phis = np.deg2rad(phis_deg)\n"
        "    r = np.stack([\n"
        "        skull_R * np.cos(phis),\n"
        "        skull_R * np.sin(phis),\n"
        "        np.zeros_like(phis)\n"
        "    ], axis=1)\n"
        "    # unit normals from skull center\n"
        "    r_hat = r / np.linalg.norm(r, axis=1)[:, None]\n"
        "\n"
        "    # force vectors inward\n"
        "    forces = np.asarray(forces_N, float)\n"
        "    F_vec = np.array([-forces[i] * r_hat[i] for i in range(3)])\n"
        "\n"
        "    # moment about z-axis\n"
        "    Mz = np.cross(r, F_vec)[:, 2].sum()\n"
        "\n"
        "    # penetration depths and range\n"
        "    depths = k_depth * np.abs((F_vec * r_hat).sum(axis=1))\n"
        "    delta_d = depths.ptp()\n"
        "\n"
        "    # Stability Index\n"
        "    SI = np.exp(-abs(Mz) / Mcrit) * np.exp(-delta_d / dcrit)\n"
        "    return SI\n"
    ),

    # Markdown cell: explain advantage
    nbf.v4.new_markdown_cell(
        "### Why this model?\n"
        "- **Includes moment balance**: directly penalizes large resultant torques\n"
        "- **Accounts for depth asymmetry**: ensures all pins penetrate uniformly\n"
        "- **Exponential combination**: smoothly blends both effects into one index\n"
    ),

    # Code cell: single-case examples
    nbf.v4.new_code_cell(
        "# Single-case examples\n"
        "SI_sym = evaluate_clamp_basic([100,100,100], [0,120,240])\n"
        "SI_asym = evaluate_clamp_basic([100,100,100], [0,100,260])\n"
        "print(f\"Symmetric SI  = {SI_sym:.3f}\")\n"
        "print(f\"Asymmetric SI = {SI_asym:.3f}\")"
    ),

    # Markdown cell: surface visualization intro
    nbf.v4.new_markdown_cell(
        "## 3D Surface over (Force A, Force B)\n"
        "Fix Pin C at 120 N and vary forces on A and B.  \n"
        "Visualize how the Stability Index changes in the plane."
    ),

    # Code cell: 3D plot
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
        "\n"
        "norm_Z = (Z - Z.min())/(Z.max()-Z.min())\n"
        "colors = plt.cm.plasma(norm_Z)\n"
        "\n"
        "fig = plt.figure(figsize=(8,6))\n"
        "ax = fig.add_subplot(111, projection='3d')\n"
        "surf = ax.plot_surface(FA, FB, Z, facecolors=colors,\n"
        "                       rstride=1, cstride=1, edgecolor='k', linewidth=0.2)\n"
        "ax.set_xlabel('Force A [N]')\n"
        "ax.set_ylabel('Force B [N]')\n"
        "ax.set_zlabel('SI')\n"
        "ax.set_title('SI Surface (Pin C = 120 N)')\n"
        "plt.show()"
    ),
]

# Write to disk
with open('DiSC_advanced_stability_notebook.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Created DiSC_advanced_stability_notebook.ipynb")
