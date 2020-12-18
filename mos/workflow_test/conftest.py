import os.path
import pathlib
import pytest
import glob

import mos.workflow

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


@pytest.fixture(scope='session')
def pkg_mos_t_xml_files():
    xml_files_pattern = str(pathlib.Path(mos.workflow.__path__[0]) /
                            'mos_stage3' /
                            'input' / '*-t.xml')

    xml_filename_list = glob.glob(xml_files_pattern)
    xml_filename_list.sort()

    assert len(xml_filename_list) > 0

    for xml_filename in xml_filename_list:
        assert os.path.exists(xml_filename)

    return xml_filename_list
