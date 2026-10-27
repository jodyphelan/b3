import logging
import os

from b3.tools.bracken import job_bracken
from b3.tools.fasta_stats import job_fasta_stats
from b3.tools.kraken2 import job_kraken2
from b3.tools.pmlst import job_pmlst
from b3.tools.shovill import job_shovill
from b3.tools.ssiamb import job_ssiamb
import typer
from pathlib import Path
from typing import Annotated

from .tools.amrfinder import job_amrfinder
from .tools.mlst import job_mlst
from .tools.rmlst import job_rmlst
from .tools.quast import job_quast
from .tools.plasmidfinder import job_plasmidfinder
from .tools.fastp import job_fastp
from .tools.uqcme import create_uqcme_input, job_uqcme
from .constants import DB_DIR
from .bridge import combine_results
from .utils import debug_temporary_directory, temporary_directory, get_absolute_path

app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to workflows",
    context_settings={"help_option_names": ["-h", "--help"]}
)

def get_dbs(db_dir: Path):
    return {
        "pmlst": db_dir / "pmlst_db",
        "amrfinder": db_dir / "amrfinder_db" / "latest",
        "plasmidfinder": db_dir / "plasmidfinder_db",
        "kraken2": db_dir / "2024-10-09T124501Z_minikraken2_v2_8GB"
    }

@app.command()
def bifrost_ONT(
    input_fasta: Annotated[Path, typer.Argument(help="Input FASTA file",callback=get_absolute_path)],
    output_dir: Annotated[Path, typer.Argument(help="Output directory",callback=get_absolute_path)],
    species: Annotated[str, typer.Argument(help="Species name")],
    db_dir: Annotated[Path, typer.Argument(help="Path to the databases directory", exists=True, callback=get_absolute_path)] = Path(DB_DIR),
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = 1,
    docker: Annotated[bool, typer.Option(help="Run in Docker", is_flag=True)] = False,
):
    """Bifrost ONT workflow."""
    
    if output_dir.exists() is False:
        output_dir.mkdir(parents=True, exist_ok=True)

    

    dbs = get_dbs(db_dir)

    with temporary_directory():
        quast_output_dir = Path("quast")
        quast_results = job_quast(
            input_fasta=input_fasta, 
            output_dir=quast_output_dir,
            docker=docker
        )
        
        mlst_output_file = Path("mlst_results.txt")
        mlst_results = job_mlst(
            input_fasta=input_fasta,
            output_file=mlst_output_file,
            threads=threads, 
            docker=docker
        )
        
        amrfinder_output_file = Path("amrfinder_results.txt")
        amrfinder_results = job_amrfinder(
            input_fasta=input_fasta, 
            output_file=amrfinder_output_file, 
            threads=threads, 
            db_path=dbs["amrfinder"], 
            docker=docker
        )
        
        rmlst_output_file = Path("rmlst_results.txt")
        rmlst_results = job_rmlst(
            input_fasta=input_fasta, 
            output_file=rmlst_output_file,
            docker=docker
        )
        
        plasmidfinder_output_dir = Path("plasmidfinder_output")
        plasmidfinder_results = job_plasmidfinder(
            input_fasta=input_fasta, 
            output_dir=plasmidfinder_output_dir, 
            db=dbs["plasmidfinder"], 
            threads=threads, 
            docker=docker
        )

        pmlst_output_file = Path("pmlst_results.txt")
        pmlst_results = job_pmlst(
            input_fasta=input_fasta,
            output_file=pmlst_output_file,
            docker=docker
        )

        temp_combined_output_file = Path("temp_combined_results.tsv")
        combine_results(
            output_file=temp_combined_output_file,
            quast_result=quast_results,
            plasmidfinder_result=plasmidfinder_results,
            rmlst_result=rmlst_results,
            mlst_result=mlst_results,
            pmlst_result=pmlst_results,
            amrfinder_result=amrfinder_results,
        )

        uqcme_input_file = Path("uqcme_input.tsv")
        create_uqcme_input(
            input_tsv=temp_combined_output_file,
            species=species,
            output_tsv=uqcme_input_file
        )

        uqcme_results = job_uqcme(
            input_tsv=uqcme_input_file,
            docker=docker
        )

        final_output_file = Path("combined_results.tsv")
        combine_results(
            output_file=final_output_file,
            quast_result=quast_results,
            plasmidfinder_result=plasmidfinder_results,
            rmlst_result=rmlst_results,
            mlst_result=mlst_results,
            pmlst_result=pmlst_results,
            amrfinder_result=amrfinder_results,
            uqcme_result=uqcme_results
        )

        files_to_save = [
            "combined_results.tsv",
        ]

        for file_name in files_to_save.values():
            if Path(file_name).exists():
                Path(file_name).rename(output_dir / file_name.name)

