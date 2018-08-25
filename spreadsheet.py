# -*- coding: utf-8 -*-

"""
AutoHunt.utils
"""

from gspread import authorize, exceptions
from gspread.models import Cell
from gspread.utils import *
from oauth2client.service_account import ServiceAccountCredentials
import logging
import unidecode
import time
import pandas as pd
import random
import datetime

from config import *
from format import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('AutoHunt.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def random_wait(time_range):
    time.sleep(random.uniform(time_range[0], time_range[1]))

def logprint(msg):
    print(msg)
    logger.info('%s', msg)

def safe_attr(dic, k):
    try:
        return dic[k]
    except KeyError:
        return ''

def safe_div(num, denum):
    if num == NOT_FOUND_ITEM or denum == NOT_FOUND_ITEM:
        return NOT_FOUND_ITEM
    num = str(num).replace('€', '').replace(' ', '')
    denum = str(denum)
    if num.isdigit() and denum.isdigit():
        num, denum = int(num), int(denum)
        if denum != 0:
            return int(num / denum)
    return NOT_FOUND_ITEM

def range_to_gridrange_object(range, worksheet_id):
    parts = range.split(':')
    start = parts[0]
    end = parts[1] if len(parts) > 1 else ''
    (row_offset, column_offset) = a1_to_rowcol(start)
    (last_row, last_column) = a1_to_rowcol(end) if end else (row_offset, column_offset)
    return {
        'sheetId': worksheet_id,
        'startRowIndex': row_offset-1,
        'endRowIndex': last_row,
        'startColumnIndex': column_offset-1,
        'endColumnIndex': last_column
    }

def format_range(worksheet, name, cell_format):
    """Update a range of :class:`Cell` objects to have the specified cell formatting.
    :param name: A string with range value in A1 notation, e.g. 'A1:A5'.
    :param cell_format: A models.CellFormat object.
    """
    body = {
        'requests': [{
            'repeatCell': {
                'range': range_to_gridrange_object(name, worksheet.id),
                'cell': { 'userEnteredFormat': cell_format.to_props() },
                'fields': ",".join(cell_format.affected_fields('userEnteredFormat'))
            }
        }]
    }
    return worksheet.spreadsheet.batch_update(body)

def open_spreadsheet(name_of_spreadsheet):
    """
    Open spreadsheet using its name in the Google Spreadsheet Console, and return its two worksheet : input and result
    It also adds a method to 'result' called 'format_range', which is not supported in gspread 3.0.1 yet.
    :param name_of_spreadsheet: The name of the main Google Spreadsheet
    :return: Input and Result worksheet
    """
    logprint("Opening of Spreadsheet {}...".format(name_of_spreadsheet))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('Apps Script Execution API Quic-0d5369b6757b.json', scope)
    try:
        gc = authorize(credentials)
        sheet_result = gc.open(name_of_spreadsheet).get_worksheet(1)
        sheet_input = gc.open(name_of_spreadsheet).get_worksheet(0)
        logprint("Opening of the Spreadsheet: OK")
    except exceptions.RequestError:
        logprint("Cannot open Google Spreadsheet. Retry one more time in 10 seconds to access it.")
        time.sleep(10)
        gc = authorize(credentials)
        sheet_result = gc.open(name_of_spreadsheet).get_worksheet(1)
        sheet_input = gc.open(name_of_spreadsheet).get_worksheet(0)
        logprint("Opening of the Spreadsheet: OK")
    setattr(sheet_result, 'format_range', format_range)
    return sheet_result, sheet_input

def order_with_boost(input_sheet_values, result_df):
    """
    Take into account the keywords from the input_sheet
    :param input_sheet_values: values already downloaded, to avoid making a second heavy HTTP call
    :param result_df: the Dataframe we need to boost / clean
    """
    keywords = {}
    for i in range(KEYWORDS_COL_NUMBERS):
        keywords = {**keywords, **{row[X_INDEX_KEYWORD + 2*i]: row[X_INDEX_KEYWORD + 2*i + 1] for row in
                    input_sheet_values if row[X_INDEX_KEYWORD + 2*i + 1] not in [NOT_FOUND_ITEM, NOT_BOOSTED_ITEM]}}

    x_list, xx_list, xxx_list = [], [], []
    for k, v in list(keywords.items()):
        # Boost keyword
        if v == 'x':
            x_list.append(unidecode.unidecode(k.lower().replace(':', '').replace('  ', '')))
        # Compulsory keyword
        if v == 'xx':
            xx_list.append(unidecode.unidecode(k.lower().replace(':', '').replace('  ', '')))
        # Trash keyword
        if v == 'xxx':
            xxx_list.append(unidecode.unidecode(k.lower().replace(':', '').replace('  ', '')))

    print('keywords : {0}\nx : {1}\nxx : {2}\nxxx : {3}'.format(keywords, x_list, xx_list, xxx_list))
    # Gathering the two columns with the potential keywords
    result_df['description_general_info'] = (result_df[results.description] + result_df[results.general_info]).apply(lambda x: (unidecode.unidecode(x.lower())))

    # Selecting only the rows including all the compulsory keywords
    result_df = result_df[
        result_df.description_general_info.apply(lambda sentence: all(word in sentence for word in xx_list))]

    # Dropping the rows including at least one trash keyword
    result_df = result_df[~result_df.description_general_info.str.contains('|'.join(xxx_list))]

    # Sorting rows including boost keywords on the top of the Dataframe to make them stand clear from the rest
    result_df['boost'] = pd.Series({i: 0 for i in range(result_df.shape[0])})

    def boost(cell):
        for elem in x_list:
            if elem in cell:
                return 1
        return 0

    result_df['boost'] = result_df['description_general_info'].apply(boost)
    result_df = result_df.sort_values(['boost'], ascending=False).drop(['boost', 'description_general_info'], axis=1)

    return result_df

def _cellrepr(value, allow_formulas):
    """
    Get a string representation of dataframe value.
    :param :value: the value to represent
    :param :allow_formulas: if True, allow values starting with '='
            to be interpreted as formulas; otherwise, escape
            them with an apostrophe to avoid formula interpretation.
    """
    if pd.isnull(value) is True:
        return ""
    if isinstance(value, float):
        value = repr(value)
    else:
        value = str(value)
    if (not allow_formulas) and value.startswith('='):
        value = "'%s" % value
    return value

def _resize_to_minimum(worksheet, rows=None, cols=None):
    """
    Resize the worksheet to guarantee a minimum size, either in rows,
    or columns, or both.
    Both rows and cols are optional.
    """
    # get the current size
    current_cols, current_rows = (
        worksheet.col_count,
        worksheet.row_count
        )
    if rows is not None and rows <= current_rows:
        rows = None
    if cols is not None and cols <= current_cols:
        cols = None

    if cols is not None or rows is not None:
        worksheet.resize(rows, cols)

def set_with_dataframe(worksheet,
                       dataframe,
                       row=1,
                       col=1,
                       include_index=False,
                       include_column_header=True,
                       resize=False,
                       allow_formulas=True):
    """
    Sets the values of a given DataFrame, anchoring its upper-left corner
    at (row, col). (Default is row 1, column 1.)
    :param worksheet: the gspread worksheet to set with content of DataFrame.
    :param dataframe: the DataFrame.
    :param include_index: if True, include the DataFrame's index as an
            additional column. Defaults to False.
    :param include_column_header: if True, add a header row before data with
            column names. (If include_index is True, the index's name will be
            used as its column's header.) Defaults to True.
    :param resize: if True, changes the worksheet's size to match the shape
            of the provided DataFrame. If False, worksheet will only be
            resized as necessary to contain the DataFrame contents.
            Defaults to False.
    :param allow_formulas: if True, interprets `=foo` as a formula in
            cell values; otherwise all text beginning with `=` is escaped
            to avoid its interpretation as a formula. Defaults to True.
    """
    # x_pos, y_pos refers to the position of data rows only,
    # excluding any header rows in the google sheet.
    # If header-related params are True, the values are adjusted
    # to allow space for the headers.
    y, x = dataframe.shape
    if include_index:
        col += 1
    if include_column_header:
        row += 1
    if resize:
        worksheet.resize(y + row - 1, x + col - 1)
    else:
        _resize_to_minimum(worksheet, y + row - 1, x + col - 1)

    updates = []

    if include_column_header:
        for idx, val in enumerate(dataframe.columns):
            updates.append(
                (row - 1,
                 col+idx,
                 _cellrepr(val, allow_formulas))
            )
    if include_index:
        for idx, val in enumerate(dataframe.index):
            updates.append(
                (idx+row,
                 col-1,
                 _cellrepr(val, allow_formulas))
            )
        if include_column_header:
            updates.append(
                (row-1,
                 col-1,
                 _cellrepr(dataframe.index.name, allow_formulas))
            )

    for y_idx, value_row in enumerate(dataframe.values):
        for x_idx, cell_value in enumerate(value_row):
            updates.append(
                (y_idx+row,
                 x_idx+col,
                 _cellrepr(cell_value, allow_formulas))
            )

    if not updates:
        logger.debug("No updates to perform on worksheet.")
        return

    cells_to_update = [ Cell(row=row, col=col, value=value) for row, col, value in updates ]
    logprint("{} cell updates to send".format(len(cells_to_update)))

    resp = worksheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
    logprint("Cell update response: {}".format(resp))

def clean_data(result_df):
    # clean general info and title from useless characters
    result_df[results.general_info] = result_df[results.general_info].apply(lambda x: str(x).replace('\t', '')
                                                                            .replace('<br>', '').replace('&nbsp;', ''))
    result_df[results.arrondissement] = result_df[results.title]
    result_df[results.saler_coord] = result_df[results.saler_coord].apply(lambda x: str(x).replace('\t', '').replace('\n', ''))

    # turn price into an int
    result_df[results.price] = result_df[results.price].apply(lambda x: str(x).replace('€', '').replace('&nbsp;', '')
                                                                            .replace('.', ''))\
                                                       .apply(lambda x: int(x) if x.isdigit() else x)
    # turn surface into an int
    result_df[results.surface] = result_df[results.surface].apply(lambda x: str(x).split('m')[0])\
                                                           .apply(lambda x: int(x) if x.isdigit() else x)

    # display image on Google Spreadsheet, size 16:9
    result_df[results.photo_url] = result_df[results.photo_url].apply(lambda x: '=IMAGE("{0}"; 4; 300; 534)'.format(x))

    # compute price per square meter
    result_df[results.price_per_sq] = result_df.apply(lambda row: safe_div(num=row[results.price],
                                                                           denum=row[results.surface]), axis=1)
    return result_df

def _get_style_body(result_sheet, params):
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": result_sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": params.col_start_index,
                        "endIndex": params.col_end_index
                    },
                    "properties": {
                        "pixelSize": params.col_pixel_size
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": result_sheet.id,
                        "dimension": "ROWS",
                        "startIndex": params.row_start_index,
                        "endIndex": params.row_end_index
                    },
                    "properties": {
                        "pixelSize": params.row_pixel_size
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }
    return body

