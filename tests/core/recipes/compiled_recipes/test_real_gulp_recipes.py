import os
from shutil import which

import pytest
from ase.build import bulk, molecule

from quacc.recipes.gulp.core import relax_job, static_job

has_gulp = bool(
    (bool(which("gulp")) or os.environ.get("ASE_GULP_COMMAND"))
    and os.environ.get("GULP_LIB")
)

pytestmark = pytest.mark.skipif(
    not has_gulp,
    reason="Needs GULP",
)


def test_static_job(tmpdir):
    tmpdir.chdir()

    atoms = molecule("H2O")

    output = static_job(atoms)
    assert output["natoms"] == len(atoms)
    assert output["parameters"]["keywords"] == "gfnff"
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    output = static_job(atoms, keywords={"gwolf": True})
    assert output["natoms"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "gwolf" in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    output = static_job(atoms, use_gfnff=False)
    assert output["natoms"] == len(atoms)
    assert "gfnff" not in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    atoms = bulk("Cu") * (2, 2, 2)
    output = static_job(atoms)
    assert output["nsites"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "gwolf" in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]

    output = static_job(atoms, keywords={"gwolf": None})
    assert output["nsites"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]

    output = static_job(atoms, use_gfnff=False)
    assert output["nsites"] == len(atoms)
    assert "gfnff" not in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]


def test_relax_job(tmpdir):
    tmpdir.chdir()

    atoms = molecule("H2O")

    output = relax_job(atoms)
    assert output["natoms"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" not in output["parameters"]["keywords"]
    assert "conv" in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    output = relax_job(atoms, relax_cell=False, keywords={"gwolf": True})
    assert output["natoms"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" not in output["parameters"]["keywords"]
    assert "conv" in output["parameters"]["keywords"]
    assert "gwolf" in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    output = relax_job(atoms, use_gfnff=False)
    assert output["natoms"] == len(atoms)
    assert "gfnff" not in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" not in output["parameters"]["keywords"]
    assert "conv" in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" in output["parameters"]["options"]
    assert "output cif gulp.cif" not in output["parameters"]["options"]

    atoms = bulk("Cu") * (2, 2, 2)
    output = relax_job(atoms, relax_cell=True)
    assert output["nsites"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" in output["parameters"]["keywords"]
    assert "conv" not in output["parameters"]["keywords"]
    assert "gwolf" in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]

    output = relax_job(atoms, keywords={"gwolf": True})
    assert output["nsites"] == len(atoms)
    assert "gfnff" in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" not in output["parameters"]["keywords"]
    assert "conv" in output["parameters"]["keywords"]
    assert "gwolf" in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]

    output = relax_job(atoms, relax_cell=True, use_gfnff=False)
    assert output["nsites"] == len(atoms)
    assert "gfnff" not in output["parameters"]["keywords"]
    assert "opti" in output["parameters"]["keywords"]
    assert "conp" in output["parameters"]["keywords"]
    assert "conv" not in output["parameters"]["keywords"]
    assert "gwolf" not in output["parameters"]["keywords"]
    assert "dump every gulp.res" in output["parameters"]["options"]
    assert "output xyz gulp.xyz" not in output["parameters"]["options"]
    assert "output cif gulp.cif" in output["parameters"]["options"]
