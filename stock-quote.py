#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2018 Jim Fridlund <jim@code4fun.us>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import sys
import getopt
import json
import re
import requests

version = '0.0'

# Interactive session is default. Disable using --batch flag.
interactive = True

# Output format supported (default is text).
valid_format = ['json', 'simple', 'text']

# IEX Trading attribution.
def _display_data_source():
    """Display stock information source."""
    msg = "Data provided for free by IEX Group Inc.\n" \
        "https://iextrading.com/api-exhibit-a/\n\n" \
        "Realtime quote and/or trade prices are not sourced from all markets.\n"
    print(msg)

# ANSI color support
class ansi:
    RESET = '\x1b[0m'
    HEADER = '\x1b[1;33;44m'
    BOLD = '\x1b[1m'
    UNDERLINE = '\x1b[4m'
    INVERSE = '\x1b[7m'
    RED = '\x1b[91m'
    GREEN = '\x1b[92m'
    YELLOW = '\x1b[93m'
    BLUE = '\x1b[94m'
    PURPLE = '\x1b[95m'

def _colorize_str(color, str):
    """Given a string, change its text color (interactive sessions only)."""
    if interactive:
        str = color + str + ansi.RESET
    return str

#
# Just print <ticker>:<price>
#
def _stock_info_simple(ticker, stock_data):
    print(ticker + ':' + str(stock_data['quote']['latestPrice']))

#
# Display stock data like what you would see from Yahoo! finance.
#
# Note: some fields have null data so need to check to prevent
# script from crashing.
#
def _stock_info_text(ticker, stock_data):
    """Print out stock data suitable for console w/colors."""
    quote_dict = stock_data['quote']
    stats_dict = stock_data['stats']

    # Strip trailing ' (The)$'
    company_name = re.sub(r'(.*) \(The\)$', r'\1', quote_dict['companyName'])
    company_str = _colorize_str(ansi.HEADER, "%s (%s)" % (company_name, quote_dict['symbol']))
    print(company_str)
    print("%s" % (quote_dict['primaryExchange']))

    latest_price = quote_dict['latestPrice']
    prev_close = quote_dict['previousClose']
    price_delta = latest_price - prev_close
    percent_change = (price_delta / prev_close) * 100
    latest_price_str = _colorize_str(ansi.YELLOW, "$%.2f " % (latest_price))
    print(latest_price_str, end='')
    if price_delta > 0:
        delta_str = _colorize_str(ansi.GREEN, "%+.2f (%+.2f%%)" % (price_delta, percent_change))
    elif price_delta < 0:
        delta_str = _colorize_str(ansi.RED, "%+.2f (%+.2f%%)" % (price_delta, percent_change))
    else:
        delta_str = "%+.2f (%+.2f%%)" % (price_delta, percent_change)
    print(delta_str)

    print("%s as of %s\n" % (quote_dict['latestSource'], quote_dict['latestTime']))

    prev_close_str = "%.2f" % (quote_dict['previousClose'])
    market_cap = stats_dict['marketcap']
    if market_cap > 1e12:
        market_cap_str = "%.2fT" % (market_cap / 1e12)
    elif market_cap > 1e9:
        market_cap_str = "%.2fB" % (market_cap / 1e9)
    else:
        market_cap_str = "%.2fM" % (market_cap / 1e6)
    print("%-15s: %16s   %-15s: %12s" % ("Prev Close", prev_close_str, "Market Cap", market_cap_str))

    open_str = "%.2f" % (quote_dict['open'])
    beta_str = "%.2f" % (stats_dict['beta'])
    print("%-15s: %16s   %-15s: %12s" % ("Open", open_str, "Beta", beta_str))

    if quote_dict['iexBidPrice'] == None or quote_dict['iexBidPrice'] == 0:
        bid_str = 'N/A'
    else:
        bid_str = "%.2f x %d" % (quote_dict['iexBidPrice'], quote_dict['iexBidSize'])
    if quote_dict['peRatio'] == None:
        pe_ratio_str = 'N/A'
    else:
        pe_ratio_str = "%.2f" % (quote_dict['peRatio'])
    print("%-15s: %16s   %-15s: %12s" % ("Bid", bid_str, "PE Ratio", pe_ratio_str))

    if quote_dict['iexAskPrice'] == None or quote_dict['iexAskPrice'] == 0:
        ask_str = 'N/A'
    else:
        ask_str = "%.2f x %d" % (quote_dict['iexAskPrice'], quote_dict['iexAskSize'])
    eps_str = "%.2f" % (stats_dict['ttmEPS'])
    print("%-15s: %16s   %-15s: %12s" % ("Ask", ask_str, "EPS (TTM)", eps_str))

    day_range_str = "%.2f - %.2f" % (quote_dict['low'], quote_dict['high'])
    fwd_div_yield_str = "%.2f (%.2f%%)" % (stats_dict['dividendRate'], stats_dict['dividendYield'])
    print("%-15s: %16s   %-15s: %12s" % ("Day's Range", day_range_str, "Fwd Div & Yield", fwd_div_yield_str))

    week52_range_str = "%.2f - %.2f" % (quote_dict['week52Low'], quote_dict['week52High'])
    if stats_dict['exDividendDate'] == 0:
        # Ex dividend date unspecified
        ex_div_date_str = 'N/A'
    else:
        date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")
        mo = date_pattern.search(stats_dict['exDividendDate'])
        if mo == None:
            ex_div_date_str = 'N/A'
        else:
            ex_div_date_str = mo.group(0)
    print("%-15s: %16s   %-15s: %12s" % ("52 wk Range", week52_range_str, "Ex-Div Date", ex_div_date_str))

    volume_str = "{:,}".format(quote_dict['latestVolume'])
    print("%-15s: %16s" % ("Volume", volume_str))

    avg_volume_str = "{:,}".format(quote_dict['avgTotalVolume'])
    print("%-15s: %16s" % ("Avg. Volume", avg_volume_str))
    print()

