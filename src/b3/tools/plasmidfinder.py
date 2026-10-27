import csv
from pathlib import Path
from pathlib import Path
from typing import Annotated
from b3.models import PlasmidfinderResult, PlasmidfinderHit
from b3.utils import get_software_version, run_cmd, run_in_docker, parse_software_version
from b3.jobs import app
import json

DOCKER_CONTAINER_IMAGE = "quay.io/biocontainers/plasmidfinder:2.1.6--py314hdfd78af_2"
DOCKER_CONTAINER_VERSION = "2.1.6"

def get_coverage(data: str) -> float:
    numerator, denominator = data.split("/")
    return round(float(numerator) / float(denominator)*100, 2)

def parse_plasmidfinder_results(output_file: Path, software_version: str, db_version: str) -> PlasmidfinderResult:
    hits = []
    for row in csv.DictReader(open(output_file),delimiter="\t"):
        print(row)
        hits.append(PlasmidfinderHit(
            name=row['Plasmid'],
            contig=row['Contig'].split()[0],
            identity=float(row['Identity']),
            coverage=get_coverage(row['Query / Template length'])
        ))
    return PlasmidfinderResult(
        software_version=software_version, 
        database_version=db_version,
        hits=hits,
    )

def get_plasmidfinder_db_version(db: Path) -> str:
    version_file = db / "VERSION"
    with open(version_file, "r") as f:
        return f.read().strip()

@app.command(
    "plasmidfinder", 
    help="Run PlasmidFinder on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_plasmidfinder(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_dir: Annotated[Path, "Output directory for PlasmidFinder results"],
    db: Annotated[Path, "Path to the PlasmidFinder database"],
    threads: Annotated[int, "Number of threads to use"] = 1,
    docker: Annotated[bool, "Whether to run PlasmidFinder inside a Docker container"] = False,
) -> PlasmidfinderResult:
    """Run a PlasmidFinder job on the input FASTA file and save results to the output directory."""
    # plasmidfinder.py -i '/users/data/Services/galaxy/data/9/4/b/dataset_94bbf2c7-61c8-46bd-a5b7-b7a08b1e62f8.dat' -p '/users/data/Services/galaxy/server/tool-data/plasmidfinder-db/3e77502_2024_03_07' -l '0.6' -t '0.9' -mp blastn -x -o output_dir -tmp temp_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "plasmidfinder.py",
        "-i", input_fasta,
        "-p", db,
        "-l", "0.6",
        "-t", "0.9",
        "-mp", "blastn",
        "-x",
        "-o", output_dir,
        
    ]
    version_cmd = ["plasmidfinder.py", "--version"]
    version_regex = r"(.+)"
    if docker:
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE)
        software_version = DOCKER_CONTAINER_VERSION
    else:
        run_cmd(cmd)
        software_version = get_software_version(version_cmd, version_regex)
    db_version = get_plasmidfinder_db_version(db)
    return parse_plasmidfinder_results(output_dir / "results_tab.tsv", software_version, db_version)


