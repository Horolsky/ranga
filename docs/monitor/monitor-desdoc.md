# PAM MONITOR DESDOC
[TOC]

## Introduction

Monitor module is responsible for  local fs indexation and db updating.  

Basic idea for monitor process:

```plantuml
Monitor <- DB : fetch dirs to watch
hnote over Monitor : initial fs polling
Monitor -> DB : update on modify
hnote over Monitor: watching dirs
Monitor -> DB : update on modify
```

## Functionality

|command|descr|options|
|-|-|-|
|list|list watched dirs||
|add|add directory to the watchlist||
|remove|remove directory from the watchlist||
|update|update file records in db| -recursively |

current design does not handle directory blacklisting or path masks