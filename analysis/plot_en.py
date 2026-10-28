# -*- coding: utf-8 -*-
"""Generate English-labelled figures for the bubble-compliance report."""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "bubble")
sys.path.insert(0, HERE)
import bubble_stiffness as bs

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
G = 9.80665


def _json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def spring_en():
    df = pd.read_csv(os.path.join(DATA, "spring_calib.csv"))
    df["F"] = df["mass_kg"] * G
    k, b, r2 = bs._fit(df["x_out_mm"], df["F"])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.scatter(df["x_out_mm"], df["F"], s=28, label="measured")
    xx = np.linspace(0, df["x_out_mm"].max() * 1.05, 50)
    ax.plot(xx, k * xx + b, "r-", label=rf"$F = {k:.3f}x {b:+.2f}$")
    ax.set_xlabel(r"Spring extension $x$ (mm)")
    ax.set_ylabel(r"Force $F$ (N)")
    ax.set_title("Spring calibration")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(DATA, "spring_calib_en.png"), dpi=200)
    plt.close(fig)
    print("spring", k, b, r2)


def static_en():
    d, xcol = bs._prepare_static(os.path.join(DATA, "static.csv"))
    tab = bs._stiffness_table(d, xcol)
    rep = bs._repeat_table(d, xcol)
    fit = _json("static_fit.json")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    bs._scatter_jitter(ax, rep, "K_rep", "individual", color="0.35")
    ax.errorbar(tab["air_ml"], tab["K_N_per_mm"], yerr=tab["K_sd"].fillna(0.0),
                fmt="s", capsize=3, ms=5, color="C0", label="mean ± SD", zorder=4)
    xx = np.linspace(0.5, 5.5, 100)
    ax.plot(xx, fit["C_N_mm_per_ml"] / (fit["V0_ml"] + xx), "r-", lw=1.6,
            label=r"model $C/(V_0+V)$")
    ax.set_xlabel(r"Air volume $V$ (mL)")
    ax.set_ylabel(r"$K_{air}$ (N/mm)")
    ax.set_title("Static stiffness")
    ax.set_ylim(0, 10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[1]
    inv = 1.0 / tab["K_N_per_mm"]
    err = tab["K_sd"].fillna(0.0) / tab["K_N_per_mm"] ** 2
    rep2 = rep.copy()
    rep2["invK"] = 1.0 / rep2["K_rep"]
    bs._scatter_jitter(ax, rep2, "invK", "individual", color="0.35")
    ax.errorbar(tab["air_ml"], inv, yerr=err, fmt="s", capsize=3, ms=5,
                color="C0", label="mean ± SD", zorder=4)
    xx = np.linspace(0, 5.5, 50)
    ax.plot(xx, fit["intercept_mm_per_N"] + fit["slope_mm_per_N_per_ml"] * xx,
            "r-", lw=1.6, label=rf"fit $V_0$={fit['V0_ml']:.2f} mL")
    ax.set_xlabel(r"Air volume $V$ (mL)")
    ax.set_ylabel(r"$1/K_{air}$ (mm/N)")
    ax.set_title("Inverse stiffness")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(DATA, "static_stiffness_en.png"), dpi=200)
    plt.close(fig)


