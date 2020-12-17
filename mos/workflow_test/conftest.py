import pytest
import os.path
import pathlib
import mos.workflow

# Reuse fixtures from IFU tests
pytest_plugins = [
    "ifu.workflow_test.conftest",
]


# Then add all fixtures that need changing for MOS

@pytest.fixture(scope='session')
def pkg_mos_field_template():
    pkg_file_path = str(pathlib.Path(mos.workflow.__path__[0]) / 'mos_stage1' /
                        'aux' /
                        'mos_field_template.fits')

    assert os.path.exists(pkg_file_path)

    return pkg_file_path


@pytest.fixture(scope='session')
def pkg_mos_field_cat():
    pkg_file_path = str(pathlib.Path(mos.workflow.__path__[0]) / 'mos_stage2' /
                        'input' / 'GA-LRHIGHLAT_2020A1-mos_field_cat.fits')

    assert os.path.exists(pkg_file_path)

    return pkg_file_path
