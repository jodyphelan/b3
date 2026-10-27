import logging
from pathlib import Path
import re
from typing import Annotated
import typer
from b3.jobs import app
from b3.utils import run_cmd, get_software_version, parse_software_version, run_in_docker, get_absolute_path
from b3.models import BrackenResult, BrackenHit
import json
import csv
from pathlib import Path


DOCKER_IMAGE = "quay.io/biocontainers/bracken:3.1p1--hc52dbad_0"
VERSION = r"3.1"

def parse_bracken_report(report_path: Path, software_version: str, database_version: str) -> BrackenResult:
    with open(report_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        hits = []
        for row in reader:
            hits.append(BrackenHit(
                name=row["name"],
                taxonomy_id=int(row["taxonomy_id"]),
                taxonomy_lvl=row["taxonomy_lvl"],
                kraken_assigned_seqs=int(row["kraken_assigned_seqs"]),
                bracken_assigned_seqs=int(row["bracken_assigned_seqs"]),
                total_seqs=int(row["total_seqs"]),
                kraken_fraction_total_seqs=round(float(row["kraken_fraction_total_seqs"])*100,2),
                bracken_fraction_total_seqs=round(float(row["bracken_fraction_total_seqs"])*100,2)
            ))

    return BrackenResult(
        software_version=software_version,
        database_version=database_version,
        hits=hits
    )

@app.command(
    "bracken",
    help="Run bracken on the input FASTQ file and save results to the output JSON file.",
    no_args_is_help=True
)
def job_bracken(
    report: Annotated[Path, typer.Option(help="Input report file", exists=True, callback=get_absolute_path)],
    database: Annotated[Path, typer.Option(help="Kraken2 database path", exists=True, callback=get_absolute_path)],
    output: Annotated[Path, typer.Option(help="Output JSON file", callback=get_absolute_path)],
    docker: Annotated[bool, typer.Option(help="Run in Docker", is_flag=True)] = False

):
    # est_abundance.py -i '/users/data/Services/galaxy/data/7/c/3/dataset_7c31859a-7b72-4971-b96e-6758e5dfdc31.dat' -k '/users/data/Services/galaxy/server/tool-data/kraken2_databases/2024-10-09T124501Z_minikraken2_v2_8GB/database150mers.kmer_distrib' -l S -t 10 -o '/users/data/Services/galaxy/data/4/5/2/dataset_45242ff3-d5ba-45b9-91f3-08288f368031.dat'  --out-report bracken.report
    bracken_abundance = Path("bracken_abundance.txt")
    cmd = [
        "est_abundance.py",
        "-i", report,
        "-k", database / "database150mers.kmer_distrib",
        "-l", "S",
        "-t", "10",
        "-o", bracken_abundance
    ]

    if docker:
        run_in_docker(cmd, DOCKER_IMAGE)
    else:
        run_cmd(cmd)

    database_version = database.name

    adjust_bracken_abundance(report, bracken_abundance, output)
    return parse_bracken_report(output, VERSION, database_version)









from pathlib import Path
import csv
import json

def parse_bracken_abundances(bracken_abundances_path):
    bracken_abundances = []
    with open(bracken_abundances_path, 'r') as f:
        reader = csv.DictReader(f, dialect='excel-tab')
        for row in reader:
            b = {}
            b['name'] = row['name']
            b['taxonomy_id'] = row['taxonomy_id']
            b['taxonomy_lvl'] = row['taxonomy_lvl']
            b['kraken_assigned_seqs'] = int(row['kraken_assigned_reads'])
            b['bracken_assigned_seqs'] = int(row['new_est_reads'])
            b['bracken_fraction_total_seqs'] = float(row['fraction_total_reads'])
            bracken_abundances.append(b)

    return bracken_abundances


def parse_kraken_report(kraken_report_path):
    kraken_report = []
    with open(kraken_report_path, 'r') as f:
        for line in f:
            kraken_line = {}
            [percentage, seqs_total, seqs_this_level, taxonomic_level, ncbi_taxid, taxon_name] = line.strip().split(None, 5)
            kraken_line['percentage'] = float(percentage)
            kraken_line['seqs_total'] = int(seqs_total)
            kraken_line['seqs_this_level'] = int(seqs_this_level)
            kraken_line['taxonomic_level'] = taxonomic_level
            kraken_line['ncbi_taxid'] = ncbi_taxid
            kraken_line['taxon_name'] = taxon_name
            kraken_report.append(kraken_line)

    return kraken_report


def adjust_bracken_abundance(kraken_report: Path, bracken_abundances: Path, outfile: Path):
    kraken_report = parse_kraken_report(kraken_report)
    bracken_abundances = parse_bracken_abundances(bracken_abundances)

    try:
        kraken_report_unclassified_seqs = list(filter(lambda x: x['taxon_name'] == 'unclassified', kraken_report))[0]['seqs_this_level']
    except IndexError as e:
        kraken_report_unclassified_seqs = 0
    kraken_report_classified_seqs = list(filter(lambda x: x['taxon_name'] == 'root', kraken_report))[0]['seqs_total']

    total_seqs = kraken_report_classified_seqs + kraken_report_unclassified_seqs
    fraction_unclassified = float(kraken_report_unclassified_seqs) / float(total_seqs)

    output_fieldnames = [
        'name',
        'taxonomy_id',
        'taxonomy_lvl',
        'kraken_assigned_seqs',
        'bracken_assigned_seqs',
        'total_seqs',
        'kraken_fraction_total_seqs',
        'bracken_fraction_total_seqs',
    ]

    with open(outfile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames, dialect='excel-tab')
        writer.writeheader()
    
        for b in bracken_abundances:
            b['total_seqs'] = total_seqs
            kraken_adjusted_fraction_total_seqs = float(b['kraken_assigned_seqs']) / float(total_seqs)
            b['kraken_fraction_total_seqs'] = '{:.6f}'.format(kraken_adjusted_fraction_total_seqs)
            bracken_adjusted_fraction_total_seqs = float(b['bracken_assigned_seqs']) / float(total_seqs)
            b['bracken_fraction_total_seqs'] = '{:.6f}'.format(bracken_adjusted_fraction_total_seqs)

        bracken_unclassified_entry = {
            'name': 'unclassified',
            'taxonomy_id': 0,
            'taxonomy_lvl': 'U',
            'kraken_assigned_seqs': kraken_report_unclassified_seqs,
            'bracken_assigned_seqs': kraken_report_unclassified_seqs,
            'total_seqs': total_seqs,
            'kraken_fraction_total_seqs': '{:.6f}'.format(fraction_unclassified),
            'bracken_fraction_total_seqs': '{:.6f}'.format(fraction_unclassified),
        }
        
        bracken_abundances = sorted(bracken_abundances, key=lambda x: x['bracken_fraction_total_seqs'], reverse=True)
        bracken_abundances = [bracken_unclassified_entry] + bracken_abundances
        for b in bracken_abundances:
            writer.writerow(b)



