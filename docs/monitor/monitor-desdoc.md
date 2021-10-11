# PAM MONITOR DESDOC
[TOC]

## Introduction

Monitor module is responsible for  local fs indexation and db updating.  

Basic idea for monitor functionality:

```plantuml
Monitor <- DB : fetch dirs to watch
hnote over Monitor : initial fs polling
Monitor -> DB : update on modify
hnote over Monitor: watching dirs
Monitor -> DB : update on modify
```