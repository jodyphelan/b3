import csv
from pathlib import Path
from typing import Annotated
from ..models import MlstResult, AmrfinderResult, AmrfinderHit
from ..utils import get_software_version, run_cmd, run_in_docker, parse_software_version


from ..jobs import app

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/mlst:2.35.0--hdfd78af_0"


def parse_mlst_output(output_file: Path, software_version: str) -> MlstResult:
    """Parse the MLST output file and return an MlstResult object."""
    with open(output_file, "r") as f:
        data = f.readline().strip().split("\t")

    
    result = MlstResult(
        software_version=software_version, 
        scheme=data[1],
        st=data[2],
        alleles=data[3:],
    )
    return result


@app.command(
    "mlst", 
    help="Run MLST on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_mlst(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_file: Annotated[Path, "Output file for MLST results"],
    threads: Annotated[int, "Number of threads to use"] = 1,
    docker: Annotated[bool, "Whether to run MLST inside a Docker container"] = False,
) -> MlstResult:
    """Run an MLST job on the input FASTA file and save results to the output directory."""
    cmd = [
        "mlst",
        Path(input_fasta),
        "--threads",
        str(threads),
        "-o",
        Path(output_file),
    ]
    version_cmd = ["mlst", "--version"]
    version_regex = r"mlst (.+)"
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            version_regex,
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version(version_cmd, version_regex)
    return parse_mlst_output(output_file, software_version)

