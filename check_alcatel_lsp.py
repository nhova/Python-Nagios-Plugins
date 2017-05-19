#!/usr/bin/env python

import argparse
import nagiosplugin
import logging
import re
from pysnmp.hlapi import *

lsp_name_oid = "1.3.6.1.4.1.6527.3.1.2.6.1.1.4."
lsp_status_oid = "1.3.6.1.4.1.6527.3.1.2.6.1.1.6."

_log = logging.getLogger('nagiosplugin')
lsp_list = []

def get_lsp_list(address, community):
    p = re.compile( lsp_name_oid+"(\d+\.\d+)" )
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                    CommunityData(community, mpModel=1), UdpTransportTarget((address, 161)),
                    ContextData(), ObjectType(ObjectIdentity(lsp_name_oid)),
                    lexicographicMode=False):

        if errorIndication:
            #print(errorIndication)
            break
        elif errorStatus:
            #print('%s at %s' % (errorStatus.prettyPrint(),
            #                    errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                m = p.match(str(varBind[0]))
                lsp_list.append(m.group(1))


class LSP(nagiosplugin.Resource):

    def __init__(self, address, community, lsp_list):
        self.address = address
        self.community = community
        self.lsp_list = lsp_list

    def probe(self):
        sensors = []
        for lsp in self.lsp_list:
            sensors.append(ObjectType(ObjectIdentity(lsp_name_oid+lsp)))
            sensors.append(ObjectType(ObjectIdentity(lsp_status_oid+lsp)))

        errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),
                        CommunityData(self.community, mpModel=1), UdpTransportTarget((self.address, 161)), 
                        ContextData(), *sensors))

        for a, b in zip(*[iter(varBinds)] * 2):
            label, status = str(a[1]), b[1]
            if not label and not status:
                label, status = 'noSuchInstance', 'noSuchInstance'
            yield nagiosplugin.Metric( label + '-LSP', status, context = 'lsp_metrics')


class LSPContext(nagiosplugin.Context):
    def __init__(self, name, fmt_metric='{name} is {valueunit}', result_cls=nagiosplugin.result.Result):

        super(LSPContext, self).__init__(name, fmt_metric, result_cls)

    def evaluate(self, metric, resource):
        if metric.value == 1:
            return self.result_cls(nagiosplugin.state.Critical, 'LSP state unknown', metric)
        elif metric.value == 2:
            return self.result_cls(nagiosplugin.state.Ok, 'LSP OK', metric)
        elif metric.value == 3:
            return self.result_cls(nagiosplugin.state.Critical, 'LSP Down', metric)
        elif metric.value == 4:
            return self.result_cls(nagiosplugin.state.Warn, 'LSP State Transition', metric)
        elif metric.value == 'noSuchInstance':
            return self.result_cls(nagiosplugin.state.Critical, 'ERROR: Nonexsitant LSP', None)
        else:
            return self.result_cls(nagiosplugin.state.Unknown, 'LSP state unknown', metric)

class Summary(nagiosplugin.Summary):
    def ok(self, results):
        msg = []
        for result in results:
            msg.append('{}: {}'.format(result.metric.name, result.hint))
        return ', '.join(msg)

    def problem(self, results):
        msg = []
        for result in results:
            if result.metric:
                msg.append('{}: {}'.format(result.metric.name, result.hint))
            else:
                msg.append('{}'.format( result.hint))
        return ', '.join(msg)

@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('host',
                      help = 'Hostname or IP of device')
    argp.add_argument('community', 
                      help = 'SNMP community string')
    argp.add_argument('--lsp', nargs='+',
                      help = 'One or more LSP IDs')
    args = argp.parse_args()

    address = args.host
    community = args.community
   
    if not args.lsp:  
        get_lsp_list(address, community) 
    else:
        for lsp in args.lsp:
            lsp_list.append(lsp)    

    check = nagiosplugin.Check( LSP(address, community, lsp_list), LSPContext('lsp_metrics'),  Summary() )
    check.main()

if __name__ == '__main__':
    main()