def step_en():
    raw = pd.read_csv(os.path.join(DATA, "step_summary_raw.csv"))
    agg = pd.read_csv(os.path.join(DATA, "step_summary.csv"))
    fit = _json("step_fit.json")

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    bs._scatter_jitter(ax, raw, "tau_s", "individual", color="0.35")
    ax.errorbar(agg["air_ml"], agg["tau_mean"], yerr=agg["tau_sd"],
                fmt="s", capsize=3, ms=5, color="C0", label="mean ± SD", zorder=4)
    xx = np.linspace(0.5, 5.5, 50)
    ax.plot(xx, fit["intercept_s"] + fit["slope_s_per_ml"] * xx, "r-", lw=1.6,
            label=rf"$\tau = {fit['intercept_s']:.3f} + {fit['slope_s_per_ml']:.3f}V$")
    ax.set_xlabel(r"Air volume $V$ (mL)")
    ax.set_ylabel(r"Time constant $\tau$ (s)")
    ax.set_title("Step response")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(DATA, "step_tau_en.png"), dpi=200)
    plt.close(fig)

    # representative curves
    meta = pd.read_csv(os.path.join(DATA, "step_meta.csv"))
    curves = []
    for _, r in meta.iterrows():
        fn = str(r["file"]).strip()
        path = os.path.join(DATA, "step", fn)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        t = pd.to_numeric(df["t_ms"], errors="coerce").to_numpy(float) / 1000.0
        x = pd.to_numeric(df["x_out_mm"], errors="coerce").to_numpy(float)
        ok = np.isfinite(t) & np.isfinite(x)
        t, x = t[ok], x[ok]
        order = np.argsort(t)
        t, x = t[order], x[order]
        n = len(x)
        k0 = max(3, n // 10)
        x0 = float(np.median(x[:k0]))
        xf = float(np.median(x[-k0:]))
        dx = xf - x0
        if abs(dx) < 0.02:
            continue
        y = (x - x0) / dx
        t10 = bs._cross(t, y, 0.10)
        t63 = bs._cross(t, y, 0.632)
        if not np.isfinite(t63):
            continue
        tau = (t63 - t10) / 0.89464 if np.isfinite(t10) else np.nan
        curves.append({"air": float(r["air_ml"]), "tau": tau,
                       "t": t - (t10 if np.isfinite(t10) else t[0]), "y": y})

    chosen = []
    for air in sorted({c["air"] for c in curves}):
        group = [c for c in curves if c["air"] == air and np.isfinite(c["tau"])]
        if not group:
            continue
        mt = np.mean([c["tau"] for c in group])
        chosen.append(min(group, key=lambda c: abs(c["tau"] - mt)))

    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    colors = {1.0: "C0", 2.0: "C1", 5.0: "C2"}
    for c in chosen:
        ax.plot(c["t"], c["y"], lw=1.6, color=colors.get(c["air"]),
                label=f"{c['air']:g} mL")
    ax.axhline(0.632, color="gray", ls="--", lw=1)
    tmax = max(float(np.nanmax(c["t"])) for c in chosen)
    ax.set_xlim(-0.2, tmax * 1.02)
    ax.set_xlabel(r"Relative time $t-t_{10}$ (s)")
    ax.set_ylabel("Normalized output displacement")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.02),
              ncol=3, frameon=False)
    one = [c for c in chosen if c["air"] == 1.0]
    if one:
        c1 = one[0]
        axins = ax.inset_axes([0.56, 0.10, 0.38, 0.38])
        axins.plot(c1["t"], c1["y"], lw=1.6, color=colors[1.0])
        axins.axhline(0.632, color="gray", ls="--", lw=0.8)
        axins.set_xlim(0, 0.4)
        axins.set_ylim(0, 1.05)
        axins.tick_params(labelsize=6)
        axins.set_title(r"$1$ mL zoom ($0$-$0.4$ s)", fontsize=7)
        axins.grid(alpha=0.25)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(DATA, "step_examples_en.png"), dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def demo_en():
    d, xcol = bs._prepare_static(os.path.join(DATA, "demo.csv"))
    tab = bs._stiffness_table(d, xcol)
    rep = bs._repeat_table(d, xcol)
    fit = _json("static_fit.json")
    k_s = _json("spring_fit.json")["k"]
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    bs._scatter_jitter(ax, rep, "K_rep", "individual", color="0.35")
    ax.errorbar(tab["air_ml"], tab["K_N_per_mm"], yerr=tab["K_sd"].fillna(0.0),
                fmt="s", capsize=3, ms=5, color="C0", label="mean ± SD", zorder=4)
    xx = np.linspace(0.5, 5.5, 100)
    ax.plot(xx, k_s + fit["C_N_mm_per_ml"] / (fit["V0_ml"] + xx), "r-", lw=1.6,
            label=r"model $k_s + C/(V_0+V)$")
    ax.set_xlabel(r"Air volume $V$ (mL)")
    ax.set_ylabel(r"$K_{eff}$ (N/mm)")
    ax.set_title("Soft joint: stiffness vs air volume")
    ax.set_ylim(0, 10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(DATA, "demo_stiffness_en.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    spring_en()
    static_en()
    step_en()
    demo_en()
    print("English figures written to", DATA)
