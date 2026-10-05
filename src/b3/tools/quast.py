from pathlib import Path
from typing import Annotated
from b3.models import QuastResult
from b3.utils import run_cmd
from ..jobs import app
from platform import platform
import os

def parse_quast_results(output_dir: Path) -> QuastResult:
    """Parse QUAST results from the output directory and return a QuastResult object."""
    extract = {}
    normalised_keys = {
        "# contigs": {"name":"num_contigs","type": int},
        "GC (%)": {"name":"gc_content","type": float},
        "L50": {"name":"l50","type": int},
        "L90": {"name":"l90","type": int},
        "N50": {"name":"n50","type": int},
        "N90": {"name":"n90","type": int},
        "Total length": {"name":"total_length","type": int},
        "Largest contig": {"name":"largest_contig","type": int}
    }
    for line in open((output_dir / "report.tsv")):
        row = line.strip().split("\t")
        if row[0] in normalised_keys:
            key_info = normalised_keys[row[0]]
            extract[key_info["name"]] = key_info["type"](row[1])
    result = QuastResult(**extract)
    return result

@app.command(
    "quast", 
    help="Run QUAST on the input FASTA and FASTQ files and save results to the output directory.",
    no_args_is_help=True
)
def job_quast(
    input_fasta: Annotated[Path, "Input FASTA file"], 
    output_dir: Annotated[Path, "Output directory for QUAST results"], 
    threads: Annotated[int, "Number of threads to use"] = 1
) -> QuastResult:
    """Run a QUAST job on the input FASTA and FASTQ files and save results to the output directory."""
    if "arm64" in platform():
        #docker run --rm -v "$PWD:/data/" quay.io/biocontainers/quast:5.3.0--py313pl5321h5ca1c30_2  quast --nanopore /data/filtered_reads.fastq.gz  -o /data/ /data/contigs.fasta --threads 4
        cwd = os.getcwd()
        fasta_input_dir = input_fasta.parent
        cmd = f'docker run --rm -v "{fasta_input_dir}:/data/" -v "{cwd}:/output/" quay.io/biocontainers/quast:5.3.0--py313pl5321h5ca1c30_2 quast -o /output/{output_dir.name} /data/{input_fasta.name} --threads {threads}'
    else:
        cmd = f"quast -o {output_dir} {input_fasta} --threads {threads}"
    run_cmd(cmd)
    return parse_quast_results(output_dir)