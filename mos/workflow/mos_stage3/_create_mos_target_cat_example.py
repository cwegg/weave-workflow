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
import numpy as np
from astropy.io import fits

from ifu.workflow.utils import populate_fits_table_template


def set_keywords_info():
    trimester = '2020A1'
    author = 'a@domain.com'
    report_verbosity = 1
    cc_report = 'b@domain.com,c@domain.com'

    return trimester, author, report_verbosity, cc_report


def get_data_dict(catalogue_template):
    # Fot testing put 10 targets in two different fields
    data_dict = {}

    fields = 2
    targets_per_field = 10
    catalogue_length = targets_per_field*fields

    data_dict['TARGSRVY'] = ['GA-LRHIGHLAT']*catalogue_length
    data_dict['TARGCAT'] = ['GA-LRHIGHLAT_2020A1']*catalogue_length
    data_dict['TARGPROG'] = ['POI|EMP']*targets_per_field + \
                            ['POI|BHB']*targets_per_field
    data_dict['TARGID'] = np.arange(catalogue_length)
    data_dict['TARGNAME'] = ['']*catalogue_length
    data_dict['TARGUSE'] = (['T']*9 + ['S'])*2
    data_dict['TARGCLASS'] = ['STAR']*catalogue_length

    data_dict['TARGPRIO'] = ([10.0]*2 + [1.0]*(targets_per_field-2))*2

    data_dict['PROGTEMP'] = ['13331']*targets_per_field + \
                            ['11222.1+']*targets_per_field

    data_dict['OBSTEMP'] = ['DACEB']*catalogue_length


    # For testing place 10 targets in a line at constant dec
    data_dict['GAIA_RA'] = np.append(np.linspace(-0.55,0.45,targets_per_field)+100,
                                     np.linspace(-0.55,0.45,targets_per_field)+200)

    data_dict['GAIA_DEC'] = [50.0]*catalogue_length
    data_dict['GAIA_ID'] = ['']*catalogue_length
    data_dict['GAIA_DR'] = ['']*catalogue_length
    data_dict['GAIA_EPOCH'] = [2015.5]*catalogue_length
    data_dict['GAIA_PMRA'] = [0.0]*catalogue_length
    data_dict['GAIA_PMRA_ERR'] = [0.0]*catalogue_length
    data_dict['GAIA_PMDEC'] = [0.0]*catalogue_length
    data_dict['GAIA_PMDEC_ERR'] = [0.0]*catalogue_length
    data_dict['GAIA_PARAL'] = [0.0]*catalogue_length
    data_dict['GAIA_PARAL_ERR'] = [0.0]*catalogue_length


    # Add photometry elements
    data_dict['MAG_G'] = np.arange(catalogue_length)*0.5 + 10
    data_dict['MAG_G_ERR'] = [0.1]*catalogue_length
    data_dict['MAG_R'] = np.arange(catalogue_length)*0.5 + 11
    data_dict['MAG_R_ERR'] = [0.1]*catalogue_length

    # Fill up other columns with their null or meaningless values
    with fits.open(catalogue_template) as hdul:
        for column in hdul[1].columns:
            if column.name not in data_dict:
                if column.null is not None:
                    data_dict[column.name] = [column.null] * catalogue_length
                else:
                    if 'A' in column.format:
                        data_dict[column.name] = [''] * catalogue_length
                    elif ('E' in column.format) or ('D' in column.format):
                        data_dict[column.name] = [0.0] * catalogue_length
                    elif 'I' in column.format:
                        data_dict[column.name] = [0] * catalogue_length

    return data_dict


def create_mos_target_cat(catalogue_template, data_dict, output_filename,
                          trimester, author, report_verbosity=1, cc_report='',
                          overwrite=False):
    """
    Create a IFU driver catalogue using a template and the needed information.

    Parameters
    ----------
    template : str
        A FITS file containing a catalogue template.
    data_dict : dict
        A dictionary with the information needed to populate the columns of the
        IFU driver template. The keys of the dictionary should be the column
        names, while their values should be list or array-like objects with the
        information of each column.
    output_filename : str
        The name of the output file for the new IFU driver catalogue.
    trimester : str
        The trimester of the catalogue (e.g. 2020A1).
    author : str
        The email address of the author of the catalogue.
    report_verbosity : {0, 1}, optional
        The level of verbosity which will be inherited in the files to be
        submitted to WASP.
    cc_report : str, optional
        A comma separated list of email addresses to be CC'ed in WASP
        submisions.
    overwrite : bool, optional
        Overwrite the output FITS file containing the IFU driver catalogue.

    Returns
    -------
    output_filename : str
        The name of the output file for the new target catalogue.
    """

    assert report_verbosity in [0, 1]

    primary_kwds = {'TRIMESTE': trimester, 'VERBOSE': report_verbosity,
                    'AUTHOR': author, 'CCREPORT': cc_report}

    populate_fits_table_template(catalogue_template, data_dict,
                                 output_filename, primary_kwds=primary_kwds,
                                 update_datetime=True, overwrite=overwrite)

    return output_filename


if __name__ == '__main__':

    ############################################################################
    # Set the location of the template and the output file and directory

    catalogue_template = os.path.join('aux',
                                      'GA-LRHIGHLAT_CatalogueTemplate.fits')

    output_dir = 'input'
    output_filename = os.path.join(output_dir,
                                   'GA-LRHIGHLAT_2020A1.fits')

    ############################################################################
    # Create the output directory if it does not exist

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ############################################################################
    # Get a dictionary with the data which will populate the template

    # NOTE: See the above function get_data_dict to understand the structure of
    # the dictionary

    data_dict = get_data_dict(catalogue_template)

    ############################################################################
    # Set the needed information to populate some keywords of the primary header

    trimester, author, report_verbosity, cc_report = set_keywords_info()

    ############################################################################
    # Create the IFU driver catalogue

    create_mos_target_cat(catalogue_template, data_dict, output_filename,
                         trimester, author, report_verbosity=report_verbosity,
                         cc_report=cc_report)
