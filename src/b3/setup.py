from pathlib import Path
from .utils import run_cmd
from .constants import DB_DIR
from typer import Typer
from typing import Annotated
from .tools.amrfinder import download_amrfinder_db
from .tools.pmlst import download_pmlst_db
from .tools.plasmidfinder import download_plasmidfinder_db


app = Typer(
    no_args_is_help=True,
    help="Commands related to setup",
    context_settings={"help_option_names": ["-h", "--help"]}
)




@app.command(
    help="Download all required databases to the specified output directory"
)
def download_dbs(
    outdir: Annotated[Path, "Output directory for databases"] = Path(DB_DIR),
    docker: Annotated[bool, "Whether to run the download inside a Docker container"] = False
):
    download_amrfinder_db(outdir / "amrfinder_db", docker=docker)
    download_pmlst_db(outdir / "pmlst_db", docker=docker)
    download_plasmidfinder_db(outdir / "plasmidfinder_db")
    