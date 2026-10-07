from collections import OrderedDict
import json
import logging
from ..models import FastaqcResult
from b3 import __version__ as b3_version
from b3.jobs import app
from typing import Annotated

def parse_fasta_stats_output(filename: str) -> FastaqcResult:
    
    data = json.load(open(filename))
    return FastaqcResult(
        software_version=b3_version,
        num_contigs=data["num_contigs"],
        gc_content=data["gc_content"],
        L50=data["L50"],
        L90=data["L90"],
        N50=data["N50"],
        N90=data["N90"],
        total_length=data["total_length"],
        largest_contig=data["largest_contig"]
    )

def get_fasta_dictionary(filename:str) -> dict:
    fa_dict = OrderedDict()
    seq_name = ""

    for l in open(filename):
        line = l.rstrip()
        if line=="": continue
        if line.startswith(">"):
            seq_name = line[1:].split()[0]
            fa_dict[seq_name] = []
        else:
            fa_dict[seq_name].append(line)
    result = {}
    for seq in fa_dict:
        result[seq] = "".join(fa_dict[seq])
        result[seq] = result[seq].upper()
    return result

def get_fasta_stats_stats(fa_dict: dict) -> dict:
    concatenated_seq = "".join(fa_dict.values())
    stats = {}
    stats["gc_content"] = round((concatenated_seq.count("G") + concatenated_seq.count("C")) / len(concatenated_seq)*100, 2)
    stats["num_contigs"] = len(fa_dict)
    stats["L50"] = calculate_Lx(fa_dict, 50)
    stats["L90"] = calculate_Lx(fa_dict, 90)
    stats["N50"] = calculate_Nx(fa_dict, 50)
    stats["N90"] = calculate_Nx(fa_dict, 90)
    stats["total_length"] = len(concatenated_seq)
    stats["largest_contig"] = max(len(seq) for seq in fa_dict.values()) if fa_dict else 0

    return stats

def calculate_Lx(fa_dict: dict, x: int) -> int:
    lengths = sorted((len(seq) for seq in fa_dict.values()), reverse=True)
    total_length = sum(lengths)
    cumsum = 0
    for i, length in enumerate(lengths):
        cumsum += length
        if cumsum >= total_length * x / 100:
            return i + 1
    return 0

def calculate_Nx(fa_dict: dict, x: int) -> int:
    lengths = sorted((len(seq) for seq in fa_dict.values()), reverse=True)
    total_length = sum(lengths)
    cumsum = 0
    for length in lengths:
        cumsum += length
        if cumsum >= total_length * x / 100:
            return length
    return 0

@app.command(
    "fasta-stats", 
    help="Run FASTA QC on the input FASTA file and save results to the output directory.",
    no_args_is_help=True
)
def job_fasta_stats(
    input_fasta: Annotated[str, "Input FASTA file"], 
    output_file: Annotated[str, "Output JSON file with FASTA Stats results"]
) -> dict:
    logging.info(f"Running FASTA Stats on {input_fasta}")
    fa_dict = get_fasta_dictionary(input_fasta)
    stats = get_fasta_stats_stats(fa_dict)
    with open(output_file, "w") as f:
        json.dump(stats, f)

    return parse_fasta_stats_output(output_file)