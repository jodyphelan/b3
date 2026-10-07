from pathlib import Path
from b3.constants import PLASMIDFINDER_DB
from pathlib import Path
from typing import Annotated
from b3.models import PlasmidfinderResult, PlasmidfinderHit
from b3.utils import get_software_version, run_cmd
from b3.jobs import app
import json

def parse_plasmidfinder_results(output_file: Path, software_version: str, db_version: str) -> PlasmidfinderResult:
    hits = []
    with open(output_file, "r") as f:
        data = json.load(f)
        for hit_data in data['seq_regions'].values():
            hits.append(PlasmidfinderHit(**hit_data))
    return PlasmidfinderResult(
        software_version=software_version, 
        database_version=db_version,
        hits=hits,
    )

def get_plasmidfinder_db_version() -> str:
    version_file = Path(PLASMIDFINDER_DB) / "VERSION"
    with open(version_file, "r") as f:
        return f.read().strip()

@app.command(
    "plasmidfinder", 
    help="Run PlasmidFinder on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_plasmidfinder(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_file: Annotated[Path, "Output file for PlasmidFinder results"],
    threads: Annotated[int, "Number of threads to use"] = 1
) -> PlasmidfinderResult:
    """Run a PlasmidFinder job on the input FASTA file and save results to the output directory."""

    cmd = f"python -m plasmidfinder -i {input_fasta} -j {output_file} -p {PLASMIDFINDER_DB}"
    run_cmd(cmd)
    software_version = get_software_version("python -m plasmidfinder --version", "(.+)")
    db_version = get_plasmidfinder_db_version()
    return parse_plasmidfinder_results(output_file, software_version, db_version)


