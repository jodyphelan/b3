
from pathlib import Path
import json

from b3.models import RmlstResult
from typing import Annotated
from b3.utils import run_cmd

from ..jobs import app

def parse_rmlst_output(output_file: Path) -> RmlstResult:
    data = json.load(open(output_file))
    result = RmlstResult(taxon=data['taxon_prediction'][0]['taxon'], support=data['taxon_prediction'][0]['support'])
    return result

@app.command(
    "rmlst", 
    help="Run rMLST on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_rmlst(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_file: Annotated[Path, "Output file for rMLST results"],
) -> RmlstResult:
    """Run an rMLST job on the input FASTA file and save results to the output directory."""
    cmd = f"rmlst-cli --fasta {input_fasta} --output {output_file}"
    run_cmd(cmd)
    return parse_rmlst_output(output_file)