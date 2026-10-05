import typer
from .utils import run_cmd
from pathlib import Path
from .models import (
    MlstResult,
    AmrfinderHit,
    AmrfinderResult,
    PlasmidfinderResult,
    RmlstResult,
    QuastResult,
    PlasmidfinderResult,
)
import csv
from typing import Annotated
import json


app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to jobs",
    context_settings={"help_option_names": ["-h", "--help"]}
)






