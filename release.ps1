$version = Read-Host "Please enter version"

flet pack ".\interface.py" --add-data "unity;UnityPy/resources" --add-data "resources;resources" --name "MDTR_v$version" --icon "images/icon.png" --file-version $version