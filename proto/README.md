# ffindex prototype

`ffindex` is a prototype of PAM application implemented with Python and PyQt.  
The goal of the prototype is to give a sense of basic functionality of the desired application in a CLI.

## Application design
under the hood the `ffindex` functionality is split between the `client` and `monitor` applications.  

`monitor` app is responsible for indexation of the local file system and updating the database.  
Retrieving metadata from the files is also in the scope of `monitor` app ( [proto.monitor.dumper](monitor/dumper.py) module).  

`client` application delivers the basic CLI, including the `monitor` control commands (`run`, `stop`, `port`, `status`, `update`).  
Other functionality includes retrieving data from the database with commands like `tables`, `show` and `search`, and
managing directory watchlist with `monitor` `add` and `remove` commands.

`add` and `remove` commands are are handled by the `monitor` server, or, if it is offline, by the `client` app,  
which operates directly on database in this case, but without recursive update and metadata extracting.  
`monitor` `update` command cannot be executed without launching server.

## CLI design

ffindex CLI implemented using `argparse` library.   
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

