from pathlib import Path
import sys
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

@app.command(
    help="Set up Conda environments from the specified deployment directory"
)
def setup_conda_envs(
    deployment_dir: Annotated[Path, "Directory to set up Conda environments"] = Path(sys.base_prefix + "/envs")
):
    this_file_locaiton = Path(__file__).resolve()
    conda_files_location = this_file_locaiton.parent / "tools" /   "conda_envs"
    deployment_dir.mkdir(parents=True, exist_ok=True)
    for conda_env_file in conda_files_location.glob("*.txt"):
        env_name = conda_env_file.stem
        print(f"Setting up Conda environment '{env_name}' from file '{conda_env_file}'")
        #conda create --prefix <deployment_dir / env_name> --file <conda_env_file>
        run_cmd([
            "conda", "create", "--prefix", str(deployment_dir / env_name), "--file", str(conda_env_file)
        ])
    