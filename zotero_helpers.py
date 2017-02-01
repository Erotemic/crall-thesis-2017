# -*- coding: utf-8 -*-
"""
References:

    pip install pygnotero
    pip install git+https://github.com/smathot/Gnotero.git

    pip install mozrepl
"""
from __future__ import absolute_import, division, print_function
#import re
import utool as ut


def get_zotero_path():
    from os.path import expanduser
    if ut.get_computer_name().lower() == 'hyrule':
        zotero_fpath = expanduser('~/.zotero/zotero/a4dxx4ff.default/zotero')
    elif ut.get_computer_name().lower() == 'ooo':
        zotero_fpath = expanduser('~/.zotero/zotero/a4dxx4ff.default/zotero')
        # zotero_fpath = expanduser('~/AppData/Roaming/Zotero/Zotero/Profiles/xrmkwlkz.default/zotero')
    return zotero_fpath


def get_libzotero():
    #import pygnotero
    zotero_fpath = get_zotero_path()
    from pygnotero import libzotero
    #zotero_folder = "/home/sebastiaan/Zotero"
    zotero = libzotero.libzotero(zotero_fpath)
    return zotero


def clean_tags():
    zotero = get_libzotero()
    # dict of all zotero items
    # items = zotero.index
    # get sql cursor
    cur = zotero.cur
    if False:
        sorted(ut.util_sqlite.get_tablenames(cur))
        ut.print_database_structure(cur)
        # Debug info about tags table in sql

        # The `tags` table stores all tags
        # The itemTags table stores the association between items and tags
        ut.get_table_columninfo_list(cur, 'fields')
        # ut.get_table_columninfo_list(cur, 'relations')
        ut.get_table_columninfo_list(cur, 'fieldsCombined')

        ut.get_table_columninfo_list(cur, 'itemData')
        ut.get_table_columninfo_list(cur, 'itemDataValues')

        ut.get_table_columninfo_list(cur, 'tags')
        ut.get_table_columninfo_list(cur, 'itemTags')

    import pandas as pd
    pd.options.display.max_colwidth = 40
    pd.options.display.max_rows = 20
    def pandas_sql(table, columns):
        return pd.DataFrame(ut.get_table_rows(cur, table, columns),
                            columns=columns)

    item_df = pandas_sql('items', ('itemID', 'itemTypeID', 'libraryID', 'key')).set_index('itemID', drop=False)
    tags_df = pandas_sql('tags', ('tagID', 'name', 'type', 'libraryID', 'key')).set_index('tagID', drop=False)
    itemData_df = pandas_sql('itemData', ('itemID', 'fieldID', 'valueID'))

    itemTag_df = pandas_sql('itemTags', ('itemID', 'tagID'))

    itemDataValues_df = pandas_sql('itemDataValues', ('valueID', 'value')).set_index('valueID')
    field_df = pandas_sql('fields', ('fieldID', 'fieldName', 'fieldFormatID')).set_index('fieldID')

    itemData_df['value'] = itemDataValues_df['value'].loc[itemData_df['valueID'].values].values
    itemData_df['fieldName'] = field_df['fieldName'].loc[itemData_df['fieldID'].values].values

    titles = itemData_df[itemData_df['fieldName'] == 'title']
    assert len(ut.unique(ut.map_vals(len, titles.groupby('itemID').indices).values())) == 1

    # itemTag_df.groupby('itemID').count()
    # Find how often each tag is used
    tagid_to_count = itemTag_df.groupby('tagID').count()
    tagid_to_count = tagid_to_count.rename(columns={'itemID': 'nItems'})
    tagid_to_count['name'] = tags_df.loc[tagid_to_count.index]['name']
    tagid_to_count = tagid_to_count.sort_values('nItems')

    bad_tags = tagid_to_count[tagid_to_count['nItems'] == 1]

    tagid_to_count['tag_ncharsize'] = tagid_to_count['name'].apply(len)
    tagid_to_count = tagid_to_count.sort_values('tag_ncharsize')
    bad_tags = tagid_to_count[tagid_to_count['tag_ncharsize'] > 25]['name'].values.tolist()

    def clean_tags2():
        api_key = 'fBDBqRPwW9O3mYyNLiksBKZy'
        base_url = 'https://api.zotero.org'
        library_id = '1279414'
        library_type = 'user'
        from pyzotero import zotero
        zot = zotero.Zotero(library_id, library_type, api_key)

        for chunk in ut.ProgChunks(bad_tags, 50):
            zot.delete_tags(*chunk)

    if False:
        api_key = 'fBDBqRPwW9O3mYyNLiksBKZy'
        base_url = 'https://api.zotero.org'
        user_id = '1279414'
        userOrGroupPrefix = '/users/' + user_id
        params = {'v': 3, 'key': api_key}

        items_resp = requests.get(base_url + userOrGroupPrefix + '/items', params=params)
        print(items_resp.content)
        print(items_resp)

        json_tags = []
        get_url = base_url + userOrGroupPrefix + '/tags'
        while True:
            print('get_url = %r' % (get_url,))
            tag_resp = requests.get(get_url, params=params)
            if tag_resp.status_code != 200:
                break
            json_tags.extend(tag_resp.json())
            if 'next' in tag_resp.links:
                get_url = tag_resp.links['next']['url']
            else:
                break

        version_to_tags = ut.ddict(list)
        bad_tags = []
        for tag in ut.ProgIter(json_tags, label='parsing tags'):
            # x = requests.get(tag['links']['self']['href'], params=params)
            if tag['meta']['numItems'] == 1:
                import urllib2
                try:
                    bad_tags.append(urllib2.quote(tag['tag']))
                except Exception as ex:
                    print('cant encode tag=%r' % (tag,))
                    pass

        for chunk in ut.ProgIter(ut.ichunks(bad_tags, 50), length=len(bad_tags) / 50):
            search_url = base_url + userOrGroupPrefix + '/items?tag=' + ' || '.join(chunk)
            r = requests.get(search_url, params=params)
            matching_items = r.json()
            # assert len(matching_items) == 1
            for item in matching_items:
                version = item['version']
            version_to_tags[item['version']].append(tag['tag'])

        # DELETE MULTIPLE TAGS
        import requests
        for chunk in ut.ichunks(bad_tags['name'], 50):
            import urllib2
            encoded_chunk = []
            for t in chunk:
                try:
                    encoded_chunk.append(urllib2.quote(t))
                except Exception:
                    print(t)
            suffix = ' || '.join(encoded_chunk)
            delete_url = base_url + userOrGroupPrefix + '/tags?' + suffix
            print('delete_url = %r' % (delete_url,))
            resp = requests.delete(delete_url, params=params)

        bad_tags = tagid_to_count[tagid_to_count['nItems'] == 1]
        bad_tags['tagID'] = bad_tags.index
        for tagid in bad_tags:
            delete from itemTags where tagID in (select tagID from tags where type=1);
        pass
        for name in k['name'].values.tolist()
    item_df['title'] = titles.set_index('itemID')['value']
    for idx, item in zotero.index.items():
        sql_title = item_df.loc[item.id]['title']
        if item.title != sql_title:
            if pd.isnull(sql_title) and item.title is not None:
                print(item.__dict__)
                print(item_df.loc[item.id])
                print('item.title = %r' % (item.title,))
                print('sql_title = %r' % (sql_title,))
                assert False

    duplicate_tags = [
        (name, idxs) for name, idxs in tags_df.groupby('name', sort=True).indices.items() if len(idxs) > 2
    ]
    tagname_to_tagid = tags_df.groupby('name', sort=True).first()
    new_to_oldtags = {}
    # Determine which tagi to use for each name
    for tagname, idxs in duplicate_tags:
        tags_subdf = tags_df.iloc[idxs]
        mapping = itemTag_df[itemTag_df['tagID'].isin(tags_subdf['tagID'])]
        tag_hist = mapping.groupby('tagID').count()
        best_tagid = tag_hist['itemID'].idxmax()

        new_to_oldtags[best_tagid] = set(tag_hist['itemID'].values) - {best_tagid}

        tagname_to_tagid.loc[tagname] = tags_df.loc[best_tagid]
        # for col in tagname_to_tagid.columns:
        #     tagname_to_tagid.loc[tagname][col] = tags_df.loc[best_tagid][col]
        # tags_df.loc[best_tagid]

    if False:
        # Update tagIds
        for newid, oldids in new_to_oldtags.items():
            for oldid in oldids:
                # cur.execute('SELECT itemID, tagID FROM itemTags WHERE tagID=?', (oldid,))
                import sqlite3
                try:
                    cmd = 'UPDATE itemTags SET tagID=? WHERE tagID=?'
                    args = (newid, oldid)
                    print('(%s) args = %r' % (cmd, args,))
                    cur.execute(cmd, args)
                    print(cur.fetchall())
                except sqlite3.IntegrityError:
                    print('error')
                    pass

    # tags_df.groupby('name', sort=True)

    # itemTag_df.groupby('itemID')
    # duptags = tags_df.iloc[tags_df.groupby('name', sort=True).indices['animals']]
    # duptags['tagID']
    # flags = itemTag_df['tagID'].isin(duptags['tagID'])
    # dup_rel = itemTag_df[flags]
    # item_df['title'].loc[dup_rel['itemID']].values
    # tags_df.iloc[tags_df.groupby('name', sort=True).indices['animals']]

    # tags_df[tags_df['type'] == 1]
    # tags_df[tags_df['type'] == 0]
    # tags_df['libraryID'].unique()
    # tags_df['type'].unique()

    '''
    SELECT
    SELECT FROM itemTags WHERE name in (animals)
    '''

    item_tag_pairs = ut.get_table_rows(cur, 'itemTags', ('itemID', 'tagID'))
    # Group tags by item
    itemid_to_tagids = ut.group_pairs(item_tag_pairs)
    # Group items by tags
    tagid_to_itemids = ut.group_pairs(map(tuple, map(reversed, item_tag_pairs)))

    # mapping from tagid to name
    tagid_to_name = dict(ut.get_table_rows(cur, 'tags', ('tagID', 'name')))

    tagid_freq = list(ut.sort_dict(ut.map_vals(len, tagid_to_itemids), 'vals').items())
    ut.sort_dict(ut.map_vals(sum, ut.group_pairs([(freq, tagid_to_name.get(tagid, tagid)) for tagid, freq in tagid_freq])), 'vals')
    tagname_freq = ut.map_keys(lambda k: tagid_to_name.get(k, k), tagid_freq)


