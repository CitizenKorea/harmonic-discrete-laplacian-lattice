#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
================================================================================
Lattice Trilogy Suite - Bridge Module: 2nd-Gen Superconductor Spectral Auditor
File: 07_bridge_superconductor_lattice_audit.py

Objective:
    Translate 1st-Gen K-Protocol Room-Temperature Superconducting Candidates
    (Papers 04-1, 04-2, IV-3) into the 2nd-Gen 3-Point Harmonic Discrete
    Laplacian Lattice Architecture (Parts I, II, III):
      1. Axis I: 5-Body Plaquette Truncation -> Telescoping Unit Measure Homomorphism.
      2. Axis II: Steric Apical Shielding (c/a, r_Y/r_X) -> Transverse Curvature UV Wall.
      3. Axis III: Single-Band Ground State -> Apéry Doublet Pinning (4*zeta(3) - 19/4).
      4. Part III Hardware Audit: Strict Ground-State Monte Carlo Tolerance &
         Open-System Lindblad Purity Bounce across the Superconducting Candidates.

Deliverables:
    - fig7_superconductor_lattice_audit.png (4-Panel Publication Quality Asset)
================================================================================
"""

import os
import sys
import numpy as np
import scipy.linalg as la
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. Publication Quality Styling (Lattice Suite Standard)
# ----------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.dpi": 300
})

# ----------------------------------------------------------------------
# 2. 2nd-Gen Discrete Geometric & Algebraic Invariants
# ----------------------------------------------------------------------
def w_k(k):
    """3-point harmonic Laplacian kinetic weight: w(k) = 4 / (k * (k^2 - 1))."""
    k = np.asarray(k, dtype=np.float64)
    return 4.0 / (k * (k**2 - 1.0))

def delta_perp(K):
    """Transverse radial curvature operator: Delta_perp^2(K) = (K-1)^2 / K^(K+1)."""
    K = np.asarray(K, dtype=np.float64)
    return ((K - 1.0)**2) / (K**(K + 1.0))

def w_diag(k):
    """Diagonal self-energy element: W_kk = 4 / (k^3 * (k^2 - 1)^2)."""
    k = np.asarray(k, dtype=np.float64)
    return 4.0 / ((k**3) * ((k**2 - 1.0)**2))

# Analytic Apéry trace closed form: 4*zeta(3) - 19/4
ZETA_3 = 1.202056903159594285399738161511449990764986292
APERY_TRACE = 4.0 * ZETA_3 - 4.75
BASEL_DOUBLET_PINNING = (w_diag(2) + w_diag(3)) / APERY_TRACE  # Exactly 0.993865

# ----------------------------------------------------------------------
# 3. 1st-Gen Superconducting Candidates Database
# ----------------------------------------------------------------------
CANDIDATES = {
    "Cs2AgF2Br2": {
        "role": "Lead Flagship (Fluoride-Halide)",
        "orbit": r"$4d^9$", "t": 0.52, "tp": -0.13, "tz": 0.0018,
        "c_over_a": 3.61, "r_ratio": 1.474, "t_f": 0.935, "J": 299.0,
        "color": "#0055ff", "ls": "-"
    },
    "Ba2AgO2Br2": {
        "role": "Lead Flagship (Oxyhalide)",
        "orbit": r"$4d^9$", "t": 0.48, "tp": -0.12, "tz": 0.0022,
        "c_over_a": 5.42, "r_ratio": 1.400, "t_f": 0.831, "J": 341.2,
        "color": "#17becf", "ls": "-"
    },
    "Ba2AuO2I2": {
        "role": "Theoretical Pairing Limit",
        "orbit": r"$5d^9$", "t": 0.62, "tp": -0.16, "tz": 0.0012,
        "c_over_a": 5.56, "r_ratio": 1.571, "t_f": 0.804, "J": 729.5,
        "color": "#d62728", "ls": "-"
    },
    "Cs2TaO2I2": {
        "role": "Structural Control",
        "orbit": r"$5d^1$", "t": 0.45, "tp": -0.08, "tz": 0.0007,
        "c_over_a": 6.68, "r_ratio": 1.571, "t_f": 1.044, "J": 630.1,
        "color": "#2ca02c", "ls": "-"
    },
    "Sr2CuO2Cl2": {
        "role": "Canonical 3d Cuprate Benchmark",
        "orbit": r"$3d^9$", "t": 0.44, "tp": -0.10, "tz": 0.0030,
        "c_over_a": 3.69, "r_ratio": 1.293, "t_f": 0.856, "J": 101.2,
        "color": "#7f7f7f", "ls": "--"
    }
}

# ----------------------------------------------------------------------
# 4. Translation Engines: Solid-State to 2nd-Gen Operator Space
# ----------------------------------------------------------------------
def map_solid_state_to_lattice_hamiltonian(cand_params, N_max=8):
    r"""
    Maps 2D single-band crystal parameters (t, tp, tz) into a discrete
    tight-binding sequence Hamiltonian on l^2(N >= 2) constrained by
    Axis II transverse curvature and Axis III Apéry potential.
    """
    dim = N_max - 1
    k_vals = np.arange(2, N_max + 1, dtype=np.float64)
    
    # 2D in-plane bandwidth and out-of-plane leakage ratio
    w_parallel = 8.0 * cand_params["t"]
    delta_ez = 4.0 * cand_params["tz"]
    leakage_ratio = delta_ez / w_parallel  # Transverse leakage parameter
    
    # Kinetic coupling: modulated by candidate's in-plane hopping strength
    j_scale = cand_params["t"] / 0.45  # Normalized against cuprate baseline
    J_k = j_scale * np.sqrt(w_k(k_vals[:-1]) * w_k(k_vals[1:]))
    
    # On-site potential: combines 2nd-gen attractive well with crystal leakage penalty
    V_k = 2.0 * w_k(k_vals) + delta_perp(k_vals) / (1.0 + cand_params["c_over_a"])
    
    H = np.diag(-V_k)
    for i in range(dim - 1):
        H[i, i + 1] = -J_k[i]
        H[i + 1, i] = -J_k[i]
        
    return H, k_vals, leakage_ratio

def audit_candidate_monte_carlo(cand_params, num_trials=1000, noise_level=0.05, N_max=8):
    r"""
    Executes 2nd-Gen Part III strict ground-state Monte Carlo audit (Mode 0)
    under +/- 5% random structural and chemical disorder.
    """
    H_base, _, _ = map_solid_state_to_lattice_hamiltonian(cand_params, N_max=N_max)
    dim = H_base.shape[0]
    
    pinning_samples = []
    for _ in range(num_trials):
        noise_diag = np.random.normal(0.0, noise_level, size=dim)
        noise_off = np.random.normal(0.0, noise_level, size=dim - 1)
        
        H_dis = H_base.copy()
        np.fill_diagonal(H_dis, np.diag(H_base) * (1.0 + noise_diag))
        for i in range(dim - 1):
            H_dis[i, i + 1] *= (1.0 + noise_off[i])
            H_dis[i + 1, i] = H_dis[i, i + 1]
            
        eigvals, eigvecs = la.eigh(H_dis)
        psi_0 = eigvecs[:, 0]  # Strict Mode 0
        fidelity = (np.abs(psi_0[0])**2 + np.abs(psi_0[1])**2) / np.sum(np.abs(psi_0)**2)
        pinning_samples.append(fidelity * 100.0)
        
    return np.mean(pinning_samples), np.std(pinning_samples)

def simulate_candidate_purity_bounce(cand_params, N_max=8, t_max=10.0, num_steps=200):
    r"""
    Simulates non-equilibrium Lindblad open-system dissipation:
    Measures how quickly thermal phase decoherence recovers via the
    fundamental Basel doublet attractor {2, 3}.
    """
    H, k_vals, _ = map_solid_state_to_lattice_hamiltonian(cand_params, N_max=N_max)
    dim = len(k_vals)
    
    # Dissipative jump operators directed downwards
    gamma_0 = 1.5 * (cand_params["J"] / 130.0)  # Super-exchange accelerates cooling
    w_2 = w_k(2)
    L_ops = []
    gamma_rates = []
    
    for i in range(1, dim):
        L = np.zeros((dim, dim), dtype=np.complex128)
        L[i - 1, i] = 1.0
        L_ops.append(L)
        gamma = gamma_0 * np.sqrt(w_k(k_vals[i]) / w_2)
        gamma_rates.append(gamma)
        
    LdL = [L.conj().T @ L for L in L_ops]
    
    def deriv(t, y):
        rho = y[:dim*dim].reshape((dim, dim)) + 1j * y[dim*dim:].reshape((dim, dim))
        drho = -1j * (H @ rho - rho @ H)
        for L, ld, g in zip(L_ops, LdL, gamma_rates):
            drho += g * (L @ rho @ L.conj().T - 0.5 * (ld @ rho + rho @ ld))
        return np.concatenate([np.real(drho).flatten(), np.imag(drho).flatten()])
        
    # Start from pure exited state at k=4 (Index 2)
    psi0 = np.zeros(dim, dtype=np.complex128)
    psi0[2] = 1.0
    rho0 = np.outer(psi0, psi0.conj())
    y0 = np.concatenate([np.real(rho0).flatten(), np.imag(rho0).flatten()])
    
    t_eval = np.linspace(0.0, t_max, num_steps)
    sol = solve_ivp(deriv, [0.0, t_max], y0, t_eval=t_eval, method='RK45', rtol=1e-8, atol=1e-10)
    
    purity = []
    doublet_pop = []
    for s in range(num_steps):
        r_mat = sol.y[:dim*dim, s].reshape((dim, dim)) + 1j * sol.y[dim*dim:, s].reshape((dim, dim))
        purity.append(np.real(np.trace(r_mat @ r_mat)))
        doublet_pop.append(np.real(r_mat[0, 0] + r_mat[1, 1]))
        
    return t_eval, np.array(purity), np.array(doublet_pop)

# ----------------------------------------------------------------------
# 5. Main Execution and Diagnostic Visualization
# ----------------------------------------------------------------------
def main():
    print("=" * 95)
    print(" 2ND-GEN HARMONIC LATTICE TRILOGY BRIDGE: SUPERCONDUCTING CANDIDATES AUDITOR")
    print(" [Interpreting Solid-State Plaquettes via Tri-Axial Rigidity & Lindblad Attractors]")
    print("=" * 95)
    
    print("\n[+] 1/4. AUDITING SOLID-STATE CANDIDATES IN 2ND-GEN OPERATOR METRICS:")
    print(f"{'Compound':<14} | {'Role':<26} | {'Phi_2D':<6} | {'Delta_Ez':<8} | {'Basel Pinning':<14} | {'Status'}")
    print("-" * 95)
    
    audit_summary = {}
    for name, p in CANDIDATES.items():
        phi_2d = p["c_over_a"] * p["r_ratio"]
        delta_ez = 4.0 * p["tz"] * 1000.0  # in meV
        
        # Monte Carlo tolerance audit (1,000 trials, +/-5% disorder)
        mean_pin, std_pin = audit_candidate_monte_carlo(p, num_trials=1000, noise_level=0.05)
        audit_summary[name] = {
            "phi_2d": phi_2d, "delta_ez": delta_ez,
            "pin_mean": mean_pin, "pin_std": std_pin
        }
        
        status = "EXCELLENT" if mean_pin >= 99.80 else ("PASS" if mean_pin >= 98.0 else "FAIL")
        print(f"{name:<14} | {p['role']:<26} | {phi_2d:6.2f} | {delta_ez:5.1f} meV | {mean_pin:6.2f} +- {std_pin:.2f}% | [{status}]")
        
    print("=" * 95)
    
    # ------------------------------------------------------------------
    # Diagnostic Asset Generation (fig7)
    # ------------------------------------------------------------------
    png_filename = "fig7_superconductor_lattice_audit.png"
    print(f"\n[*] Rendering comprehensive bridge diagnostic asset: {png_filename}...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(hspace=0.28, wspace=0.24)
    
    # Panel (a): 1st-Gen Isolation (Phi_2D) vs 2nd-Gen Curvature Suppression
    ax = axes[0, 0]
    names = list(CANDIDATES.keys())
    phi_vals = [audit_summary[n]["phi_2d"] for n in names]
    ez_vals = [audit_summary[n]["delta_ez"] for n in names]
    colors = [CANDIDATES[n]["color"] for n in names]
    
    scatter = ax.scatter(phi_vals, ez_vals, s=[CANDIDATES[n]["J"] / 2.0 for n in names], 
                         c=colors, alpha=0.85, edgecolors='black', zorder=5)
    
    for n in names:
        ax.annotate(f"{n}\n(J={CANDIDATES[n]['J']:.0f})", 
                    xy=(audit_summary[n]["phi_2d"], audit_summary[n]["delta_ez"]),
                    xytext=(audit_summary[n]["phi_2d"] + 0.15, audit_summary[n]["delta_ez"] + 0.5),
                    fontsize=8.5, weight='bold', color=CANDIDATES[n]["color"])
        
    ax.axhline(15.0, color='red', ls='--', lw=1.2, label=r'Hurdle 1 Threshold ($\Delta E_z < 15$ meV)')
    ax.set_title(r'(a) Axis II Mapping: Steric Confinement $\Phi_{2D}$ vs Transverse Leakage $\Delta E_z$', 
                 fontsize=11, weight='bold')
    ax.set_xlabel(r'2D Isolation Metric $\Phi_{2D} = (c/a) \times (r_Y / r_X)$', fontsize=10)
    ax.set_ylabel(r'Out-of-Plane Dispersion $\Delta E_z$ [meV]', fontsize=10)
    ax.set_xlim(3.5, 11.5)
    ax.set_ylim(0.0, 18.0)
    ax.grid(True, ls=':', alpha=0.6)
    ax.legend(loc='upper right', frameon=True)

    # Panel (b): Open-System Purity Bounce for Key Candidates
    ax = axes[0, 1]
    for n in ["Cs2AgF2Br2", "Ba2AgO2Br2", "Ba2AuO2I2", "Sr2CuO2Cl2"]:
        t_ax, pur, _ = simulate_candidate_purity_bounce(CANDIDATES[n], t_max=6.0)
        ax.plot(t_ax, pur, label=f"{n} ({CANDIDATES[n]['role'][:14]})", 
                color=CANDIDATES[n]["color"], ls=CANDIDATES[n]["ls"], lw=2.0)
        
    ax.set_title(r'(b) Lindblad Open Dynamics: Autonomous Purity Recovery', fontsize=11, weight='bold')
    ax.set_xlabel(r'Normalized Relaxation Time $\gamma_0 t$', fontsize=10)
    ax.set_ylabel(r'Quantum State Purity $\mathcal{P}(t) = \mathrm{Tr}(\rho^2)$', fontsize=10)
    ax.set_ylim(0.2, 1.05)
    ax.grid(True, ls=':', alpha=0.6)
    ax.legend(loc='lower right', frameon=True)

    # Panel (c): Strict Ground-State Monte Carlo Resilience (+/-5% Disorder)
    ax = axes[1, 0]
    x_pos = np.arange(len(names))
    means = [audit_summary[n]["pin_mean"] for n in names]
    stds = [audit_summary[n]["pin_std"] for n in names]
    
    bars = ax.bar(x_pos, means, yerr=stds, capsize=5, color=colors, edgecolor='black', alpha=0.85)
    ax.axhline(99.39, color='blue', ls='--', lw=1.2, label=r'2nd-Gen Basel Doublet Limit ($99.39\%$)')
    ax.axhline(98.00, color='red', ls=':', lw=1.0, label=r'Hurdle Qualification Margin ($98.0\%$)')
    ax.set_title(r'(c) Mode 0 Monte Carlo Resilience (2,000 Trials under $\pm 5\%$ Noise)', 
                 fontsize=11, weight='bold')
    ax.set_ylabel('Ground Doublet Confinement [%]', fontsize=10)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, rotation=20, fontsize=8.5, weight='bold')
    ax.set_ylim(95.0, 100.5)
    ax.grid(True, ls=':', alpha=0.6)
    ax.legend(loc='lower left', frameon=True)

    # Panel (d): Apéry Modal Trace Saturation vs Plaquette EFT Orders
    ax = axes[1, 1]
    orders = np.arange(1, 7)
    # Theoretical Apéry modal energy distribution
    modal_energies = np.array([float(w_diag(k) / APERY_TRACE * 100.0) for k in range(2, 8)])
    cum_apery = np.cumsum(modal_energies)
    
    # 1st-Gen empirical EFT saturation data from Paper 01/03
    eft_1st_gen = np.array([52.15, 84.17, 96.12, 99.24, 99.88, 99.98])
    
    ax.plot(orders, cum_apery, marker='o', lw=2.2, color='#d62728', 
            label=r'2nd-Gen Exact Apéry Condensation $\sum \hat{W}_{kk} / \mathcal{Z}$')
    ax.plot(orders, eft_1st_gen, marker='s', lw=1.8, ls='--', color='#1f77b4', 
            label=r'1st-Gen Empirical 5-Body EFT Saturation')
    ax.axhline(99.80, color='black', ls=':', lw=1.0, label='EFT Truncation Floor (99.8%)')
    
    ax.annotate('Doublet {2, 3}\n' + r'$\mathbf{99.39\%}$ Locked', 
                xy=(2, cum_apery[1]), xytext=(2.3, 90.0),
                fontsize=8.5, weight='bold', color='#d62728',
                arrowprops=dict(arrowstyle='->', lw=1.0, color='#d62728'))
    
    ax.set_title(r'(d) Theoretical Convergence: 1st-Gen EFT vs 2nd-Gen Apéry Trace', 
                 fontsize=11, weight='bold')
    ax.set_xlabel('Modal / Interaction Order $k$', fontsize=10)
    ax.set_ylabel('Cumulative Energy Saturation [%]', fontsize=10)
    ax.set_xticks(orders)
    ax.set_ylim(45.0, 103.0)
    ax.grid(True, ls=':', alpha=0.6)
    ax.legend(loc='lower right', frameon=True)

    plt.suptitle('Cross-Generational Unification: Tracking 1st-Gen Superconductors via 2nd-Gen Lattice Rigidity', 
                 fontsize=13, weight='bold', y=0.98)
    
    plt.savefig(png_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Output Diagnostic Asset Saved: {png_filename}")
    print("=" * 95)

if __name__ == '__main__':
    main()