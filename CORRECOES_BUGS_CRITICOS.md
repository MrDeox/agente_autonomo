# Correções para Bugs Críticos - Projeto Hephaestus

## Bug #1: Importação Incorreta no main.py

**Arquivo:** `main.py`
**Linha:** 13

### Código Atual:
```python
# Import the FastAPI app instance from app.py
from app import app
```

### Correção:
```python
# Import the FastAPI app instance from tools/app.py
from tools.app import app
```

## Bug #2: Dependências Ausentes - requirements.txt

**Arquivo:** `requirements.txt`

### Código Atual:
```
requests>=2.31.0
google-generativeai
python-dotenv>=1.0.0
psutil>=5.9.8
pytest>=7.0.0
pytest-mock>=3.0.0
radon>=5.1.0
pandas>=1.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
```

### Correção:
```
requests>=2.31.0
google-generativeai>=0.8.5,<0.9.0
python-dotenv>=1.0.0
psutil>=5.9.8
pytest>=7.0.0
pytest-mock>=3.0.0
radon>=5.1.0
pandas>=1.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
omegaconf>=2.3.0
hydra-core>=1.3.2,<2.0.0
typer>=0.16.0,<0.17.0
jsonschema>=4.24.0,<5.0.0
termcolor>=2.4.0
openai>=1.13.3
pydantic>=2.6.4
loguru>=0.7.2
gitpython>=3.1.42
ruamel.yaml>=0.18.6
```

## Bug #3: Configuração Inconsistente de Dependências

**Arquivo:** `pyproject.toml`

### Problema:
O arquivo tem configurações híbridas entre Poetry e setuptools.

### Correção - Opção 1 (Usar apenas Poetry):
```toml
[tool.poetry]
name = "agente-autonomo"
version = "0.1.0"
description = ""
authors = ["MrDeox <arthurptc33@gmail.com>"]
readme = "README.md"
package-mode = false

[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.31.0"
google-generativeai = "^0.8.5"
python-dotenv = "^1.0.0"
psutil = "^5.9.8"
pytest = "^7.0.0"
pytest-mock = "^3.0.0"
radon = "^5.1.0"
pandas = "^1.0.0"
fastapi = "^0.100.0"
uvicorn = {extras = ["standard"], version = "^0.20.0"}
omegaconf = "^2.3.0"
hydra-core = "^1.3.2"
typer = "^0.16.0"
jsonschema = "^4.24.0"
termcolor = "^2.4.0"
openai = "^1.13.3"
pydantic = "^2.6.4"
loguru = "^0.7.2"
gitpython = "^3.1.42"
"ruamel.yaml" = "^0.18.6"

[tool.poetry.dev-dependencies]
pytest = "^8.1.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### Correção - Opção 2 (Usar apenas setuptools):
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agente-autonomo"
version = "0.1.0"
description = ""
authors = [
    {name = "MrDeox", email = "arthurptc33@gmail.com"}
]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31.0",
    "google-generativeai>=0.8.5,<0.9.0",
    "python-dotenv>=1.0.0",
    "psutil>=5.9.8",
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
    "radon>=5.1.0",
    "pandas>=1.0.0",
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.20.0",
    "omegaconf>=2.3.0",
    "hydra-core>=1.3.2,<2.0.0",
    "typer>=0.16.0,<0.17.0",
    "jsonschema>=4.24.0,<5.0.0",
    "termcolor>=2.4.0",
    "openai>=1.13.3",
    "pydantic>=2.6.4",
    "loguru>=0.7.2",
    "gitpython>=3.1.42",
    "ruamel.yaml>=0.18.6"
]
```

## Bug #4: Tratamento de Exceções no memory.py

**Arquivo:** `agent/memory.py`
**Linha:** 675

### Código Atual:
```python
try:
    # Extract hour from timestamp
    date_obj = datetime.datetime.fromisoformat(obj["date"].replace("Z", "+00:00"))
    hour = date_obj.hour
    
    if obj in self.completed_objectives:
        hourly_success[hour]["successes"] += 1
    else:
        hourly_success[hour]["failures"] += 1
except (ValueError, KeyError):
    continue
```

### Correção:
```python
try:
    # Extract hour from timestamp
    date_str = obj.get("date", "")
    if not date_str:
        continue
    
    # Handle different date formats
    if date_str.endswith("Z"):
        date_str = date_str.replace("Z", "+00:00")
    
    date_obj = datetime.datetime.fromisoformat(date_str)
    hour = date_obj.hour
    
    if obj in self.completed_objectives:
        hourly_success[hour]["successes"] += 1
    else:
        hourly_success[hour]["failures"] += 1
except (ValueError, KeyError, TypeError) as e:
    self.logger.debug(f"Failed to parse date from object: {obj}. Error: {e}")
    continue
```

