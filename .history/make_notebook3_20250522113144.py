import nbformat as nbf

# Create a new notebook object
nb = nbf.v4.new_notebook()

# Define the notebook cells
nb.cells = [
    # Title
    nbf.v4.new_markdown_cell(
        "# Advanced DiSC Stability Analysis Notebook\n\n"
        "This notebook implements a realistic **Stability Index (SI)** model for the\n"
        "Digital Skull Clamp (DiSC). It combines twisting moments, uneven pin depths,\n"
        "and an optional global shear force so pin angles (`phis_deg`) matter."
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
        "3. **Global shear force** applied along +X so angles matter  \n"
        "$$\n"
        "\\mathbf{F}_{\\rm shear} = [F_{\\rm shear}, 0, 0]\n"
        "$$\n\n"
        "4. **Stability Index (SI)**:  \n"
        "$$\n"
        "SI = \\exp\\biggl(-\\frac{|M_z|}{M_{\\rm crit}}\\biggr) \\times "
        "\\exp\\biggl(-\\frac{\\Delta d}{d_{\\rm crit}}\\biggr)\n"
        "$$\n"
    ),
    # Function definition with global shear
    nbf.v4.new_code_cell(
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "from mpl_toolkits.mplot3d import Axes3D\n\n"
        "def evaluate_clamp_basic(forces_N, phis_deg,\n"
        "                         skull_R=85.0,\n"
        "                         k_depth=0.04,\n"
        "                         Mcrit=50.0,\n"
        "                         dcrit=1.0,\n"
        "                         F_shear=0.0):\n"
        "    \"\"\"\n"
        "    Compute Stability Index (SI) for a three-pin clamp.\n"
        "    Inputs:\n"
        "      - forces_N: [F1, F2, F3] normal forces (N)\n"
        "      - phis_deg: [ϕ1, ϕ2, ϕ3] pin angles (deg)\n"
        "      - skull_R: radius (mm)\n"
        "      - k_depth: mm per N\n"
        "      - Mcrit: moment scale\n"
        "      - dcrit: depth-scale\n"
        "      - F_shear: global shear force along +X (N)\n"
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
        "    shear_vec = np.array([F_shear, 0.0, 0.0])\n"
        "    forces = np.asarray(forces_N, float)\n"
        "    F_vec = np.array([-forces[i] * r_hat[i] + shear_vec for i in range(3)])\n"
        "    Mz = np.cross(r, F_vec)[:, 2].sum()\n"
        "    depths = k_depth * np.abs((F_vec * r_hat).sum(axis=1))\n"
        "    delta_d = depths.ptp()\n"
        "    SI = np.exp(-abs(Mz) / Mcrit) * np.exp(-delta_d / dcrit)\n"
        "    return SI\n"
    ),
    # Explanation for global shear
    nbf.v4.new_markdown_cell(
        "### How pin angles now matter\n"
        "- We apply one **global shear force** along X instead of per-pin tangential.\n"
        "- Different pin angles produce different twisting moments via `r × F_shear`.\n"
        "- Now, when `F_shear > 0`, changing `phis_deg` yields different SI values."
    ),
    # Test code cell
    nbf.v4.new_code_cell(
        "# Test with and without shear, and two angle sets\n"
        "for shear in (0.0, 10.0):\n"
        "    print(f\"F_shear = {shear} N\")\n"
        "    for phis in ([0, 120, 240], [0, 100, 260]):\n"
        "        SI = evaluate_clamp_basic([100,100,100], phis, F_shear=shear)\n"
        "        print(f\"  phis={phis} -> SI = {SI:.3f}\")"
    ),
    # Visualization
    nbf.v4.new_markdown_cell(
        "## Compare Stability Surfaces\n"
        "Side-by-side 3D plots for Pin C fixed at 100 N."
    ),
    nbf.v4.new_code_cell(
        "force_min, force_max, N = 20, 200, 40\n"
        "fA = np.linspace(force_min, force_max, N)\n"
        "fB = np.linspace(force_min, force_max, N)\n"
        "FC = 100.0\n"
        "fig = plt.figure(figsize=(16,6))\n"
        "for idx, shear in enumerate((0.0, 20.0), start=1):\n"
        "    ax = fig.add_subplot(1, 2, idx, projection='3d')\n"
        "    FA, FB = np.meshgrid(fA, fB)\n"
        "    Z = np.zeros_like(FA)\n"
        "    for i in range(N):\n"
        "        for j in range(N):\n"
        "            Z[i,j] = evaluate_clamp_basic([FA[i,j], FB[i,j], FC], [0,120,240], F_shear=shear)\n"
        "    norm_Z = (Z - Z.min())/(Z.max()-Z.min())\n"
        "    colors = plt.cm.plasma(norm_Z)\n"
        "    ax.plot_surface(FA, FB, Z, facecolors=colors, rstride=1, cstride=1, edgecolor='k')\n"
        "    ax.set_title(f\"F_shear={shear} N\")\n"
        "    ax.set_xlabel('Force A [N]')\n"
        "    ax.set_ylabel('Force B [N]')\n"
        "    ax.set_zlabel('SI')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    )
]

# Write notebook to file
notebook_path = 'DiSC_advanced_stability_notebook.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at: {notebook_path}")


# Write notebook to file
notebook_path = 'DiSC_advanced_stability_notebook_phys_deg.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at: {notebook_path}")
