
2) pyproject.toml (makes `umcp` installable, fixes your earlier import/pytest collection failures)
Use PEP 621 metadata so tooling is declarative and predictable. :contentReference[oaicite:2]{index=2}  
This also aligns with GitHub’s recommended Python CI approach (install dependencies, run tests). :contentReference[oaicite:3]{index=3}

Recommended: `src/` layout from day one.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "umcp-platform"
version = "0.1.0"
description = "Platform-style catalog of UMCP kernel and weld samples."
readme = "README.md"
requires-python = ">=3.10"
authors = [{ name = "Clement Paulus" }]
license = { text = "MIT" }

dependencies = [
  "numpy>=1.24",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "ruff>=0.6",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["umcp*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
