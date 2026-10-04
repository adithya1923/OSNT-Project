import json
from pathlib import Path


def configure_metrics(experiment, bottleneck_interface):
    experiment.require_qdisc_stats(bottleneck_interface)


def _load_json(path):
    with open(path, "r") as file:
        return json.load(file)


def _find_samples(obj, required_keys):
    samples = []

    if isinstance(obj, list):
        for item in obj:
            samples.extend(
                _find_samples(item, required_keys)
            )

    elif isinstance(obj, dict):
        if all(key in obj for key in required_keys):
            samples.append(obj)
        else:
            for value in obj.values():
                samples.extend(
                    _find_samples(value, required_keys)
                )

    return samples


def _numeric_values(samples, key):
    values = []

    for sample in samples:
        try:
            values.append(float(sample[key]))
        except (KeyError, TypeError, ValueError):
            continue

    return values


def _average(values):
    if not values:
        return None

    return sum(values) / len(values)


def _extract_flow_samples(data, node_name):
    """
    Extract all measurement samples belonging to one
    specific source node.

    NeST stores flows in the form:

        node
          -> destination:port
             -> samples

    The meta entry identifies the destination and timing,
    while the remaining entries contain measurements.
    """

    node_data = data.get(node_name, [])

    samples = []

    def collect(obj):
        if isinstance(obj, list):
            for item in obj:
                collect(item)

        elif isinstance(obj, dict):
            if (
                "timestamp" in obj
                and not obj.get("meta", False)
            ):
                samples.append(obj)
            else:
                for value in obj.values():
                    collect(value)

    collect(node_data)

    return samples


def _jain_fairness(values):
    """
    Calculate Jain's fairness index.

    For two flows:

        J = (sum(x))^2 / (n * sum(x^2))

    A value of 1 means equal sharing.
    """

    valid_values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not valid_values:
        return None

    denominator = len(valid_values) * sum(
        value ** 2
        for value in valid_values
    )

    if denominator == 0:
        return None

    numerator = sum(valid_values) ** 2

    return numerator / denominator


def _extract_mixed_flow_metrics(
    ss_data,
    netperf_data,
):
    """
    Extract per-flow metrics for the mixed ECN/non-ECN
    experiment.

    The mixed topology uses:

        h1_ecn   -> ECN-capable flow
        h3_noecn -> non-ECN flow
    """

    ecn_ss_samples = _extract_flow_samples(
        ss_data,
        "h1_ecn",
    )

    non_ecn_ss_samples = _extract_flow_samples(
        ss_data,
        "h3_noecn",
    )

    ecn_netperf_samples = _extract_flow_samples(
        netperf_data,
        "h1_ecn",
    )

    non_ecn_netperf_samples = _extract_flow_samples(
        netperf_data,
        "h3_noecn",
    )

    ecn_sending_rates = _numeric_values(
        ecn_netperf_samples,
        "sending_rate",
    )

    non_ecn_sending_rates = _numeric_values(
        non_ecn_netperf_samples,
        "sending_rate",
    )

    ecn_delivery_rates = _numeric_values(
        ecn_ss_samples,
        "delivery_rate",
    )

    non_ecn_delivery_rates = _numeric_values(
        non_ecn_ss_samples,
        "delivery_rate",
    )

    ecn_rtts = _numeric_values(
        ecn_ss_samples,
        "rtt",
    )

    non_ecn_rtts = _numeric_values(
        non_ecn_ss_samples,
        "rtt",
    )

    ecn_avg_sending = _average(
        ecn_sending_rates
    )

    non_ecn_avg_sending = _average(
        non_ecn_sending_rates
    )

    metrics = {
        "ecn_flow_avg_sending_rate": (
            ecn_avg_sending
        ),
        "non_ecn_flow_avg_sending_rate": (
            non_ecn_avg_sending
        ),
        "ecn_flow_avg_delivery_rate": (
            _average(ecn_delivery_rates)
        ),
        "non_ecn_flow_avg_delivery_rate": (
            _average(non_ecn_delivery_rates)
        ),
        "ecn_flow_avg_tcp_rtt_ms": (
            _average(ecn_rtts)
        ),
        "non_ecn_flow_avg_tcp_rtt_ms": (
            _average(non_ecn_rtts)
        ),
    }

    metrics["jain_fairness"] = _jain_fairness(
        [
            ecn_avg_sending,
            non_ecn_avg_sending,
        ]
    )

    return metrics


