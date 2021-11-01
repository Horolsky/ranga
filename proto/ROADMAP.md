# ffindex prototype

`ffindex` is choosen as a working name for the application

This prototype partially implements the functionality of PAM project on Python.

The idea for current iteration is to complete in CLI the two basic functionalities of the desired application - `file monitor` and `metadata indexer`

## CLI design

CLI codegeneration source: [cli_schema.yml](client/cli_schema.yml)

### comprehensive CLI tree
ffindexer subcommands and options

 - **search**: search metadata by keyword
    - **keywords**: filenames, metadata values
    - **category**: specific categories by which to search (filename, path, <metadata key>)
    - **exact**: search only for whole word matches
    - **mode**: sqlite3 output mode (csv, column, html, line, list)
    - **headless**: exclude header from the output
 - **show**: show table from database
    - **table**: database table or view
    - **mode**: sqlite3 output mode (csv, column, html, line, list)
    - **headless**: exclude header from the output
 - **tables**: list table names
 - **monitor**: local file system monitor server
    - **list**: list watched root dirs 
    - **add**: add directory to the watchlist
    - **remove**: remove directory from the watchlist
    - **update**: update file records in database
    - **run**: run monitor server
    - **stop**: stop monitor server
    - **port**: get/set port number
    - **status**: show monitor server status


## Application design
under the hood the `ffindex` functionality is split between the `indexer` and `monitor` applications.  

`monitor` app is responsible for indexation of the local file system and updating the database.  
Retrieving metadata from the media files is also in the scope of `monitor` app.  
`indexer` application delivers the basic CLI, including the `monitor` control commands, i. e.  
`run`, `stop`, `port` and `status`.  
`monitor` `add` and `remove` commands are are handled by the `monitor` server, or, if it is offline, by the `indexer` app,  
which operates directly on database in this case, but without recursive update and metadata extracting.  
`add` and `remove` commands works only with directories, masking files currently not implemented.
`monitor` `update` command cannot be executed without launching server.

other commands are executed by `indexer` app.