Inherite from layer-hpccsystems-base and has interface-hpccsystems-plugin 
It includes functions to install and configure HPCC Platform, etc

To to plugin interface is not clean. Evne there are some commmon code in reactive/plugin_base.py
but the method reply on "hpcc-plugin" service name which is set in metadata.yaml in concrete
charm



