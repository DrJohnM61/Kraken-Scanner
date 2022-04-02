import currency_viewer as cv
import term
import sys
from select import select
from tabulate import tabulate
import tty
import termios

table = {'ccy': [], 'balance': [], 'price': [], 'value': []}

def process_output(table, item, balance, price, value):
    for i in range(len(item)):
        table['ccy'].append(item[i][0:3])
        table['price'].append(f'€{price[i]:,.6f}')
        table['balance'].append(f'{balance[i]:,.0f}')
        table['value'].append(f'€{value[i]:,.2f}')


term.clear()
print("")
old_total = 0.0
first = True
keep_running = True
paused = False

while keep_running:

    a = cv.CurrencyViewer()
    a.process_cv()

    headers = ['Currency', 'Balance', 'Price', 'Value']

    table['ccy'] = []
    table['price'] = []
    table['balance'] = []
    table['value'] = []

    process_output(table, a.currencies['fiat'], a.balance['fiat'], a.price['fiat'], a.value['fiat'])
    process_output(table, a.currencies['crypto'], a.balance['crypto'], a.price['crypto'], a.value['crypto'])

    total = int((100.0 * a.eur_total) + 0.5) / 100.0

    if first:
        old_total = total
        first = False

    numbers = '€{:,.2f}'.format(total)
    delta = abs(total - old_total)
    ndelta = '€{:,.2f}'.format(delta)

    table['price'].append(ndelta)

    table['ccy'].append('Total')
    if old_total > total:
        table['balance'].append('down')
    elif old_total < total:
        table['balance'].append('up')
    else:
        table['balance'].append('no change')
    table['value'].append(numbers)

    print(tabulate(table, headers, tablefmt='fancy_grid'))

    old_total = total

    for i in range(60):
        print('      ', 60 - i, ' \r', end='', flush=True)
        try:
            mode = termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(sys.stdin.fileno())
            restore = True
        except tty.error:
            restore = False
        rl, wl, xl = select([sys.stdin], [], [], 1)
        if not rl:
            if restore:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, mode)
            # timeout
        else:  # some input
            c = sys.stdin.read(1)
            if restore:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, mode)
            # you will probably want to add some special key support
            # for example stop on enter:
            if c == 'q':
                keep_running = False
                break
            elif c == 'r':
                break
            elif c == 'c':
                term.clear()
                break
            elif c == 'p':
                print ( 'Paused    ', ' \r', end='', flush=True )
                paused = True
                while paused:
                    try :
                        mode = termios.tcgetattr ( sys.stdin.fileno ( ) )
                        tty.setraw ( sys.stdin.fileno ( ) )
                        restore = True
                    except tty.error :
                        restore = False
                    rl, wl, xl = select ( [sys.stdin], [], [], 1 )
                    if not rl :
                        if restore :
                            termios.tcsetattr ( sys.stdin.fileno ( ), termios.TCSADRAIN, mode )
                        # timeout
                    else :  # some input - we are not bothered about the input, but lets read it anyway to flush it out
                        paused = False
                        c = sys.stdin.read ( 1 )
                        if restore :
                            termios.tcsetattr ( sys.stdin.fileno ( ), termios.TCSADRAIN, mode )
                break

    if keep_running:
        print('Refreshing      ', '\r', end='', flush=True)
        term.homePos()

    # and print newline
    sys.stderr.write('\n')
