# BODO - A production data explorer

BODO is a useful app to explore batch data from the famous process control system Botec of Krones.
    Please note that BODO ist not produced, endorsed or otherwise linked to Botec and it's owner!
    All data is retrieved from the public interface database called Iface. Only read access to this DB is necessary.  

BODO is useful as it is, but nevertheless also a demonstrator for possible further data visualisation.
    If you are interested in more and better insights into your data, please get in contact to the manufacturer of BODE:
    Mono Azul. You can find us here www.mono-azul.de

## Building

BODO is a Python 3 program that can be started by calling webengine.py file after the dependencies from requirements.txt 
are available.

Typically one would use pyinstaller to bundle it into one executable as described in the BUILD file.

## Status

BODO uses SQL to query the Iface database. These queries are based on my memories of some real world implementations.
Nevertheless, my memories could be wrong, the database structure might differ and/or the data could be in an unexpected 
format. All this could lead to error and therefore the status has to be considered ***ALPHA*** until positive feedback 
gives more confidence.
