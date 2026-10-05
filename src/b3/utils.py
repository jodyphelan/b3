import subprocess as sp
import logging
import os
import signal
import re
from shutil import which
from typing import Optional
import typer
from pathlib import Path
import logging
from b3.constants import PLASMIDFINDER_DB, AMRFINDER_DB

app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to utils",
    context_settings={"help_option_names": ["-h", "--help"]}
)

@app.command("setup")
def setup():
    conda_prefix = Path(os.getenv("CONDA_PREFIX"))
    plasmidfinder_db = Path(PLASMIDFINDER_DB)
    if plasmidfinder_db.exists() is False:
        logging.info(f"Plasmidfinder database not found at {plasmidfinder_db}")
        # git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git
        run_cmd(f"git clone https://bitbucket.org/genomicepidemiology/plasmidfinder_db.git {plasmidfinder_db}")

    else:
        logging.info(f"Plasmidfinder database found at {plasmidfinder_db}")

    amrfinder_db = Path(AMRFINDER_DB)
    if amrfinder_db.exists() is False:
        logging.info(f"AMRFinder database not found at {amrfinder_db}")
        run_cmd(f"amrfinder -u")
    else:
        logging.info(f"AMRFinder database found at {amrfinder_db}")


def run_cmd(
    cmd: str,
    desc=None,
    log: Optional[str] = None,
    exit_on_error: bool=True,
    timeout: Optional[float] = None,
) -> sp.CompletedProcess:
    if desc:
        logging.info(desc)
    processed_cmd = cmd.replace("&&","XX")
    programs = set([x.strip().split()[0] for x in re.split("[|&;]",processed_cmd.strip()) if x!=""])
    missing = [p for p in programs if which(p)==False]
    if len(missing)>0:
        raise ValueError("Cant find programs: %s\n" % (", ".join(missing)))
    logging.debug(f"Running command: {cmd}")
    log_handle = open(log,"w") if log else None
    output = log_handle if log_handle else sp.PIPE
    process = None
    try:
        process = sp.Popen(
            ["/bin/bash", "-o", "pipefail", "-c", cmd],
            stdout=output,
            stderr=output,
            start_new_session=True,
        )
        stdout, stderr = process.communicate(timeout=timeout)
        result = sp.CompletedProcess(process.args, process.returncode, stdout, stderr)
    except sp.TimeoutExpired as exc:
        if process is not None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except sp.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
        else:
            stdout = exc.stdout
            stderr = exc.stderr
        timeout_message = f"Command timed out after {timeout} seconds:\n{cmd}"
        logging.error(timeout_message)
        if exit_on_error:
            raise TimeoutError(timeout_message) from exc
        result = sp.CompletedProcess(cmd, 124, stdout, stderr)
    finally:
        if log_handle is not None:
            log_handle.close()
    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="ignore") if isinstance(result.stderr, bytes) else ""
        if stderr_text:
            logging.error(stderr_text)
        if exit_on_error:
            raise ValueError("Command Failed:\n%s\nstderr:\n%s" % (cmd, stderr_text))
    return result