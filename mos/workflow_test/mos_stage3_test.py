import pytest
import subprocess
import os.path

import mos.workflow.mos_stage3

@pytest.fixture(scope='module')
def mos_target_cat(mos_target_template, tmpdir_factory):
    file_path = str(tmpdir_factory.mktemp('output').join(
        'mos_field_cat.fits'))

    data_dict = mos.workflow.mos_stage3._get_data_dict_for_example(
        mos_target_template)

    trimester, author, report_verbosity, cc_report = \
        mos.workflow.mos_stage3._set_keywords_info_for_example()

    mos.workflow.mos_stage3.create_mos_target_cat(mos_target_template, data_dict,
                                          file_path, trimester, author,
                                          report_verbosity=report_verbosity,
                                          cc_report=cc_report)

    assert os.path.exists(file_path)

    return file_path


def test_fitscheck_mos_target_cat(mos_target_cat):
    returncode = subprocess.call(['fitscheck', mos_target_cat])

    assert returncode == 0


def test_fitsdiff_mos_field_cat(mos_target_cat, pkg_mos_target_cat):
    returncode = subprocess.call(
        ['fitsdiff', '-k', 'CHECKSUM,DATASUM,DATETIME',
         mos_target_cat, pkg_mos_target_cat])

    assert returncode == 0