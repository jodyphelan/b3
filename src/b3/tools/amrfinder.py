from pathlib import Path
import csv
from b3.utils import get_software_version, run_cmd
from b3.models import AmrfinderResult, AmrfinderHit
from typing import Annotated
from b3.jobs import app

def parse_amrfinder_output(output_file: Path, software_version: str, db_version: str) -> AmrfinderResult:
    """Parse the AMRFinder output file and return an AmrfinderResult object."""
    hits = []
    
    with open(output_file, "r") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            hit = AmrfinderHit(
                protein_id=row["Protein id"],
                contig_id=row["Contig id"],
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
                coverage_of_reference=float(row["% Coverage of reference"]),
                identity_to_reference=float(row["% Identity to reference"]),
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
    threads: Annotated[int, "Number of threads to use"] = 1
) -> AmrfinderResult:
    """Run an AMRFinder job on the input FASTA file and save results to the output directory."""
    cmd = f"amrfinder --threads {threads} --nucleotide {input_fasta} > {output_file}"
    run_cmd(cmd)
    software_version = get_software_version("amrfinder --version", "(.+)")
    db_version = get_software_version("amrfinder --database_version","Database version: (.+)")

    return parse_amrfinder_output(output_file, software_version, db_version)