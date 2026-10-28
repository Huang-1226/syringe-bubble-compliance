# -*- coding: utf-8 -*-
"""
气泡柔度 / 可变刚度 / 气泡检测 —— 数据分析

用法:
  python analysis/bubble_stiffness.py spring --dir analysis/data/bubble
  python analysis/bubble_stiffness.py static --dir analysis/data/bubble [--k-spring 0]
  python analysis/bubble_stiffness.py step   --dir analysis/data/bubble
  python analysis/bubble_stiffness.py demo   --dir analysis/data/bubble
  python analysis/bubble_stiffness.py all    --dir analysis/data/bubble

数据文件(列名):
  spring_calib.csv : mass_kg, x_out_mm, repeat, note
  static.csv       : air_ml, load_kg, x_out_mm, repeat, note   (静态实验：取下输出弹簧)
  step_meta.csv    : file, air_ml, repeat, speed_mms, note
  step/*.csv       : t_ms, x_out_mm
  demo.csv         : air_ml, load_kg, x_out_mm, repeat, note   (软体关节：装输出弹簧)

输出:
  spring_calib.png / spring_fit.json
  static_stiffness.png / static_summary.csv / static_fit.json
  step_examples.png / step_tau.png / step_summary_raw.csv / step_summary.csv / step_fit.json
  demo_stiffness.png / demo_summary.csv
"""

import argparse
import json
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

G = 9.80665
P0 = 101325.0
A_OUT_DEFAULT = 287.0


def _read(path):
    if not os.path.exists(path):
        print(f"[跳过] 找不到 {path}")
        return None
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _col(df, *names):
    for name in names:
        if name in df.columns:
            return name
    return None


def _fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2 or np.ptp(x) == 0:
        return float("nan"), float("nan"), float("nan")
    m, b = np.polyfit(x, y, 1)
    pred = m * x + b
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(m), float(b), float(r2)


def _cross(t, y, level):
    for i in range(1, len(y)):
        y0, y1 = y[i - 1], y[i]
        if (y0 < level <= y1) or (y0 > level >= y1):
            if y1 == y0:
                return float(t[i])
            f = (level - y0) / (y1 - y0)
            return float(t[i - 1] + f * (t[i] - t[i - 1]))
    return float("nan")


