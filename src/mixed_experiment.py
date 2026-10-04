from nest.experiment import Experiment

from .topologies.mixed import create_mixed_topology
from .qdisc import configure_fq_codel
from .traffic import create_tcp_flow
from .metrics import configure_metrics


def run_mixed_experiment(config):
    topology = create_mixed_topology(config)

    ecn_sender = topology["ecn_sender"]
    ecn_receiver = topology["ecn_receiver"]

    non_ecn_sender = topology["non_ecn_sender"]
    non_ecn_receiver = topology["non_ecn_receiver"]

    bottleneck = topology["r1_bottleneck"]

    ecn_receiver_if = topology["ecn_receiver_if"]
    non_ecn_receiver_if = topology["non_ecn_receiver_if"]

    # ---------------------------------------------------------
    # Configure sender-side ECN
    # ---------------------------------------------------------

    ecn_sender.configure_tcp_param(
        "ecn",
        "1",
    )

    non_ecn_sender.configure_tcp_param(
        "ecn",
        "0",
    )

    # ---------------------------------------------------------
    # Configure FQ-CoDel with ECN enabled
    #
    # Important:
    # The qdisc itself must support ECN marking so that the
    # ECN-capable flow can receive CE marks.
    # ---------------------------------------------------------

    configure_fq_codel(
        interface=bottleneck,
        config=config,
        ecn_enabled=True,
    )

    # ---------------------------------------------------------
    # Create experiment
    # ---------------------------------------------------------

    experiment = Experiment(
        config["experiment_name"]
    )

    # ---------------------------------------------------------
    # ECN-capable CUBIC flow
    # ---------------------------------------------------------

    create_tcp_flow(
        experiment=experiment,
        source=ecn_sender,
        destination=ecn_receiver,
        destination_address=ecn_receiver_if.address,
        config=config,
    )

    # ---------------------------------------------------------
    # Non-ECN CUBIC flow
    # ---------------------------------------------------------

    create_tcp_flow(
        experiment=experiment,
        source=non_ecn_sender,
        destination=non_ecn_receiver,
        destination_address=non_ecn_receiver_if.address,
        config=config,
    )

    # ---------------------------------------------------------
    # Collect bottleneck qdisc statistics
    # ---------------------------------------------------------

    configure_metrics(
        experiment,
        bottleneck,
    )

    experiment.run()