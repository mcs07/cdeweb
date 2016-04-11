# -*- coding: utf-8 -*-
"""
cdeweb.api.representations
~~~~~~~~~~~~~~~~~~~~~~~~~~

API response formats.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from io import BytesIO
import logging

import dicttoxml
import pandas as pd
from flask import make_response, abort

from . import api


log = logging.getLogger(__name__)


@api.representation('application/xml')
def output_xml(data, code, headers):
    resp = make_response(dicttoxml.dicttoxml(data, attr_type=False, custom_root='job'), code)
    resp.headers.extend(headers)
    return resp


@api.representation('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
def output_xlsx(data, code, headers):
    print(data)
    if 'result' not in data:
        abort(400, 'Result not ready')

    bio = BytesIO()
    writer = pd.ExcelWriter(bio, engine='xlsxwriter')

    # Create sheets for compound identifiers
    data_view = []
    for result in data['result']:
        doc_id = result['biblio'].get('doi', result['biblio']['filename'])
        for compound_num, record in enumerate(result.get('records', [])):
            for name in record.get('names', []):
                data_view.append({'compound_id': compound_num, 'name': name, 'doc_id': doc_id})
    df = pd.DataFrame.from_records(data_view)
    df.to_excel(writer, sheet_name='compound_names', index=False)
    data_view = []
    for result in data['result']:
        doc_id = result['biblio'].get('doi', result['biblio']['filename'])
        for compound_num, record in enumerate(result.get('records', [])):
            for label in record.get('labels', []):
                data_view.append({'compound_id': compound_num, 'label': label, 'doc_id': doc_id})
    df = pd.DataFrame.from_records(data_view)
    df.to_excel(writer, sheet_name='compound_labels', index=False)

    # Create sheet for each spectrum/property type
    for prop_type in ['ir_spectra', 'nmr_spectra', 'uvvis_spectra', 'melting_points', 'electrochemical_potentials', 'fluorescence_lifetimes', 'quantum_yields']:
        data_view = []
        for result in data['result']:
            doc_id = result['biblio'].get('doi', result['biblio']['filename'])
            for compound_num, record in enumerate(result.get('records', [])):
                for prop_num, prop in enumerate(record.get(prop_type, [])):
                    if 'peaks' in prop:
                        for peak in prop['peaks']:
                            # Create row from peak value
                            row = copy.copy(peak)
                            # Add index numbers
                            row['doc_id'] = doc_id
                            row['compound_id'] = compound_num
                            row['compound_spectrum_id'] = prop_num
                            # Pull in parent values to row
                            if 'names' in record and record['names']:
                                    row['compound_name'] = record['names'][0]
                            for metaprop in prop:
                                if not metaprop == 'peaks':
                                    row[metaprop] = prop[metaprop]
                            data_view.append(row)
                    else:
                        # Create row from prop value
                        row = copy.copy(prop)
                        # Add index numbers
                        row['doc_id'] = doc_id
                        row['compound_id'] = compound_num
                        row['compound_property_id'] = prop_num
                        # Pull in parent values to row
                        if 'names' in record and record['names']:
                            row['compound_name'] = record['names'][0]
                        data_view.append(row)

        df = pd.DataFrame.from_records(data_view)
        df.to_excel(writer, sheet_name=prop_type, index=False)

    writer.book.close()
    bio.seek(0)
    resp = make_response(bio.read(), code)
    resp.headers.extend(headers)
    return resp