def _set_style(result_sheet):
    """
    Define the size of rows and cols, and also the format of cells
    """
    image_body = _get_style_body(result_sheet, IMAGE_PARAMS)
    description_body = _get_style_body(result_sheet, IMAGE_PARAMS)
    general_info_body = _get_style_body(result_sheet, GENERALINFO_PARAMS)
    small_body = _get_style_body(result_sheet, SMALL_PARAMS)

    result_sheet.spreadsheet.batch_update(small_body)
    result_sheet.spreadsheet.batch_update(image_body)
    result_sheet.spreadsheet.batch_update(description_body)
    result_sheet.spreadsheet.batch_update(general_info_body)

    fmt_center = cellFormat(
        # backgroundColor=color(1, 0.9, 0.9),
        # textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
        wrapStrategy='WRAP',
        horizontalAlignment='CENTER'
    )
    fmt_left = cellFormat(
        # backgroundColor=color(1, 0.9, 0.9),
        # textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
        wrapStrategy='WRAP',
        horizontalAlignment='LEFT'
    )
    result_sheet.format_range(result_sheet, 'A2:Q100', fmt_center)
    result_sheet.format_range(result_sheet, 'M1:M100', fmt_left)

def export_result_to_spreadsheet(input_sheet_values, result_sheet, result_list):
    """
    Export the data inside result_list to result_sheet.
    Data is firstly transfered into a pandas DataFrame, before we iterate inside each of its row and col to create a
    Cell list to update and transmit it to the spreadsheet via a single HTTP call, so this method is super fast.

    :param result_sheet: the target google spreadsheet location for data
    :param result_list: the list of Result object containing the data to export
    :return: None, but fills the result_sheet
    """
    result_df = pd.DataFrame({results.photo_url: [], results.date_creation: [], results.price_per_sq: [], 'url':[],
                              'source': [], results.date_update: [], results.arrondissement: [], results.surface: [],
                              results.price: [], results.description: [], results.agency: [], results.saler_coord: [],
                              results.the_plus: [], results.general_info: [], results.inside: [], results.ref: []})

    # Create the final df
    for result in result_list:

        to_df = pd.DataFrame({'url': result.url, 'source': result.source, **result.info})
        result_df = pd.concat([result_df, to_df], ignore_index=True)

    print(result_df.head())

    # merge additional info together into general_info
    for attr in [results.general_info, results.inside, results.the_plus]:
        result_df[attr] = result_df[attr].apply(lambda x: x[0] if isinstance(x, list) else x)
    result_df[results.general_info] = result_df[results.general_info] + '\n' + result_df[results.the_plus] + '\n' + result_df[results.inside]
    result_df = result_df.drop([results.the_plus, results.inside], axis=1)

    # Clean the data in each cell
    result_df = clean_data(result_df)

    # Sort on date_creation in decreasing order
    result_df = result_df.sort_values([results.date_creation], ascending=False)

    # Boosts keywords value (must be the last sorting because the most important)
    result_df = order_with_boost(input_sheet_values, result_df)

    # Sorting the columns order
    columns = [results.photo_url, results.date_creation, results.price_per_sq, 'url', 'source', results.date_update,
               results.arrondissement, results.surface, results.price, results.description, results.agency,
               results.saler_coord, results.general_info, results.ref]
    result_df = result_df[columns]

    # Export this dataframe into a Google Spreadsheet
    set_with_dataframe(result_sheet, result_df)

    # Set style and cell format of the result_sheet
    _set_style(result_sheet)

def get_key(input_sheet_values):
    search_keys = {row[0]: row[1] for row in input_sheet_values if row[0] != '' and row[1] != ''}
    logprint('Search keys : {0}'.format(', '.join(['{0}: {1}'.format(k, v) for k, v in list(search_keys.items())])))
    return search_keys

def get_target_list():
    targets_list = [attr for attr in dir(targets) if not attr.startswith('__')]
    logprint('Targets List : {0}'.format(', '.join(targets_list)))
    return targets_list