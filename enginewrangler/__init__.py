from MySQLdb import connect
from importlib import import_module
from sys import stdout
from urlparse import urljoin, urlparse
from urllib import urlopen
from os import path, makedirs
import re, phpserialize, json

FORMATTERS = {
    'xml': 'enginewrangler.formatters.xml.XmlFormatter'
}

IMG_REGEX = re.compile(r'\<img[^\<\>\/]* src="([^"]+)"')

class FileDownload(str):
    pass

class Wrangler(object):
    def __init__(self,
        host = 'localhost',
        port = 3306,
        username = 'mysql',
        password = 'mysql',
        database = '',
        prefix = 'exp_',
        format = 'xml',
        output = stdout
    ):
        self._db = connect(
            host = host,
            port = port,
            user = username,
            passwd = password,
            db = database
        )

        self._prefix = prefix
        self._format = format
        self._end_calls = 0
        self._authors = {}
        self._output = output

    def load_vars_file(self, filename):
        self._vars = json.loads(
            open(filename, 'r').read()
        )

    def __enter__(self):
        self._start_spilt()
        return self

    def __exit__(self, type, value, traceback):
        self._end_split()

    def _start_split(self, output = None):
        if not output is None:
            self._output = output

        try:
            module, klass = FORMATTERS[self._format].rsplit('.', 1)
        except KeyError:
            raise Exception('%s formatter not found' % self._format.upper())

        module = import_module(module)
        klass = getattr(module, klass)

        self._formatter = klass(self._output)
        self._formatter.start_document()

    def _end_split(self, output = None):
        self.tidy()
        self._formatter.end_document()

    def _select(self, table, **kwargs):
        sql = 'SELECT * FROM `%s%s`' % (self._prefix, table)
        wheres = []
        params = []

        for key, value in kwargs.items():
            wheres.append('%s = %%s' % key)
            params.append(value)

        if any(wheres):
            sql += 'WHERE (%s)' % ' AND '.join(wheres)

        cursor = self._db.cursor()
        cursor.execute(sql, params)

        fieldnames = [f[0] for f in cursor.description]
        for row in cursor.fetchall():
            yield dict(
                [
                    (
                        fieldnames[i],
                        v
                    ) for i, v in enumerate(row)
                ]
            )

    def _pivot(self, fields_table, values_table, prefix = '', **kwargs):
        sql = 'SELECT f.%(p)sfield_id, f.%(p)sfield_name, ' \
            'f.%(p)sfield_type, f.%(p)sfield_list_items ' \
            'FROM %(f)s AS f' % {
                'f': self._prefix + fields_table,
                'p': prefix and prefix + '_' or ''
            }

        cursor = self._db.cursor()
        cursor.execute(sql)
        fieldnames = [f[0] for f in cursor.description]
        pivot_fields = {}

        for row in cursor.fetchall():
            pivot_fields[row[1]] = (row[0], row[2], row[3])

        pivot_selects = [
            'd.%sfield_id_%d as %s' % (
                prefix and prefix + '_' or '',
                field_id,
                field_name
            ) for field_name, (
                field_id,
                field_type,
                field_items
            ) in pivot_fields.items()
        ]

        for field_name, (field_id, field_type, field_items) in pivot_fields.items():
            if not field_items:
                continue

            field_item_dict = {}
            for line in field_items.splitlines():
                if line:
                    item_name, arrow, item_id = line.rpartition('=>')

                    if item_id == 'yes' and not item_name:
                        field_item_dict[item_id] = True
                    elif item_id == 'no' and not item_name:
                        field_item_dict[item_id] = False
                    else:
                        field_item_dict[item_id] = item_name

            pivot_fields[field_name] = (field_id, field_type, field_item_dict)

        sql = 'SELECT %s FROM %s%s AS d' % (
            ', '.join(pivot_selects),
            self._prefix,
            values_table
        )

        wheres = []
        params = []

        for key, value in kwargs.items():
            wheres.append('d.%s = %%s' % key)
            params.append(value)

        if any(wheres):
            sql += ' WHERE (%s)' % ' AND '.join(wheres)

        cursor = self._db.cursor()
        cursor.execute(sql, params)

        fieldnames = [f[0] for f in cursor.description]
        for row in cursor.fetchall():
            rd = dict(
                [
                    (
                        fieldnames[i],
                        v
                    ) for i, v in enumerate(row) if v
                ]
            )

            for field_name, (field_id, field_type, field_items) in pivot_fields.items():
                if not field_name in rd:
                    continue

                if field_type == 'flexibleselect':
                    if rd[field_name] in field_items:
                        rd[field_name] = field_items[rd[field_name]]

                    continue

                if field_type == 'checkboxes':
                    rd[field_name] = rd[field_name] == 'yes'
                    continue

                if field_type == 'rel':
                    rel_cursor = self._db.cursor()
                    rel_cursor.execute(
                        'SELECT rel_type, rel_child_id FROM %srelationships WHERE rel_id = %%s' % self._prefix,
                        [
                            rd[field_name]
                        ]
                    )

                    rel_fieldnames = [
                        f[0] for f in rel_cursor.description
                    ]

                    for rel_row in rel_cursor.fetchall():
                        rel_rd = dict(
                            [
                                (
                                    rel_fieldnames[i],
                                    v
                                ) for i, v in enumerate(rel_row) if v
                            ]
                        )

                        if rel_rd['rel_type'] == 'channel':
                            subrel_cursor = self._db.cursor()
                            subrel_cursor.execute(
                                'SELECT t.entry_id, t.url_title, c.channel_name FROM %schannel_titles AS t INNER JOIN %schannels AS c ON t.channel_id = c.channel_id WHERE t.entry_id = %%s' % (
                                    self._prefix,
                                    self._prefix
                                ),
                                [
                                    rel_rd['rel_child_id']
                                ]
                            )

                            subrel_fieldnames = [
                                f[0] for f in subrel_cursor.description
                            ]

                            for subrel_row in subrel_cursor.fetchall():
                                subrel_rd = dict(
                                    [
                                        (
                                            subrel_fieldnames[i],
                                            v
                                        ) for i, v in enumerate(subrel_row) if v
                                    ]
                                )

                                rd[field_name] = {
                                    subrel_rd['channel_name']: {
                                        'id': subrel_rd['entry_id'],
                                        'slug': subrel_rd['url_title']
                                    }
                                }
                        else:
                            raise Exception(
                                'Unsupported relationship type "%s"' % rel_rd['rel_type']
                            )

                        continue

                if field_type == 'file':
                    fileurl = self.vars_replace(rd[field_name])
                    rd[field_name] = FileDownload(fileurl)
                    continue

                if field_type in ('social_update',):
                    del rd[field_name]
                    continue

            return rd

        return {}

    def select_site(self, name):
        for site in self._select('sites',
            site_name = name
        ):
            self._site = site
            return

        raise Exception('Site with name \'%s\' could not be found.' % name)

    def describe_site(self):
        self.describe(self._site, 'site',
            ('label', 'name', 'description'),
            end = False
        )

    def get_channels(self):
        for channel in self._select('channels', site_id = self._site['site_id']):
            yield channel

    def get_titles(self, channel, **kwargs):
        for title in self._select('channel_titles',
            site_id = self._site['site_id'],
            channel_id = channel,
            **kwargs
        ):
            yield title

    def get_title_categories(self, title):
        sql = 'SELECT t.entry_id, c.cat_name AS name, c.cat_url_title AS slug ' \
            'FROM %s AS c ' \
            'INNER JOIN %s AS t ON c.cat_id = t.cat_id ' \
            'WHERE t.entry_id = %%s ' \
            'ORDER BY t.entry_id, c.cat_url_title' % (
                self._prefix + 'categories',
                self._prefix + 'category_posts'
            )

        cursor = self._db.cursor()
        cursor.execute(sql, [title])

        fieldnames = [f[0] for f in cursor.description]
        for row in cursor.fetchall():
            yield dict(
                [
                    (
                        fieldnames[i],
                        v
                    ) for i, v in enumerate(row)
                ]
            )

    def get_author(self, id):
        if id in self._authors:
            return self._authors[id]

        for user in self._select('members',
            member_id = id
        ):
            self._authors[id] = user
            return user

        raise Exception('User with ID %d not found' % id)

    def _prepare(self, item, prefix, fields = [], aliases = {}, transformers = {}):
        def a(key):
            if key in aliases.keys():
                return aliases[key]

            return key

        def t(key, value):
            if key in transformers.keys():
                v = transformers[key](value)
                if isinstance(v, (list, tuple)):
                    return v

                return key, v

            return key, value

        nd = {}
        all_fields = list(fields) + aliases.keys() + transformers.keys()

        for key, value in item.items():
            if not value:
                continue

            if key in all_fields:
                k, v = t(a(key), value)
            elif key.startswith(prefix):
                if key[len(prefix) + 1:] in fields:
                    k, v = t(a(key[len(prefix) + 1:]), value)
                else:
                    continue
            elif not any(all_fields):
                k, v = t(a(key), value)
            else:
                continue

            nd[k] = v

        return nd

    def describe(self, item, prefix, fields = [], end = True, aliases = {}, transformers = {}, section_name = None):
        self._formatter.start_section(section_name or prefix)

        for key, value in self._prepare(item, prefix, fields, aliases, transformers).items():
            if isinstance(value, dict):
                self.describe(value, key)
            else:
                self._formatter.property(
                    key,
                    self.vars_replace(value)
                )

        if end:
            self._formatter.end_section()
        else:
            self._end_calls += 1

    def tidy(self, count = None):
        if count is None:
            while self._end_calls:
                self._formatter.end_section()
                self._end_calls -= 1
        else:
            while count and self._end_calls:
                self._formatter.end_section()
                self._end_calls -= 1
                count -= 1

    def parse_for_images(self, value, save_dir, domain = None, save_base = None):
        text = str(value)

        if save_base and not save_base.endswith('/'):
            save_base += '/'

        for match in IMG_REGEX.finditer(text, re.MULTILINE):
            groups = match.groups()
            for group in groups:
                if not group and not group.strip():
                    continue

                saved = self.save_download(
                    group, save_dir,
                    domain, save_base
                )

                if saved:
                    text = text.replace(group, saved)

        return text

    def save_download(self, url, save_dir, domain = None, save_base = None):
        if domain:
            old_url = urljoin('http://%s/' % domain, group)
        else:
            old_url = url
            if old_url.startswith('//'):
                old_url = 'http:%s' % old_url

            if not old_url.startswith('http:') and not old_url.startswith('https:'):
                return

            domain = urlparse(old_url).netloc

        if save_dir:
            new_filename = path.join(save_dir, *urlparse(old_url).path.split('/'))
            new_dir = path.join(*path.split(new_filename)[:-1])

            if not path.exists(new_dir):
                makedirs(new_dir)

            if not path.exists(new_filename):
                open(new_filename, 'web').write(
                    urlopen(old_url).read()
                )

        if save_base:
            return old_url.replace(
                'http://%s/' % domain,
                save_base
            ).replace(
                'https://%s/' % domain,
                save_base
            ).replace(
                '//%s/' % domain,
                save_base
            )

        return old_url

    def vars_replace(self, text):
        if not isinstance(text, (str, unicode)):
            return text

        for key, value in self._vars.items():
            if ('{%s}' % str(key)) in text:
                text = text.replace(
                    '{%s}' % key,
                    value
                )

        return text
