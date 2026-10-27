import logging
from pathlib import Path
import re
from typing import Annotated
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, parse_software_version, run_in_docker
from b3.models import FastpResult
import json
from pathlib import Path



DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/fastp:1.4.0--h43da1c4_0"
VERSION_REGEX = r"fastp (.+)"


def parse_fastp_json(json_file: str, software_version: str) -> FastpResult:
    with open(json_file, "r") as f:
        data = json.load(f)
    return FastpResult(
        software_version=software_version,
        adapter_trimmed_bases=int(data['adapter_cutting']['adapter_trimmed_bases']),
        adapter_trimmed_reads=int(data['adapter_cutting']['adapter_trimmed_reads']),
        before_filtering_read1_mean_length=int(data['summary']['before_filtering']['read1_mean_length']),
        before_filtering_read2_mean_length=int(data['summary']['before_filtering']['read2_mean_length']),
        before_filtering_total_reads=int(data['summary']['before_filtering']['total_reads']),
        after_filtering_read1_mean_length=int(data['summary']['after_filtering']['read1_mean_length']),
        after_filtering_read2_mean_length=int(data['summary']['after_filtering']['read2_mean_length']),
        after_filtering_total_reads=int(data['summary']['after_filtering']['total_reads']),
        duplication_rate=float(data['duplication']['rate']),
        low_quality_reads=int(data['filtering_result']['low_quality_reads']),
        num_cycles=int(re.search(r'(\d+) cycles', data['summary']['sequencing']).group(1)),
        too_long_reads=int(data['filtering_result']['too_long_reads']),
        too_many_n_reads=int(data['filtering_result']['too_many_N_reads']),
        too_short_reads=int(data['filtering_result']['too_short_reads']),

    )



@app.command(
    "fastp",
    help="Run fastp on the input FASTQ file and save results to the output JSON file.",
    no_args_is_help=True
)
def job_fastp(
    input_read1: Annotated[Path, "Input FASTQ file for forward reads"], 
    input_read2: Annotated[Path, "Input FASTQ file for reverse reads"], 
    output_read1: Annotated[Path, "Output FASTQ file for forward reads"],
    output_read2: Annotated[Path, "Output FASTQ file for reverse reads"], 
    json_output: Annotated[Path, "Output JSON file for fastp results"],
    threads: Annotated[int, "Number of threads to use for fastp"] = 1, 
    docker: Annotated[bool, "Whether to run fastp inside a Docker container"] = False,
) -> dict:
    logging.info(f"Running fastp on {input_read1} and {input_read2}")
    cmd = [
        "fastp",
        "--thread", threads,
        "-i", input_read1,
        "-I", input_read2,
        "-o", output_read1,
        "-O", output_read2,
        "--detect_adapter_for_pe",
        "-c",
        "--json", json_output,
    ]
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(["fastp", "--version"], DOCKER_CONTAINER_IMAGE).stdout, 
            VERSION_REGEX
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version("fastp --version", VERSION_REGEX)

    return parse_fastp_json(str(json_output), software_version=software_version)

