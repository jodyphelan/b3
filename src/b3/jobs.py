import typer


app = typer.Typer(
    no_args_is_help=True,
    help="Commands related to jobs",
    context_settings={"help_option_names": ["-h", "--help"]}
)






