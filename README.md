# Newsly

**Newsly** is a newsbot written by Chris Pappalardo (<cpappala@gmail.com>).  It checks for news every few minutes and prints the results to either stdout (console) or IRC.

## Requirements

**Newsly** uses [newsapi.org](https://newsapi.org) for news.  You can register for a free API key with newsapi and use it with **Newsly**.

Clone the repo and install the python dependencies:

```sh
git clone <https://github.com/ChrisPappalardo/newsly>
cd newsly
pip install -r requirements.txt
```

## Usage

```sh
NEWS_API_KEY=<your key> python app.py
```

## Environment Options

- `TIMEZONE` - Your timezone
- `DELAY` - News loop delay in minutes
- `IRC` - Set to `true` to enable IRC (optional)
