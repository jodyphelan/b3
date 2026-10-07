import logging
import os

from b3.tools.fasta_stats import job_fasta_stats
import typer
from pathlib import Path
from typing import Annotated

from .tools.amrfinder import job_amrfinder
from .tools.mlst import job_mlst
from .tools.rmlst import job_rmlst
from .tools.quast import job_quast
from .tools.plasmidfinder import job_plasmidfinder

from .bridge import combine_results
from .utils import temporary_directory, get_absolute_path

app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to workflows",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.command()
def bifrost_ONT(
    input_fasta: Annotated[Path, typer.Argument(help="Input FASTA file",callback=get_absolute_path)],
    output_dir: Annotated[Path, typer.Argument(help="Output directory",callback=get_absolute_path)],
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = 1
):
    """Bifrost ONT workflow."""
    
    if output_dir.exists() is False:
        output_dir.mkdir(parents=True, exist_ok=True)

    files_to_save = {
        'combined_result': "combined_results.tsv",
    }

    with temporary_directory():
        fasta_stats_output_file = Path("fasta_stats_results.json")
        fasta_stats_results = job_fasta_stats(input_fasta=input_fasta, output_file=fasta_stats_output_file)
        mlst_output_file = Path("mlst_results.txt")
        mlst_results = job_mlst(input_fasta=input_fasta, output_file=mlst_output_file, threads=threads)
        amrfinder_output_file = Path("amrfinder_results.txt")
        amrfinder_results = job_amrfinder(input_fasta=input_fasta, output_file=amrfinder_output_file, threads=threads)
        rmlst_output_file = Path("rmlst_results.txt")
        rmlst_results = job_rmlst(input_fasta=input_fasta, output_file=rmlst_output_file)
        plasmidfinder_output_file = Path("plasmidfinder_results.json")
        plasmidfinder_results = job_plasmidfinder(input_fasta=input_fasta, output_file=plasmidfinder_output_file, threads=threads)

        combined_output_file = output_dir / "combined_results.tsv"
        combine_results(
            output_file=combined_output_file,
            mlst_result=mlst_results,
            amrfinder_result=amrfinder_results,
            rmlst_result=rmlst_results,
            fasta_stats_result=fasta_stats_results,
            plasmidfinder_result=plasmidfinder_results
        )

        for file_name in files_to_save.values():
            if Path(file_name).exists():
                Path(file_name).rename(output_dir / file_name)


