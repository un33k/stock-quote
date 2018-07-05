# stock-quote

A simple command line based stock quote script. This is written in Python
and uses stock data provided by [IEX].

## Installation

The script is a standalone Python 3 script that you can copy to a common
path such as /usr/local/bin. It requires the *requests* module:

```
pip3 install requests
```

## Usage

Invoke the script passing a list of tickers from the command line.

```
$ stock-quote aapl
Apple Inc. (AAPL)
Nasdaq Global Select
$185.54 +1.62 (+0.88%)
IEX real time price as of 1:58:57 PM

Prev Close     :           183.92   Market Cap     :      903.99B
Open           :           185.33   Beta           :         1.17
Bid            :     180.88 x 100   PE Ratio       :        17.91
Ask            :     185.61 x 100   EPS (TTM)      :        10.36
Day's Range    :  184.28 - 186.41   Fwd Div & Yield: 2.92 (1.56%)
52 wk Range    :  142.41 - 194.20   Ex-Div Date    :   2018-05-11
Volume         :       10,595,635
Avg. Volume    :       23,614,599

Data provided for free by IEX Group Inc.
https://iextrading.com/api-exhibit-a/

Realtime quote and/or trade prices are not sourced from all markets.
```

## IEX API

The stock data provided for free by [IEX][IEX API]. View [IEX's Terms of Use][IEX Terms].

Realtime quote and/or trade prices are not sourced from all markets.

[IEX]: https://iextrading.com/developer/
[IEX API]: https://iextrading.com/developer/docs/
[IEX Terms]: https://iextrading.com/api-terms/
