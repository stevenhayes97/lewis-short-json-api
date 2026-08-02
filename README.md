# JSON Lewis & Short
A Latin dictionary in JSON format, based off of the Perseus Project's Lewis and Short XML version.

## Loading into a database

`tools/ls_db.py` loads the `ls_*.json` files into SQLite, PostgreSQL or MySQL,
verifies the load is lossless, and then removes the JSON from the repository.
See [tools/README.md](tools/README.md) for the schema and the steps.

## Credits

Text provided by Perseus Digital Library, with funding from The National Endowment for the Humanities. 

Original version available for viewing and download at http://www.perseus.tufts.edu/