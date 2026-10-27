import logging
from pathlib import Path
import re
from typing import Annotated
import typer
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, parse_software_version, run_in_docker, get_absolute_path
from b3.models import PmlstResult
import json
import csv
from pathlib import Path


DOCKER_IMAGE = "quay.io/biocontainers/pmlst_ssi:2.1.1--pyhdfd78af_0"
VERSION = r"3.1"

def get_db_version(database: Path) -> str:
    version_file = database / "version.txt"
    data = {}
    for l in open(version_file):
        data[l.split(": ")[0].strip()] = l.split(": ")[1].strip()
    data['commit'] = data['commit'][:7]
    version_string = "%(version)s_%(commit)s_%(source)s" % data
    return version_string

def parse_pmlst_report(report_path: Path, software_version: str, database_version: str) -> PmlstResult:
    for row in csv.DictReader(open(report_path),delimiter="\t"):
        pass

    return PmlstResult(
        software_version=software_version,
        database_version=database_version,
        IncF=int(row["IncF"]) if row["IncF"]!="" else None,
        IncI1=int(row["IncI1"]) if row["IncI1"]!="" else None,
        IncA_C=int(row["IncA/C"]) if row["IncA/C"]!="" else None,
        IncHI1=int(row["IncHI1"]) if row["IncHI1"]!="" else None,
        IncHI2=int(row["IncHI2"]) if row["IncHI2"]!="" else None,
        IncN=int(row["IncN"]) if row["IncN"]!="" else None,
        pmlst_summary=row.get("pMLST summary")
    )



@app.command(
    "pmlst",
    help="Run pmlst on the input FASTQ file and save results to the output JSON file.",
    no_args_is_help=True
)
def job_pmlst(
    input_fasta: Annotated[Path, typer.Option(help="Input FASTA file", exists=True, callback=get_absolute_path)],
    pf_report: Annotated[Path, typer.Option(help="Input plasmidfinder report file", exists=True, callback=get_absolute_path)],
    database: Annotated[Path, typer.Option(help="Kraken2 database path", exists=True, callback=get_absolute_path)],
    output_dir: Annotated[Path, typer.Option(help="Output directory for pmlst results", callback=get_absolute_path)],
    docker: Annotated[bool, typer.Option(help="Run in Docker", is_flag=True)] = False

):
    # pmlst -i '/users/data/Services/galaxy/data/9/4/b/dataset_94bbf2c7-61c8-46bd-a5b7-b7a08b1e62f8.dat' -mp blastn -o output_dir -t tmp_dir -pf '/users/data/Services/galaxy/data/a/6/d/dataset_a6df9383-5910-40f4-ad68-7cb6cdba1264.dat' -p '/users/data/Services/galaxy/server/tool-data/pmlst_db/2023-04-24' -c '0.6' -id '0.95' -so > 'XXXX'
    cmd = [
        "pmlst",
        "-i", input_fasta,
        "-mp", "blastn",
        "-o", output_dir,
        "-pf", pf_report,
        "-p", database,
        "-c", "0.6",
        "-id", "0.95",
        "-so"
    ]

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if docker:
        # save into a file
        run_in_docker(cmd, DOCKER_IMAGE)
    else:
        run_cmd(cmd)

    database_version = get_db_version(database)
    
    return parse_pmlst_report(output_dir / "simple_output.tsv", VERSION, database_version)