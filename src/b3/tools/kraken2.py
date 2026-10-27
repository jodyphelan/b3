import logging
from pathlib import Path
import re
from typing import Annotated, Optional
from b3.jobs import app
from b3.utils import get_absolute_path, run_cmd, get_software_version, run_in_docker, parse_software_version
from b3.models import Kraken2Result
import json
import typer
from pathlib import Path

DOCKER_IMAGE = "quay.io/biocontainers/kraken2:2.17.2--pl5321h3be2455_0"
VERSION_REGEX = r"Kraken version (.+)"

def parse_kraken2_json(software_version: str, database_version: str) -> Kraken2Result:
    return Kraken2Result(
        software_version=software_version,
        database_version=database_version
    )

@app.command(
    "kraken2",
    help="Run kraken2 on the input FASTQ file and save results to the output JSON file.",
    no_args_is_help=True
)
def job_kraken2(
    input_read1: Annotated[Path, typer.Option(help="Input FASTQ file for forward reads", exists=True, callback=get_absolute_path)],
    output_file: Annotated[Path, typer.Option(help="Output JSON file", callback=get_absolute_path)],
    report_file: Annotated[Path, typer.Option(help="Output report file", callback=get_absolute_path)],
    database: Annotated[Path, typer.Option(help="Kraken2 database path", exists=True, callback=get_absolute_path)],
    input_read2: Annotated[Optional[Path], typer.Option(help="Input FASTQ file for reverse reads", exists=True, callback=get_absolute_path)] = None,
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = 1,
    docker: Annotated[bool, typer.Option(help="Run the command in Docker")] = False,
):
    cmd = [
        "kraken2", 
        "--db", database,
        "--report", report_file, 
        "--output", output_file, 
        "--threads", str(threads),
        "--confidence", "0.0",
        "--minimum-base-quality", "0",
        "--minimum-hit-groups", "2",
        input_read1
    ]
    if input_read2 is not None:
        cmd.append(input_read2)
        cmd.append("--paired")
    version_cmd = ["kraken2", "--version"]
    if docker:
        run_in_docker(cmd, DOCKER_IMAGE)
        software_version = parse_software_version(run_in_docker(version_cmd, DOCKER_IMAGE).stdout, VERSION_REGEX)
    else:
        run_cmd(cmd)
        software_version = parse_software_version(run_cmd(version_cmd).stdout, VERSION_REGEX)



    db_version = database.name
    return parse_kraken2_json(software_version=software_version, database_version=db_version)
