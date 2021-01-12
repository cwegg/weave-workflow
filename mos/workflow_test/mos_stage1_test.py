#!/usr/bin/env python3

#
# Copyright (C) 2020 Cambridge Astronomical Survey Unit
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.
#

import os
import subprocess

import pytest

import ifu.workflow
import mos.workflow.mos_stage1


@pytest.fixture(scope='module')
def mos_field_template(master_cat, tmpdir_factory):
    file_path = str(
        tmpdir_factory.mktemp('aux').join('mos_field_template.fits'))

    mos.workflow.mos_stage1.create_mos_field_template(master_cat, file_path)

    assert os.path.exists(file_path)

    return file_path


def test_fitscheck_mos_field_template(mos_field_template):
    returncode = subprocess.call(['fitscheck', mos_field_template])

    assert returncode == 0


def test_fitsdiff_mos_field_template(mos_field_template,
                                     pkg_mos_field_template):
    returncode = subprocess.call([
        'fitsdiff', '-k', 'CHECKSUM,DATASUM', mos_field_template,
        pkg_mos_field_template
    ])

    assert returncode == 0


@pytest.fixture(scope='module')
def mos_field_cat(mos_field_template, tmpdir_factory):
    file_path = str(tmpdir_factory.mktemp('output').join('mos_field_cat.fits'))

    data_dict = mos.workflow.mos_stage1._get_data_dict_for_example()

    trimester, author, report_verbosity, cc_report = \
        mos.workflow.mos_stage1._set_keywords_info_for_example()

    mos.workflow.mos_stage1.create_mos_field_cat(
        mos_field_template,
        data_dict,
        file_path,
        trimester,
        author,
        report_verbosity=report_verbosity,
        cc_report=cc_report)

    assert os.path.exists(file_path)

    return file_path


def test_fitscheck_mos_field_cat(mos_field_cat):
    returncode = subprocess.call(['fitscheck', mos_field_cat])

    assert returncode == 0


def test_fitsdiff_mos_field_cat(mos_field_cat, pkg_mos_field_cat):
    returncode = subprocess.call([
        'fitsdiff', '-k', 'CHECKSUM,DATASUM,DATETIME', mos_field_cat,
        pkg_mos_field_cat
    ])

    assert returncode == 0
