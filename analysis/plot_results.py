import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "processed"
PLOTS_DIR = PROJECT_ROOT / "analysis" / "plots"


def load_csv(filename):
    path = RESULTS_DIR / filename

    with open(path, "r", newline="") as file:
        return list(csv.DictReader(file))


def to_float(value):
    if value is None or value == "":
        return None

    return float(value)


def to_label(value):
    return str(value)


def ensure_plot_directory():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_comparison(
    rows,
    x_column,
    x_label,
    y_column,
    y_label,
    title,
    filename,
):
    values = []
    ecn_off = []
    ecn_on = []

    for row in rows:
        value = to_label(row[x_column])

        if value not in values:
            values.append(value)

    for value in values:
        off_row = next(
            (
                row
                for row in rows
                if to_label(row[x_column]) == value
                and row["condition"] == "ecn_off"
            ),
            None,
        )

        on_row = next(
            (
                row
                for row in rows
                if to_label(row[x_column]) == value
                and row["condition"] == "ecn_on"
            ),
            None,
        )

        ecn_off.append(
            to_float(off_row[y_column])
            if off_row
            else None
        )

        ecn_on.append(
            to_float(on_row[y_column])
            if on_row
            else None
        )

    x = list(range(len(values)))
    width = 0.35

    plt.figure(figsize=(9, 5))

    plt.bar(
        [i - width / 2 for i in x],
        ecn_off,
        width=width,
        label="ECN OFF",
    )

    plt.bar(
        [i + width / 2 for i in x],
        ecn_on,
        width=width,
        label="ECN ON",
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(x, values)
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / filename,
        dpi=300,
    )

    plt.close()


def generate_standard_plots(filename, parameter_column, prefix, parameter_label):
    rows = load_csv(filename)

    plot_comparison(
        rows,
        parameter_column,
        parameter_label,
        "drops",
        "Packets dropped",
        f"Packet Drops vs {parameter_label}",
        f"{prefix}_drops.png",
    )

    plot_comparison(
        rows,
        parameter_column,
        parameter_label,
        "ecn_marks",
        "ECN marks",
        f"ECN Marks vs {parameter_label}",
        f"{prefix}_ecn_marks.png",
    )

    plot_comparison(
        rows,
        parameter_column,
        parameter_label,
        "avg_tcp_rtt_ms",
        "Average TCP RTT (ms)",
        f"Average TCP RTT vs {parameter_label}",
        f"{prefix}_tcp_rtt.png",
    )

    plot_comparison(
        rows,
        parameter_column,
        parameter_label,
        "avg_sending_rate",
        "Average sending rate (Mbps)",
        f"Average Recorded Sending Rate vs {parameter_label}",
        f"{prefix}_sending_rate.png",
    )

    plot_comparison(
        rows,
        parameter_column,
        parameter_label,
        "max_qlen",
        "Maximum queue length (packets)",
        f"Maximum Queue Length vs {parameter_label}",
        f"{prefix}_max_queue.png",
    )


def plot_mixed_results():
    rows = load_csv("mixed.csv")

    # Only use rows where per-flow metrics exist.
    valid_rows = [
        row
        for row in rows
        if row["ecn_flow_avg_sending_rate"] != ""
        and row["non_ecn_flow_avg_sending_rate"] != ""
    ]

    if not valid_rows:
        print("No complete mixed-flow data found.")
        return

    row = valid_rows[-1]

    labels = [
        "ECN flow",
        "Non-ECN flow",
    ]

    throughputs = [
        to_float(row["ecn_flow_avg_sending_rate"]),
        to_float(row["non_ecn_flow_avg_sending_rate"]),
    ]

    delivery_rates = [
        to_float(row["ecn_flow_avg_delivery_rate"]),
        to_float(row["non_ecn_flow_avg_delivery_rate"]),
    ]

    rtts = [
        to_float(row["ecn_flow_avg_tcp_rtt_ms"]),
        to_float(row["non_ecn_flow_avg_tcp_rtt_ms"]),
    ]

    # ---------------------------------------------------------
    # Throughput
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        labels,
        throughputs,
    )

    plt.xlabel("Flow")
    plt.ylabel("Average sending rate (Mbps)")
    plt.title("Mixed Traffic: Per-Flow Throughput")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "mixed_flow_throughput.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Delivery rate
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        labels,
        delivery_rates,
    )

    plt.xlabel("Flow")
    plt.ylabel("Average delivery rate (Mbps)")
    plt.title("Mixed Traffic: Per-Flow Delivery Rate")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "mixed_flow_delivery_rate.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # RTT
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        labels,
        rtts,
    )

    plt.xlabel("Flow")
    plt.ylabel("Average TCP RTT (ms)")
    plt.title("Mixed Traffic: Per-Flow RTT")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "mixed_flow_rtt.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Jain fairness
    # ---------------------------------------------------------

    fairness = to_float(
        row["jain_fairness"]
    )

    plt.figure(figsize=(6, 5))

    plt.bar(
        ["Mixed ECN / non-ECN"],
        [fairness],
    )

    plt.ylim(0, 1.05)
    plt.ylabel("Jain's fairness index")
    plt.title("Mixed Traffic: Fairness")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "mixed_fairness.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Drops vs ECN marks
    # ---------------------------------------------------------

    drops = to_float(row["drops"])
    marks = to_float(row["ecn_marks"])

    plt.figure(figsize=(7, 5))

    plt.bar(
        ["Packet drops", "ECN marks"],
        [drops, marks],
    )

    plt.ylabel("Count")
    plt.title("Mixed Traffic: Drops and ECN Marks")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "mixed_drops_vs_marks.png",
        dpi=300,
    )

    plt.close()

    print()
    print("Mixed-flow metrics used for plotting:")
    print(
        f"  ECN flow throughput     : "
        f"{throughputs[0]:.4f} Mbps"
    )
    print(
        f"  Non-ECN flow throughput : "
        f"{throughputs[1]:.4f} Mbps"
    )
    print(
        f"  ECN flow RTT            : "
        f"{rtts[0]:.4f} ms"
    )
    print(
        f"  Non-ECN flow RTT        : "
        f"{rtts[1]:.4f} ms"
    )
    print(
        f"  Jain fairness           : "
        f"{fairness:.4f}"
    )


