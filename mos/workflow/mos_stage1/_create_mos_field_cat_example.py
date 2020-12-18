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

from mos.workflow.mos_stage1 import create_mos_field_cat


def set_keywords_info():
    trimester = '2020A1'
    author = 'a@domain.com'
    report_verbosity = 1
    cc_report = 'b@domain.com,c@domain.com'

    return trimester, author, report_verbosity, cc_report


def get_data_dict():
    data_dict = {}

    data_dict['TARGSRVY'] = ['GA-LRHIGHLAT']*2

    data_dict['FIELD_NAME'] = ['Spam','Eggs']

    data_dict['PROGTEMP'] = \
        ['13331', '11222.1+']

    data_dict['OBSTEMP'] = ['DACEB']*2

    data_dict['FIELD_RA'] = \
        [100.,200.]

    data_dict['FIELD_DEC'] = \
        [50.,50.]

    data_dict['MAX_FIBRES'] = \
        [1000, 1000]

    return data_dict


if __name__ == '__main__':

    ############################################################################
    # Set the location of the template and the output file and directory

    mos_field_template = os.path.join('aux', 'mos_field_template.fits')

    output_dir = 'output'
    output_filename = os.path.join(output_dir,
                                   'GA-LRHIGHLAT_2020A1-mos_field_cat.fits')

    ############################################################################
    # Create the output directory if it does not exist

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ############################################################################
    # Get a dictionary with the data which will populate the template

    # NOTE: See the above function get_data_dict to understand the structure of
    # the dictionary

    data_dict = get_data_dict()

    ############################################################################
    # Set the needed information to populate some keywords of the primary header

    trimester, author, report_verbosity, cc_report = set_keywords_info()

    ############################################################################
    # Create the IFU driver catalogue

    create_mos_field_cat(mos_field_template, data_dict, output_filename,
                          trimester, author, report_verbosity=report_verbosity,
                          cc_report=cc_report)

