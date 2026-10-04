import multiprocessing as mp


def main():
    mp.set_start_method("fork")

    from src.config import load_config
    from src.experiment import run_experiment
    from src.results import (
        snapshot_dump_directories,
        process_completed_experiment,
    )

    config = load_config("configs/baseline.json")

    experiment_name = config["experiment_name"]
    experiment_group = config["experiment_group"]

    experiments = [
        ("ecn_off", False),
        ("ecn_on", True),
    ]

    for condition, ecn_enabled in experiments:
        print()
        print("=" * 60)
        print(f"Running baseline condition: {condition}")
        print(f"ECN enabled: {ecn_enabled}")
        print("=" * 60)

        before_dumps = snapshot_dump_directories(experiment_name)

        run_experiment(
            config=config,
            ecn_enabled=ecn_enabled,
        )

        organized_dir, processed_file, metrics = (
            process_completed_experiment(
                experiment_name=experiment_name,
                experiment_group=experiment_group,
                parameter_name="baseline",
                parameter_value="default",
                condition=condition,
                before_dumps=before_dumps,
            )
        )

        print()
        print(f"Organized raw results: {organized_dir}")
        print(f"Processed results: {processed_file}")
        print("Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

    print()
    print("=" * 60)
    print("Baseline experiment completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()