def get_item_resource():
    """
    from zotero_helpers import *
    """
    #item_list = zotero.search('Distinctive Image Features from Scale-Invariant Keypoints')
    #item_list = zotero.search('lowe_distinctive_2004')

    zotero_fpath = get_zotero_path()
    from os.path import join

    # FIND THE BIBTEX ITEMID
    import sqlite3
    bibsql = join(zotero_fpath, 'betterbibtex.sqlite')
    con = sqlite3.connect(bibsql)
    cur = con.cursor()
    # ut.util_sqlite.get_tablenames(cur)
    #ut.util_sqlite.print_database_structure(cur)
    itemID = ut.util_sqlite.get_table_rows(cur, 'keys', 'itemID', where='citekey=?', params='lowe_distinctive_2004')
    con.close()
    ###############

    zotero = get_libzotero()
    item = zotero.index[itemID]
    cur = zotero.cur   # NOQA

    zotero.index[1434].title

    # ENTIRE DATABASE INFO
    ut.print_database_structure(cur)

    # FIND WHERE ATTACHMENT EXITS
    for tablename in ut.get_tablenames(cur):
        try:
            x = ut.get_table_csv(cur, tablename).find('ijcv04.pdf')
        except Exception as ex:
            continue
        if x != -1:
            print(tablename)
            print(x)
    tablename = 'itemDataValues'
    print(ut.truncate_str(ut.get_table_csv(cur, tablename), maxlen=5000))

    tablename = 'itemDataValues'
    column_list = ut.get_table_columns(cur, tablename)

    import six
    for column in column_list:
        for rowx, row in enumerate(column):
            if isinstance(row, six.string_types):
                if row.find('ijcv04.pdf') > -1:
                    print(rowx)
                    print(row)
    valueID = column_list[0][3003]
    value = column_list[1][3003]

    ut.util_sqlite.get_table_rows(cur, 'itemData', None, where='valueID=?', params=valueID, unpack=False)

    ###

    #ut.rrrr()
    tablename = 'itemAttachments'
    colnames = tuple(ut.get_table_columnname_list(cur, tablename))


    print(ut.get_table_csv(cur, tablename, ['path']))
    _row_list = ut.get_table_rows(cur, tablename, 'itemID', unpack=True)
    ut.get_table_rows(cur, tablename, colnames, unpack=False)
    ut.get_table_num_rows(cur, tablename)
    itemID = ut.util_sqlite.get_table_rows(cur, tablename, colnames, where='itemID=?', params=itemID, unpack=False)


