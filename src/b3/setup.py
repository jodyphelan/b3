from pathlib import Path
from .utils import run_cmd
from .constants import DB_DIR
from typer import Typer
from typing import Annotated


app = Typer(
    no_args_is_help=True,
    help="Commands related to setup",
    context_settings={"help_option_names": ["-h", "--help"]}
)


def download_ftp_tree(ftp, remote_dir, local_dir):
    parent = ftp.pwd()
    ftp.cwd(remote_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    for name, facts in ftp.mlsd():
        entry_type = facts.get("type")
        print(f"Processing entry: {name}, type: {entry_type}")

        if entry_type == "dir" and name not in (".", ".."):
            child_local = local_dir / name
            child_local.mkdir(exist_ok=True)

            # recurse into child directory
            download_ftp_tree(ftp, name, child_local)

            # return to the parent directory before processing next sibling
            ftp.cwd(parent)

        elif entry_type == "file":
            target = local_dir / name
            with open(target, "wb") as f:
                ftp.retrbinary(f"RETR {name}", f.write)

@app.command(
    no_args_is_help=True,
    help="Download the AMRFinder database to the local directory"
)
def download_amrfinder_db(outdir: Path):
    cmds = [
        "amrfinder_update",
        "-d", outdir
    ]
    run_cmd(cmds)



@app.command(
    no_args_is_help=True,
    help="Download the pMLST database to the specified output directory"
)
def download_pmlst_db(
    outdir: Path
):
    cmds = [
        "pmlst-download-db",
        outdir
    ]
    run_cmd(cmds)


@app.command(
    no_args_is_help=True,
    help="Download the PlasmidFinder database to the specified output directory"
)
def download_plasmidfinder_db(
    outdir: Path
):
    cmds = [
        "git",
        "clone",
        "https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git",
        str(outdir)
    ]
    run_cmd(cmds)


@app.command(
    help="Download all required databases to the specified output directory"
)
def download_dbs(outdir: Annotated[Path, "Output directory for databases"] = Path(DB_DIR)):
    outdir.mkdir(parents=True, exist_ok=True)
    download_amrfinder_db(outdir / "amrfinder_db" )
    download_pmlst_db(outdir / "pmlst_db")
    download_plasmidfinder_db(outdir / "plasmidfinder_db")