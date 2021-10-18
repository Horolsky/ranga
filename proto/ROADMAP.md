# ffpam prototype

`ffpam` is choosen as a working name for the application

This prototype partially implements the functionality of PAM project on Python.

The idea for current iteration is to complete in CLI the two basic functionalities of the desired application - `file monitor` and `metadata indexer`

## ffpam functionality tree
 
- `monitor` module 
    - **list** watched dirs  
    - **add** directory to the watchlist  
    - **remove** directory from the watchlist  
    - **update** file records in db  
- `indexer` module  
    - **search** metadata by keyword  
    - **show** tables in database 

## Ideas for CLI design
`monitor` commands are invoked as `ffpam monitor <args>`, as the monitor itself is the separate app, while `search` and `show` are called directly from `ffpam`, which is the actual indexer app.  
`ffpam monitor update` command can be also aliased as `ffpam update`.