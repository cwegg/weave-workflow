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


import argparse
import glob
import logging
import os
import re
import xml.dom.minidom
from collections import OrderedDict

import numpy as np
from astropy.io import fits

from workflow.utils.get_resources import (get_blank_xml_template,
                                          get_progtemp_file,
                                          get_obstemp_file)

from ifu.workflow.stage2.create_xml_files import _XMLFromFields
from ifu.workflow.utils.get_progtemp_info import get_obsmode_from_progtemp


class _MOSFieldCat(_XMLFromFields):
    """
    Convert the field data from anMOS  field center catalogue to a set of XMLs.

    This class provides code to take an MOS field center catalogue and convert
    it into XML fields.

    Parameters
    ----------
    filename : str
        A FITS file containing an MOS field centers produced by stage 1.
    """
    def __init__(self, filename):
        super().__init__(filename, mode='mos')

    def _generate_mos_xmls(self, mos_entry_list, xml_template, progtemp_dict,
                           obstemp_dict, output_dir='', prefix='',
                           suffix=''):

        output_file_list = []

        # How do you group bundles belonging to the same field?
        group_id = (
        'FIELD_NAME', 'PROGTEMP', 'OBSTEMP', 'FIELD_RA', 'FIELD_DEC')

        # Group the MOS entries per field

        fields_dict = OrderedDict()

        for mos_entry in mos_entry_list:

            key = tuple(mos_entry[col] for col in group_id)

            if key not in fields_dict.keys():
                fields_dict[key] = []

            fields_dict[key].append(mos_entry)

        # Group the targets in each field per OB

        ob_nested_list = []

        for key in fields_dict.keys():

            # Get the entries in the field
            field_entry_list = fields_dict[key]

            ob_nested_list.append(field_entry_list)


        # Proccess OB grouping
        logging.info('Processing {} MOS fields'.format(len(fields_dict)))

        for entry_group in ob_nested_list:
            # Make the OB name be part of the xml name
            thisprefix = entry_group[0]['FIELD_NAME']+'_'
            if prefix is not None:
                thisprefix = prefix+'_'+thisprefix
            output_file = self._process_ob(entry_group, xml_template,
                                           progtemp_dict, obstemp_dict,
                                           spatial_binning=1,
                                           output_dir=output_dir,
                                           prefix=thisprefix,
                                           suffix=suffix)

            output_file_list.append(output_file)

        return output_file_list



    def generate_xmls(self, xml_template, progtemp_file=None,
                      obstemp_file=None, output_dir='',
                      prefix='', suffix='', pass_datamver=False):

        # Get the DATAMVER of the XML template

        xml_template_dom = xml.dom.minidom.parse(xml_template)
        xml_datamver = xml_template_dom.childNodes[0].getAttribute('datamver')

        # Get the dictionaries to interpret PROGTEMP and OBSTEMP
        progtemp_dict = self._get_progtemp_dict(progtemp_file, pass_datamver)
        obstemp_dict = self._get_obstemp_dict(obstemp_file, pass_datamver)

        # Check DATAMVER of the IFU driver cat, the XML template, PROGTEMP file
        # and OBSTEMP file are consistent

        if self.datamver != xml_datamver:
            logging.critical(
                'DATAMVER mismatch ({} != {}) for XML template: '.format(
                    self.datamver, xml_datamver) +
                'Stop unless you are sure!')

            if pass_datamver == False:
                raise SystemExit(2)

        # Get the mos entries in case we have some fields with the wrong
        # progtemp

        mos_entry_list = []

        for i, entry in enumerate(self.data):

            progtemp = entry['PROGTEMP']

            try:
                obsmode = get_obsmode_from_progtemp(progtemp,
                                                    progtemp_dict=progtemp_dict)
            except:
                obsmode = None

            if obsmode == 'MOS':
                mos_entry_list.append(entry)
            else:
                logging.warning('unexpected PROGTEMP in row {}: {}'.format(
                    i + 1, progtemp))

        # Generate the  XMLs
        output_file_list = self._generate_mos_xmls(
            mos_entry_list, xml_template, progtemp_dict, obstemp_dict,
            output_dir=output_dir, prefix=prefix, suffix=suffix)

        return output_file_list


