#!/usr/bin/env python3
"""
analyze_response_times.py

Reads a CSV file named 'response_times.txt' from a given directory and produces:
  1. boxplot_response_times.pdf  — boxplot of response times per service URL
  2. barplot_success_failure.pdf — bar plot of successes vs failures per service URL

CSV format (no header, semicolon-separated):
    <http_status_code>; <response_time>; <service_url>; <custom_tag>

The custom_tag field is a pipe-separated list of "<function>:<region>" tokens
indicating where each function completed, e.g.:
    auth:eu-west|db:us-east|cache:eu-west

Produces:
  1. boxplot_response_times.pdf  — response time distribution per service
  2. barplot_success_failure.pdf — Success / Dropped / Failed counts per service
  3. region_completion.pdf       — stacked % bar chart: one row per function,
                                   segments coloured by region

Usage:
    python analyze_response_times.py /path/to/directory
"""

import sys
import os
import csv

import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ── helpers ──────────────────────────────────────────────────────────────────

def load_data(directory: str) -> pd.DataFrame:
    csv_path = os.path.join(directory, "response_times.txt")
    if not os.path.isfile(csv_path):
        sys.exit(f"ERROR: File not found: {csv_path}")

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter=";")
        for lineno, row in enumerate(reader, start=1):
            if not row or all(cell.strip() == "" for cell in row):
                continue                          # skip blank lines
            if len(row) < 4:
                print(f"  WARNING: line {lineno} has fewer than 4 fields — skipped")
                continue
            try:
                status    = int(row[0].strip())
                resp_time = float(row[1].strip())
            except ValueError:
                print(f"  WARNING: line {lineno} has non-numeric status/time — skipped")
                continue
            url    = row[2].strip()
            regionsCompl = row[3].strip()
            nodeCompl = row[4].strip()

            # Parse pipe-separated "function:region" tokens
            completions = []
            for token in regionsCompl.split("|"):
                token = token.strip()
                if ":" in token:
                    func, region = token.split(":", 1)
                    completions.append((func.strip(), region.strip()))
                elif token:
                    print(f"  WARNING: line {lineno} token '{token}' "
                          f"is not in <function>:<region> format — skipped")

            # Parse pipe-separated "function:node" tokens
            completionsNode = []
            for token in nodeCompl.split("|"):
                token = token.strip()
                if ":" in token:
                    func, node = token.split(":", 1)
                    completionsNode.append((func.strip(), node.strip()))
                elif token:
                    print(f"  WARNING: line {lineno} token '{token}' "
                          f"is not in <function>:<node> format — skipped")

            rows.append({"status": status, "response_time": resp_time,
                         "url": url,  "completions": completions, "completionsNode": completionsNode})

    if not rows:
        sys.exit("ERROR: No valid data rows found in response_times.txt")

    df = pd.DataFrame(rows)

    def classify(status: int) -> str:
        if 200 <= status <= 299:
            return "Success"
        if status == 429:
            return "Dropped"
        return "Failed"

    df["outcome"] = df["status"].apply(classify)
    return df


def short_label(url: str, max_len: int = 40) -> str:
    """Shorten a URL for use as an axis label."""
    return url if len(url) <= max_len else "…" + url[-(max_len - 1):]


# ── plot 1 : boxplot of response times per service ───────────────────────────