def test_libzoter():
    zotero = get_libzotero()
    item_list = zotero.search('')
    for item in item_list:
        print(item.title)
        pass
    if False:
        #set(ut.flatten([dir(x) for x in item_list]))
        item_list = zotero.search('Combining Face with Face-Part Detectors under Gaussian Assumption')
        [x.simple_format() for x in item_list]
        item_list = zotero.search('Lowe')

    if False:
        import mozrepl
        repl = mozrepl.Mozrepl(4242, u'localhost')  # NOQA
        temp_fpath = 'foo.txt'
        repl.connect(4242, u'localhost')
        r"""
        http://www.curiousjason.com/zoterotobibtex.html
        https://github.com/bard/mozrepl/wiki
        "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" -profile "C:\Users\joncrall\AppData\Roaming\Mozilla\Firefox\Profiles\7kadig32.default" -repl 4242
        telnet localhost 4242

        """

        execute_string = unicode(ut.codeblock(
            r'''
            filename = '%s';
            var file = Components.classes["@mozilla.org/file/local;1"].createInstance(Components.interfaces.nsILocalFile);
            file.initWithPath(filename);
            var zotero = Components.classes['@zotero.org/Zotero;1'].getService(Components.interfaces.nsISupports).wrappedJSObject;
            var translatorObj = new Zotero.Translate('export');
            translatorObj.setLocation(file);
            translatorObj.setTranslator('9cb70025-a888-4a29-a210-93ec52da40d4');
            translatorObj.translate();
            ''') % (temp_fpath))
        print(execute_string)
        repl.execute(execute_string)