def create_xml_files(mos_field_list, output_dir, xml_template,
                     progtemp_file=None, obstemp_file=None,
                     prefix=None, suffix='',
                     pass_datamver=False, overwrite=False):
    """
    Create XML files with targets from an MOS field list fits file.

    Parameters
    ----------
    mos_field_list : str
        A FITS file containing a list of MOS field centers.
    output_dir : str
        Name of the directory which will contain the output XML files.
    xml_template : str
        A blank XML template to be populated with the information of the OBs.
    progtemp_file : str, optional
        A progtemp.dat file with the definition of PROGTEMP.
    obstemp_file : str, optional
        A obstemp.dat file with the definition of OBSTEMP.
    prefix : str, optional
        Prefix to be used in the output files (it will be derived from
        ifu_driver_cat_filename if None is provided).
    suffix : str, optional
        Suffix to be used in the output files.
    pass_datamver : bool, optional
        Continue even if DATAMVER mismatch is detected.
    overwrite : bool, optional
        Overwrite the output FITS file.

    Returns
    -------
    output_file_list : list of str
        A list with the output XML files.
    """

    # Check that the input IFU driver cat exists and is a file

    assert os.path.isfile(mos_field_list)

    # Create an object with the IFU driver cat

    mos_field_cat = _MOSFieldCat(mos_field_list)

    # Remove the previous files if overwriting has been requested

    if overwrite == True:
        mos_field_cat.remove_xmls(output_dir=output_dir, prefix=prefix,
                                   suffix=suffix)

    # Create the XML files

    output_file_list = mos_field_cat.generate_xmls(
        xml_template, progtemp_file=progtemp_file, obstemp_file=obstemp_file,
        output_dir=output_dir, prefix=prefix, suffix=suffix,
        pass_datamver=pass_datamver)

    return output_file_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Create XML files with targets from an MOS field list')

    parser.add_argument('mos_field_list',
                        help="""a FITS file containing an MOS fields""")

    parser.add_argument('--xml_template',
                        default=os.path.join('aux', 'BlankXMLTemplate.xml'),
                        help="""a blank XML template to be populated with the
                        information of the OBs""")

    parser.add_argument('--progtemp_file',
                        default=os.path.join('aux', 'progtemp.dat'),
                        help="""a progtemp.dat file with the definition of
                        PROGTEMP""")

    parser.add_argument('--obstemp_file',
                        default=os.path.join('aux', 'obstemp.dat'),
                        help="""a obstemp.dat file with the definition of
                        OBSTEMP""")

    parser.add_argument('--outdir', dest='output_dir', default='output',
                        help="""name of the directory which will containe the
                        output XML files""")

    parser.add_argument('--prefix', dest='prefix', default=None,
                        help="""prefix to be used in the output files (it will
                        be derived from ifu_driver_cat if non provided)""")

    parser.add_argument('--pass_datamver', dest='pass_datamver',
                        action='store_true',
                        help='continue even if DATAMVER mismatch is detected')

    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='overwrite the output files')

    parser.add_argument('--log_level', default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the level for the logging messages')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    if not os.path.exists(args.output_dir):
        logging.info('Creating the output directory')
        os.makedirs(args.output_dir)

    xml_template_dir = os.path.dirname(args.xml_template)
    if not os.path.exists(xml_template_dir):
        logging.info('Creating the directory of the blank XML template')
        os.makedirs(xml_template_dir)

    if not os.path.exists(args.xml_template):
        logging.info('Downloading the blank XML template')
        get_blank_xml_template(file_path=args.xml_template)

    if not os.path.exists(args.progtemp_file):
        logging.info('Downloading the progtemp file')
        get_progtemp_file(file_path=args.progtemp_file)

    if not os.path.exists(args.obstemp_file):
        logging.info('Downloading the obstemp file')
        get_obstemp_file(file_path=args.obstemp_file)

    create_xml_files(args.mos_field_list, args.output_dir, args.xml_template,
                     progtemp_file=args.progtemp_file,
                     obstemp_file=args.obstemp_file,
                     prefix=args.prefix, pass_datamver=args.pass_datamver,
                     overwrite=args.overwrite)

