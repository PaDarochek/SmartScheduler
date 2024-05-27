"""Default: lint, test and create wheel"""

import glob

import tomli
from doit.tools import create_folder

DOIT_CONFIG = {"default_tasks": ["lint", "test", "wheel"]}


def dumpkeys(infile, table, outfile):
    """Dumps TOML table keys one per line."""
    with open(infile, "rb") as fin:
        full = tomli.load(fin)
    with open(outfile, "w") as fout:
        print(*full[table], sep="\n", file=fout)


def task_lint():
    """Run linter on the project using flake8, black and isort."""
    yield {
        "name": "flake8",
        "actions": ["flake8 ."],
    }
    yield {
        "name": "black-check",
        "actions": ["black --check ."],
    }
    yield {
        "name": "isort-check",
        "actions": ["isort --check ."],
    }
    yield {
        "name": "docformatter-check",
        "actions": ["docformatter --recursive --check ."],
    }


def task_format():
    """Format the code."""
    return {"actions": ["isort .", "black .", "docformatter --recursive ."]}


def task_docupdate():
    """Update documentation."""
    return {"actions": ["sphinx-apidoc -f -o docs/source scheduler"]}


def task_doc():
    """Build documentation."""
    return {
        "actions": ["sphinx-build -M html docs/source docs/build"],
        "task_dep": ["docupdate"],
    }


def task_test():
    """Run unit tests."""
    yield {"actions": ["coverage run -m unittest -v"], "name": "run"}
    yield {"actions": ["coverage report"], "verbosity": 2, "name": "report"}


def task_pot():
    """Re-create .pot ."""
    return {
        "actions": ["pybabel extract -o Scheduler.pot scheduler"],
        "file_dep": glob.glob("scheduler/*.py"),
        "targets": ["Scheduler.pot"],
    }


def task_po():
    """Update translations."""
    return {
        "actions": [
            (
                "pybabel update --ignore-pot-creation-date "
                "-D Scheduler -d po -i Scheduler.pot -l ru"
            )
        ],
        "file_dep": ["Scheduler.pot"],
        "targets": ["po/ru/LC_MESSAGES/Scheduler.po"],
    }


def task_mo():
    """Compile translations."""
    return {
        "actions": [
            (create_folder, ["scheduler/po/ru/LC_MESSAGES"]),
            "pybabel compile -D Scheduler -l ru "
            + "-i po/ru/LC_MESSAGES/Scheduler.po -d scheduler/po",
        ],
        "file_dep": ["po/ru/LC_MESSAGES/Scheduler.po"],
        "targets": ["scheduler/po/ru/LC_MESSAGES/Scheduler.mo"],
    }


def task_git_clean():
    """Clean all generated files not tracked by GIT."""
    return {"actions": ["git clean -xdf"]}


def task_requirements():
    """Dump Pipfile requirements."""
    return {
        "actions": [(dumpkeys, ["Pipfile", "packages", "requirements.txt"])],
        "file_dep": ["Pipfile"],
        "targets": ["requirements.txt"],
    }


def task_sdist():
    """Create source distribution."""
    return {
        "actions": ["python -m build -s -n"],
        "task_dep": ["git_clean", "requirements"],
    }


def task_wheel():
    """Create binary wheel distribution."""
    return {
        "actions": ["python -m build -w"],
        "task_dep": ["mo", "requirements"],
    }