## Bug #5: Problema de Splitting de String

**Arquivo:** `agent/memory.py`
**Linha:** 492

### Código Atual:
```python
reason, keyword = group_key.split("_", 1)
```

### Correção:
```python
if "_" in group_key:
    reason, keyword = group_key.split("_", 1)
else:
    reason = group_key
    keyword = "unknown"
```

## Bug #6: Verificação de Diretório no config_loader.py

**Arquivo:** `agent/config_loader.py`
**Linha:** 34

### Código Atual:
```python
hydra.initialize_config_dir(
    config_dir=os.path.join(Path.cwd(), "config"),
    version_base=None
)
```

### Correção:
```python
config_dir = os.path.join(Path.cwd(), "config")
if not os.path.exists(config_dir):
    raise RuntimeError(f"Configuration directory not found: {config_dir}")

hydra.initialize_config_dir(
    config_dir=config_dir,
    version_base=None
)
```

## Bug #7: Criação de Diretórios no hephaestus_agent.py

**Arquivo:** `agent/hephaestus_agent.py`
**Linha:** 89

### Código Atual:
```python
self.evolution_log_file = "logs/evolution_log.csv"
```

### Correção:
```python
self.evolution_log_file = "logs/evolution_log.csv"
# Ensure logs directory exists
os.makedirs(os.path.dirname(self.evolution_log_file), exist_ok=True)
```

## Bug #8: Validação de Paths no patch_applicator.py

**Arquivo:** `agent/patch_applicator.py`
**Linha:** 224

### Código Atual:
```python
normalized = Path(os.path.normpath(file_path_str))
full_path = Path(base_path).resolve() / normalized
```

### Correção:
```python
# Validate and normalize the file path
normalized = Path(os.path.normpath(file_path_str))

# Prevent directory traversal attacks
if ".." in normalized.parts:
    logger.error(f"Invalid file path (directory traversal): {file_path_str}")
    overall_success = False
    continue

# Ensure the path is within the base directory
base_path_resolved = Path(base_path).resolve()
full_path = base_path_resolved / normalized

# Additional security check
try:
    full_path.resolve().relative_to(base_path_resolved)
except ValueError:
    logger.error(f"File path outside base directory: {file_path_str}")
    overall_success = False
    continue
```

## Bug #9: Validação de Input no FastAPI

**Arquivo:** `tools/app.py`
**Linha:** 15

### Código Atual:
```python
class Objective(BaseModel):
    objective: str
```

### Correção:
```python
from pydantic import BaseModel, Field, validator
import re

class Objective(BaseModel):
    objective: str = Field(..., min_length=1, max_length=1000)
    
    @validator('objective')
    def validate_objective(cls, v):
        # Remove potentially dangerous characters
        if re.search(r'[<>"|&;`$(){}[\]\\]', v):
            raise ValueError('Objective contains invalid characters')
        
        # Ensure it's not just whitespace
        if not v.strip():
            raise ValueError('Objective cannot be empty or whitespace only')
        
        return v.strip()
```

## Bug #10: Tratamento de Configuração Nula

**Arquivo:** `agent/hephaestus_agent.py`
**Linha:** 66

### Código Atual:
```python
architect_model_config = self.config.get("models", {}).get("architect_default")
```

### Correção:
```python
models_config = self.config.get("models")
if not models_config:
    raise RuntimeError("No models configuration found in config")

architect_model_config = models_config.get("architect_default")
if not architect_model_config:
    raise RuntimeError("No architect_default model configuration found")
```

## Comandos para Aplicar as Correções

### 1. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 2. Ou usar Poetry (se escolher essa opção):
```bash
poetry install
```

### 3. Verificar se os diretórios necessários existem:
```bash
mkdir -p logs config
```

### 4. Executar testes básicos:
```bash
python -c "import agent.config_loader; print('Config loader OK')"
python -c "import tools.app; print('FastAPI app OK')"
python -c "import cli; print('CLI OK')"
```

## Notas Importantes

1. **Backup**: Sempre fazer backup dos arquivos antes de aplicar as correções
2. **Testes**: Executar testes após cada correção para verificar se não introduziu novos bugs
3. **Dependências**: Escolher entre Poetry ou setuptools e remover a configuração não utilizada
4. **Segurança**: As correções de segurança são especialmente importantes em ambiente de produção

## Prioridade de Aplicação

1. **Imediata**: Bugs #1, #2, #3 (sem esses o sistema não funciona)
2. **Alta**: Bugs #4, #5, #6, #7 (previnem crashes)
3. **Média**: Bugs #8, #9, #10 (melhoram segurança e robustez)

Após aplicar essas correções, o sistema deve estar funcional e mais estável.