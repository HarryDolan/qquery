"""Command line interface to qquery.  Use -h or --help for help."""

import qquery as qq
import argparse
import time
import math

def main():
    parser = argparse.ArgumentParser(description='Query a Quicken data base.')
    parser.add_argument('--qdb', required=True, help='Path to data base file')
    parser.add_argument('--list-accounts', action='store_true')
    parser.add_argument('--list-categories', action='store_true')
    parser.add_argument('--list-payees', action='store_true')
    parser.add_argument('--list-transactions', action='store_true')
    parser.add_argument('--list-securities', action='store_true')
    parser.add_argument('--list-quotes', action='store_true')
    parser.add_argument('--restrict-to-accounts',
                        help='Limit to specified (comma separated) accounts')
    parser.add_argument('--restrict-to-categories',
                        help='Limit to specified categories')
    parser.add_argument('--restrict-to-payees',
                        help='Limit to specified payees')
    parser.add_argument('--restrict-to-securities',
                        help='Limit to specified securities')
    parser.add_argument('--date-from',
                        help='Limit transactions to and after date')
    parser.add_argument('--date-to',
                        help='Limit transactions to and before date')
    parser.add_argument('--report-holdings', action='store_true',
                        help='Report account holdings (cash and securities).')
    parser.add_argument('--report-cash-flow', action='store_true',
                        help='Report total income or outgo by category.')
    args = parser.parse_args()

    qq.open(args.qdb)

    if args.restrict_to_accounts != None:
        qq.setRestrictToAccounts (args.restrict_to_accounts.split(','))
    if args.restrict_to_categories != None:
        qq.setRestrictToCategories (args.restrict_to_categories.split(','))
    if args.restrict_to_payees != None:
        qq.setRestrictToPayees (args.restrict_to_payees.split(','))
    if args.restrict_to_securities != None:
        qq.setRestrictToSecurities (args.restrict_to_securities.split(','))
    qq.setRestrictToDates (args.date_from, args.date_to)

##############################################################################
    if args.list_accounts:
        for account in qq.getAccounts():
            print ('[{:2}] {:30}'.format (account['key'], account['name']))

##############################################################################
    elif args.list_categories:
        for category in qq.getCategories():
            print ('[{:3}] {:30}'.format (category['key'], category['path']))

##############################################################################
    elif args.list_payees:
        for payee in qq.getPayees():
            print ('[{:5}] {:30}'.format (payee['key'], payee['name']))

##############################################################################
    elif args.list_transactions:
        for t in qq.getTransactions():
            line = '[{:5}] '   .format(t['key']) \
                   + '{:8}'    .format(t['date'])  \
                   + '{:30}'   .format (' [{:}]'.format(t['accountKey']) + \
                                        '{:15}'.format(t['accountName'])) \
                   + '{:30}'   .format (' [{:}]'.format(t['payeeKey']) + \
                                        '{:15}'.format(t['payeeName'])) \
                   + '{:11.2f}'.format(t['amount']) \
                   + '{:30}'   .format (' [{:}]'.format(t['categoryKey']) + \
                                        '{:15}'.format(t['categoryPath']))
            if t['securityKey'] is not None:
                line += ' [{:}]'.format(t['securityKey']) \
                        + '{:15}'.format(t['securityName']) \
                        + ' ({:})'.format(t['securityTicker']) \
                        + '{:11.3f}'.format(float(t['securityShares']))
            print (line)

##############################################################################
    elif args.list_securities:
        for security in qq.getSecurities():
            print ('[{:3d}] {:15} {:30}'.format (security['key'],
                                                 security['ticker'],
                                                 security['name']))

##############################################################################
    elif args.list_quotes:
        for security in qq.getSecurities():
            print ('[{:3}] {:15} {:30}'.format (security['key'],
                                                security['ticker'],
                                                security['name']))
            for quote in qq.getQuotes(security['key']):
                print ('            {:8} {:9.3f}'.format (quote['date'],
                                                          quote['price']))

##############################################################################
    elif args.report_holdings:
        if args.date_to != None:
            theDate = args.date_to
        else:
            now = time.localtime()
            theDate = '{:4}-{:02}-{:02}'.format(now.tm_year,
                                                now.tm_mon,
                                                now.tm_mday)
            # Exclude future dates:
            qq.setRestrictToDates (args.date_from, theDate)
        balCash = {}
        balShares = {}
        for t in qq.getTransactions():
            aName = t['accountName']
            if aName in balCash.keys():
                balCash[aName] += t['amount']
            else:
                balCash[aName] = t['amount']
                balShares[aName] = {}
            sName = t['securityName']
            if sName != None:
                if sName in balShares[aName].keys():
                    balShares[aName][sName] += t['securityShares']
                else:
                    balShares[aName][sName] = t['securityShares']
        for aName in sorted(balCash.keys()):
            balTotal = balCash[aName]
            for sName in sorted(balShares[aName].keys()):
                price = qq.getPriceOnDate (sName, theDate)
                value = balShares[aName][sName] * price
                if value > 0.0005:
                    balTotal += value
                else:
                    del balShares[aName][sName]
            if math.fabs(balTotal)>.001:
                print ('{:10} '      .format(theDate) \
                       + '{:55.55}    '.format(aName) \
                       + '{:10.2f}'    .format(balTotal))
                if len(balShares[aName].keys()) > 0:
                    for sName in sorted(balShares[aName].keys()):
                        price = qq.getPriceOnDate (sName, theDate)
                        value = balShares[aName][sName] * price
                        print ('               ' \
                               + '{:20.20} '  .format(sName) \
                               + '{:10.3f} @ '.format(balShares[aName][sName]) \
                               + '{:7.3f} = ' .format(price) \
                               + '{:10.2f}'   .format(value))
                    if balCash[aName]>=0.01:
                        print ('               ' \
                               + 'Cash                                        ' \
                               + '{:10.2f}'.format(balCash[aName]))

##############################################################################
    elif args.report_cash_flow:
        amount = {}
        for t in qq.getTransactions():
            if t['categoryPath'] in amount.keys():
                amount[t['categoryPath']] += t['amount']
            else:
                amount[t['categoryPath']] = t['amount']
        for path in sorted(amount.keys()):
            print ('{:30} {:12.2f}'.format (path, amount[path]))