def _save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _spring_k(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return float(json.load(f).get("k", 0.0))
    return 0.0


def cmd_spring(args):
    df = _read(os.path.join(args.dir, "spring_calib.csv"))
    if df is None:
        return
    xcol = _col(df, "x_out_mm", "x_mm")
    if xcol is None or "mass_kg" not in df.columns:
        print("[跳过] spring_calib.csv 需要 mass_kg 和 x_out_mm")
        return
    df["mass_kg"] = pd.to_numeric(df["mass_kg"], errors="coerce")
    df[xcol] = pd.to_numeric(df[xcol], errors="coerce")
    d = df.dropna(subset=["mass_kg", xcol])
    if len(d) < 2:
        print("[跳过] spring_calib.csv 有效数据不足")
        return
    F = d["mass_kg"].to_numpy(float) * G
    x = d[xcol].to_numpy(float)
    k, b, r2 = _fit(x, F)
    print(f"弹簧标定: k={k:.4f} N/mm, b={b:.3f} N, R2={r2:.4f}, n={len(d)}")

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.scatter(x, F, s=28, label="measured")
    xx = np.linspace(0, float(np.max(x)) * 1.05, 50)
    ax.plot(xx, k * xx + b, "r-", label=f"F={k:.3f}x{b:+.2f}")
    ax.set_xlabel("弹簧伸长 x (mm)")
    ax.set_ylabel("力 F (N)")
    ax.set_title("弹簧标定")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    png = os.path.join(args.dir, "spring_calib.png")
    fig.savefig(png, dpi=150)
    plt.close(fig)
    _save_json(os.path.join(args.dir, "spring_fit.json"),
               {"k": k, "b": b, "r2": r2, "n": int(len(d))})
    print("图 ->", png)


def _stiffness_table(df, xcol):
    rows = []
    for air, g in df.groupby("air_ml"):
        g = g.dropna(subset=[xcol, "force_N"])
        if len(g) < 2 or g[xcol].nunique() < 2:
            continue
        K_all, b_all, r2_all = _fit(g[xcol], g["force_N"])
        K_mean, K_sd, n_rep = K_all, float("nan"), 1
        if "repeat" in g.columns and g["repeat"].nunique() > 1:
            ks = []
            for _, gr in g.groupby("repeat"):
                gr = gr.dropna(subset=[xcol, "force_N"])
                if len(gr) >= 2 and gr[xcol].nunique() >= 2:
                    kr, _, _ = _fit(gr[xcol], gr["force_N"])
                    if np.isfinite(kr):
                        ks.append(kr)
            n_rep = len(ks)
            if len(ks) >= 2:
                K_mean = float(np.mean(ks))
                K_sd = float(np.std(ks, ddof=1))
        rows.append({"air_ml": float(air), "K_N_per_mm": K_mean, "K_sd": K_sd,
                     "K_pooled": K_all, "b_N": b_all, "r2_pooled": r2_all,
                     "n_points": int(len(g)), "n_rep": int(n_rep)})
    return pd.DataFrame(rows)


def _repeat_table(df, xcol):
    rows = []
    for air, g in df.groupby("air_ml"):
        groups = g.groupby("repeat") if "repeat" in g.columns else [(1, g)]
        for rep, gr in groups:
            gr = gr.dropna(subset=[xcol, "force_N"])
            if len(gr) < 2 or gr[xcol].nunique() < 2:
                continue
            K, b, r2 = _fit(gr[xcol], gr["force_N"])
            if not np.isfinite(K):
                continue
            rows.append({"air_ml": float(air), "repeat": rep, "K_rep": K,
                         "b_rep": b, "r2_rep": r2, "n_rep": int(len(gr))})
    return pd.DataFrame(rows)


def _scatter_jitter(ax, df, ycol, label, color="0.35", jitter=0.06):
    d = df.dropna(subset=[ycol])
    xs, ys = [], []
    for air, g in d.groupby("air_ml"):
        n = len(g)
        offs = np.linspace(-jitter, jitter, n) if n > 1 else [0.0]
        xs.extend((float(air) + np.asarray(offs)).tolist())
        ys.extend(g[ycol].astype(float).tolist())
    if xs:
        ax.scatter(xs, ys, s=20, c=color, alpha=0.7, marker="o",
                   linewidths=0, label=label, zorder=3)


def _prepare_static(path):
    df = _read(path)
    if df is None:
        return None
    xcol = _col(df, "x_out_mm", "x_mm")
    if xcol is None or "air_ml" not in df.columns:
        print(f"[跳过] {os.path.basename(path)} 需要 air_ml 和 x_out_mm")
        return None
    df["air_ml"] = pd.to_numeric(df["air_ml"], errors="coerce")
    df[xcol] = pd.to_numeric(df[xcol], errors="coerce")
    if "force_N" in df.columns:
        df["force_N"] = pd.to_numeric(df["force_N"], errors="coerce")
    elif "load_kg" in df.columns:
        df["load_kg"] = pd.to_numeric(df["load_kg"], errors="coerce")
        df["force_N"] = df["load_kg"] * G
    else:
        print(f"[跳过] {os.path.basename(path)} 需要 force_N 或 load_kg")
        return None
    df = df.dropna(subset=["air_ml", xcol, "force_N"])
    if df.empty:
        print(f"[跳过] {os.path.basename(path)} 没有有效数据")
        return None
    return df, xcol


def cmd_static(args):
    prep = _prepare_static(os.path.join(args.dir, "static.csv"))
    if prep is None:
        return
    d, xcol = prep
    tab = _stiffness_table(d, xcol)
    if tab.empty:
        print("[跳过] 每个气泡量至少需要 2 个负载点")
        return
    k_s = float(args.k_spring) if args.k_spring is not None else 0.0
    tab["K_air_N_per_mm"] = (tab["K_N_per_mm"] - k_s).where(tab["K_N_per_mm"] - k_s > 0.01)
    tab.to_csv(os.path.join(args.dir, "static_summary.csv"), index=False, encoding="utf-8-sig")
    rep_tab = _repeat_table(d, xcol)
    rep_tab["K_air_rep"] = rep_tab["K_rep"] - k_s
    if not rep_tab.empty:
        rep_tab.to_csv(os.path.join(args.dir, "static_repeats.csv"), index=False, encoding="utf-8-sig")
    print(tab.to_string(index=False))

    fit = {}
    t2 = tab.dropna(subset=["K_air_N_per_mm"])
    if len(t2) >= 2 and t2["air_ml"].nunique() >= 2:
        inv = 1.0 / t2["K_air_N_per_mm"].to_numpy(float)
        b1, a1, r2 = _fit(t2["air_ml"].to_numpy(float), inv)
        if np.isfinite(b1) and b1 > 0:
            V0 = a1 / b1
            C = 1.0 / b1
            fit = {"slope_mm_per_N_per_ml": b1, "intercept_mm_per_N": a1, "r2": r2,
                   "V0_ml": float(V0), "C_N_mm_per_ml": float(C), "k_spring": k_s}
            print(f"1/K_air = {a1:.4f} + {b1:.4f}*V_air  (R2={r2:.4f})")
            print(f"  => 基线气泡 V0={V0:.2f} mL, C={C:.3f} N*mm/mL")
            if args.area_out:
                n_est = C * 1000.0 / ((P0 / 1e6) * args.area_out ** 2)
                fit["n_est"] = float(n_est)
                print(f"  => 用 A_out={args.area_out} mm2 估 n={n_est:.2f} (1=等温, 1.4=绝热)")
    _save_json(os.path.join(args.dir, "static_fit.json"), fit)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    _scatter_jitter(ax, rep_tab, "K_rep", "单次")
    ax.errorbar(tab["air_ml"], tab["K_N_per_mm"], yerr=tab["K_sd"].fillna(0.0),
                fmt="s", capsize=3, ms=5, color="C0", label="均值±SD", zorder=4)
    if fit:
        pos = tab.loc[tab["air_ml"] > 0, "air_ml"]
        xlo = float(pos.min()) * 0.8 if len(pos) else 0.05
        xhi = float(tab["air_ml"].max()) * 1.05 + 0.05
        xx = np.linspace(max(xlo, 0.05), xhi, 100)
        ax.plot(xx, fit["k_spring"] + fit["C_N_mm_per_ml"] / (fit["V0_ml"] + xx), "r-",
                lw=1.6, label="模型")
    if k_s > 0:
        ax.axhline(k_s, color="gray", ls="--", lw=1, label=f"弹簧 k={k_s:.2f}")
    ymax = float(np.nanmax(tab["K_N_per_mm"] + tab["K_sd"].fillna(0.0))) * 1.35
    ax.set_ylim(0, max(ymax, k_s * 1.2, 1.0))
    ax.set_xlabel("气泡量 V_air (mL)")
    ax.set_ylabel("等效刚度 K (N/mm)")
    ax.set_title("刚度 - 气泡量")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[1]
    if fit:
        rep2 = rep_tab[rep_tab["K_air_rep"] > 0.01].copy()
        rep2["invK_air_rep"] = 1.0 / rep2["K_air_rep"]
        _scatter_jitter(ax, rep2, "invK_air_rep", "单次")
        inv_sd = t2["K_sd"].fillna(0.0) / t2["K_N_per_mm"] ** 2
        ax.errorbar(t2["air_ml"], 1.0 / t2["K_air_N_per_mm"], yerr=inv_sd,
                    fmt="s", capsize=3, ms=5, color="C0", label="均值±SD", zorder=4)
        xx = np.linspace(0, float(np.max(t2["air_ml"])) * 1.1 + 0.1, 50)
        ax.plot(xx, fit["intercept_mm_per_N"] + fit["slope_mm_per_N_per_ml"] * xx, "r-",
                lw=1.6, label=f"拟合 V0={fit['V0_ml']:.2f} mL")
        ax.set_xlabel("气泡量 V_air (mL)")
        ax.set_ylabel("1/K_air (mm/N)")
        ax.set_title("1/K - 气泡量")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.5, "not enough data", ha="center", va="center")
        ax.set_axis_off()
    fig.tight_layout()
    png = os.path.join(args.dir, "static_stiffness.png")
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print("图 ->", png)


