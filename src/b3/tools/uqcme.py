
import csv
from pathlib import Path
from b3.jobs import app
from b3.utils import get_software_version, parse_software_version, run_cmd, run_in_docker
from b3.models import UqcmeResult

DOCKER_CONTAINER_IMAGE="quay.io/biocontainers/uqcme-cli:0.9.4--pyhdfd78af_0"

@app.command(
    help="Path to the input TSV file containing key-value pairs."
)
def create_uqcme_input(
    input_tsv: Path,
    species: str,
    output_tsv: Path,
):
    lookup = {}
    for row in csv.DictReader(input_tsv.open(), delimiter='\t'):
        lookup[row['key']] = row['value']

    row = {
        'sample_name': "sample1",
        'species': species,
        'N50': lookup['quast:N50'],
        'bin_contigs_at_1x': lookup['quast:num_contigs'],
        'bin_length_at_1x': lookup['quast:total_length'],
        'percent_classified_species_1_whats_my_species': lookup['bracken:species1_pct'], # what happens if the contaminant is more abundant than the target species?
        'percent_classified_species_2_whats_my_species': lookup['bracken:species2_pct'],
        'GC': lookup['quast:gc_content'],
        'n_per_100_kbp': lookup['quast:n_per_100_kbp']
    }

    with output_tsv.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys(), delimiter='\t')
        writer.writeheader()
        writer.writerow(row)

def parse_uqcme_output(input_file: Path, software_version: str) -> UqcmeResult:
    reader = csv.DictReader(input_file.open(), delimiter='\t')
    row = next(reader)
    return UqcmeResult(
        software_version=software_version,
        qc_outcome = row['qc_outcome'],
        qc_action = row['qc_action'],
        failed_rules = row.get('failed_rules'),
        passed_rules = row.get('passed_rules'),
        skipped_rules = row.get('skipped_rules'),
        missing_qc_fields = row.get('missing_qc_fields')
    )


@app.command(
    "uqcme",
    help="Run UQCME on the input TSV file",
    no_args_is_help=True
)
def job_uqcme(
    input_tsv: Path,
    docker: bool = False
):
    cmd = [
        "uqcme",
        "--file",
        input_tsv
    ]
    version_cmd = ["uqcme", "--version"]
    if docker:
        print("Running UQCME in Docker container...")
        cwd = Path.cwd()
        print(f"Current working directory: {cwd}")
        run_in_docker(cmd, DOCKER_CONTAINER_IMAGE, extra_docker_args=["-w", "/mnt/volume0"])
        software_version = parse_software_version(
            run_in_docker(version_cmd, DOCKER_CONTAINER_IMAGE).stdout,
            r"uQCme (.+) ",
        )
    else:
        run_cmd(cmd)
        software_version = get_software_version("uQCme --version", r"uqcme (.+) ")

    return parse_uqcme_output(Path("qc_results.tsv"), software_version)


    