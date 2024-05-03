from PyQt5.QtCore import QSettings

de: dict[str, str] = {
    "a SAGis plugin": "ein SAGis Plugin",
    "The following software components are required for": "Die folgenden Softwarekomponenten werden benötigt für",
    "Do you want to install the missing components?": "Sollen die fehlenden Komponenten installiert werden?",
    "Missing Dependencies": "Fehlende Abhängigkeiten",
    "Installed": "Installiert",
    "Installation error": "Fehler bei Installation",
    "Error installing Python packages": "Fehler beim Installieren der Python-Pakete",
    "Python packages successfully installed": "Python-Pakete erfolgreich installiert"
}


def translate(source: str) -> str:
    locale = QSettings().value("locale/userLocale")[0:2]

    if locale == "de":
        return de.get(source, source)

    return source