def cmd_step(args):
    meta = _read(os.path.join(args.dir, "step_meta.csv"))
    if meta is None:
        return
    if "file" not in meta.columns or "air_ml" not in meta.columns:
        print("[跳过] step_meta.csv 需要 file 和 air_ml")
        return

    rows, curves = [], []
    for _, r in meta.iterrows():
        fn = str(r["file"]).strip()
        if not fn or fn.startswith("_"):
            continue
        path = fn if os.path.isabs(fn) else os.path.join(args.dir, "step", fn)
        if not os.path.exists(path):
            alt = os.path.join(args.dir, fn)
            path = alt if os.path.exists(alt) else path
        df = _read(path)
        if df is None:
            continue
        tcol = _col(df, "t_ms", "t_s")
        xcol = _col(df, "x_out_mm", "x_mm")
        if tcol is None or xcol is None:
            print(f"[跳过] {fn} 需要 t_ms 和 x_out_mm")
            continue
        t = pd.to_numeric(df[tcol], errors="coerce").to_numpy(float)
        x = pd.to_numeric(df[xcol], errors="coerce").to_numpy(float)
        ok = np.isfinite(t) & np.isfinite(x)
        t, x = t[ok], x[ok]
        if len(t) < 10:
            continue
        if tcol == "t_ms":
            t = t / 1000.0
        order = np.argsort(t)
        t, x = t[order], x[order]

        n = len(x)
        k0 = max(3, n // 10)
        x0 = float(np.median(x[:k0]))
        xf = float(np.median(x[-k0:]))
        dx = xf - x0
        if abs(dx) < 0.02:
            print(f"[跳过] {fn} 位移变化太小 ({dx:.3f} mm)")
            continue
        tail = x[-k0:]
        drift = abs(float(tail[-1] - tail[0])) if len(tail) > 1 else 0.0
        if drift > 0.02 * abs(dx):
            print(f"[提示] {fn} 末尾还在变化 {drift:.3f} mm，tau 可能偏小；建议延长记录")
        y = (x - x0) / dx
        t10_abs = _cross(t, y, 0.10)
        t63_abs = _cross(t, y, 0.632)
        t90_abs = _cross(t, y, 0.90)
        t_start = _cross(t, y, 0.02)
        if not np.isfinite(t_start):
            t_start = float(t[0])
        if not np.isfinite(t63_abs):
            print(f"[跳过] {fn} 响应没到 63%")
            continue
        tau = (t63_abs - t10_abs) / 0.89464 if np.isfinite(t10_abs) else float("nan")
        delay = t10_abs - t_start if np.isfinite(t10_abs) else float("nan")
        rise = t90_abs - t10_abs if np.isfinite(t90_abs) and np.isfinite(t10_abs) else float("nan")
        rows.append({"file": fn, "air_ml": float(r["air_ml"]),
                     "repeat": r.get("repeat", ""), "speed_mms": r.get("speed_mms", ""),
                     "x0_mm": x0, "xf_mm": xf, "dx_mm": dx,
                     "tau_s": tau, "delay_s": delay, "rise_s": rise,
                     "overshoot": float(np.nanmax(y) - 1.0)})
        t_ref = t10_abs if np.isfinite(t10_abs) else t[0]
        curves.append({"file": fn, "air_ml": float(r["air_ml"]),
                       "tau": tau, "t": t - t_ref, "y": y})

    raw = pd.DataFrame(rows)
    if raw.empty:
        print("[跳过] step_meta.csv 没有可用数据")
        return
    raw.to_csv(os.path.join(args.dir, "step_summary_raw.csv"), index=False, encoding="utf-8-sig")
    agg = (raw.groupby("air_ml")
              .agg(tau_mean=("tau_s", "mean"), tau_sd=("tau_s", "std"),
                   delay_mean=("delay_s", "mean"), rise_mean=("rise_s", "mean"),
                   overshoot_mean=("overshoot", "mean"), n=("tau_s", "size"))
              .reset_index())
    agg.to_csv(os.path.join(args.dir, "step_summary.csv"), index=False, encoding="utf-8-sig")
    print(agg.to_string(index=False))

    if curves:
        cdf = pd.DataFrame([{"file": c["file"], "air_ml": c["air_ml"], "tau": c["tau"]}
                            for c in curves])
        cdf = cdf.dropna(subset=["tau"])
        if not cdf.empty:
            cdf["dist"] = (cdf["tau"] - cdf.groupby("air_ml")["tau"].transform("mean")).abs()
            chosen = (cdf.sort_values(["air_ml", "dist"])
                         .groupby("air_ml", as_index=False).first())
            by_file = {c["file"]: c for c in curves}
            selected = [by_file[f] for f in chosen["file"]]
        else:
            selected = curves[:1]
        selected.sort(key=lambda c: c["air_ml"])

        fig, ax = plt.subplots(figsize=(5.6, 3.8))
        colors = {1.0: "C0", 2.0: "C1", 5.0: "C2"}
        for c in selected:
            ax.plot(c["t"], c["y"], lw=1.6, color=colors.get(c["air_ml"]),
                    label=f"{c['air_ml']:g} mL")
        ax.axhline(0.632, color="gray", ls="--", lw=1)
        tmax = max(float(np.nanmax(c["t"])) for c in selected)
        ax.set_xlim(-0.2, tmax * 1.02)
        ax.set_xlabel("相对时间 t − t10 (s)")
        ax.set_ylabel("归一化输出位移")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.02),
                  ncol=3, frameon=False)

        one = [c for c in selected if c["air_ml"] == 1.0]
        if one:
            c1 = one[0]
            axins = ax.inset_axes([0.56, 0.10, 0.38, 0.38])
            axins.plot(c1["t"], c1["y"], lw=1.6, color=colors[1.0])
            axins.axhline(0.632, color="gray", ls="--", lw=0.8)
            axins.set_xlim(0, 0.4)
            axins.set_ylim(0, 1.05)
            axins.tick_params(labelsize=6)
            axins.set_title("1 mL 放大（相对时间 0–0.4 s）", fontsize=7)
            axins.grid(alpha=0.25)

        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(os.path.join(args.dir, "step_examples.png"), dpi=150,
                    bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    _scatter_jitter(ax, raw, "tau_s", "单次")
    ax.errorbar(agg["air_ml"], agg["tau_mean"], yerr=agg["tau_sd"],
                fmt="s", capsize=3, ms=5, color="C0", label="均值±SD", zorder=4)
    fit = {}
    if len(agg) >= 2 and agg["air_ml"].nunique() >= 2:
        m, b, r2 = _fit(agg["air_ml"], agg["tau_mean"])
        fit = {"slope_s_per_ml": m, "intercept_s": b, "r2": r2}
        xx = np.linspace(0, float(np.max(agg["air_ml"])) * 1.1 + 0.1, 50)
        ax.plot(xx, m * xx + b, "r-", label=f"tau={m:.3f}V{b:+.3f}")
        print(f"tau = {b:.3f} + {m:.3f}*V_air  (R2={r2:.4f})")
    ax.set_xlabel("气泡量 V_air (mL)")
    ax.set_ylabel("时间常数 tau (s)")
    ax.set_title("响应时间 - 气泡量")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    png = os.path.join(args.dir, "step_tau.png")
    fig.savefig(png, dpi=150)
    plt.close(fig)
    _save_json(os.path.join(args.dir, "step_fit.json"), fit)
    print("图 ->", png)


def cmd_demo(args):
    prep = _prepare_static(os.path.join(args.dir, "demo.csv"))
    if prep is None:
        return
    d, xcol = prep
    tab = _stiffness_table(d, xcol)
    if tab.empty:
        print("[跳过] demo.csv 每个气泡量至少需要 2 个负载点")
        return
    rep_tab = _repeat_table(d, xcol)
    k_s = float(args.k_spring) if args.k_spring is not None else _spring_k(os.path.join(args.dir, "spring_fit.json"))
    tab["K_air_model_N_per_mm"] = np.nan
    fit_path = os.path.join(args.dir, "static_fit.json")
    if os.path.exists(fit_path):
        with open(fit_path, encoding="utf-8") as f:
            fit = json.load(f)
        if "C_N_mm_per_ml" in fit and "V0_ml" in fit:
            tab["K_air_model_N_per_mm"] = fit["C_N_mm_per_ml"] / (fit["V0_ml"] + tab["air_ml"])
    tab["K_eff_model_N_per_mm"] = k_s + tab["K_air_model_N_per_mm"]
    tab.to_csv(os.path.join(args.dir, "demo_summary.csv"), index=False, encoding="utf-8-sig")
    if not rep_tab.empty:
        rep_tab.to_csv(os.path.join(args.dir, "demo_repeats.csv"), index=False, encoding="utf-8-sig")
    print(tab.to_string(index=False))

    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    _scatter_jitter(ax, rep_tab, "K_rep", "单次")
    ax.errorbar(tab["air_ml"], tab["K_N_per_mm"], yerr=tab["K_sd"].fillna(0.0),
                fmt="s", capsize=3, ms=5, color="C0", label="均值±SD", zorder=4)
    if tab["K_eff_model_N_per_mm"].notna().any():
        pos = tab.loc[tab["air_ml"] > 0, "air_ml"]
        xlo = float(pos.min()) * 0.8 if len(pos) else 0.05
        xhi = float(tab["air_ml"].max()) * 1.05 + 0.05
        xx = np.linspace(max(xlo, 0.05), xhi, 100)
        ax.plot(xx, k_s + fit["C_N_mm_per_ml"] / (fit["V0_ml"] + xx), "r-", lw=1.6,
                label="model k_s+C/(V0+V)")
        ymax = float(np.nanmax(tab["K_N_per_mm"] + tab["K_sd"].fillna(0.0))) * 1.35
        ax.set_ylim(0, max(ymax, k_s * 1.2, 1.0))
    ax.set_xlabel("气泡量 V_air (mL)")
    ax.set_ylabel("等效刚度 K_eff (N/mm)")
    ax.set_title("软体关节：刚度 - 气泡量")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    png = os.path.join(args.dir, "demo_stiffness.png")
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print("图 ->", png)


def _run(args, func, name):
    print(f"\n===== {name} =====")
    try:
        func(args)
    except Exception as exc:
        print(f"[失败] {name}: {exc}")


def cmd_all(args):
    _run(args, cmd_spring, "spring")
    _run(args, cmd_static, "static")
    _run(args, cmd_step, "step")
    _run(args, cmd_demo, "demo")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_dir = os.path.join(here, "data", "bubble")

    p = argparse.ArgumentParser(description="气泡柔度 / 可变刚度 / 气泡检测 分析")
    sub = p.add_subparsers(dest="cmd", required=True)
    funcs = {"spring": cmd_spring, "static": cmd_static, "step": cmd_step,
             "demo": cmd_demo, "all": cmd_all}
    for name, func in funcs.items():
        sp = sub.add_parser(name)
        sp.add_argument("--dir", default=default_dir, help="数据目录")
        sp.add_argument("--k-spring", type=float, default=None,
                        help="静态实验里若装了输出弹簧，填它的 k 以扣除；默认 0")
        sp.add_argument("--area-out", type=float, default=A_OUT_DEFAULT,
                        help="输出针筒面积 mm2，用于估算绝热指数 n")
        sp.set_defaults(func=func)

    args = p.parse_args()
    os.makedirs(args.dir, exist_ok=True)
    args.func(args)


if __name__ == "__main__":
    main()
