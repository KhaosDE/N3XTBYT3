"""Startdatei für Doppelklick und für PyInstaller (.exe).

In der .exe fragt zuerst das Selbst-Update (Paket n3xtbyt3_update), ob es eine neuere Version gibt.
Ist eine geladen und gestartet, endet dieses Programm; sonst startet N3XTBYT3 ganz normal.
"""

import sys

if __name__ == "__main__":
    from n3xtbyt3_update import beim_start

    if beim_start(sys.argv[1:]):
        sys.exit(0)
    from n3xtbyt3.oberflaeche.app import main

    main()
