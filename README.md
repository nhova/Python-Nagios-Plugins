# check_alcatel_lsp
Nagios style plugin to check Alcatel LSP status.

Sample output:

```
LSP OK - BAUHAUS-PE1-LSP: LSP OK, BAUHAUS-PE2-LSP: LSP OK, BAUHAUS-PE3-monitoring-LSP: LSP OK
```

```
usage: check_alcatel_lsp.py [-h] [--lsp LSP [LSP ...]] host community

positional arguments:
  host                 Hostname or IP of device
  community            SNMP community string

optional arguments:
  -h, --help           show this help message and exit
  --lsp LSP [LSP ...]  One or more LSP IDs
```

**Collect all LSPs and report status**
    check_alcatel_lsp.py 192.168.1.1 public

**Collect specific LSPs and report status**
    check_alcatel_lsp.py 192.168.1.1 public --lsp 1.1 1.2