def test_zotero_sql():
    r"""
    "C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
    "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" -profile "C:\Users\joncrall\AppData\Roaming\Mozilla\Firefox\Profiles\7kadig32.default" -repl 4242

    References:
        http://www.cogsci.nl/blog/tutorials/97-writing-a-command-line-zotero-client-in-9-lines-of-code
        https://forums.zotero.org/discussion/2919/command-line-export-to-bib-file/
        http://www.curiousjason.com/zoterotobibtex.html

        https://addons.mozilla.org/en-US/firefox/addon/mozrepl/

        # bibtex plugin
        https://github.com/ZotPlus/zotero-better-bibtex

        https://groups.google.com/forum/#!forum/zotero-dev

    Ignore:
        C:\Users\joncrall\AppData\Roaming\Zotero\Zotero\Profiles\xrmkwlkz.default\zotero\translators
    """

    cur = zotero.cur   # NOQA
    #ut.rrrr()
    # ENTIRE DATABASE INFO
    ut.print_database_structure(cur)

    tablename_list = ut.get_tablenames(cur)
    colinfos_list = [ut.get_table_columninfo_list(cur, tablename) for tablename in tablename_list]   # NOQA
    numrows_list = [ut.get_table_num_rows(cur, tablename) for tablename in tablename_list]    # NOQA

    tablename = 'items'
    colnames = ('itemID',)   # NOQA
    colinfo_list = ut.get_table_columninfo_list(cur, tablename)  # NOQA

    itemtype_id_list = ut.get_table_rows(cur, 'items', ('itemTypeID',))

    ut.get_table_columninfo_list(cur, 'itemTypeFields')

    ut.get_table_rows(cur, 'itemTypeFields', ('fieldID',), where='itemTypeID=?', params=itemtype_ids)   # NOQA
    ut.get_table_rows(cur, 'itemTypeFields', ('orderIndex',), where='itemTypeID=?', params=itemtype_ids)   # NOQA

    ut.get_table_rows(cur, 'itemTypeFields', ('',), where='itemTypeID=?', params=itemtype_ids)   # NOQA

    itemData   # NOQA

    # Item Table INFO
    ut.get_table_columninfo_list(cur, 'tags')
    ut.get_table_columninfo_list(cur, 'items')
    ut.get_table_columninfo_list(cur, 'itemTypeFields')
    ut.get_table_columninfo_list(cur, 'itemData')
    ut.get_table_columninfo_list(cur, 'itemDataValues')
    ut.get_table_columninfo_list(cur, 'fields')
    ut.get_table_columninfo_list(cur, 'fieldsCombined')

    ut.get_table_rows(cur, 'fields', ('fieldName',))

    # The ID of each item in the database
    itemid_list = ut.get_table_rows(cur, 'items', ('itemID',))
    # The type of each item
    itemtype_id_list = ut.get_list_column(ut.get_table_rows(cur, 'items', ('itemTypeID',), where='itemID=?', params=itemid_list), 0)

    # The different types of items
    itemtype_ids = list(set(itemtype_id_list))

    # The fields of each item type
    fieldids_list_ = ut.get_table_rows(cur, 'itemTypeFields', ('fieldID',), where='itemTypeID=?', params=itemtype_ids)
    orderids_list_ = ut.get_table_rows(cur, 'itemTypeFields', ('orderIndex',), where='itemTypeID=?', params=itemtype_ids)
    fieldids_list = [ut.sortedby(f, o) for f, o in zip(fieldids_list_, orderids_list_)]

    itemtypeid2_fields = dict(zip(itemtype_ids, fieldids_list))

    itemid_fieldids_list = [[(itemID[0], fieldID[0]) for fieldID in itemtypeid2_fields[itemTypeID]] for itemID, itemTypeID in list(zip(itemid_list, itemtype_id_list))[0:7]]
    flat_list, cumsum_list = ut.invertible_flatten2(itemid_fieldids_list)
    # Get field values
    flat_valueID_list = ut.get_table_rows(cur, 'itemData', ('valueID',), where='itemID=? and fieldID=?', params=flat_list)
    valueIDs_list = ut.unflatten2(flat_valueID_list, cumsum_list)

    filtered_itemid_fieldids_list = [[if_ for if_, v in zip(ifs, vs) if len(v) > 0] for ifs, vs in zip(itemid_fieldids_list, valueIDs_list)]

    filtered_flat_list, filtered_cumsum_list = ut.invertible_flatten2(filtered_itemid_fieldids_list)
    # Get field values
    filt_flat_valueID_list = ut.get_table_rows(cur, 'itemData', ('valueID',), where='itemID=? and fieldID=?', params=filtered_flat_list)
    filt_flat_valueID_list_ = ut.get_list_column(filt_flat_valueID_list, 0)
    filt_flat_fieldname_list = ut.get_table_rows(cur, 'fields', ('fieldName',), where='fieldID=?', params=ut.get_list_column(filtered_flat_list, [1]))
    filt_flat_value_list = ut.get_table_rows(cur, 'itemDataValues', ('value',), where='valueID=?', params=filt_flat_valueID_list_)   # NOQA
    #

    filt_fieldname_list = ut.unflatten2(filt_flat_fieldname_list, filtered_cumsum_list)   # NOQA
    filt_valueIDs_list = ut.unflatten2(filt_flat_valueID_list, filtered_cumsum_list)  # NOQA

    ut.get_table_rows(cur, 'itemTypeFields', ('fieldID', 'orderIndex'), where='itemTypeID=?', params=itemtype_ids)

    all_values = ut.get_list_column(ut.get_table_rows(cur, 'itemDataValues', ('value',)), 0)
    import re
    import six
    for value in all_values:
        if isinstance(value, six.string_types) and re.search('CVPR', value):
            print(value)
    #key_list = ut.get_table_rows(cur, 'items', 'key')
    #libid_list = ut.get_table_rows(cur, 'items', 'libraryID')
