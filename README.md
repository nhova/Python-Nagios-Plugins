# check_alcatel_lsp
Nagios style plugin to check Alcatel LSP status 

Sample output:

```
LSP OK - BAU-PE1-LSP: LSP OK, BAU-PE2-LSP: LSP OK, BAU-PE3-monitoring-LSP: LSP OK
```

```
usage: check_alcatel_lsp.py [-h] -H HOST -C COMMUNITY

optional arguments:
  -h, --help                            show this help message and exit
  -H HOST, --host HOST                  Hostname or IP of device
  -C COMMUNITY, --community COMMUNITY   SNMP community string
```
