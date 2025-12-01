"""
Utility functions for loading CSV and XLSX files.
"""

from argparse import ArgumentTypeError
from logging import Logger, getLogger
from json import dumps
from pathlib import Path

import pandas
from pandas import DataFrame, Series, read_csv, to_numeric, read_excel, isna, concat

# Set up logging
logger: Logger = getLogger(__name__)


def csv_file_only(param: str) -> Path:
    """
    Takes a path and makes sure it's a CSV file.

    :param param: The string input parameter.
    :raises ArgumentTypeError: If it's not a CSV file.
    :return: That string as a file path.
    """
    path: Path = Path(param)
    if path.suffix.lower() != ".csv":
        raise ArgumentTypeError(f"File must have a csv extension. Extension is: {path.suffix}")

    return path


def xlsx_file_only(param: str) -> Path:
    """
    Takes a path and makes sure it's a CSV file.

    :param param: The string input parameter.
    :raises ArgumentTypeError: If it's not a CSV file.
    :return: That string as a file path.
    """
    path: Path = Path(param)
    if path.suffix.lower() != ".xlsx":
        raise ArgumentTypeError(f"File must have an xlsx extension. Extension is: {path.suffix}")

    return path


def strip_dataframe_whitespace(dataframe: DataFrame):
    """
    Strips whitespace from all the text columns of a dataframe.

    :param dataframe: The dataframe to strip.
    :return: None, this is done in-place.
    """
    def parse_object(x: object) -> object:
        if isinstance(x, str):
            return str.strip(x)
        else:
            return x

    logger.info("Strip trailing whitespace")
    for column in dataframe.columns:
        if dataframe[column].dtype in ['object', 'str']:
            dataframe[column] = dataframe[column].apply(parse_object)

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
        equation_rows = dataframe[column].astype('str').str.contains('=').fillna(False)
        dataframe.loc[equation_rows, column] = dataframe.loc[equation_rows, column].astype('str').str.lstrip('=').apply(pandas.eval).astype('float')
        percentage_rows = dataframe[column].astype('str').str.contains('%').fillna(False)
        dataframe.loc[percentage_rows, column] = dataframe.loc[percentage_rows, column].astype('str').str.rstrip('%').astype('float')/100.0


