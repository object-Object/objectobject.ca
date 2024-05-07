import json
import os

import nox

nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = []


@nox.session
def synth(session: nox.Session):
    session.install("-e", ".[aws-cdk]")
    session.run("cdk", "synth", *session.posargs, external=True)


@nox.session(python=None)
def deploy_cdk_ci(session: nox.Session):
    session.notify(
        "deploy_cdk",
        [
            "--ci",
            "--require-approval=never",
            "--no-lookups",
            "--app=cdk.out",
            *session.posargs,
        ],
    )


@nox.session
def deploy_cdk(session: nox.Session):
    session.install("-e", ".[aws-cdk]")
    session.run(
        "cdk",
        "deploy",
        "--outputs-file=outputs.json",
        *session.posargs,
        external=True,
    )
    session.notify("parse_outputs")


@nox.session(python=None)
def parse_outputs(session: nox.Session):
    with open("outputs.json") as f:
        outputs: dict[str, dict[str, str]] = json.load(f)

    if (n := len(outputs)) != 1:
        stacks = ", ".join(outputs.keys())
        raise ValueError(f"Expected outputs from 1 stack, got {n}: {stacks}")

    stack_name, stack_outputs = outputs.popitem()
    set_output("StackName", stack_name)
    for key, value in stack_outputs.items():
        set_output(key, value)


def set_output(key: str, value: str):
    message = f"{key}={value}"
    if github_output := os.getenv("GITHUB_OUTPUT"):
        with open(github_output, "a") as f:
            print(message, file=f)
    else:
        print(message)
