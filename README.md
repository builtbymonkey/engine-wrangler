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

```bash
pip install git+git://github.com/substrakt/engine-wrangler.git
```

## Using Engine Wrangler

```bsah
Usage: ew [options]

Options:
  -h, --help            show this help message and exit
  -o HOST, --host=HOST  MySQL host
  -p PORT, --port=PORT  MySQL port
  -u USERNAME, --user=USERNAME
                        MySQL username
  -w PASSWORD, --password=PASSWORD
                        MySQL password
  -d DATABASE, --database=DATABASE
                        MySQL database name
  -r PREFIX, --prefix=PREFIX
                        ExpressionEngine table prefix
  -s SITE, --site=SITE  ExpressionEngine site name
  -f FORMAT, --format=FORMAT
                        Output file format
  -l, --split           Split output by content type
  -m IMAGE_PATH, --imgpath=IMAGE_PATH
                        Path to store images
  -n IMAGE_DOMAIN, --imgdomain=IMAGE_DOMAIN
                        Domain for images
  -a NEW_BASE, --newbase=NEW_BASE
                        Replace domains in image URLs with this string
```

### Example: Dump the whole site

```bash
ew -d ee -u root > output.xml
```

This logs into the local MySQL server using the root account and selects the
`ee` database. It exports the default site to a file called output.xml.

### Example: Dump site, channel by channel

```bash
ew -d ee -u root --split
```

This logs into the local MySQL server using the root account and selects the
`ee` database. It exports the default site to a directory it creates, called
output, with a file called index.php with a summary of the site, and a
<channel>.xml file for each channel found in the database. The structure of
this XML is slightly different, in that - with the exception of the index.xml
file - there are no `<site>` or `<section>` tags.

### Configuration

You can also place a file called ew.cfg in the same directory from which you're
calling the `ew` command (not necessarily the directory in which this package
is stored), similar to the supplied ew.cfg.sample file. Use that to specify
arguments if you need to repeatedly run the `ew` command and don't want to have
to remember all the parameters. All the valid options supported by the `ew`
command can be set in this config file.

### Downloading images

Content that looks like HTML is parsed for `<img>` tags. Adding the
`--imgpath <DIR>` argument downloads those images to the specified
location.

Specifying `--imgdomain` sets the domain name where legacy images are
stored. Use this if you're expecting relative URLs. If not, you can ommit this
option and all images with valid URLs will be downloaded.

If you're moving to a CMS with a specific media storage structure - for example
WordPress - you can specify the new base URL for all images with the `--newbase`
argument. This will replace image URLs containing the pattern '//olddomain/'
with '//newdomain/'.

### Todo

1. Add more export formats

### Get in touch

I'm Steadman, Technical Director of Substrakt. You can find us at
<http://substrakt.co.uk/>, and more of my code at
<http://code.steadman.io>.
