from contextlib import contextmanager
import subprocess
import subprocess as sp
import logging
import os
import signal
import re
from shutil import which
import tempfile
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

def get_absolute_path(p: Path) -> Path:
    return p.absolute()

@contextmanager
def temporary_directory():
    cwd = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            logging.debug(f"Temporary directory created at {temp_dir_path}")
            os.chdir(temp_dir_path)
            yield temp_dir_path
    finally:
        os.chdir(cwd)

@contextmanager
def debug_temporary_directory():
    cwd = Path.cwd()
    try:
        dirname = Path("debug_tmpdir")
        if not dirname.exists():
            dirname.mkdir(parents=True, exist_ok=True)
        temp_dir_path = dirname
        logging.debug(f"Debug temporary directory created at {temp_dir_path}")
        os.chdir(temp_dir_path)
        yield temp_dir_path
    finally:
        os.chdir(cwd)

def run_cmd(
    cmd: str|list,
    desc=None,
    log: Optional[str] = None,
    exit_on_error: bool=True,
    timeout: Optional[float] = None,
) -> sp.CompletedProcess:
    if isinstance(cmd, list):
        cmd = " ".join(str(c) for c in cmd)
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


def get_software_version(version_command: str, version_regex: str) -> str:
    with sp.Popen(
        ["/bin/bash", "-c", version_command],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        start_new_session=True,
    ) as process:
        stdout, _stderr = process.communicate()
        output = stdout.decode("utf-8", errors="ignore") if stdout else ""
        match = re.search(version_regex, output)
        if not match:
            raise ValueError(f"Could not determine software version from command: {version_command}")
        return match.group(1)

def parse_software_version(output: str, version_regex: str) -> str:
    match = re.search(version_regex, output)
    if not match:
        raise ValueError(f"Could not determine software version from output: {output}")
    return match.group(1)


def run_in_docker(
    cmd: list[str | Path],
    image: str,
    extra_docker_args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """
    Run a command inside a Docker container using the specified image.
    Return the stdout and stderr of the command executed inside the Docker container.
    """
    docker_cmd = ["docker", "run", "--rm"]

    if extra_docker_args:
        docker_cmd.extend(extra_docker_args)

    translated_cmd = []
    mounts = {}

    for arg in cmd:
        if isinstance(arg, Path):
            host_path = arg.resolve()
            host_dir = host_path.parent

            if host_dir not in mounts:
                container_dir = f"/mnt/volume{len(mounts)}"
                mounts[host_dir] = container_dir

                docker_cmd.extend([
                    "-v",
                    f"{host_dir}:{container_dir}",
                ])

            container_path = (
                Path(mounts[host_dir]) / host_path.name
            )

            translated_cmd.append(str(container_path))

        else:
            translated_cmd.append(str(arg))

    docker_cmd.append(image)
    docker_cmd.extend(translated_cmd)
    logging.info("Running Docker command: %s", " ".join(docker_cmd))
    result = sp.run(docker_cmd, check=True, capture_output=True, text=True)
    return result
