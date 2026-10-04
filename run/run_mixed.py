import multiprocessing as mp


def main():
    # Required for the current Python/NeST environment.
    mp.set_start_method("fork")

    from src.config import load_config
    from src.mixed_experiment import run_mixed_experiment
    from src.results import (
        snapshot_dump_directories,
        process_completed_experiment,
    )

    config = load_config("configs/mixed.json")

    experiment_name = config["experiment_name"]
    experiment_group = config["experiment_group"]

    condition = "ecn_mixed"

    print()
    print("=" * 70)
    print("Running mixed ECN/non-ECN experiment")
    print("=" * 70)

    print()
    print("Configuration:")
    print("  ECN flow     : ECN enabled")
    print("  Non-ECN flow : ECN disabled")
    print("  CC algorithm : CUBIC")
    print("  Bottleneck   : 10 Mbps / 10 ms")
    print("  Queue limit  : 100 packets")
    print("  Duration     : 20 seconds")

    before_dumps = snapshot_dump_directories(
        experiment_name
    )

    run_mixed_experiment(
        config=config
    )

    (
        organized_dir,
        processed_file,
        metrics,
    ) = process_completed_experiment(
        experiment_name=experiment_name,
        experiment_group=experiment_group,
        parameter_name="mixed_traffic",
        parameter_value="1_ecn_1_non_ecn",
        condition=condition,
        before_dumps=before_dumps,
    )

    print()
    print("=" * 70)
    print("Mixed experiment completed")
    print("=" * 70)

    print()
    print(f"Raw results: {organized_dir}")
    print(f"Processed results: {processed_file}")

    print()
    print("Metrics:")

    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()