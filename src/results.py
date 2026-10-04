import csv
import shutil
from pathlib import Path

from .metrics import extract_metrics


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"
PROCESSED_DIR = RESULTS_DIR / "processed"


def snapshot_dump_directories(experiment_name):
    pattern = f"{experiment_name}*_dump"

    return {
        path.resolve()
        for path in PROJECT_ROOT.glob(pattern)
        if path.is_dir()
    }


def find_new_dump(experiment_name, before):
    pattern = f"{experiment_name}*_dump"

    after = {
        path.resolve()
        for path in PROJECT_ROOT.glob(pattern)
        if path.is_dir()
    }

    new_dumps = after - before

    if len(new_dumps) != 1:
        raise RuntimeError(
            f"Expected exactly one new NeST dump for "
            f"'{experiment_name}', found {len(new_dumps)}."
        )

    return next(iter(new_dumps))


def _safe_directory_name(value):
    """
    Convert a parameter value into a filesystem-friendly name.
    """

    text = str(value)

    replacements = {
        "/": "_",
        "\\": "_",
        " ": "_",
        ":": "_",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def _next_run_directory(base_dir):
    base_dir.mkdir(parents=True, exist_ok=True)

    existing = []

    for path in base_dir.glob("run_*"):
        if path.is_dir():
            try:
                existing.append(int(path.name.split("_")[1]))
            except (IndexError, ValueError):
                continue

    next_number = max(existing, default=0) + 1

    return base_dir / f"run_{next_number:03d}"


def organize_dump(
    dump_dir,
    experiment_group,
    parameter_name,
    parameter_value,
    condition,
):
    parameter_directory = _safe_directory_name(parameter_value)

    destination_base = (
        RAW_DIR
        / experiment_group
        / parameter_directory
        / condition
    )

    destination = _next_run_directory(destination_base)

    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(
        str(dump_dir),
        str(destination)
    )

    return destination


def _round_metrics(metrics):
    rounded = {}

    for key, value in metrics.items():
        if isinstance(value, float):
            rounded[key] = round(value, 4)
        else:
            rounded[key] = value

    return rounded


def save_processed_result(
    experiment_group,
    parameter_name,
    parameter_value,
    condition,
    run_directory,
    metrics,
):
    output_file = (
        PROCESSED_DIR
        / f"{experiment_group}.csv"
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    row = {
        "experiment_group": experiment_group,
        "parameter": parameter_name,
        "parameter_value": parameter_value,
        "condition": condition,
        "run_directory": str(
            run_directory.resolve().relative_to(PROJECT_ROOT)
        ),
        **_round_metrics(metrics),
    }

    if output_file.exists():

        with open(
            output_file,
            "r",
            newline=""
        ) as file:

            existing_reader = csv.DictReader(file)
            existing_rows = list(existing_reader)
            existing_fields = (
                existing_reader.fieldnames or []
            )

        all_fields = list(
            dict.fromkeys(
                existing_fields + list(row.keys())
            )
        )

        for existing_row in existing_rows:
            for field in all_fields:
                existing_row.setdefault(field, "")

        for field in all_fields:
            row.setdefault(field, "")

        with open(
            output_file,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=all_fields
            )

            writer.writeheader()
            writer.writerows(existing_rows)
            writer.writerow(row)

    else:

        with open(
            output_file,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=list(row.keys())
            )

            writer.writeheader()
            writer.writerow(row)

    return output_file


def process_completed_experiment(
    experiment_name,
    experiment_group,
    parameter_name,
    parameter_value,
    condition,
    before_dumps,
):
    dump_dir = find_new_dump(
        experiment_name,
        before_dumps
    )

    metrics = extract_metrics(dump_dir)

    organized_dir = organize_dump(
        dump_dir=dump_dir,
        experiment_group=experiment_group,
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        condition=condition,
    )

    processed_file = save_processed_result(
        experiment_group=experiment_group,
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        condition=condition,
        run_directory=organized_dir,
        metrics=metrics,
    )

    return (
        organized_dir,
        processed_file,
        metrics,
    )