def load_units_from_load_master_excel(path: Path) -> DataFrame:
    """
    Loads the Units and their task rows from the Load Master tab of the spreadsheet

    DF keys are approached from the perspective of a `Unit` model.

    :param path: The Excel spreadsheet to read.
    :return: The data.
    """

    logger.info(f"Importing unit tasks from: {path}")

    # Read the unit XLSX.
    dataframe: DataFrame = read_excel(path, sheet_name="Load Master", header=0, index_col=False)
    dataframe = dataframe.rename(
        columns={
            'Conversion Old-To-New': 'conversion_old_to_new',
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
    )

    # Stop when we get to the non-unit tasks
    end_index: int = dataframe[dataframe["conversion_old_to_new"] == "School Management Roles"].index[0]
    dataframe = dataframe[:end_index].apply(to_numeric, errors='ignore')

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
    dataframe: DataFrame = read_csv(path, sheet_name="Load Master", header=0, index_col=False)
    dataframe = dataframe.rename(
        columns={
            'Unit co-ord load': 'load_fixed',
            'lst time unit co-ord load': 'load_fixed_first',
            'Group': 'group',
            'Description/Unit title': 'name',
            'Notes': 'notes',
        },

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


def load_nonunit_tasks_from_excel(path: Path) -> DataFrame:
    """
    Loads non-units tasks from the Load Master tab of the spreadsheet

    DF keys are approached from the perspective of a `Unit` model.

    :param path: The Excel spreadsheet to read.
    :return: The data.
    """

    logger.info(f"Importing non-unit tasks from: {path}")

    # Read the unit XLSX.
    df_1: DataFrame = read_excel(path, sheet_name="Load Master", header=0, index_col=False)
    df_1 = df_1.rename(
        columns={
            "Conversion Old-To-New": "conversion_old_to_new",
            "Task Category/Unit Code": "unit__code",
            "Description/Unit title": "task__title",
            "Task Description": "academic_group__short_name",
            "Unit co-ord load": "task__load_fixed",
            "lst time unit co-ord load": "task__load_fixed_first",
        },
    )

    desired_columns: list[str] = [
        "unit__code", "task__title", "academic_group__short_name",
        "task__description", "task__load_fixed_first", "task__load_fixed", "task__notes"
    ]

    def combine_columns(cols: Series) -> str:
        """
        Combines all the columns of a row into one notes field.

        :param cols: Series for the row.
        :return: No notes if none, or Pandas throws away the whole row on merge (???)
        """
        notes: str = ""
        for col in cols:
            if not isna(col):
                notes += f"{str.strip(str(col))}\n"

        if notes:
            return notes
        else:
            return "NO NOTES"

    start_index: int = df_1[df_1.conversion_old_to_new == "S2"].index[-1] + 1
    end_index: int = df_1[df_1.conversion_old_to_new == "Project Supervision"].index[0]
    df_1 = df_1[start_index:end_index]
    df_1 = df_1[df_1.unit__code.isin(['MANG', 'COMM', 'PCAP'])]
    df_1['task__notes'] = df_1[df_1.columns[6:]].apply(combine_columns, axis=1)
    df_1 = df_1.drop(columns=set(df_1.columns) - set(desired_columns))
    strip_dataframe_whitespace(df_1)

    # Read the rows with fewer columns
    df_2: DataFrame = read_excel(path, sheet_name="Load Master", header=0, index_col=False)
    df_2 = df_2.rename(
        columns={
            "Conversion Old-To-New": "conversion_old_to_new",
            "Task Category/Unit Code": "unit__code",
            "Description/Unit title": "task__title",
            "Task Description": "task__description",
            "Unit co-ord load": "task__load_fixed",
        },
    )
    start_index: int = df_2[df_2.conversion_old_to_new == "Administration"].index[0] + 1
    end_index: int = df_2[df_2.conversion_old_to_new == "PCAP"].index[0]
    df_2 = df_2[start_index:end_index]
    df_2 = df_2[df_2.unit__code.isin(["MANG", "COMM", "PCAP"])]
    df_2["task__notes"] = df_2[df_2.columns[5:]].apply(combine_columns, axis=1)
    df_2 = df_2.drop(columns=set(df_2.columns) - set(desired_columns))
    strip_dataframe_whitespace(df_2)

    dataframe: DataFrame = concat([df_1, df_2], sort=False, join='outer')
    dataframe.loc[dataframe.task__load_fixed > 700, ("task__load_fixed_first")] = None
    dataframe.loc[dataframe.task__load_fixed > 700, ("task__load_fixed")] = -1
    return dataframe


def load_staff_tasks_from_excel(path: Path) -> DataFrame:
    """
    Loads the "Staff Tasks" sheet of the Excel file.

    This has lines for each task, plus a final line for each staff member saying "Total".

    :param path: The Excel spreadsheet to read.
    :return: A dataframe that represents the "Staff tasks" sheet.
    """
    dataframe: DataFrame = read_excel(path, sheet_name="Staff Tasks", header=0, index_col=False)
    dataframe.rename(
        columns={
            'STAFF': 'staff__name',
            'TASK CAT/UNIT CODE': 'code',
            'TASK DETAIL': 'task__title',
            'Comments': 'task__notes',
            'DESCRIPTION/UNIT TITLE': 'task__description',
            'Group': "academic_group__name"
        },
        inplace=True
    )

    # Remove whitespace, then drop the rows with no staff name or "Total" in
    strip_dataframe_whitespace(dataframe)
    dataframe = dataframe[dataframe.staff__name.astype(bool)]  # Remove lines with no staff
    dataframe = dataframe[dataframe.code.astype(bool)]  # Remove lines with no task code
    dataframe = dataframe[dataframe.task__title.astype(bool) | dataframe.task__description.astype(bool)]  # Rremove 'summary' lines (may have '-')
    dataframe.loc[dataframe.code.isin(["MANG", "COMM", "PCAP"]), "task__title"] = dataframe.task__description
    dataframe.loc[dataframe.code.isin(["MANG", "COMM", "PCAP"]), "task__description"] = None
    dataframe = dataframe[dataframe.staff__name.str.contains("Total") == False]
    return dataframe


def load_staff_contracts_from_excel(path: Path) -> DataFrame:
    """
    Loads the "Staff Contracts" sheet of the Excel file.

    Some of the columns have trailing whitespace in the names (???).

    :param path: The Excel spreadsheet to read.
    :return: A dataframe that represents the "Staff Contract Detail" sheet.
    """
    dataframe: DataFrame = read_excel(path, sheet_name="Staff Contract Detail", header=0, index_col=False)
    dataframe = dataframe.rename(
        columns={ column: column.strip() for column in dataframe.columns }
    )

    dataframe = dataframe.rename(
        columns={
            "STAFF": "name", "fte frac": "fte_fraction", "Fixed hrs": "hours_fixed", "Gender": "gender", "Comment": "notes",
            "Over/Underload This year": "load_balance_final", "Group": "academic_group",
        }
    )

    strip_dataframe_whitespace(dataframe)
    for column in {"fte_fraction", "hours_fixed", "Cumulative to AY21/22", "Cumulative Overload at end 22/23", "load_balance_final"}:
        dataframe[column] = dataframe[column].fillna(0)

    # Stop when we find the "Grand Total" row
    end_index: int = dataframe[dataframe["name"] == "Grand Total"].index[0]
    return dataframe[:end_index].apply(to_numeric, errors="ignore")
