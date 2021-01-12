import pytest
import subprocess
import os.path

import mos.workflow.mos_stage3


@pytest.fixture(scope='module')
def mos_target_cat(mos_target_template, tmpdir_factory):
    file_path = str(tmpdir_factory.mktemp('output').join('mos_field_cat.fits'))

    data_dict = mos.workflow.mos_stage3._get_data_dict_for_example(
        mos_target_template)

    trimester, author, report_verbosity, cc_report = \
        mos.workflow.mos_stage3._set_keywords_info_for_example()

    mos.workflow.mos_stage3.create_mos_target_cat(
        mos_target_template,
        data_dict,
        file_path,
        trimester,
        author,
        report_verbosity=report_verbosity,
        cc_report=cc_report)

    assert os.path.exists(file_path)

    return file_path


def test_fitscheck_mos_target_cat(mos_target_cat):
    returncode = subprocess.call(['fitscheck', mos_target_cat])

    assert returncode == 0


def test_fitsdiff_mos_field_cat(mos_target_cat, pkg_mos_target_cat):
    returncode = subprocess.call([
        'fitsdiff', '-k', 'CHECKSUM,DATASUM,DATETIME', mos_target_cat,
        pkg_mos_target_cat
    ])

    assert returncode == 0


@pytest.fixture(scope='module')
def mos_t_xml_files(pkg_mos_xml_files, mos_target_cat, tmpdir_factory):
    output_dir = str(tmpdir_factory.mktemp('output'))

    xml_filename_list = mos.workflow.mos_stage3.add_targets(pkg_mos_xml_files,
                                                            mos_target_cat,
                                                            output_dir,
                                                            clean_targets=True)

    return xml_filename_list


def test_diff_t_xml_files(mos_t_xml_files, pkg_mos_t_xml_files):
    assert len(mos_t_xml_files) == len(pkg_mos_t_xml_files)

    mos_t_xml_files.sort(key=os.path.basename)
    pkg_mos_t_xml_files.sort(key=os.path.basename)

    for ref_file, copy_file in zip(mos_t_xml_files, pkg_mos_t_xml_files):
        assert os.path.basename(ref_file) == os.path.basename(copy_file)

        returncode = subprocess.call(['diff', '-q', ref_file, copy_file])

        assert returncode == 0
