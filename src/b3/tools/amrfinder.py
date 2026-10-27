from pathlib import Path
import csv
import sys
from b3.utils import get_software_version, run_cmd, run_in_docker, parse_software_version
from b3.models import AmrfinderResult, AmrfinderHit
from typing import Annotated
from b3.jobs import app

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/ncbi-amrfinderplus:4.2.7--hf69ffd2_0"

def parse_amrfinder_output(output_file: Path, software_version: str, db_version: str) -> AmrfinderResult:
    """Parse the AMRFinder output file and return an AmrfinderResult object."""
    hits = []
    
    with open(output_file, "r") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            hit = AmrfinderHit(
                protein_id=row["Protein id"],
                contig=row["Contig id"],
                start=int(row["Start"]),
                stop=int(row["Stop"]),
                strand=row["Strand"],
                element_symbol=row["Element symbol"],
                element_name=row["Element name"],
                scope=row["Scope"],
                type=row["Type"],
                subtype=row["Subtype"],
                class_=row["Class"],
                subclass=row["Subclass"],
                method=row["Method"],
                target_length=int(row["Target length"]),
                reference_sequence_length=int(row["Reference sequence length"]),
                coverage=float(row["% Coverage of reference"]),
                identity=float(row["% Identity to reference"]),
                alignment_length=int(row["Alignment length"]),
                closest_reference_accession=row["Closest reference accession"],
                closest_reference_name=row["Closest reference name"],
                hmm_accession=row["HMM accession"],
                hmm_description=row["HMM description"]
            )
            hits.append(hit)

    return AmrfinderResult(
        software_version=software_version, 
        database_version=db_version,
        hits=hits
    )

@app.command(
    "amrfinder", 
    help="Run AMRFinder on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_amrfinder(
    input_fasta: Annotated[Path, "Input FASTA file"], 
    output_file: Annotated[Path, "Output file for AMRFinder results"], 
    threads: Annotated[int, "Number of threads to use"] = 1,
    db_path: Annotated[Path, "Path to the AMRFinder database"] = Path(sys.base_prefix + "/share/amrfinderplus/data/latest"),
    docker: Annotated[bool, "Whether to run AMRFinder inside a Docker container"] = False,
) -> AmrfinderResult:
    """Run an AMRFinder job on the input FASTA file and save results to the output directory."""

    
    cmd = [
        "amrfinder",
        "--threads", str(threads),
        "--nucleotide", input_fasta,
        "-o", output_file,
        "--database", db_path,
    ]
    tool_version_cmd = ["amrfinder", "--version"]
    tool_version_regex = r"(.+)"
    db_version_cmd = ["amrfinder", "--database_version", "--database", db_path]
    db_version_regex = r"Database version: (.+)"

    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = parse_software_version(
            run_in_docker(tool_version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            tool_version_regex
        )
        db_version = parse_software_version(
            run_in_docker(db_version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            db_version_regex
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version(tool_version_cmd, tool_version_regex)
        db_version = get_software_version(db_version_cmd, db_version_regex)

    return parse_amrfinder_output(output_file, software_version, db_version)