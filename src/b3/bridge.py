import json

from .models import (
    MlstResult,
    AmrfinderHit,
    AmrfinderResult,
    PlasmidfinderResult,
    RmlstResult,
    QuastResult,
    FastaqcResult,
)
from pathlib import Path
import csv
from typing import Optional


def combine_results(
    output_file: Path,
    mlst_result: Optional[MlstResult] = None,
    amrfinder_result: Optional[AmrfinderResult] = None,
    rmlst_result: Optional[RmlstResult] = None,
    fasta_stats_result: Optional[FastaqcResult] = None,
    plasmidfinder_result: Optional[PlasmidfinderResult] = None,
):
    rows = []

    # mlst
    if mlst_result is not None:
        rows.append({
            'key': 'mlst:software_version',
            'value': mlst_result.software_version
        })
        rows.append({
            'key': 'mlst:st',
            'value': mlst_result.st
        })
        rows.append({
            'key': 'mlst:scheme',
            'value': mlst_result.scheme
        })

    # amrfinder
    if amrfinder_result is not None:
        rows.append({
            'key': 'amrfinder:software_version',
            'value': amrfinder_result.software_version
        })
        rows.append({
            'key': 'amrfinder:database_version',
            'value': amrfinder_result.database_version
        })
        for hit in amrfinder_result.hits:
            rows.append({
                'key': f'amrfinder:hit:{hit.element_symbol}',
                'value': hit.contig_id
            })

    # rmlst
    if rmlst_result is not None:
        rows.append({
            'key': 'rmlst:software_version',
            'value': rmlst_result.software_version
        })
        rows.append({
            'key': 'rmlst:taxon',
            'value': rmlst_result.taxon
        })
        rows.append({
            'key': 'rmlst:support',
            'value': rmlst_result.support
        })

    # quast
    if fasta_stats_result is not None:
        rows.append({
            'key': 'fasta_stats:software_version',
            'value': fasta_stats_result.software_version
        })
        rows.append({
            'key': 'fasta_stats:num_contigs',
            'value': fasta_stats_result.num_contigs
        })
        rows.append({
            'key': 'fasta_stats:gc_content',
            'value': fasta_stats_result.gc_content
        })
        rows.append({
            'key': 'fasta_stats:L50',
            'value': fasta_stats_result.L50
        })
        rows.append({
            'key': 'fasta_stats:L90',
            'value': fasta_stats_result.L90
        })
        rows.append({
            'key': 'fasta_stats:N50',
            'value': fasta_stats_result.N50
        })
        rows.append({
            'key': 'fasta_stats:N90',
            'value': fasta_stats_result.N90
        })
        rows.append({
            'key': 'fasta_stats:total_length',
            'value': fasta_stats_result.total_length
        })
        rows.append({
            'key': 'fasta_stats:largest_contig',
            'value': fasta_stats_result.largest_contig
        })

    # plasmidfinder
    if plasmidfinder_result is not None:
        rows.append({
            'key': 'plasmidfinder:software_version',
            'value': plasmidfinder_result.software_version
        })
        rows.append({
            'key': 'plasmidfinder:database_version',
            'value': plasmidfinder_result.database_version
        })
        for hit in plasmidfinder_result.hits:
            rows.append({
                'key': f'plasmidfinder:hit:{hit.name}',
                'value': hit.query_id
            })

    jsonified_rows = []
    final_rows = []
    for row in rows:
        tmp = json.dumps(row)
        if tmp not in jsonified_rows:
            jsonified_rows.append(tmp)
            final_rows.append(row)
    # write to output file
    writer = csv.DictWriter(output_file.open('w', newline=''), fieldnames=['key', 'value'], delimiter='\t')
    writer.writeheader()
    writer.writerows(final_rows)