"""Core recipes for Gaussian."""
from __future__ import annotations

import multiprocessing
from typing import TYPE_CHECKING

from ase.calculators.gaussian import Gaussian

from quacc import SETTINGS, job
from quacc.runners.ase import run_calc
from quacc.schemas.cclib import cclib_summarize_run
from quacc.utils.dicts import merge_dicts

if TYPE_CHECKING:
    from typing import Any

    from ase import Atoms

    from quacc.schemas.cclib import cclibSchema

_LABEL = "Gaussian"
LOG_FILE = f"{_LABEL}.log"
GAUSSIAN_CMD = f"{SETTINGS.GAUSSIAN_CMD} < {_LABEL}.com > {LOG_FILE}"


@job
def static_job(
    atoms: Atoms,
    charge: int = 0,
    spin_multiplicity: int = 1,
    xc: str = "wb97x-d",
    basis: str = "def2-tzvp",
    copy_files: list[str] | None = None,
    **kwargs,
) -> cclibSchema:
    """
    Carry out a single-point calculation.

    Parameters
    ----------
    atoms
        Atoms object
    charge
        Charge of the system.
    spin_multiplicity
        Multiplicity of the system.
    xc
        Exchange-correlation functional
    basis
        Basis set
    copy_files
        Files to copy to the runtime directory.
    **kwargs
        Custom kwargs for the Gaussian calculator. Set a value to
        `None` to remove a pre-existing key entirely. For a list of available
        keys, refer to the `ase.calculators.gaussian.Gaussian` calculator.

        !!! Info "Calculator defaults"

            ```python
            {
                "mem": "16GB",
                "chk": "Gaussian.chk",
                "nprocshared": multiprocessing.cpu_count(),
                "xc": xc,
                "basis": basis,
                "charge": charge,
                "mult": spin_multiplicity,
                "sp": "",
                "scf": ["maxcycle=250", "xqc"],
                "integral": "ultrafine",
                "nosymmetry": "",
                "pop": "CM5",
                "gfinput": "",
                "ioplist": ["6/7=3", "2/9=2000"],
            }
            ```

    Returns
    -------
    cclibSchema
        Dictionary of results, as specified in
        [quacc.schemas.cclib.cclib_summarize_run][]
    """

    defaults = {
        "mem": "16GB",
        "chk": "Gaussian.chk",
        "nprocshared": multiprocessing.cpu_count(),
        "xc": xc,
        "basis": basis,
        "charge": charge,
        "mult": spin_multiplicity,
        "sp": "",
        "scf": ["maxcycle=250", "xqc"],
        "integral": "ultrafine",
        "nosymmetry": "",
        "pop": "CM5",
        "gfinput": "",
        "ioplist": ["6/7=3", "2/9=2000"],  # see ASE issue #660
    }
    return _base_job(
        atoms,
        defaults=defaults,
        calc_swaps=kwargs,
        additional_fields={"name": "Gaussian Static"},
        copy_files=copy_files,
    )


@job
def relax_job(
    atoms: Atoms,
    charge: int,
    spin_multiplicity: int,
    xc: str = "wb97x-d",
    basis: str = "def2-tzvp",
    freq: bool = False,
    copy_files: list[str] | None = None,
    **kwargs,
) -> cclibSchema:
    """
    Carry out a geometry optimization.

    Parameters
    ----------
    atoms
        Atoms object
    charge
        Charge of the system.
    spin_multiplicity
        Multiplicity of the system.
    xc
        Exchange-correlation functional
    basis
        Basis set
    freq
        If a frequency calculation should be carried out.
    copy_files
        Files to copy to the runtime directory.
    **kwargs
        Custom kwargs for the Gaussian calculator. Set a value to
        `None` to remove a pre-existing key entirely. For a list of available
        keys, refer to the `ase.calculators.gaussian.Gaussian` calculator.

        !!! Info "Calculator defaults"

            ```python
            {
                "mem": "16GB",
                "chk": "Gaussian.chk",
                "nprocshared": multiprocessing.cpu_count(),
                "xc": xc,
                "basis": basis,
                "charge": charge,
                "mult": spin_multiplicity,
                "opt": "",
                "pop": "CM5",
                "scf": ["maxcycle=250", "xqc"],
                "integral": "ultrafine",
                "nosymmetry": "",
                "freq": "" if freq else None,
                "ioplist": ["2/9=2000"],
            }
            ```

    Returns
    -------
    cclibSchema
        Dictionary of results, as specified in
        [quacc.schemas.cclib.cclib_summarize_run][]
    """

    defaults = {
        "mem": "16GB",
        "chk": "Gaussian.chk",
        "nprocshared": multiprocessing.cpu_count(),
        "xc": xc,
        "basis": basis,
        "charge": charge,
        "mult": spin_multiplicity,
        "opt": "",
        "pop": "CM5",
        "scf": ["maxcycle=250", "xqc"],
        "integral": "ultrafine",
        "nosymmetry": "",
        "freq": "" if freq else None,
        "ioplist": ["2/9=2000"],  # ASE issue #660
    }
    return _base_job(
        atoms,
        defaults=defaults,
        calc_swaps=kwargs,
        additional_fields={"name": "Gaussian Relax"},
        copy_files=copy_files,
    )


def _base_job(
    atoms: Atoms,
    defaults: dict[str, Any] | None = None,
    calc_swaps: dict[str, Any] | None = None,
    additional_fields: dict[str, Any] | None = None,
    copy_files: list[str] | None = None,
) -> cclibSchema:
    """
    Base job function for carrying out Gaussian recipes.

    Parameters
    ----------
    atoms
        Atoms object
    defaults
        Default parameters for the calculator.
    calc_swaps
        Dictionary of custom kwargs for the Gaussian calculator. Set a value to
        `None` to remove a pre-existing key entirely. For a list of available
        keys, refer to the `ase.calculators.gaussian.Gaussian` calculator.
    additional_fields
        Additional fields to supply to the summarizer.
    copy_files
        Files to copy to the runtime directory.

    Returns
    -------
    cclibSchema
        Dictionary of results, as specified in
        [quacc.schemas.cclib.cclib_summarize_run][]
    """
    flags = merge_dicts(defaults, calc_swaps)

    atoms.calc = Gaussian(command=GAUSSIAN_CMD, label=_LABEL, **flags)
    atoms = run_calc(atoms, geom_file=LOG_FILE, copy_files=copy_files)

    return cclib_summarize_run(atoms, LOG_FILE, additional_fields=additional_fields)
