import logging
from pathlib import Path
from typing import Annotated
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, run_in_docker, parse_software_version
from b3.models import ShovillResult
import json

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/shovill:1.4.2--hdfd78af_1"



@app.command(
    "shovill",
    help="Run shovill for genome assembly",
    no_args_is_help=True,
)
def job_shovill(
    input_read1: Annotated[Path, "Input FASTQ file for forward reads"], 
    input_read2: Annotated[Path, "Input FASTQ file for reverse reads"], 
    output_dir: Annotated[Path, "Output directory for assembled contigs"], 
    threads: Annotated[int, "Number of threads to use for shovill"] = 1,
    docker: Annotated[bool, "Whether to run shovill inside a Docker container"] = False,
) -> ShovillResult:
    logging.info(f"Running shovill on {input_read1} and {input_read2}")

    cmd = [
        "shovill",
        "--outdir",
        output_dir,
        "--cpus",
        str(threads),
        "--ram",
        "8",
        "--R1",
        input_read1,
        "--R2",
        input_read2,
        "--namefmt",
        "contig%05d",
        "--depth",
        "100",
        "--minlen",
        "0",
        "--mincov",
        "2",
        "--assembler",
        "spades",
        "--nocorr",
        "--force"
    ]
    version_cmd = ["shovill", "--version"]
    version_regex = r"shovill (.+)"
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            version_regex,
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version(version_cmd, version_regex)
    return ShovillResult(software_version=software_version)