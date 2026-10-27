from typing import Annotated, Optional
from pathlib import Path
from b3.models import SylphResult
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, run_in_docker, parse_software_version
import tempfile
import shutil
import os.path

DOCKER_CONTAINER_IMAGE="quay.io/biocontainers/sylph:1.0.0--hb42e459_0"

def parse_sylph_output(software_version: str) -> SylphResult:
    pass

@app.command(
    "sylph",
    help = "Run sylph on the fastq files",
    no_args_is_help=True
)
def job_sylph(
    input_read1: Annotated[Path, "Input fastq file for forward reads"],
    input_read2: Annotated[Optional[Path], "Input fastq file for forward reads"],
    db: Annotated[Path, "Sylph database file(s)"],
    output_sketch: Annotated[Path, "Output sketch file"],
    output_tsv: Annotated[Path, "Output CSV with taxonomic information"],
    threads: Annotated[int, "Number of threads to use"] = 1,
    docker: Annotated[bool, "Whether to run shovill inside a Docker container"] = False,
):
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        cmd = [
            "sylph",
            "sketch",
            "-d", tempdir,
            "-t", threads

        ]

        if input_read1 and input_read2:
            cmd.extend([
                "-1", input_read1,
                "-2", input_read2
            ])
        else:
            cmd.extend([
                "-r", input_read1
            ])

        if docker:
            run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        else:
            run_cmd(cmd)

        temp_sketch_file = tempdir / os.listdir(str(tempdir))[0]
        # shutil.move(str(temp_sketch_file), output_sketch)
        temp_sketch_file.rename(output_sketch)

        cmd = [
            "sylph",
            "profile",
            db,
            output_sketch,
            "-o", output_tsv
        ]
        version_cmd = ["sylph", "--version"]
        if docker:
            run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
            software_version = run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE)
            software_version = parse_software_version(
                        run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
                        r"sylph (.+)",
                    )
        else:
            run_cmd(cmd)
            software_version = get_software_version("sylph --version", r"sylph (.+)")

        return parse_sylph_output(software_version)