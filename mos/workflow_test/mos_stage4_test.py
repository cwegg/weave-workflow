import pytest
import subprocess
import os.path
import mos.workflow.mos_stage4


@pytest.fixture(scope='module')
def mos_tgc_xml_files(pkg_mos_t_xml_files, tmpdir_factory):
    output_dir = str(tmpdir_factory.mktemp('output'))

    xml_filename_list = mos.workflow.mos_stage4.add_guide_and_calib_stars(
        pkg_mos_t_xml_files, output_dir)

    return xml_filename_list


def test_diff_tgc_xml_files(mos_tgc_xml_files, pkg_mos_tgc_xml_files):
    assert len(mos_tgc_xml_files) == len(pkg_mos_tgc_xml_files)

    mos_tgc_xml_files.sort(key=os.path.basename)
    pkg_mos_tgc_xml_files.sort(key=os.path.basename)

    for ref_file, copy_file in zip(mos_tgc_xml_files, pkg_mos_tgc_xml_files):
        assert os.path.basename(ref_file) == os.path.basename(copy_file)

        returncode = subprocess.call(['diff', '-q', ref_file, copy_file])

        assert returncode == 0
