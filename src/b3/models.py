from pydantic import BaseModel

class MlstResult(BaseModel):
    software_version: str
    scheme: str
    st: str
    alleles: list[str]
    
#Protein id      Contig id       Start   Stop    Strand  Element symbol  Element name    Scope   Type    Subtype Class   Subclass        Method  Target length   Reference sequence length          % Coverage of reference % Identity to reference Alignment length        Closest reference accession     Closest reference name  HMM accession   HMM description
class AmrfinderHit(BaseModel):
    protein_id: str
    contig_id: str
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
    coverage_of_reference: float
    identity_to_reference: float
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
    l50: int
    l90: int
    n50: int
    n90: int
    total_length: int
    largest_contig: int


class PlasmidfinderHit(BaseModel):
    type: str
    phenotypes: list[str]
    ref_database: str
    key: str
    gene: bool
    name: str
    identity: float
    alignment_length: int
    ref_seq_length: int
    coverage: float
    ref_id: str
    ref_acc: str
    ref_start_pos: int
    ref_end_pos: int
    query_id: str
    query_start_pos: int
    query_end_pos: int
    note: str
    query_string: str
    alignment_string: str
    ref_string: str

class PlasmidfinderResult(BaseModel):
    software_version: str
    database_version: str
    hits: list[PlasmidfinderHit] = []

class RmlstResult(BaseModel):
    software_version: str
    taxon: str
    support: int