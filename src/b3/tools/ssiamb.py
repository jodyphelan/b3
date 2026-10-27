
from pathlib import Path

from b3.models import SsiambResult
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, run_in_docker, parse_software_version
import csv

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/ssiamb:1.0.0--pyhdfd78af_0"


def parse_ssiamb_output(report_file: str, software_version: str) -> SsiambResult:

    for row in csv.DictReader(open(report_file), delimiter='\t'):
        print(row)
        count = int(row['ambiguous_sites'])
    return SsiambResult(software_version=software_version, count=count)

@app.command(
    "ssiamb",
    help="Run ssiamb on the specified output directory.",
    no_args_is_help=True
)
def job_ssiamb(
    input_read1: Path,
    input_read2: Path,
    assembly: Path,
    output_dir: Path,
    threads: int = 1,
    docker: bool = False,
) -> SsiambResult:
    # ssiamb self --r1 '/users/data/Services/galaxy/data/2/4/b/dataset_24b57cec-8ed0-4e0d-ac67-2047dfc5be83.dat' --r2 '/users/data/Services/galaxy/data/7/1/7/dataset_717fa70d-5df4-4a60-92d5-ae113112d917.dat' --assembly '/users/data/Services/galaxy/data/b/2/1/dataset_b212c97a-d08e-41c4-89c4-d1fa8b02c126.dat' --sample 'sample1' --outdir outputs --threads "${GALAXY_SLOTS:-1}" --dp-min '10' --maf-min '0.1'
    cmd = [
        "ssiamb",
        "self",
        "--r1",
        input_read1,
        "--r2",
        input_read2,
        "--assembly",
        assembly,
        "--sample",
        "sample1",
        "--outdir",
        output_dir,
        "--threads",
        str(threads),
        "--dp-min",
        "10",
        "--maf-min",
        "0.1",
    ]
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(["ssiamb", "--version"], DOCKER_CONTAINER_IMAGE).stdout,
            r"ssiamb (.+)",
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version("ssiamb --version", "ssiamb (.+)")
    return parse_ssiamb_output(report_file=f"{output_dir}/sample1.summary.tsv", software_version=software_version)