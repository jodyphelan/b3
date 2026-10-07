"""
Pathogen Profiler NG package.
"""
import typer
import logging
logging.basicConfig(level=logging.DEBUG)

__version__ = "0.1.0"


from .jobs import app as jobs_app
from .workflows import app as workflows_app
from .utils import app as utils_app

# Import tool modules so their @app.command decorators register with the jobs app.
from .tools import amrfinder, fasta_stats, mlst, plasmidfinder, quast, rmlst  

# automatically show help when no command is provided
app = typer.Typer(
    no_args_is_help=True,
    help="Pathogen Profiler NG: A tool for profiling pathogens from sequencing data.",
)

app.add_typer(jobs_app, name="job", help="Commands related to jobs")
app.add_typer(workflows_app, name="wf", help="Commands related to workflows")
app.add_typer(utils_app, name="utils", help="Commands related to utils")

