from pathlib import Path
from typing import Annotated
from b3.models import QuastResult
from b3.utils import get_software_version, run_cmd, run_in_docker, parse_software_version
from ..jobs import app

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/quast:5.3.0--py313pl5321h5ca1c30_2"

def parse_quast_results(output_dir: Path, software_version: str) -> QuastResult:
    """Parse QUAST results from the output directory and return a QuastResult object."""
    extract = {}
    normalised_keys = {
        "# contigs": {"name":"num_contigs","type": int},
        "GC (%)": {"name":"gc_content","type": float},
        "L50": {"name":"L50","type": int},
        "L90": {"name":"L90","type": int},
        "N50": {"name":"N50","type": int},
        "N90": {"name":"N90","type": int},
        "Total length": {"name":"total_length","type": int},
        "Largest contig": {"name":"largest_contig","type": int},
        "# N's per 100 kbp": {"name":"n_per_100_kbp","type": float}
    }
    for line in open((output_dir / "report.tsv")):
        row = line.strip().split("\t")
        if row[0] in normalised_keys:
            key_info = normalised_keys[row[0]]
            extract[key_info["name"]] = key_info["type"](row[1])
    result = QuastResult(software_version=software_version, **extract)
    return result

@app.command(
    "quast", 
    help="Run QUAST on the input FASTA and FASTQ files and save results to the output directory.",
    no_args_is_help=True
)
def job_quast(
    input_fasta: Annotated[Path, "Input FASTA file"], 
    output_dir: Annotated[Path, "Output directory for QUAST results"], 
    threads: Annotated[int, "Number of threads to use"] = 1,
    docker: Annotated[bool, "Whether to run QUAST inside a Docker container"] = False,
) -> QuastResult:
    """Run a QUAST job on the input FASTA and FASTQ files and save results to the output directory."""
    cmd = [
        "quast",
        "-o",
        output_dir,
        input_fasta,
        "--threads",
        str(threads),
    ]
    version_cmd = ["quast", "--version"]
    version_regex = r"QUAST v(.+)"
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            version_regex,
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version(version_cmd, version_regex)
    return parse_quast_results(output_dir, software_version)