def configure_fq_codel(
    interface,
    config,
    ecn_enabled
):
    qdisc = config["qdisc"]

    parameters = {
        "limit": str(qdisc["limit"]),
        "flows": str(qdisc["flows"]),
        "target": str(qdisc["target"]),
        "interval": str(qdisc["interval"]),
    }

    if ecn_enabled:
        parameters["ecn"] = ""
    else:
        parameters["noecn"] = ""

    topology = config["topology"]

    interface.set_attributes(
        topology["bottleneck_bandwidth"],
        topology["bottleneck_delay"],
        "fq_codel",
        **parameters
    )