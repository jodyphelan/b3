import logging
import os

import typer
from pathlib import Path
from typing import Annotated

from .tools.amrfinder import job_amrfinder
from .tools.mlst import job_mlst
from .tools.rmlst import job_rmlst
from .tools.quast import job_quast
from .tools.plasmidfinder import job_plasmidfinder

from .bridge import combine_results

import tempfile

app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to workflows",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.command()
def bifrost_ONT(
    input_fasta: Annotated[Path, typer.Argument(help="Input FASTA file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = 1
):
    """Bifrost ONT workflow."""
    
    if output_dir.exists() is False:
        output_dir.mkdir(parents=True, exist_ok=True)

    files_to_save = {
        'mlst_result': "mlst_results.txt",
    }

    input_fasta = input_fasta.absolute()
    output_dir = output_dir.absolute()

    current_dir = Path.cwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        logging.debug(f"Temporary directory created at {temp_dir_path}")
        os.chdir(temp_dir_path)

        sym_input_fasta = temp_dir_path / input_fasta.name
        sym_input_fasta.hardlink_to(input_fasta)
        input_fasta = sym_input_fasta

        mlst_output_file = Path("mlst_results.txt")
        mlst_results = job_mlst(input_fasta=input_fasta, output_file=mlst_output_file, threads=threads)
        amrfinder_output_file = Path("amrfinder_results.txt")
        amrfinder_results = job_amrfinder(input_fasta=input_fasta, output_file=amrfinder_output_file, threads=threads)
        rmlst_output_file = Path("rmlst_results.txt")
        rmlst_results = job_rmlst(input_fasta=input_fasta, output_file=rmlst_output_file)
        quast_output_dir = Path("quast_results")
        quast_results = job_quast(input_fasta=input_fasta,output_dir=quast_output_dir,threads=threads)
        plasmidfinder_output_file = Path("plasmidfinder_results.json")
        plasmidfinder_results = job_plasmidfinder(input_fasta=input_fasta, output_file=plasmidfinder_output_file, threads=threads)

        for file_name in files_to_save.values():
            if Path(file_name).exists():
                Path(file_name).rename(output_dir / file_name)
        os.chdir(current_dir)


    combined_output_file = output_dir / "combined_results.txt"
    combine_results(
        output_file=combined_output_file,
        mlst_result=mlst_results,
        amrfinder_result=amrfinder_results,
        rmlst_result=rmlst_results,
        quast_result=quast_results,
        plasmidfinder_result=plasmidfinder_results
    )