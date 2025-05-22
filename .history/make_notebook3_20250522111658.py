import nbformat as nbf

# Create a new notebook object
nb = nbf.v4.new_notebook()

# Define the notebook cells
nb.cells = [
    # Title
    nbf.v4.new_markdown_cell(
        "# Advanced DiSC Stability Analysis Notebook\n\n"
        "This notebook implements a more realistic **Stability Index (SI)** model for the\n"
        "Digital Skull Clamp (DiSC), combining both twisting moments, uneven pin depths,\n"
        "and optional tangential loads so pin angles (`phis_deg`) matter."
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
        "3. **Optional tangential load** adds a sideways force so angles matter\n\n"
        "4. **Stability Index (SI)**:  \n"
        "$$\n"
        "SI = \\exp\\biggl(-\\frac{|M_z|}{M_{\\rm crit}}\\biggr) \\times "
        "\\exp\\biggl(-\\frac{\\Delta d}{d_{\\rm crit}}\\biggr)\n"
        "$$\n"
    ),
    # Function definition with F_shear
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
        "      - forces_N: [F1, F2, F3] forces from sensors (N)\n"
        "      - phis_deg: [ϕ1, ϕ2, ϕ3] pin angles from tracker (deg)\n"
        "      - skull_R: radius of skull (mm)\n"
        "      - k_depth: mm of penetration per N of force\n"
        "      - Mcrit: moment scaling constant\n"
        "      - dcrit: depth-range scaling constant\n"
        "      - F_shear: optional tangential force (N) at each pin\n"
        "    Returns:\n"
        "      - SI: stability index (0–1)\n"
        "    \"\"\"\n"
        "    # angles in radians\n"
        "    phis = np.deg2rad(phis_deg)\n"
        "    # radial position vectors\n"
        "    r = np.stack([\n"
        "        skull_R * np.cos(phis),\n"
        "        skull_R * np.sin(phis),\n"
        "        np.zeros_like(phis)\n"
        "    ], axis=1)\n"
        "    # unit radial directions\n"
        "    r_hat = r / np.linalg.norm(r, axis=1)[:, None]\n"
        "    # tangential unit directions (perpendicular in plane)\n"
        "    t_hat = np.stack([-np.sin(phis), np.cos(phis), np.zeros_like(phis)], axis=1)\n"
        "    # build force vectors: radial + optional shear\n"
        "    forces = np.asarray(forces_N, float)\n"
        "    F_vec = np.array([-forces[i] * r_hat[i] + F_shear * t_hat[i] for i in range(3)])\n"
        "    # moment about z-axis\n"
        "    Mz = np.cross(r, F_vec)[:, 2].sum()\n"
        "    # penetration depths\n"
        "    depths = k_depth * np.abs((F_vec * r_hat).sum(axis=1))\n"
        "    delta_d = depths.ptp()\n"
        "    # Stability Index\n"
        "    SI = np.exp(-abs(Mz) / Mcrit) * np.exp(-delta_d / dcrit)\n"
        "    return SI\n"
    ),
    # Explanation cell
    nbf.v4.new_markdown_cell(
        "### How angles (phis) now matter\n"
        "- We added an optional **tangential force** $F_{shear}$ at each pin, perpendicular to the pin axis.\n"
        "- The tangential force creates a non-zero moment $M_z$ via $\\mathbf r_i \\times \\mathbf F_i$.\n"
        "- By setting `F_shear > 0`, different pin angles ϕ lead to different twisting moments and SI < 1.\n"
    ),
    # Test unequal phi with shear
    nbf.v4.new_code_cell(
        "# Test phis with and without shear\n"
        "for shear in (0.0, 10.0):\n"
        "    print(f\"F_shear = {shear}\")\n"
        "    for phis in ([0,120,240], [0,100,260]):\n"
        "        SI = evaluate_clamp_basic([100,100,100], phis, F_shear=shear)\n"
        "        print(f\"  phis={phis}, SI={SI:.3f}\")\n"
    ),
    # Subplot 3D surface with shear demonstration
    nbf.v4.new_code_cell(
        "force_min, force_max, N = 20, 200, 40\n"
        "fA = np.linspace(force_min, force_max, N)\n"
        "fB = np.linspace(force_min, force_max, N)\n"
        "FC = 100.0\n"
        "for shear in (0.0, 20.0):\n"
        "    fig = plt.figure(figsize=(8, 4))\n"
        "    ax = fig.add_subplot(121 + (1 if shear>0 else 0), projection='3d')\n"
        "    FA, FB = np.meshgrid(fA, fB)\n"
        "    Z = np.zeros_like(FA)\n"
        "    for i in range(N):\n"
        "        for j in range(N):\n"
        "            Z[i,j] = evaluate_clamp_basic([FA[i,j], FB[i,j], FC], [0,120,240], F_shear=shear)\n"
        "    norm_Z = (Z - Z.min())/(Z.max()-Z.min())\n"
        "    colors = plt.cm.plasma(norm_Z)\n"
        "    ax.plot_surface(FA, FB, Z, facecolors=colors, rstride=1, cstride=1, edgecolor='k')\n"
        "    ax.set_title(f\"F_shear={shear} N\")\n"
        "    ax.set_xlabel('A'); ax.set_ylabel('B'); ax.set_zlabel('SI')\n"
        "plt.tight_layout()\n"
        "plt.show()"
    )
]



# Write notebook to file
notebook_path = 'DiSC_advanced_stability_notebook_phys_deg.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at: {notebook_path}")
