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
        zotero_fpath = expanduser('~/AppData/Roaming/Zotero/Zotero/Profiles/xrmkwlkz.default/zotero')
    return zotero_fpath


def get_libzotero():
    #import pygnotero
    zotero_fpath = get_zotero_path()
    from pygnotero import libzotero
    #zotero_folder = "/home/sebastiaan/Zotero"
    zotero = libzotero.libzotero(zotero_fpath)
    return zotero


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
    #ut.util_sqlite.get_tablenames(cur)
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
