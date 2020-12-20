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
import logging
import os
import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord

from ifu.workflow.utils.classes import OBXML


def clean_xml_targets(ob_xml):
    # Remove any template targets
    for field in ob_xml.fields.getElementsByTagName('field'):
        for target in field.getElementsByTagName('target'):
            if target.getAttribute('targsrvy') == '%%%':
                field.removeChild(target)

def add_targets(
        xml_file_list, target_cat, output_dir, max_radius=1.0,
        clean_targets=True, overwrite=False):
    """
    Add guide and calib stars to XML files.

    Parameters
    ----------
    xml_file_list : list of str
        A list of input OB XML files.
    target_cat :  str
        The filename of the catalogue to be added
    output_dir : str
        Name of the directory which will containe the output XML files.
    max_radius : float
        The maxium radius from the field center to add.
    clean_targets : bool, optional
        Remove template targets from the XML.
    overwrite : bool, optional
        Overwrite the output FITS file.

    Returns
    -------
    output_file_list : list of str
        A list with the output XML files.
    """

    output_file_list = []

    xml_file_list.sort()

    # Load our catalogue and compute coordinates since this is common to all
    # fields
    catalogue = Table.read(target_cat)
    catalogue_coords = SkyCoord(ra=catalogue['GAIA_RA'],dec=catalogue[
        'GAIA_DEC'], unit='deg')

    for xml_file in xml_file_list:

        # Check that the input XML exists and is a file

        assert os.path.isfile(xml_file)

        # Choose the output filename depedending on the input filename

        input_basename_wo_ext = os.path.splitext(os.path.basename(xml_file))[0]

        if (input_basename_wo_ext.endswith('-t') or
                input_basename_wo_ext.endswith('-')):
            output_basename_wo_ext = input_basename_wo_ext + 't'
        else:
            output_basename_wo_ext = input_basename_wo_ext + '-t'

        output_file = os.path.join(output_dir, output_basename_wo_ext + '.xml')

        # Save the output filename for the result

        output_file_list.append(output_file)

        # If the output file already exists, delete it or continue with the next
        # one

        if os.path.exists(output_file):
            if overwrite == True:
                logging.info('Removing previous file: {}'.format(output_file))
                os.remove(output_file)
            else:
                logging.info(
                    'Skipping file {} as its output already exists: {}'.format(
                        xml_file, output_file))
                continue

        # Read the input file, add the guide and calib stars and write it to the
        # output file

        ob_xml = OBXML(xml_file)

        # First find rows where TARGSRVY, PROGTEMP, OBSTEMP match since these
        # are the only potential targets
        # Let's start creating a mask without any filter

        mask = np.zeros(len(catalogue), dtype=bool)
        # Add to the mask only those targets whose TARGSRVY is in the surveys
        # element
        for element in ob_xml.surveys.getElementsByTagName('survey'):
            mask += (catalogue['TARGSRVY'] == element.getAttribute('name'))


        # Filter FITS data comparing the values of the column OBSTEMP with the
        # obstemp attribute of the XML

        obstemp = ob_xml._get_obstemp()
        mask *= (catalogue['OBSTEMP'] == obstemp)

        # Filter FITS data comparing the values of the column PROGTEMP with the
        # progtemp attribute of the XML

        progtemp = ob_xml._get_progtemp()
        #mask *= (catalogue['PROGTEMP'] == progtemp) TODO we should filter on
        # this when Sergey updates progtemp

        # Then find targets that are inside the fov
        field = ob_xml.fields.getElementsByTagName('field')[0]
        field_ra = field.getAttribute('RA_d')
        field_dec = field.getAttribute('Dec_d')
        field_center_coords = SkyCoord(ra=field_ra, dec=field_dec,unit='deg')

        offset = field_center_coords.separation(catalogue_coords[mask]).deg
        mask[mask] *= (offset <= max_radius)
        logging.info('Catalogue: {} Found {} targets for '
                     '{}'.format(target_cat, mask.sum(), xml_file))

        # And finally add them
        ob_xml._add_table_as_targets(catalogue[mask])

        if clean_targets:
            clean_xml_targets(ob_xml)

        ob_xml.write_xml(output_file)

    return output_file_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Add guide and calib stars to XML files')

    parser.add_argument('target_cat',
                        help="""A catalogue containing targets""")

    parser.add_argument('xml_file', nargs='+',
                        help="""one or more input OB XML files""")

    parser.add_argument('--outdir', dest='output_dir', default='output',
                        help="""name of the directory which will contain the
                        output XML files""")

    parser.add_argument('--max_radius', default=1.0, type=float,
                        help="""Add targets within these degrees of the 
                        field center""")

    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite the output files')

    parser.add_argument('--clean', action='store_true',
                        help="""remove any template targets (should be 
                        called when adding the last catalogue)""")

    parser.add_argument('--log_level', default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the level for the logging messages')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    if not os.path.exists(args.output_dir):
        logging.info('Creating the output directory')
        os.mkdir(args.output_dir)

    add_targets(xml_file_list=args.xml_file, target_cat=args.target_cat,
                output_dir=args.output_dir, max_radius=args.max_radius,
                clean_targets=args.clean,
                overwrite=args.overwrite)


