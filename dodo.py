import glob

DOIT_CONFIG = {"default_tasks": ["lint", "test"]}


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
    return {"actions": ["python3 -m unittest discover"]}


def task_pot():
    """Re-create .pot ."""
    return {
        "actions": ["pybabel extract -o scheduler/Scheduler.pot scheduler"],
        "file_dep": glob.glob("scheduler/*.py"),
        "targets": ["scheduler/Scheduler.pot"],
    }


def task_po():
    """Update translations."""
    return {
        "actions": [
            (
                "pybabel update -D Scheduler -d scheduler -i "
                "scheduler/Scheduler.pot -l ru"
            )
        ],
        "file_dep": ["scheduler/Scheduler.pot"],
        "targets": ["scheduler/ru/LC_MESSAGES/Scheduler.po"],
    }


def task_mo():
    """Compile translations."""
    return {
        "actions": [
            (
                "pybabel compile -D Scheduler -l ru "
                "-i scheduler/ru/LC_MESSAGES/Scheduler.po -d scheduler"
            ),
        ],
        "file_dep": ["scheduler/ru/LC_MESSAGES/Scheduler.po"],
        "targets": ["scheduler/ru/LC_MESSAGES/Scheduler.mo"],
    }


def task_git_clean():
    """Clean all generated files not tracked by GIT."""
    return {"actions": ["git clean -xdf"]}
