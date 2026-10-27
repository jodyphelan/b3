
from pathlib import Path
import json

from b3.models import RmlstResult
from typing import Annotated
from b3.utils import run_cmd, get_software_version, run_in_docker, parse_software_version

from ..jobs import app

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/rmlst-cli:1.1--pyhdfd78af_0"

def parse_rmlst_output(output_file: Path, software_version: str) -> RmlstResult:
    data = json.load(open(output_file))
    result = RmlstResult(
        software_version=software_version,
        taxon=data['taxon_prediction'][0]['taxon'], 
        support=data['taxon_prediction'][0]['support']
    )
    return result

@app.command(
    "rmlst", 
    help="Run rMLST on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_rmlst(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_file: Annotated[Path, "Output file for rMLST results"],
    docker: Annotated[bool, "Whether to run rMLST inside a Docker container"] = False,
) -> RmlstResult:
    """Run an rMLST job on the input FASTA file and save results to the output directory."""
    cmd = [
        "rmlst-cli",
        "--fasta",
        input_fasta,
        "--output",
        output_file,
    ]
    version_cmd = ["rmlst-cli", "--version"]
    version_regex = r"rmlst (.+)"
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            version_regex,
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version(version_cmd, version_regex)
    return parse_rmlst_output(output_file, software_version)