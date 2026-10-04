from nest.experiment import Flow


def create_tcp_flow(
    experiment,
    source,
    destination,
    destination_address,
    config,
):
    traffic = config["traffic"]

    number_of_streams = traffic.get(
        "number_of_streams",
        1
    )

    flow = Flow(
        source_node=source,
        destination_node=destination,
        destination_address=destination_address,
        start_time=traffic["start_time"],
        stop_time=traffic["duration"],
        number_of_streams=number_of_streams,
    )

    experiment.add_tcp_flow(
        flow,
        congestion_algorithm="cubic"
    )

    return flow