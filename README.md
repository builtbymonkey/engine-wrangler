# Engine Wrangler

A Python script that makes sense out of ExpressionEngine sites,
channels, titles and custom fields, and prints them out in any
format (currently only supporting XML).

It's not the quickest or most efficient system, and I suspect there's a lot it
can't do yet (I know it can't yet handle file URLs), but it understands other
custom field types like selects and booleans, and can render those out. It was
built in about four hours, so there's plenty more scope for improvement. (It
was also the first time I'd written a script that could be run from the
command line).

OK, enough disclaimers. Let's get into this thing.

## Installation

This isn't on PyPi yet, so you can install it from straight from Git.
You should probably use it with Virtualenv.

### Install from Github

```
pip install git+git://github.com/substrakt/engine-wrangler.git
```

## Usage

Once installed, you can just run `ew` with the following parameters:

- `-h` or `--help`: Show this help message and exit
- `-o HOST` or `--host=HOST`: MySQL host (defaults to `localhost`)
- `-p PORT` or `--port=PORT`: MySQL port (defaults to `3306`)
- `-u USERNAME` or `--user=USERNAME`: MySQL username (defaults to `mysql`)
- `-w PASSWORD` or `--password=PASSWORD`: MySQL password (defaults to `mysql`)
- `-d DATABASE` or `--database=DATABASE`: MySQL database name (defaults to `mysql`)
- `-r PREFIX` or `--prefix=PREFIX`: ExpressionEngine table prefix (defaults to `exp_`)
- `-s SITE` or `--site=SITE`: ExpressionEngine site name (defaults to `default_site`)
- `-f FORMAT` or `--format=FORMAT`: Output file format (defaults to `xml`)

### Example: Dump the whole site

```
ew -d ee -u root > output.xml
```

This logs into the local MySQL server using the root account and selects the
`ee` database. It exports the default site to a file called output.xml.

### Example: Dump site, channel by channel

```
ew -d ee -u root --split
```

This logs into the local MySQL server using the root account and selects the
`ee` database. It exports the default site to a directory it creates, called
output, with a file called index.php with a summary of the site, and a
<channel>.xml file for each channel found in the database. The structure of
this XML is slightly different, in that - with the exception of the index.xml
file - there are no `<site>` or `<section>` tags.

### Todo

1. Add more export formats
2. Look into allowing either filtering by channel, or splitting channels up
into separate files

### Get in touch

I'm Steadman, Technical Director of Substrakt. You can find us at
<http://substrakt.co.uk/>, and more of my code at
<http://code.steadman.io>.
