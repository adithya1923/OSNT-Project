import multiprocessing as mp
import sys


def main():
    mp.set_start_method("fork")

    from src.config import (
        load_config,
        set_config_value,
    )

    from src.experiment import run_experiment

    from src.results import (
        snapshot_dump_directories,
        process_completed_experiment,
    )

    if len(sys.argv) != 2:
        print(
            "Usage: "
            "sudo ~/python-projects/myenv/bin/python "
            "-m run.run_sweep <config_file>"
        )
        print()
        print("Example:")
        print(
            "sudo ~/python-projects/myenv/bin/python "
            "-m run.run_sweep configs/bandwidth.json"
        )
        return

    config_path = sys.argv[1]

    config = load_config(config_path)

    experiment_group = config["experiment_group"]

    sweep = config["sweep"]

    parameter_name = sweep["parameter"]
    parameter_values = sweep["values"]

    conditions = [
        ("ecn_off", False),
        ("ecn_on", True),
    ]

    for parameter_value in parameter_values:

        print()
        print("#" * 70)
        print(
            f"Parameter: {parameter_name}"
        )
        print(
            f"Value: {parameter_value}"
        )
        print("#" * 70)

        current_config = set_config_value(
            config,
            parameter_name,
            parameter_value,
        )

        current_config["experiment_name"] = (
            f"{config['experiment_name']}-"
            f"{parameter_value}"
        )

        for condition, ecn_enabled in conditions:

            print()
            print("=" * 60)
            print(
                f"Running {experiment_group}: "
                f"{parameter_value} / "
                f"{condition.upper()}"
            )
            print("=" * 60)

            before_dumps = (
                snapshot_dump_directories(
                    current_config["experiment_name"]
                )
            )

            run_experiment(
                config=current_config,
                ecn_enabled=ecn_enabled
            )

            (
                organized_dir,
                processed_file,
                metrics,
            ) = process_completed_experiment(
                experiment_name=(
                    current_config[
                        "experiment_name"
                    ]
                ),
                experiment_group=experiment_group,
                parameter_name=parameter_name,
                parameter_value=parameter_value,
                condition=condition,
                before_dumps=before_dumps,
            )

            print()
            print(
                f"Raw results: {organized_dir}"
            )

            print(
                f"Processed results: "
                f"{processed_file}"
            )

            print("Metrics:")

            for key, value in metrics.items():
                print(
                    f"  {key}: {value}"
                )

    print()
    print("=" * 70)
    print(
        f"{experiment_group.capitalize()} "
        f"sweep completed successfully."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()