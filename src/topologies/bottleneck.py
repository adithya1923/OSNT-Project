from nest.topology import Node, Router, connect
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper


def create_bottleneck(config):
    topology = config["topology"]

    endpoint_bandwidth = topology["endpoint_bandwidth"]
    endpoint_delay = topology["endpoint_delay"]

    bottleneck_bandwidth = topology["bottleneck_bandwidth"]
    bottleneck_delay = topology["bottleneck_delay"]

    h1 = Node("h1")
    h2 = Node("h2")

    r1 = Router("r1")
    r2 = Router("r2")

    n1 = Network("10.0.1.0/24")
    n2 = Network("10.0.2.0/24")
    n3 = Network("10.0.3.0/24")

    h1_if, r1_if = connect(
        h1,
        r1,
        network=n1
    )

    r1_bottleneck, r2_bottleneck = connect(
        r1,
        r2,
        network=n2
    )

    r2_if, h2_if = connect(
        r2,
        h2,
        network=n3
    )

    AddressHelper.assign_addresses()

    h1_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay
    )

    r1_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay
    )

    r1_bottleneck.set_attributes(
        bottleneck_bandwidth,
        bottleneck_delay
    )

    r2_bottleneck.set_attributes(
        bottleneck_bandwidth,
        bottleneck_delay
    )

    r2_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay
    )

    h2_if.set_attributes(
        endpoint_bandwidth,
        endpoint_delay
    )

    h1.add_route("DEFAULT", h1_if)
    h2.add_route("DEFAULT", h2_if)

    r1.add_route("DEFAULT", r1_bottleneck)
    r2.add_route("DEFAULT", r2_bottleneck)

    return h1, h2, r1_bottleneck, h2_if