from pathlib import Path
from b3.constants import PLASMIDFINDER_DB
from typing import Annotated
from b3.models import PlasmidfinderResult, PlasmidfinderHit
from b3.utils import run_cmd
from b3.jobs import app
import json

def parse_plasmidfinder_results(output_file: Path) -> PlasmidfinderResult:
    hits = []
    with open(output_file, "r") as f:
        data = json.load(f)
        for hit_data in data['seq_regions'].values():
            hits.append(PlasmidfinderHit(**hit_data))
    return PlasmidfinderResult(hits=hits)

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
    #python -m plasmidfinder -i contigs.fasta -j pf.json -p ./plasmidfinder_db

    cmd = f"python -m plasmidfinder -i {input_fasta} -j {output_file} -p {PLASMIDFINDER_DB}"
    run_cmd(cmd)
    return parse_plasmidfinder_results(output_file)