@app.command()
def bifrost_illumina(
    input_read1: Annotated[Path, typer.Argument(help="Input FASTQ file for forward reads", exists=True, callback=get_absolute_path)],
    input_read2: Annotated[Path, typer.Argument(help="Input FASTQ file for reverse reads", exists=True, callback=get_absolute_path)],
    species: Annotated[str, typer.Argument(help="Species name")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory", callback=get_absolute_path)],
    db_dir: Annotated[Path, typer.Argument(help="Path to database directory", exists=True, callback=get_absolute_path)] = Path(DB_DIR),
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = 1,
    docker: Annotated[bool, typer.Option(help="Run in Docker", is_flag=True)] = False,
):
    """Bifrost Illumina workflow."""

    if output_dir.exists() is False:
        output_dir.mkdir(parents=True, exist_ok=True)

    

    dbs = get_dbs(db_dir)

    with debug_temporary_directory():
        fastp_output_read1 = Path("fastp_output_read1.fastq")
        fastp_output_read2 = Path("fastp_output_read2.fastq")
        fastp_output_json = Path("fastp_output.json")
        fastp_results = job_fastp(
            input_read1=input_read1,
            input_read2=input_read2,
            output_read1=fastp_output_read1,
            output_read2=fastp_output_read2,
            json_output=fastp_output_json,
            threads=threads,
            docker=docker
        )

        shovill_output_dir = Path("shovill_output")
        shovill_contigs = shovill_output_dir / "contigs.fa"
        shovill_results = job_shovill(
            input_read1=fastp_output_read1,
            input_read2=fastp_output_read2,
            output_dir=shovill_output_dir,
            threads=threads,
            docker=docker
        )

        quast_output_dir = Path("quast_output")
        quast_results = job_quast(
            input_fasta=shovill_contigs,
            output_dir=quast_output_dir,
            threads=threads,
            docker=docker
        )

        amrfinder_output_file = Path("amrfinder_output.txt")
        amrfinder_results = job_amrfinder(
            input_fasta=shovill_contigs,
            output_file=amrfinder_output_file,
            db_path=dbs["amrfinder"],
            threads=threads,
            docker=docker
        )


        kraken_report_file = Path("kraken_report.txt")
        kraken_results = job_kraken2(
            input_read1=fastp_output_read1,
            input_read2=fastp_output_read2,
            output_file=Path("kraken_output.txt"),
            report_file=kraken_report_file,
            database=dbs["kraken2"],
            threads=threads,
            docker=docker
        )

        bracken_report_file = Path("bracken_report.txt")
        bracken_results = job_bracken(
            report=kraken_report_file,
            database=dbs["kraken2"],
            output=bracken_report_file,
            docker=docker
        )

        plasmidfinder_output_dir = Path("plasmidfinder_output")
        plasmidfinder_results = job_plasmidfinder(
            input_fasta=shovill_contigs,
            output_dir=plasmidfinder_output_dir,
            db=dbs["plasmidfinder"],
            threads=threads,
            docker=docker
        )


        rmlst_output_file = Path("rmlst_output.txt")
        rmlst_results = job_rmlst(
            input_fasta=shovill_contigs,
            output_file=rmlst_output_file,
            docker=docker
        )

        mlst_output_file = Path("mlst_output.txt")
        mlst_results = job_mlst(
            input_fasta=shovill_contigs,
            output_file=mlst_output_file,
            threads=threads,
            docker=docker
        )


        pmlst_results = job_pmlst(
            input_fasta=shovill_contigs,
            pf_report=plasmidfinder_output_dir / "results_tab.tsv",
            database=dbs["pmlst"],
            output_dir=Path("."),
            docker=docker
        )

        

        amrfinder_output_file = Path("amrfinder_output.txt")
        amrfinder_results = job_amrfinder(
            input_fasta=shovill_contigs,
            output_file=amrfinder_output_file,
            threads=threads,
            docker=docker
        )

        ssiamb_output_dir = Path("ssiamb")
        ssiamb_results = job_ssiamb(
            input_read1=fastp_output_read1,
            input_read2=fastp_output_read2,
            assembly=shovill_contigs,
            output_dir=ssiamb_output_dir,
            threads=threads,
            docker=docker
        )

        temp_combined_output_file = Path("temp_combined_results.tsv")
        combine_results(
            output_file=temp_combined_output_file,
            quast_result=quast_results,
            fastp_result=fastp_results,
            bracken_result=bracken_results,
            plasmidfinder_result=plasmidfinder_results,
            rmlst_result=rmlst_results,
            mlst_result=mlst_results,
            pmlst_result=pmlst_results,
            amrfinder_result=amrfinder_results,
            ssiamb_result=ssiamb_results,
        )

        uqcme_input_file = Path("uqcme_input.tsv")
        create_uqcme_input(
            input_tsv=temp_combined_output_file,
            species=species,
            output_tsv=uqcme_input_file
        )

        uqcme_results = job_uqcme(
            input_tsv=uqcme_input_file,
            docker=docker
        )

        final_output_file = Path("combined_results.tsv")
        combine_results(
            output_file=final_output_file,
            quast_result=quast_results,
            fastp_result=fastp_results,
            bracken_result=bracken_results,
            plasmidfinder_result=plasmidfinder_results,
            rmlst_result=rmlst_results,
            mlst_result=mlst_results,
            pmlst_result=pmlst_results,
            amrfinder_result=amrfinder_results,
            ssiamb_result=ssiamb_results,
            uqcme_result=uqcme_results
        )

        files_to_save = [
                final_output_file,
                bracken_report_file,
                shovill_contigs
            ]

        for file_name in files_to_save:
            if Path(file_name).exists():
                Path(file_name).rename(output_dir / file_name.name)
