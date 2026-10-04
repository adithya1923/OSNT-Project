from nest.experiment import Experiment

from .topologies.bottleneck import create_bottleneck
from .qdisc import configure_fq_codel
from .traffic import create_tcp_flow
from .metrics import configure_metrics


def run_experiment(config, ecn_enabled):
    h1, h2, bottleneck, h2_if = create_bottleneck(config)

    h1.configure_tcp_param(
        "ecn",
        "1" if ecn_enabled else "0"
    )

    h2.configure_tcp_param(
        "ecn",
        "1" if ecn_enabled else "0"
    )

    configure_fq_codel(
        interface=bottleneck,
        config=config,
        ecn_enabled=ecn_enabled
    )

    experiment = Experiment(
        config["experiment_name"]
    )

    create_tcp_flow(
        experiment=experiment,
        source=h1,
        destination=h2,
        destination_address=h2_if.address,
        config=config
    )

    configure_metrics(
        experiment,
        bottleneck
    )

    experiment.run()