def main():
    ensure_plot_directory()

    print("Generating bandwidth plots...")
    generate_standard_plots(
        "bandwidth.csv",
        "parameter_value",
        "bandwidth",
        "Bottleneck Bandwidth",
    )

    print("Generating delay plots...")
    generate_standard_plots(
        "delay.csv",
        "parameter_value",
        "delay",
        "Bottleneck Delay",
    )

    print("Generating queue-size plots...")
    generate_standard_plots(
        "queue_size.csv",
        "parameter_value",
        "queue_size",
        "Queue Limit",
    )

    print("Generating traffic-load plots...")
    generate_standard_plots(
        "traffic_load.csv",
        "parameter_value",
        "traffic_load",
        "Number of CUBIC Streams",
    )

    # Baseline has no sweep parameter.
    # It will be handled separately below.

    print("Generating baseline plots...")

    baseline_rows = load_csv("baseline.csv")

    # Baseline contains multiple repetitions for each
    # ECN condition. Average the repetitions before plotting.
    baseline_labels = [
        "ECN OFF",
        "ECN ON",
    ]

    def baseline_average(condition, column):
        values = [
            to_float(row[column])
            for row in baseline_rows
            if row["condition"] == condition
        ]

        values = [
            value
            for value in values
            if value is not None
        ]

        if not values:
            return None

        return sum(values) / len(values)

    baseline_drops = [
        baseline_average("ecn_off", "drops"),
        baseline_average("ecn_on", "drops"),
    ]

    baseline_marks = [
        baseline_average("ecn_off", "ecn_marks"),
        baseline_average("ecn_on", "ecn_marks"),
    ]

    baseline_rtt = [
        baseline_average("ecn_off", "avg_tcp_rtt_ms"),
        baseline_average("ecn_on", "avg_tcp_rtt_ms"),
    ]

    baseline_rate = [
        baseline_average("ecn_off", "avg_sending_rate"),
        baseline_average("ecn_on", "avg_sending_rate"),
    ]

    # ---------------------------------------------------------
    # Baseline drops
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        baseline_labels,
        baseline_drops,
    )

    plt.ylabel("Average packets dropped")
    plt.title("Baseline: Average Packet Drops")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "baseline_drops.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Baseline ECN marks
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        baseline_labels,
        baseline_marks,
    )

    plt.ylabel("Average ECN marks")
    plt.title("Baseline: Average ECN Marks")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "baseline_ecn_marks.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Baseline RTT
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        baseline_labels,
        baseline_rtt,
    )

    plt.ylabel("Average TCP RTT (ms)")
    plt.title("Baseline: Average TCP RTT")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "baseline_tcp_rtt.png",
        dpi=300,
    )

    plt.close()

    # ---------------------------------------------------------
    # Baseline sending rate
    # ---------------------------------------------------------

    plt.figure(figsize=(7, 5))

    plt.bar(
        baseline_labels,
        baseline_rate,
    )

    plt.ylabel("Average sending rate (Mbps)")
    plt.title("Baseline: Average Sending Rate")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "baseline_sending_rate.png",
        dpi=300,
    )

    plt.close()

    print("Generating mixed-traffic plots...")
    plot_mixed_results()

    print()
    print("=" * 60)
    print("All plots generated successfully.")
    print("=" * 60)
    print()
    print(f"Plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()