import os


CONDA_PREFIX = os.environ.get("CONDA_PREFIX", "")
PLASMIDFINDER_DB = os.path.join(CONDA_PREFIX, "share", "plasmidfinder_db")
AMRFINDER_DB = os.path.join(CONDA_PREFIX, "share", "amrfinderplus")