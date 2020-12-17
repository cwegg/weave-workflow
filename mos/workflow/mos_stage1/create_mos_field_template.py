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

# Code mostly from ifu/stage1/create_ifu_driver_cat.py

# We create a new field list fits file based on the SPA template. This is so
# that the format of the SPA columns is correct, and can easily be updated.
# We have to add one extra column that isn't in the templates - a MAX_FIBRES
# column, since when surveys share, this can be field dependent.

import argparse
import collections
import logging
import os.path

from astropy.io import fits as _fits
import datetime as _datetime

from ifu.workflow.utils import create_sub_template
from ifu.workflow.utils.get_resources import get_master_cat


def _add_column_to_fits_template(template, column, update_datetime=False,
                                 checksum=True):
    """
    Add a column in-place to a fits file.

    Parameters
    ----------
    template : str
        Any catalogue template containing the SPA columns.
    update_datetime : bool, optional
        Update DATETIME keyword in the new MOS field template.
    """

    # Read the catalogue template
    hdulist = _fits.open(template)
    primary_hdr = hdulist[0].header
    template_hdu = hdulist[1]

    # Update the keyword DATETIME if requested (and it exists)
    if (update_datetime is True) and ('DATETIME' in primary_hdr.keys()):
        datetime_str = _datetime.datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        primary_hdr['DATETIME'] = datetime_str

    hdu = _fits.BinTableHDU.from_columns(template_hdu.columns + column)

    # Create the primary HDU
    primary_hdu = _fits.PrimaryHDU(header=primary_hdr)

    # Create a HDU list and save it to a file
    hdulist = _fits.HDUList([primary_hdu, hdu])

    hdulist.writeto(template, checksum=checksum, overwrite=True)


def create_mos_field_template(catalogue_template, output_filename,
                              update_datetime=False, overwrite=False):
    """
    Create a template for the IFU driver catalogues.

    Parameters
    ----------
    catalogue_template : str
        Any catalogue template containing the SPA columns.
    output_filename : str
        The name of the output file for the new IFU driver template.
    update_datetime : bool, optional
        Update DATETIME keyword in the new IFU driver template.
    overwrite : bool, optional
        Overwrite the output FITS file containing the MOS field template.
    """

    # Set the list of columns which will be added to the table

    col_list = ['TARGSRVY', 'PROGTEMP', 'OBSTEMP', 'GAIA_RA', 'GAIA_DEC']

    # Set the extension name

    extname = 'MOS FIELD LIST'

    # Choose the keywords which will be inherited from the catalogue template

    inherited_kwds = ['DATAMVER', 'TRIMESTE', 'DATETIME']

    # Set the information of the new keywords that will be added

    new_primary_kwds = collections.OrderedDict()
    new_primary_kwds['VERBOSE'] = \
        (1, 'Attribute "report_verbosity" of the XML files')
    new_primary_kwds['AUTHOR'] = ('', None)
    new_primary_kwds['CCREPORT'] = ('', None)

    # Create a dictionary to renaming the columns - this is ugly,
    # particularly stealing the IFU_DITHER to use as MAX_FIBRES

    rename_col_dict = {'GAIA_RA': 'FIELD_RA',
                       'GAIA_DEC': 'FIELD_DEC'}

    # Create the sub-template with the above parameters

    create_sub_template(catalogue_template, output_filename, col_list,
                        extname=extname, inherit_primary_kwds=False,
                        inherited_kwds=inherited_kwds,
                        new_primary_kwds=new_primary_kwds,
                        rename_col_dict=rename_col_dict,
                        update_datetime=update_datetime, overwrite=overwrite)

    # Add the MAX_FIBRES column - This won't look like a SPA column,
    # but  since there is no UCD etc. then this is anyway inevitable
    column = _fits.Column(name='MAX_FIBRES', format='I', null=0,
                          disp='I3')
    _add_column_to_fits_template(output_filename, column,
                                 update_datetime=update_datetime, checksum=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Create a template for the MOS driver catalogues')

    parser.add_argument('--in', dest='catalogue_template',
                        default=os.path.join('aux',
                                             'Master_CatalogueTemplate.fits'),
                        help="""name of catalogue template containing the SPA
                        columns""")

    parser.add_argument('--out', dest='mos_field_template',
                        default=os.path.join('aux', 'mos_field_template.fits'),
                        help="""name for the output file which will contain the
                        new template for the MOS field center catalogues""")

    parser.add_argument('--update_datetime', action='store_true',
                        help="""update DATETIME keyword from the catalogue
                        template""")

    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite the output file')

    parser.add_argument('--log_level', default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the level for the logging messages')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    if not os.path.exists(args.catalogue_template):
        logging.info('Downloading the master catalogue template')
        get_master_cat(file_path=args.catalogue_template)

    create_mos_field_template(args.catalogue_template,
                              args.mos_field_template,
                              update_datetime=args.update_datetime,
                              overwrite=args.overwrite)
