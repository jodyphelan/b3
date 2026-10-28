import json

from .models import (
    MlstResult,
    AmrfinderResult,
    PlasmidfinderResult,
    RmlstResult,
    QuastResult,
    FastaqcResult,
    FastpResult,
    SsiambResult,
    PmlstResult,
    BrackenResult,
    UqcmeResult,
)
import b3
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
    fastp_result: Optional[FastpResult] = None,
    pmlst_result: Optional[PmlstResult] = None,
    bracken_result: Optional[BrackenResult] = None,  
    quast_result: Optional[QuastResult] = None,
    ssiamb_result: Optional[SsiambResult] = None,
    uqcme_result: Optional[UqcmeResult] = None,

):
    rows = [
        {
            'key': 'b3:version',
            'value': b3.__version__
        }
    ]

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
        rows.append({
            'key': 'mlst:alleles',
            'value': ",".join(map(str, mlst_result.alleles))
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
        hit_keys = ["element_symbol", "element_name","subclass","strand","stop","start","identity","coverage","contig"]
        hit_data = {k:[] for k in hit_keys}
        for hit in amrfinder_result.hits:
            for hit_key in hit_keys:
                hit_data[hit_key].append(getattr(hit, hit_key))
        for hit_key in hit_keys:
            rows.append({
                'key': f'amrfinder:{hit_key}',
                'value': "|".join(map(str, hit_data[hit_key]))
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
    if quast_result is not None:
        for key in ["software_version", "num_contigs", "total_length", "largest_contig", "N50", "N90", "L50", "L90","gc_content","n_per_100_kbp"]:
            rows.append({
                'key': f'quast:{key}',
                'value': getattr(quast_result, key)
            })

    
    
    
    if fasta_stats_result is not None:
        keys = ["software_version", "num_contigs", "gc_content", "L50", "L90", "N50", "N90", "total_length", "largest_contig"]
        for key in keys:
            rows.append({
                'key': f'fasta_stats:{key}',
                'value': getattr(fasta_stats_result, key)
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
        hit_keys = ["name", "contig", "identity", "coverage"]
        hit_data = {k:[] for k in hit_keys}
        for hit in plasmidfinder_result.hits:
            for hit_key in hit_keys:
                hit_data[hit_key].append(getattr(hit, hit_key))
        for hit_key in hit_keys:
            rows.append({
                'key': f'plasmidfinder:{hit_key}',
                'value': "|".join(map(str, hit_data[hit_key]))
            })
    # ssiamb
    if ssiamb_result is not None:
        rows.append({
            'key': 'ssiamb:software_version',
            'value': ssiamb_result.software_version
        })
        rows.append({
            'key': 'ssiamb:count',
            'value': ssiamb_result.count
        })

    # fastp
    if fastp_result is not None:
        for key, value in fastp_result.dict().items():
            rows.append({
                'key': f'fastp:{key}',
                'value': value
            })

    # bracken
    if bracken_result is not None:
        rows.append({
            'key': 'bracken:software_version',
            'value': bracken_result.software_version
        })
        rows.append({
            'key': 'bracken:database_version',
            'value': bracken_result.database_version
        })
        
        
        unclassified_hit = [hit for hit in bracken_result.hits if hit.taxonomy_lvl == 'U'][0]
        classified_hits = [hit for hit in bracken_result.hits if hit.taxonomy_lvl != 'U']

        rows.append({
            'key': 'bracken:species',
            'value': f"{classified_hits[0].name} + {unclassified_hit.name}"
        })
        rows.append({
            'key': 'bracken:spcecies_pct',
            'value': unclassified_hit.bracken_fraction_total_seqs + classified_hits[0].bracken_fraction_total_seqs
        })
        rows.append({
            'key': 'bracken:species1',
            'value': classified_hits[0].name
        })
        rows.append({
            'key': 'bracken:species1_pct',
            'value': classified_hits[0].bracken_fraction_total_seqs
        })
        rows.append({
            'key': 'bracken:species2',
            'value': unclassified_hit.name
        })
        rows.append({
            'key': 'bracken:species2_pct',
            'value': unclassified_hit.bracken_fraction_total_seqs
        })

    # uqcme
    if uqcme_result is not None:
        for key, value in uqcme_result.dict().items():
            rows.append({
                'key': f'uqcme:{key}',
                'value': value
            })

    # pmlst 

    if pmlst_result is not None:
        for key, value in pmlst_result.dict().items():
            rows.append({
                'key': f'pmlst:{key}',
                'value': value
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