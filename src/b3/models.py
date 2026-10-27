from pydantic import BaseModel, Field

class MlstResult(BaseModel):
    software_version: str
    scheme: str
    st: str
    alleles: list[str]
    
#Protein id      Contig id       Start   Stop    Strand  Element symbol  Element name    Scope   Type    Subtype Class   Subclass        Method  Target length   Reference sequence length          % Coverage of reference % Identity to reference Alignment length        Closest reference accession     Closest reference name  HMM accession   HMM description
class AmrfinderHit(BaseModel):
    protein_id: str
    contig: str
    start: int
    stop: int
    strand: str
    element_symbol: str
    element_name: str
    scope: str
    type: str
    subtype: str
    class_: str
    subclass: str
    method: str
    target_length: int
    reference_sequence_length: int
    coverage: float
    identity: float
    alignment_length: int
    closest_reference_accession: str
    closest_reference_name: str
    hmm_accession: str
    hmm_description: str

class AmrfinderResult(BaseModel):
    software_version: str
    database_version: str
    hits: list[AmrfinderHit] = []

class QuastResult(BaseModel):
    software_version: str
    num_contigs: int
    gc_content: float
    L50: int
    L90: int
    N50: int
    N90: int
    total_length: int
    largest_contig: int
    n_per_100_kbp: float


class PlasmidfinderHit(BaseModel):
    name: str
    contig: str
    identity: float
    coverage: float

class PlasmidfinderResult(BaseModel):
    software_version: str
    database_version: str
    hits: list[PlasmidfinderHit] = []

class RmlstResult(BaseModel):
    software_version: str
    taxon: str
    support: int


class FastaqcResult(BaseModel):
    software_version: str
    num_contigs: int
    gc_content: float
    L50: int
    L90: int
    N50: int
    N90: int
    total_length: int
    largest_contig: int

class FastpResult(BaseModel):
    software_version: str
    adapter_trimmed_bases: int
    adapter_trimmed_reads: int
    before_filtering_read1_mean_length: int
    before_filtering_read2_mean_length: int
    before_filtering_total_reads: int
    after_filtering_read1_mean_length: int
    after_filtering_read2_mean_length: int
    after_filtering_total_reads: int
    duplication_rate: float
    low_quality_reads: int
    num_cycles: int
    too_long_reads: int
    too_many_n_reads: int
    too_short_reads: int


class ShovillResult(BaseModel):
    software_version: str

class SsiambResult(BaseModel):
    software_version: str

class SylphResult(BaseModel):
    software_version: str

class Kraken2Result(BaseModel):
    software_version: str
    database_version: str

class BrackenHit(BaseModel):
    name: str
    taxonomy_id: int
    taxonomy_lvl: str
    kraken_assigned_seqs: int
    bracken_assigned_seqs: int
    total_seqs: int
    kraken_fraction_total_seqs: float
    bracken_fraction_total_seqs: float

class BrackenResult(BaseModel):
    software_version: str
    database_version: str
    hits: list[BrackenHit] = []

class PmlstResult(BaseModel):
    software_version: str
    database_version: str
    plasmids: str | None = None
    IncF: int | None = None
    IncI1: int | None = None
    IncA_C: int | None = Field(default=None, alias="IncA/C")
    IncHI1: int | None = None
    IncHI2: int | None = None
    IncN: int | None = None
    pmlst_summary: str | None = Field(default=None, alias="pMLST summary")

class SsiambResult(BaseModel):
    software_version: str
    count: int


class UqcmeResult(BaseModel):
    software_version: str
    qc_outcome: str
    qc_action: str
    failed_rules: str | None = None
    passed_rules: str | None = None
    skipped_rules: str | None = None
    missing_qc_fields: str | None = None