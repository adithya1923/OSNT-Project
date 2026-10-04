from nest.topology import Node, Router, connect
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper


def create_mixed_topology(config):
    topology = config["topology"]

    endpoint_bandwidth = topology["endpoint_bandwidth"]
    endpoint_delay = topology["endpoint_delay"]

    bottleneck_bandwidth = topology["bottleneck_bandwidth"]
    bottleneck_delay = topology["bottleneck_delay"]

    # ECN-capable sender and receiver
    ecn_sender = Node("h1_ecn")
    ecn_receiver = Node("h2_ecn")

    # Non-ECN sender and receiver
    non_ecn_sender = Node("h3_noecn")
    non_ecn_receiver = Node("h4_noecn")

    r1 = Router("r1")
    r2 = Router("r2")

    # Separate endpoint networks.
    n1 = Network("10.0.1.0/24")
    n2 = Network("10.0.2.0/24")
    n3 = Network("10.0.3.0/24")
    n4 = Network("10.0.4.0/24")
    n5 = Network("10.0.5.0/24")

    # ECN sender -> r1
    ecn_sender_if, r1_ecn_if = connect(
        ecn_sender,
        r1,
        network=n1,
    )

    # Non-ECN sender -> r1
    non_ecn_sender_if, r1_noecn_if = connect(
        non_ecn_sender,
        r1,
        network=n2,
    )

    # Shared bottleneck
    r1_bottleneck, r2_bottleneck = connect(
        r1,
        r2,
        network=n3,
    )

    # r2 -> ECN receiver
    r2_ecn_if, ecn_receiver_if = connect(
        r2,
        ecn_receiver,
        network=n4,
    )

    # r2 -> Non-ECN receiver
    r2_noecn_if, non_ecn_receiver_if = connect(
        r2,
        non_ecn_receiver,
        network=n5,
    )

    AddressHelper.assign_addresses()

    # Endpoint links
    ecn_sender_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    r1_ecn_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    non_ecn_sender_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    r1_noecn_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    r2_ecn_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    ecn_receiver_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    r2_noecn_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    non_ecn_receiver_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay,
    )

    # Shared bottleneck
    r1_bottleneck.set_attributes(
        bottleneck_bandwidth,
        bottleneck_delay,
    )

    r2_bottleneck.set_attributes(
        bottleneck_bandwidth,
        bottleneck_delay,
    )

    # Host default routes
    ecn_sender.add_route(
        "DEFAULT",
        ecn_sender_if,
    )

    non_ecn_sender.add_route(
        "DEFAULT",
        non_ecn_sender_if,
    )

    ecn_receiver.add_route(
        "DEFAULT",
        ecn_receiver_if,
    )

    non_ecn_receiver.add_route(
        "DEFAULT",
        non_ecn_receiver_if,
    )

    # Router default routes through the bottleneck.
    r1.add_route(
        "DEFAULT",
        r1_bottleneck,
    )

    r2.add_route(
        "DEFAULT",
        r2_bottleneck,
    )

    return {
        "ecn_sender": ecn_sender,
        "ecn_receiver": ecn_receiver,
        "non_ecn_sender": non_ecn_sender,
        "non_ecn_receiver": non_ecn_receiver,
        "r1_bottleneck": r1_bottleneck,
        "ecn_receiver_if": ecn_receiver_if,
        "non_ecn_receiver_if": non_ecn_receiver_if,
    }