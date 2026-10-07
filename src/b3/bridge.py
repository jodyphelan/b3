import json

from .models import (
    MlstResult,
    AmrfinderHit,
    AmrfinderResult,
    PlasmidfinderResult,
    RmlstResult,
    QuastResult,
)
from pathlib import Path
import csv
from typing import Optional


def combine_results(
    output_file: Path,
    mlst_result: Optional[MlstResult] = None,
    amrfinder_result: Optional[AmrfinderResult] = None,
    rmlst_result: Optional[RmlstResult] = None,
    quast_result: Optional[QuastResult] = None,
    plasmidfinder_result: Optional[PlasmidfinderResult] = None,
):
    rows = []

    # mlst
    if mlst_result is not None:
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
        for hit in amrfinder_result.hits:
            rows.append({
                'key': f'amrfinder:hit:{hit.element_symbol}',
                'value': hit.contig_id
            })

    # rmlst
    if rmlst_result is not None:
        rows.append({
            'key': 'rmlst:taxon',
            'value': rmlst_result.taxon
        })
        rows.append({
            'key': 'rmlst:support',
            'value': rmlst_result.support
        })

    # quast
    if quast_result is not None:
        rows.append({
            'key': 'quast:num_contigs',
            'value': quast_result.num_contigs
        })
        rows.append({
            'key': 'quast:gc_content',
            'value': quast_result.gc_content
        })
        rows.append({
            'key': 'quast:l50',
            'value': quast_result.l50
        })
        rows.append({
            'key': 'quast:l90',
            'value': quast_result.l90
        })
        rows.append({
            'key': 'quast:n50',
            'value': quast_result.n50
        })
        rows.append({
            'key': 'quast:n90',
            'value': quast_result.n90
        })
        rows.append({
            'key': 'quast:total_length',
            'value': quast_result.total_length
        })
        rows.append({
            'key': 'quast:largest_contig',
            'value': quast_result.largest_contig
        })

    # plasmidfinder
    if plasmidfinder_result is not None:
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