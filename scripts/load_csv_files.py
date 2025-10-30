"""
Imports Units from the Load Master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_units_from_csv.py
    ```
"""
from logging import getLogger, Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL
from pathlib import Path

import pandas
from pandas import DataFrame, read_csv, isnull, to_numeric, Series

# Set up logging
logger: Logger = getLogger(__name__)


def strip_dataframe_whitespace(dataframe: DataFrame):
    """
    Strips whitespace from all the text columns of a dataframe.

    :param dataframe: The dataframe to strip.
    :return: None, this is done in-place.
    """
    logger.info("Strip trailing whitespace")
    for column in dataframe.columns:
        if dataframe[column].dtype == 'object':
            dataframe[column] = dataframe[column].str.strip()

        dataframe[dataframe[column] == ''] = None


def convert_columns_to_ints(dataframe: DataFrame, columns: list[str]):
    """
    Converts a set of columns from floats/text/whatever into ints,
    and replaces any problems with 0.

    :param dataframe: The dataframe to convert.
    :param columns: The list of columns to work over.
    :return: None, this is done in-place.
    """
    for column in columns:
        dataframe[column] = to_numeric(dataframe[column], errors='coerce')
        dataframe[column] = dataframe[column].fillna(0)


def convert_percentage_columns_to_floats(dataframe: DataFrame, columns: list[str]):
    """
    Converts a set of columns from percentages (expressed as text or equations) into floats.

    :param dataframe: The dataframe to convert.
    :param columns: The list of columns to work over.
    :return: None, this is done in-place.
    """
    for column in columns:
        equation_rows = dataframe[column].str.contains('=').fillna(False)
        dataframe.loc[equation_rows, column] = dataframe.loc[equation_rows, column].str.lstrip('=').apply(pandas.eval)
        percentage_rows = dataframe[column].str.contains('%').fillna(False)
        dataframe.loc[percentage_rows, column] = dataframe.loc[percentage_rows, column].str.rstrip('%').astype('float')/100.0


def load_units_from_load_master_csv(
        path: Path
) -> DataFrame:
    """
    Loads the Units and their task rows from the Load Master tab of the spreadsheet

    DF keys are approached from the perspective of a `Unit` model.

    :param path: Path to the file to load. Should be the 'load master' tab of the CSV,
        but cut to only the rows with units.
    :return: The data.
    """
    logger.info(f"Importing unit tasks from: {path}")

    # Read the unit task CSV.
    dataframe: DataFrame = read_csv(path, header=0, index_col=False)
    dataframe.rename(
        columns={
            'Deputy /Assessors etc': 'hours_fixed_deputy',
            'Number of Synoptic lectures': 'synoptic_lectures',
            'Number of Lectures/Problems Classes Run by Coordinator': 'lectures',
            'Coursework (number of items prepared)': 'coursework',
            'Coursework (fraction of module mark)': 'coursework_mark_fraction',
            'Fraction of Courseowork marked by coordinator': 'task__coursework_fraction',
            'Examination (fraction of module mark)': 'exam_mark_fraction',
            'Fraction of Examination marked by coordinator': 'task__exam_fraction',
            'Total Number of CATS': 'credits',
            'Task Description': 'task__name',
            'Number of Students': 'students',
            'Description/Unit title': 'unit_name',
            'Task Category/Unit Code': 'code',
            dataframe.columns[17]: 'notes'
        },
        inplace=True,
    )

    strip_dataframe_whitespace(dataframe)

    logger.info("Convert raw numbers columns to ints")
    convert_columns_to_ints(
        dataframe,
        ['hours_fixed_deputy', 'synoptic_lectures', 'coursework', 'credits', 'students', 'lectures']
    )

    logger.info("Convert fraction columns to floats")
    convert_percentage_columns_to_floats(
        dataframe,
        ['exam_mark_fraction', 'coursework_mark_fraction', 'task__coursework_fraction', 'task__exam_fraction']
    )
    return dataframe


def load_nonunit_tasks_from_load_master_csv(
        path: Path,
) -> DataFrame:
    """
    Loads non-unit tasks from the Load Master tab of the spreadsheet

    Note: More prep is required for this one. The notes all need to be consolidated into a single column, titled 'Notes'.
    The group column needs to be named 'Group'.
    DF keys are approached from the perspective of a `Task` model.

    :param path: Path to the file to load. Should be the 'load master' tab of the CSV,
        but cut to only the rows with non-unit tasks.
    :return: The data.
    """
    logger.info(f"Importing non-unit tasks from: {path}")


    # Read the unit task CSV.
    dataframe: DataFrame = read_csv(path, header=0, index_col=False)
    dataframe.rename(
        columns={
            'Unit co-ord load': 'load_fixed',
            'lst time unit co-ord load': 'load_fixed_first',
            'Group': 'group',
            'Description/Unit title': 'name',
            'Notes': 'notes',
        },
        inplace=True,
    )

    logger.info("Strip trailing whitespace")
    strip_dataframe_whitespace(dataframe)

    logger.info("Convert raw numbers columns to ints")
    convert_columns_to_ints(
        dataframe,
        ['load_fixed', 'load_fixed_first']
    )

    def convert_load_fixed_first(row: Series):
        """
        The first-time load column can be either an offset (e.g. +15 hours) *or* a flat value (e.g. 115 hours).

        :param row: A row from the dataframe.
        :return: The first-time task offset, or None if none.
        """
        if not row['load_fixed_first']:
            return None
        elif row['load_fixed'] == row['load_fixed_first']:
            return None
        elif row['load_fixed_first'] > row['load_fixed']:
            return row['load_fixed_first'] - row['load_fixed']
        else:
            return row['load_fixed_first']

    logger.info("Standardising fixed load first-time adjustment column")
    dataframe['load_fixed_first'] = dataframe.apply(convert_load_fixed_first)

    logger.info("Converting unit codes")
    dataframe['group'] = dataframe.apply(lambda row: row['group'][0] if row['group'] else None)
    return dataframe


def load_tasks_from_staff_contract_csv(path: Path) -> DataFrame:
    """

    :param path:
    :return:
    """
    dataframe: DataFrame = read_csv(path, header=0, index_col=False)
    dataframe.rename(
        columns={
            'STAFF': 'staff_name',
            'TASK CAT/UNIT CODE': 'code',
            'TASK DETAIL': 'task_name',
        },
        inplace=True
    )

    strip_dataframe_whitespace(dataframe)
    return dataframe
