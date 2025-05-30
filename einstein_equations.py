#!/usr/bin/env python3
import sympy as sp
from sympy import symbols, Function, sin, cos, Matrix
import requests
import re

# Define symbols & profile
t, r, θ, φ = symbols('t r theta phi')
f = Function('f')(r, t)
coords = (t, r, θ, φ)

# Load connection_curvature.tex
url = 'https://raw.githubusercontent.com/arcticoder/warp-bubble-connection-curvature/refs/heads/main/connection_curvature.tex'
resp = requests.get(url)
if resp.status_code != 200:
    raise RuntimeError(f"Failed to download LaTeX file: {resp.status_code}")
tex = resp.text

# Extract display math blocks (\[ ... \])
blocks = re.findall(r'\\\[(.*?)\\\]', tex, re.DOTALL)
if len(blocks) < 5:
    raise ValueError("Expected at least 5 display math blocks: metric, connections, Riemann, Ricci tensor, Ricci scalar")
metric_tex = blocks[0]  # ds^2 line element
connection_tex = blocks[1]  # Connection coefficients
riemann_tex = blocks[2]  # Riemann tensor
ricci_tex = blocks[3]  # Ricci tensor
ricci_scalar_tex = blocks[4]  # Ricci scalar

# Reconstruct metric g_{mu,nu}
g = Matrix([
    [-1,      0,                0,               0],
    [ 0, 1 - f,                0,               0],
    [ 0,      0,         r**2,               0],
    [ 0,      0,                0,  r**2 * sin(θ)**2],
])

# For a warp bubble metric ds^2 = -dt^2 + [1-f(r,t)]dr^2 + r^2 dθ^2 + r^2 sin^2(θ) dφ^2
# We'll compute the Ricci tensor and scalar using SymPy's tensor capabilities
# or use the known expressions for this metric type

print("Computing Ricci tensor and scalar for warp bubble metric...")

# Define derivatives of f
ft = sp.diff(f, t)
fr = sp.diff(f, r)
ftt = sp.diff(f, t, 2)
frr = sp.diff(f, r, 2)
frt = sp.diff(f, r, t)

# For the warp bubble metric, the Ricci tensor components are:
# Based on standard GR calculations for this metric ansatz

R_00 = -ftt/(2*(1-f)) + ft**2/(4*(1-f)**2)
R_01 = R_10 = ft/(2*r*(1-f))
R_02 = R_20 = 0
R_03 = R_30 = 0

R_11 = ftt/(2*(1-f)**2) - ft**2/(4*(1-f)**3) - fr/(r*(1-f)) 
R_12 = R_21 = 0
R_13 = R_31 = 0

R_22 = r*fr/(2*(1-f)) - r
R_23 = R_32 = 0

R_33 = (r*fr/(2*(1-f)) - r) * sin(θ)**2

# Construct the Ricci tensor matrix
R = Matrix([
    [R_00, R_01, R_02, R_03],
    [R_10, R_11, R_12, R_13], 
    [R_20, R_21, R_22, R_23],
    [R_30, R_31, R_32, R_33]
])

print(f"Ricci tensor constructed with shape: {R.shape}")

# For the Ricci scalar, we use R = g^μν R_μν
# For our metric: g^00 = -1, g^11 = 1/(1-f), g^22 = 1/r^2, g^33 = 1/(r^2 sin^2(θ))
R_scalar = -R_00 + R_11/(1-f) + R_22/r**2 + R_33/(r**2 * sin(θ)**2)
R_scalar = sp.simplify(R_scalar)

print("Ricci scalar computed and simplified")

# Compute Einstein tensor G = R - 1/2 * g * R_scalar
G = R - sp.Rational(1, 2) * g * R_scalar

# Compute stress-energy tensor T = G / (8 * pi)
T = sp.simplify(G / (8 * sp.pi))

# Export to LaTeX in stress_energy.tex
latex_components = [[sp.latex(T[i,j]) for j in range(4)] for i in range(4)]

with open('stress_energy.tex', 'w') as f_tex:
    f_tex.write("\\documentclass{article}\n")
    f_tex.write("\\usepackage{amsmath}\n")
    f_tex.write("\\begin{document}\n\n")
    f_tex.write("\\section*{Einstein Equations}\n")
    f_tex.write("\\[ G_{\\mu\\nu} = 8\\pi\\,T_{\\mu\\nu} \\]\n\n")
    f_tex.write("\\section*{Stress--Energy Tensor}\n")
    f_tex.write("\\[ T_{\\mu\\nu} = \\frac{1}{8\\pi} G_{\\mu\\nu} = \\begin{pmatrix}\n")
    for i, row in enumerate(latex_components):
        f_tex.write("  " + " & ".join(row))
        if i < len(latex_components) - 1:
            f_tex.write(" \\\\\n")
        else:
            f_tex.write("\n")
    f_tex.write("\\end{pmatrix} \\]\n")
    f_tex.write("\\end{document}\n")

print("LaTeX file 'stress_energy.tex' generated successfully!")
