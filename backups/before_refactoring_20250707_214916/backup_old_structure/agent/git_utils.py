from pathlib import Path
from typing import Optional, Tuple
import logging

from agent.tool_executor import run_git_command


def initialize_git_repository(logger: logging.Logger) -> bool:
    """Ensure a git repository exists and is configured.

    Parameters
    ----------
    logger: logging.Logger
        Logger for reporting progress and errors.

    Returns
    -------
    bool
        True if the repository is ready to use, False on fatal error.
    """
    git_dir = Path(".git")
    if git_dir.is_dir():
        logger.info("Repositório Git já existe.")
        # Ensure user configuration exists
        check_name_success, _ = run_git_command(['git', 'config', 'user.name'])
        check_email_success, _ = run_git_command(['git', 'config', 'user.email'])
        if not (check_name_success and check_email_success):
            logger.warning("Git user.name ou user.email não configurados. Tentando configurar localmente.")
            name_success, name_out = run_git_command(
                ['git', 'config', '--local', 'user.name', 'Hephaestus Agent']
            )
            email_success, email_out = run_git_command(
                ['git', 'config', '--local', 'user.email', 'hephaestus@example.com']
            )
            if not (name_success and email_success):
                logger.error(
                    f"FALHA CRÍTICA ao configurar git user.name/email localmente. Name: {name_out}, Email: {email_out}"
                )
                return False
            logger.info("Git user.name e user.email configurados localmente com sucesso.")
        return True

    logger.info("Repositório Git não encontrado. Inicializando...")
    init_success, init_output = run_git_command(['git', 'init'])
    logger.debug(f"Resultado 'git init': Success={init_success}, Output:\n{init_output}")
    if not init_success:
        logger.error(f"FALHA CRÍTICA: 'git init' falhou. Output:\n{init_output}")
        return False

    logger.info("Repositório Git inicializado com sucesso.")

    name_success, name_out = run_git_command(['git', 'config', '--local', 'user.name', 'Hephaestus Agent'])
    if not name_success:
        logger.error(f"FALHA CRÍTICA ao configurar git user.name. Output:\n{name_out}")
        return False
    email_success, email_out = run_git_command(['git', 'config', '--local', 'user.email', 'hephaestus@example.com'])
    if not email_success:
        logger.error(f"FALHA CRÍTICA ao configurar git user.email. Output:\n{email_out}")
        return False

    logger.info("Git user.name e user.email configurados localmente.")

    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.pyc
*.$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# PEP 582; __pypackages__
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyderworkspace

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Hephaestus specific
hephaestus.log
*.DS_Store
"""
    gitignore_path = Path(".gitignore")
    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content.strip())
        logger.info(f"{gitignore_path} criado com sucesso.")
    except IOError as e:
        logger.error(f"FALHA CRÍTICA ao criar {gitignore_path}: {e}")
        return False

    add_success, add_output = run_git_command(['git', 'add', str(gitignore_path)])
    logger.debug(f"Resultado 'git add .gitignore': Success={add_success}, Output:\n{add_output}")
    if not add_success:
        logger.error(f"FALHA CRÍTICA: 'git add {gitignore_path}' falhou. Output:\n{add_output}")
        return False

    commit_message = "chore: Initial commit by Hephaestus Agent"
    commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
    logger.debug(f"Resultado 'git commit': Success={commit_success}, Output:\n{commit_output}")
    if not commit_success:
        if any(msg in commit_output.lower() for msg in ["nothing to commit", "nada a submeter", "no changes added to commit"]):
            logger.warning(f"'git commit' informou que não há nada novo para commitar. Output:\n{commit_output}")
            logger.info("Considerando a inicialização do Git como bem-sucedida.")
        else:
            logger.error(f"FALHA CRÍTICA: 'git commit' inicial falhou. Output:\n{commit_output}")
            return False

    logger.info("Commit inicial realizado com sucesso ou já existente.")
    return True