def extract_metrics(dump_dir):
    dump_dir = Path(dump_dir)

    tc_data = _load_json(
        dump_dir / "tc.json"
    )

    ss_data = _load_json(
        dump_dir / "ss.json"
    )

    ping_data = _load_json(
        dump_dir / "ping.json"
    )

    netperf_data = _load_json(
        dump_dir / "netperf.json"
    )

    # ---------------------------------------------------------
    # Aggregate qdisc metrics
    # ---------------------------------------------------------

    tc_samples = _find_samples(
        tc_data,
        {
            "kind",
            "ecn_mark",
            "drops",
            "qlen",
            "backlog",
        },
    )

    tc_samples = [
        sample
        for sample in tc_samples
        if sample.get("kind") == "fq_codel"
    ]

    # ---------------------------------------------------------
    # Aggregate TCP metrics
    # ---------------------------------------------------------

    ss_samples = _find_samples(
        ss_data,
        {
            "timestamp",
            "rtt",
            "delivery_rate",
        },
    )

    ping_samples = _find_samples(
        ping_data,
        {
            "timestamp",
            "rtt",
        },
    )

    netperf_samples = _find_samples(
        netperf_data,
        {
            "timestamp",
            "sending_rate",
        },
    )

    metrics = {}

    # ---------------------------------------------------------
    # Qdisc metrics
    # ---------------------------------------------------------

    if tc_samples:
        last_tc = tc_samples[-1]

        metrics["packets"] = int(
            float(last_tc["packets"])
        )

        metrics["bytes"] = int(
            float(last_tc["bytes"])
        )

        metrics["drops"] = int(
            float(last_tc["drops"])
        )

        metrics["ecn_marks"] = int(
            float(last_tc["ecn_mark"])
        )

        metrics["overlimits"] = int(
            float(last_tc["overlimits"])
        )

        metrics["requeues"] = int(
            float(last_tc["requeues"])
        )

        metrics["max_qlen"] = max(
            int(float(sample["qlen"]))
            for sample in tc_samples
        )

        metrics["max_backlog"] = max(
            int(float(sample["backlog"]))
            for sample in tc_samples
        )

    # ---------------------------------------------------------
    # Ping metrics
    # ---------------------------------------------------------

    if ping_samples:
        ping_rtts = _numeric_values(
            ping_samples,
            "rtt",
        )

        metrics["avg_ping_rtt_ms"] = _average(
            ping_rtts
        )

        metrics["max_ping_rtt_ms"] = max(
            ping_rtts
        )

        metrics["min_ping_rtt_ms"] = min(
            ping_rtts
        )

    # ---------------------------------------------------------
    # Aggregate TCP metrics
    # ---------------------------------------------------------

    if ss_samples:
        ss_rtts = _numeric_values(
            ss_samples,
            "rtt",
        )

        delivery_rates = _numeric_values(
            ss_samples,
            "delivery_rate",
        )

        metrics["avg_tcp_rtt_ms"] = _average(
            ss_rtts
        )

        metrics["max_tcp_rtt_ms"] = max(
            ss_rtts
        )

        metrics["avg_delivery_rate"] = _average(
            delivery_rates
        )

    # ---------------------------------------------------------
    # Aggregate Netperf metrics
    # ---------------------------------------------------------

    if netperf_samples:
        sending_rates = _numeric_values(
            netperf_samples,
            "sending_rate",
        )

        metrics["avg_sending_rate"] = _average(
            sending_rates
        )

        metrics["max_sending_rate"] = max(
            sending_rates
        )

        metrics["min_sending_rate"] = min(
            sending_rates
        )

    # ---------------------------------------------------------
    # Mixed ECN / non-ECN metrics
    # ---------------------------------------------------------

    mixed_metrics = _extract_mixed_flow_metrics(
        ss_data=ss_data,
        netperf_data=netperf_data,
    )

    # Only add mixed metrics when both flows were
    # actually found.
    if (
        mixed_metrics["ecn_flow_avg_sending_rate"]
        is not None
        and
        mixed_metrics["non_ecn_flow_avg_sending_rate"]
        is not None
    ):
        metrics.update(mixed_metrics)

    return metrics