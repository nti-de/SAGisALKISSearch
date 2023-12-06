# SAGis ALKIS Suche
###### (SAGis ALKIS Search)

SAGis ALKIS Suche ist eine Erweiterung für die GIS-Software QGIS zum Einbinden, Durchsuchen und Exportieren von ALKIS Flurstückdaten. \
Unterstützt werden mit dem [SAGis ALKIS](https://www.nti.biz/de/produkte/sagis-loesungen/sagis-alkis/) Konverter erstellte Datenbanken (PostgreSQL/SQLite).

## Funktionen

- Einbinden der Datenbank
- Suche nach Straßennamen, Gebäuden und Flurstücken
- Anzeigen von Flurstückdaten
- Excel Export von Flurstückdaten
- Anzeigen eines Flurstücks in [SAGis web](https://www.nti.biz/de/produkte/sagis-loesungen/sagis-web/)

## Nutzung

### Software-Voraussetzungen

- QGIS >= 3.28
- PostgreSQL >= 12 mit PostGIS 3.1

### Installation

SAGis Excel Export kann über das QGIS-Plugin Repository heruntergeladen werden.

Für eine erfolgreiche Ausführung des Programms müssen zudem folgende Python-Komponenten installiert werden:
- pandas (getestet mit Version 2.0.2)
- xlsxwriter (getestet mit Version 3.1.9)
- xsdata (getestet mit Version 23.8)

<details><summary><b>Anleitung anzeigen</b></summary>

1. Suchen Sie das Installationsverzeichnis von QGIS (Zumeist `C:\OSGeo4W\` oder `C:\Program Files\QGIS 3.*'`)

2. Im Verzeichnis befindet sich die _OSGeo4W-Shell_ (Datei mit dem Namen `OSGeo4W.bat`). Starten Sie die _OSGeo4W-Shell_ und führen Sie den folgenden Befehl im sich öffnenden Programm aus:

  ```sh
  o4w_env & python3 -m pip install xlsxwriter xsdata
  ```
</details>

### Kontakt
- Mail: qgis-de@nti.biz
- Web: https://nti.biz/de
---

<sup>
Copyright (C) 2023 NTI Deutschland GmbH
</sup></br>
<sup>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
</sup>
<sup>
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
</sup>
<sup>
You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.
</sup>