import pytest
import os.path
import subprocess
import mos.workflow.mos_stage2

@pytest.fixture(scope='module')
def mos_xml_files(pkg_mos_field_cat, blank_xml_template, progtemp_file,
                obstemp_file, tmpdir_factory):
    output_dir = str(tmpdir_factory.mktemp('output'))

    xml_filename_list = mos.workflow.mos_stage2.create_xml_files(
        pkg_mos_field_cat, output_dir, blank_xml_template,
        progtemp_file=progtemp_file, obstemp_file=obstemp_file)

    return xml_filename_list


def test_diff_xml_files(mos_xml_files, pkg_mos_xml_files):
    assert len(mos_xml_files) == len(pkg_mos_xml_files)

    mos_xml_files.sort(key=os.path.basename)
    pkg_mos_xml_files.sort(key=os.path.basename)

    for ref_file, copy_file in zip(mos_xml_files, pkg_mos_xml_files):
        assert os.path.basename(ref_file) == os.path.basename(copy_file)

        returncode = subprocess.call(['diff', '-q', ref_file, copy_file])

        assert returncode == 0

