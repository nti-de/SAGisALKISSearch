import importlib
import os
import subprocess
import sys
from typing import Tuple

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import Qgis
from qgis.utils import iface

from .translation import translate


def check(required_packages: list[str], path_to_bundled_packages="") -> list[str]:
    """Checks whether the required packages are installed/available.
    Returns list of missing packages.

    :return: List of missing packages.
    """

    missing_packages = []
    for package in required_packages:
        if package in sys.modules or package.lower() in sys.modules:
            continue
        elif importlib.util.find_spec(package) or importlib.util.find_spec(package.lower()):
            continue
        elif path_to_bundled_packages:
            # Add plugin folder to PATH to use included packages if present (plugin folder).
            package_path = os.path.join(path_to_bundled_packages, package)
            if os.path.isdir(package_path):
                sys.path.append(path_to_bundled_packages)
                if importlib.util.find_spec(package):
                    continue
                # Try lowercase
                if importlib.util.find_spec(package.lower()):
                    continue

        missing_packages.append(package)

    return missing_packages


def install(package: str) -> Tuple[bool, str]:
    try:
        output = subprocess.check_output(["python3", "-m", "pip", "install", package], stderr=subprocess.STDOUT)
        return True, output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return False, str(e.output.decode("utf-8"))
    except Exception as e:
        return False, str(e)


def check_packages(required_packages: list[str], plugin_name="", plugin_path="") -> bool:
    """Checks whether the required packages are installed/available.
    Returns True if all packages are available. If at least one packages is missing, returns false and shows an error.

    :return: False if at least one is missing; otherwise True.
    """

    missing_packages = check(required_packages, plugin_path)

    if not missing_packages:
        return True

    message = translate("The following software components are required for") + " " + (plugin_name or translate("a SAGis Plugin"))
    message += ":\n\n"
    message += "\n".join(missing_packages)
    message += "\n\n"
    message += translate("Do you want to install the missing components?")

    dialog = QMessageBox(
        QMessageBox.Icon.Question,
        translate("Missing Dependencies"),
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    reply = dialog.exec()

    if reply == QMessageBox.StandardButton.No:
        return False

    error = False
    log = []
    for package in missing_packages:
        success, error_message = install(package)
        if success:
            log.append(f"{package} ... " + translate("Installed"))
        else:
            error = True
            log.append(f"{package} ... " + translate("Installation error") + f"\n{error_message}\n")

    if error:
        iface.messageBar().pushMessage(
            plugin_name,
            translate("Error installing Python packages"),
            "\n".join(log),
            level=Qgis.MessageLevel.Critical,
            duration=0
        )
    else:
        iface.messageBar().pushMessage(
            plugin_name,
            translate("Python packages successfully installed"),
            "\n".join(log),
            level=Qgis.MessageLevel.Success,
            duration=0
        )
        return True
