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

from ifu.workflow.utils.classes import OBXML


def add_guide_and_calib_stars(xml_file_list,
                              output_dir,
                              num_calib_stars_request=None,
                              write_useful_tables=False,
                              overwrite=False,
                              max_radius=1.0):
    """
    Add guide and calib stars to XML files.
    
    Parameters
    ----------
    max_radius : float
    xml_file_list : list of str
        A list of input OB XML files.
    output_dir : str
        Name of the directory which will containe the output XML files.
    num_calib_stars_request : int, optional
        Maximum number of calib stars in the output. None means no limit.
    write_useful_tables : bool, optional
        Write tables with the potentially useful stars, i.e. those guide or
        calib stars available for the position of the location in the sky of
        each OB XML file.
    overwrite : bool, optional
        Overwrite the output FITS file.

    Returns
    -------
    output_file_list : list of str
        A list with the output XML files.
    """

    output_file_list = []

    xml_file_list.sort()

    for xml_file in xml_file_list:

        # Check that the input XML exists and is a file

        assert os.path.isfile(xml_file)

        # Choose the output filename depedending on the input filename

        input_basename_wo_ext = os.path.splitext(os.path.basename(xml_file))[0]

        if (input_basename_wo_ext.endswith('-t')
                or input_basename_wo_ext.endswith('-')):
            output_basename_wo_ext = input_basename_wo_ext + 'gc'
        else:
            output_basename_wo_ext = input_basename_wo_ext + '-gc'

        output_file = os.path.join(output_dir, output_basename_wo_ext + '.xml')
        guide_plot_filename = os.path.join(
            output_dir, output_basename_wo_ext + '-guide_stars.png')
        calib_plot_filename = os.path.join(
            output_dir, output_basename_wo_ext + '-calib_stars.png')

        if write_useful_tables is True:
            guide_useful_table_filename = os.path.join(
                output_dir,
                output_basename_wo_ext + '-useful_guide_stars.fits')
            calib_useful_table_filename = os.path.join(
                output_dir,
                output_basename_wo_ext + '-useful_calib_stars.fits')
        else:
            guide_useful_table_filename = None
            calib_useful_table_filename = None

        # Save the output filename for the result

        output_file_list.append(output_file)

        # If the output file already exists, delete it or continue with the next
        # one

        if os.path.exists(output_file):
            if overwrite == True:
                logging.info('Removing previous file: {}'.format(output_file))
                os.remove(output_file)

                for filename in [
                        guide_plot_filename, calib_plot_filename,
                        guide_useful_table_filename,
                        calib_useful_table_filename
                ]:
                    if (filename is not None) and os.path.exists(filename):
                        logging.info(
                            'Removing previous file: {}'.format(filename))
                        os.remove(filename)

            else:
                logging.info(
                    'Skipping file {} as its output already exists: {}'.format(
                        xml_file, output_file))
                continue

        # Read the input file, add the guide and calib stars and write it to the
        # output file

        ob_xml = OBXML(xml_file)

        ob_xml.add_guide_and_calib_stars(
            guide_plot_filename=guide_plot_filename,
            guide_useful_table_filename=guide_useful_table_filename,
            calib_plot_filename=calib_plot_filename,
            calib_useful_table_filename=calib_useful_table_filename,
            num_calib_stars_request=num_calib_stars_request,
            min_calib_cut=0,
            max_calib_cut=max_radius)

        ob_xml.write_xml(output_file)

    return output_file_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Add guide and calib stars to MOS XML files')

    parser.add_argument('xml_file',
                        nargs='+',
                        help="""an input OB XML file in MOS mode""")

    parser.add_argument('--outdir',
                        dest='output_dir',
                        default='output',
                        help="""name of the directory which will contain the
                        output XML files""")

    parser.add_argument('--num_calib_stars_request',
                        default=-1,
                        type=int,
                        help="""maximum number of calib stars in the output;
                        -1 means no limit""")

    parser.add_argument('--write_useful_tables',
                        action='store_true',
                        help="""write tables with the potentially useful stars,
                        i.e. those guide or calib stars available for the
                        position of the location in the sky of each OB XML
                        file""")

    parser.add_argument('--overwrite',
                        action='store_true',
                        help='overwrite the output files')

    parser.add_argument('--log_level',
                        default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the level for the logging messages')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    if not os.path.exists(args.output_dir):
        logging.info('Creating the output directory')
        os.mkdir(args.output_dir)

    if args.num_calib_stars_request != -1:
        num_calib_stars_request = args.num_calib_stars_request
        assert type(num_calib_stars_request) == int
    else:
        num_calib_stars_request = None

    add_guide_and_calib_stars(args.xml_file,
                              args.output_dir,
                              num_calib_stars_request=num_calib_stars_request,
                              write_useful_tables=args.write_useful_tables,
                              overwrite=args.overwrite)