def _url_download(tickers):
    """This does the actual work of downloading the stock data from IEX Trading."""
    results = dict()

    params = ",".join(tickers)
    url = u'https://api.iextrading.com/1.0/stock/market/batch?symbols=' + params + '&types=quote,stats'

    r = requests.get(url)

    if r.status_code == requests.codes.ok:
        results = r.json()

    return results

#
# IEX Trading limits the number of tickers to 100 per API request. Request
# must be split into multiple requests if it is over that.
#
def stocks_download(tickers):
    """Download near real-time stock info from IEX Trading."""
    # Max allowed by IEX
    tickers_per_request = 100

    (i, tickers_remaining, results) = (0, len(tickers), dict())

    # Send ticker requests in chunks.
    while tickers_remaining > tickers_per_request:
        tickers_chunk = tickers[i:i+tickers_per_request]
        results.update(_url_download(tickers_chunk))

        i += tickers_per_request
        tickers_remaining -= tickers_per_request

    # Fetch the remaining tickers
    if tickers_remaining > 0:
        tickers_chunk = tickers[i:i+tickers_remaining]
        results.update(_url_download(tickers_chunk))

    return results

def stocks_process(format, tickers, stocks_data):
    """Process each stock data returned."""
    if (format == 'json'):
        # Useful for debugging.
        print(json.dumps(stocks_data, indent=4, sort_keys=True))

    for t in tickers:
        try:
            s = stocks_data[t]
        except KeyError:
            print("Stock data missing for '%s'\n" % (t), file=sys.stderr)
        else:
            if format == 'text':
                _stock_info_text(t, s)
            elif format == 'simple':
                _stock_info_simple(t, s)

def _usage():
    print('stock-quote version %s Copyright (c) 2018 Jim Fridlund <jim@code4fun.us>\n' % (version), file=sys.stderr)
    print('Usage: stock-quote [options] <ticker> ...\n', file=sys.stderr)
    print('Options:', file=sys.stderr)
    print(' --batch         Run in batch mode', file=sys.stderr)
    print(' --format=<fmt>  Valid format: ' + ', '.join(valid_format) + '\n', file=sys.stderr)
    sys.exit(1)

def main(argv):
    global interactive

    # Default output format.
    format = 'text'

    try:
        opts, args = getopt.getopt(argv, "bhf:", ["batch", "format=", "help"])
    except getopt.GetoptError as err:
        print("%s\n" % (err), file=sys.stderr)
        _usage()

    for opt, arg in opts:
        if opt in ("-b", "--batch"):
            interactive = False
        elif opt in ("-h", "--help"):
            _usage()
        elif opt in ("-f", "--format"):
            if arg not in valid_format:
                print("Invalid argument '" + arg + "'. Valid format: " + ", ".join(valid_format) + "\n", file=sys.stderr)
                _usage()
            else:
                format = arg

    if len(args) == 0:
        _usage()

    if interactive and not sys.stdout.isatty():
        interactive = False

    # Get the stock tickers from the command line and convert to upper case.
    tickers = [arg.upper() for arg in args]

    # Download stock quote data from IEX. The data is in JSON format.
    stocks_data = stocks_download(tickers)

    # Process it.
    stocks_process(format, tickers, stocks_data)

    # Finally, cite source of stock data.
    if format != 'simple':
        _display_data_source()

if __name__ == "__main__":
    main(sys.argv[1:])
