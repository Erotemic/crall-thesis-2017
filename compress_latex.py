#!/usr/bin/env python
import sys
import utool as ut
from os.path import join, dirname, abspath, basename


#def find_ghostscript_exe():
#    if ut.WIN32:
#        gs_exe = r'C:\Program Files (x86)\gs\gs9.16\bin\gswin32c.exe'
#    else:
#        gs_exe = 'gs'
#    return gs_exe


#def compress_pdf(pdf_fpath, output_fname=None):
#    """ uses ghostscript to write a pdf """
#    ut.assertpath(pdf_fpath)
#    suffix = '_' + ut.get_datestamp(False) + '_compressed'
#    print('pdf_fpath = %r' % (pdf_fpath,))
#    output_pdf_fpath = ut.augpath(pdf_fpath, suffix, newfname=output_fname)
#    print('output_pdf_fpath = %r' % (output_pdf_fpath,))
#    gs_exe = find_ghostscript_exe()
#    cmd_list = (
#        gs_exe,
#        '-sDEVICE=pdfwrite',
#        '-dCompatibilityLevel=1.4',
#        '-dNOPAUSE',
#        '-dQUIET',
#        '-dBATCH',
#        '-sOutputFile=' + output_pdf_fpath,
#        pdf_fpath
#    )
#    ut.cmd(*cmd_list)
#    return output_pdf_fpath

if __name__ == '__main__':
    """
    CommandLine:
        ./compress_latex.py
    """
    if len(sys.argv) == 1:
        abs_file = abspath(__file__)

        pdf_fpath = join(dirname(abs_file), 'main.pdf')
        output_fname = basename(dirname(abs_file))
        import re
        output_fname = re.sub('\d', '', output_fname).strip('-').strip('_')
    else:
        pdf_fpath = sys.argv[1]
        output_fname = None
    output_pdf_fpath = ut.compress_pdf(pdf_fpath, output_fname=output_fname)

    PUBLISH = True
    if PUBLISH:
        publish_path = ut.truepath('~/Dropbox/crall')
        ut.copy(output_pdf_fpath, publish_path)