def plot_boxplot(df: pd.DataFrame, out_path: str) -> None:
    urls   = df["url"].unique()
    groups = [df.loc[df["url"] == u, "response_time"].values for u in urls]
    labels = [short_label(u) for u in urls]

    fig_w  = max(8, len(urls) * 1.6)
    fig, ax = plt.subplots(figsize=(fig_w, 6))

    bp = ax.boxplot(groups, patch_artist=True, notch=False,
                    medianprops=dict(color="black", linewidth=2))

    colors = plt.cm.tab10.colors
    for patch, color in zip(bp["boxes"], [colors[i % 10] for i in range(len(urls))]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Response Time (s)", fontsize=11)
    ax.set_xlabel("Service URL", fontsize=11)
    ax.set_title("Response Time Distribution per Service", fontsize=13, fontweight="bold")
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
    print(f"  Saved: {out_path}")


# ── plot 2 : bar plot of successes vs dropped vs failures per service ────────

def plot_bar_success_failure(df: pd.DataFrame, out_path: str) -> None:
    CATEGORIES = ["Success", "Dropped", "Failed"]
    COLORS     = {"Success": "#2ecc71", "Dropped": "#f39c12", "Failed": "#e74c3c"}

    summary = (
        df.groupby(["url", "outcome"])
          .size()
          .unstack(fill_value=0)
    )
    for cat in CATEGORIES:
        if cat not in summary.columns:
            summary[cat] = 0
    summary = summary[CATEGORIES]          # consistent column order

    urls   = summary.index.tolist()
    labels = [short_label(u) for u in urls]
    n      = len(urls)
    x      = range(n)
    width  = 0.25                          # three bars per group

    fig_w  = max(8, n * 2.4)
    fig, ax = plt.subplots(figsize=(fig_w, 6))

    offsets = [-width, 0, width]
    for cat, offset in zip(CATEGORIES, offsets):
        bars = ax.bar(
            [i + offset for i in x],
            summary[cat],
            width,
            label=f"{cat} ({'2xx' if cat == 'Success' else '429' if cat == 'Dropped' else 'other non-2xx'})",
            color=COLORS[cat],
            alpha=0.85,
        )
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                        str(int(h)), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Number of Requests", fontsize=11)
    ax.set_xlabel("Service URL", fontsize=11)
    ax.set_title("Success / Dropped / Failed per Service", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
    print(f"  Saved: {out_path}")


# ── plot 3 : region completion % per function ────────────────────────────────

def build_region_completion_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode the per-row completions list into a flat DataFrame:
        function | region
    One row per <function>:<region> token across all CSV rows.
    """
    records = []
    for _, row in df.iterrows():
        for func, region in row["completions"]:
            records.append({"function": func, "region": region})
    if not records:
        return pd.DataFrame(columns=["function", "region"])
    return pd.DataFrame(records)


def plot_region_completion(df: pd.DataFrame, directory: str) -> None:
    comp = build_region_completion_table(df)
    if comp.empty:
        print("  No function:region data found — skipping region completion plot.")
        return

    # Percentage of completions in each region, per function
    counts = (
        comp.groupby(["function", "region"])
            .size()
            .rename("count")
            .reset_index()
    )
    totals = counts.groupby("function")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100

    # Pivot: rows = functions (sorted), columns = regions (sorted)
    pivot = (
        counts.pivot(index="function", columns="region", values="pct")
              .fillna(0)
    )
    pivot = pivot.loc[sorted(pivot.index), sorted(pivot.columns)]

    functions   = pivot.index.tolist()
    all_regions = pivot.columns.tolist()
    n_funcs     = len(functions)

    # Consistent colour per region across the whole chart
    palette      = plt.cm.tab20.colors
    region_color = {r: palette[i % len(palette)] for i, r in enumerate(all_regions)}

    fig_h = max(3, n_funcs * 0.9 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_h))

    y_positions = list(range(n_funcs))   # one horizontal bar per function

    for region in all_regions:
        lefts = [
            pivot.loc[func, all_regions[:all_regions.index(region)]].sum()
            for func in functions
        ]
        vals = [pivot.loc[func, region] for func in functions]
        bars = ax.barh(
            y_positions, vals, left=lefts,
            color=region_color[region], alpha=0.88, height=0.6,
            label=region,
        )
        # Inline percentage label when the segment is wide enough
        for bar, left, val in zip(bars, lefts, vals):
            if val >= 4:
                ax.text(
                    left + val / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    ha="center", va="center",
                    fontsize=8, fontweight="bold", color="white",
                )

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentage of completions (%)", fontsize=11)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(functions, fontsize=10)
    ax.set_title("Region Completion % per Function", fontsize=13, fontweight="bold")
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    # Legend below the chart
    ax.legend(
        title="Region", title_fontsize=9,
        loc="upper left", bbox_to_anchor=(0, -0.12),
        ncol=min(len(all_regions), 5), fontsize=9, frameon=False,
    )

    out_path = os.path.join(directory, "region_completion.pdf")
    fig.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")

def build_node_completion_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode the per-row completions list into a flat DataFrame:
        function | node
    One row per <function>:<node> token across all CSV rows.
    """
    records = []
    for _, row in df.iterrows():
        for func, region in row["completionsNode"]:
            records.append({"function": func, "node": region})
    if not records:
        return pd.DataFrame(columns=["function", "node"])
    return pd.DataFrame(records)

def plot_node_completion(df: pd.DataFrame, directory: str) -> None:
    comp = build_node_completion_table(df)
    if comp.empty:
        print("  No function:node data found — skipping node completion plot.")
        return

    # Percentage of completions in each region, per function
    counts = (
        comp.groupby(["function", "node"])
            .size()
            .rename("count")
            .reset_index()
    )
    totals = counts.groupby("function")["count"].transform("sum")
    counts["pct"] = counts["count"] / totals * 100

    # Pivot: rows = functions (sorted), columns = regions (sorted)
    pivot = (
        counts.pivot(index="function", columns="node", values="pct")
              .fillna(0)
    )
    pivot = pivot.loc[sorted(pivot.index), sorted(pivot.columns)]

    functions   = pivot.index.tolist()
    all_regions = pivot.columns.tolist()
    n_funcs     = len(functions)

    # Consistent colour per region across the whole chart
    palette      = plt.cm.tab20.colors
    region_color = {r: palette[i % len(palette)] for i, r in enumerate(all_regions)}

    fig_h = max(3, n_funcs * 0.9 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_h))

    y_positions = list(range(n_funcs))   # one horizontal bar per function

    for region in all_regions:
        lefts = [
            pivot.loc[func, all_regions[:all_regions.index(region)]].sum()
            for func in functions
        ]
        vals = [pivot.loc[func, region] for func in functions]
        bars = ax.barh(
            y_positions, vals, left=lefts,
            color=region_color[region], alpha=0.88, height=0.6,
            label=region,
        )
        # Inline percentage label when the segment is wide enough
        for bar, left, val in zip(bars, lefts, vals):
            if val >= 4:
                ax.text(
                    left + val / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    ha="center", va="center",
                    fontsize=8, fontweight="bold", color="white",
                )

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentage of completions (%)", fontsize=11)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(functions, fontsize=10)
    ax.set_title("Node Completion % per Function", fontsize=13, fontweight="bold")
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    # Legend below the chart
    ax.legend(
        title="Node", title_fontsize=9,
        loc="upper left", bbox_to_anchor=(0, -0.12),
        ncol=min(len(all_regions), 5), fontsize=9, frameon=False,
    )

    out_path = os.path.join(directory, "node_completion.pdf")
    fig.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")

# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python {os.path.basename(__file__)} <directory>")

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        sys.exit(f"ERROR: Not a directory: {directory}")

    print(f"Loading data from: {directory}")
    df = load_data(directory)
    print(f"  {len(df)} valid rows loaded across {df['url'].nunique()} unique service(s).")
    counts = df["outcome"].value_counts()
    for cat in ("Success", "Dropped", "Failed"):
        print(f"    {cat}: {counts.get(cat, 0)}")

    plot_boxplot(
        df,
        os.path.join(directory, "boxplot_response_times.pdf")
    )
    plot_bar_success_failure(
        df,
        os.path.join(directory, "barplot_success_failure.pdf")
    )
    plot_region_completion(df, directory)
    plot_node_completion(df, directory)

    print("Done.")


if __name__ == "__main__":
    main()
