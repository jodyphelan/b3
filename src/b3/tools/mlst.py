import csv
from pathlib import Path
from typing import Annotated
from ..models import MlstResult, AmrfinderResult, AmrfinderHit
from ..utils import run_cmd


from ..jobs import app


def parse_mlst_output(output_file: Path) -> MlstResult:
    """Parse the MLST output file and return an MlstResult object."""
    with open(output_file, "r") as f:
        data = f.readline().strip().split("\t")

    
    result = MlstResult(
        scheme=data[0],
        st=data[1],
        alleles=data[2:]
    )
    return result


@app.command(
    "mlst", 
    help="Run MLST on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_mlst(
    input_fasta: Annotated[Path, "Input FASTA file"],
    output_file: Annotated[Path, "Output file for MLST results"],
    threads: Annotated[int, "Number of threads to use"] = 1
) -> MlstResult:
    """Run an MLST job on the input FASTA file and save results to the output directory."""
    cmd = f"mlst {input_fasta} --threads {threads} > {output_file}"
    run_cmd(cmd)
    return parse_mlst_output(output_file)

