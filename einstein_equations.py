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
if len(blocks) < 3:
    raise ValueError("Expected at least 3 display math blocks: metric, Ricci tensor, Ricci scalar")
metric_tex = blocks[0]
ricci_tex = blocks[1]
ricci_scalar_tex = blocks[2]

# Reconstruct metric g_{mu,nu}
g = Matrix([
    [-1,      0,                0,               0],
    [ 0, 1 - f,                0,               0],
    [ 0,      0,         r**2,               0],
    [ 0,      0,                0,  r**2 * sin(θ)**2],
])

# Reconstruct Ricci tensor R_{mu,nu}
# TODO: replace with the actual entries parsed from ricci_tex
R = Matrix([
    # Example row: [R_tt, R_tr, R_tθ, R_tφ],
    # Fill in with actual expressions
])

# Reconstruct scalar curvature
# TODO: parse ricci_scalar_tex into a SymPy expression
R_scalar = sp.sympify(ricci_scalar_tex)

# Compute Einstein tensor G = R - 1/2 * g * R_scalar
G = R - sp.Rational(1, 2) * g * R_scalar

# Compute stress-energy tensor T = G / (8 * pi)
T = sp.simplify(G / (8 * sp.pi))

# Export to LaTeX in stress_energy.tex
latex_components = [[sp.latex(T[i,j]) for j in range(4)] for i in range(4)]

with open('stress_energy.tex', 'w') as f_tex:
    f_tex.write(r"\documentclass{article}\n")
    f_tex.write(r"\usepackage{amsmath}\n")
    f_tex.write(r"\begin{document}\n\n")
    f_tex.write(r"\section*{Einstein Equations}\n")
    f_tex.write(r"\[ G_{\mu\nu} = 8\pi\,T_{\mu\nu} \]\n\n")
    f_tex.write(r"\section*{Stress--Energy Tensor}\n")
    f_tex.write(r"\[ T_{\mu\nu} = \frac{1}{8\pi} G_{\mu\nu} = \begin{pmatrix}\n")
    for row in latex_components:
        f_tex.write("  " + " & ".join(row) + r" \\" + "\n")
    f_tex.write(r"\end{pmatrix}\n")
    f_tex.write(r"\end{document}")
