from typing import Tuple

from PyQt5.QtCore import QDateTime, QDate
from dateutil import parser
from qgis.PyQt.QtCore import NULL


def insert_dict_values_into_string(text: str, data: dict) -> Tuple[bool, str]:
    """Inserts values of the data dictionary into a string.
    First tries as is, then upper case followed by lower case.

    Returns True and the new string if no KeyError occurred.
    Returns False and the missing key if a KeyError occurred.
    Returns False and given string if 'data' is not a dictionary.
    """

    if not isinstance(data, dict):
        return False, text

    try:
        # Try as is
        return True, text.format(**data)
    except KeyError as e:
        try:
            # Try upper case
            upper_case = {k.upper(): v for k, v in data.items()}
            return True, text.format(**upper_case)
        except KeyError:
            try:
                # Try lower case
                lower_case = {k.lower(): v for k, v in data.items()}
                return True, text.format(**lower_case)
            except KeyError:
                return False, e.args[0]


def test_date(condition, format_="dd.MM.yyyy") -> str:
    if not condition or condition == NULL:
        return ""
    if isinstance(condition, (QDate, QDateTime)):
        return condition.toString(format_)
    try:
        datetime = parser.parse(str(condition))
        q_datetime = QDateTime(datetime)
        return q_datetime.toString(format_)
    except:
        return ""


def get_formatted_string(val, precision=3, decimals_if_needed=True) -> str:
    result = ""
    if val == NULL:
        return result
    try:
        # result = str(round(float(val), precision))
        result = "{:.{}f}".format(float(val), precision) if precision > 0 else f"{result}"
        result = result.rstrip("0").rstrip(".")if decimals_if_needed else result
        result = result.replace(".", ",")
    except:
        pass
    return result


def get_diff_in_perc(val1, val2, precision: int) -> float:
    diff = 0
    try:
        item1 = float(val1)
        item2 = float(val2)

        diff = abs(100 - (100 * item1 / item2))
    except:
        pass
    return round(diff, precision)
