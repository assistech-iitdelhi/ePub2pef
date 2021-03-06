# -*- coding: utf-8 -*-


################ problems ############
# cant convert schwa
# bullet points
# bold
# underline
# proper whitespace
# Page divided vertically
# set the properties of pef file
# other languages
# detect characters that cant be converted
# detect maths or other html attributes
# removing command line call from python code
# run the code in windows
# check whether the conversion is correct
    # (a) use back_translate
    # (b) use diff to compare with another file
# check for pef reader
# option to add new table
###################################


##########how#to#install#############

##########windows########
# pip install louis-1.3
# download calibre for windows
# download pef plugin in calibre
#########################

##########linux##########
#########################

#####################################
"""
based on the TXTOutput plugin for Calibre by John Schember <john@nachtimwald.com
"""

import os
import shutil
import lxml.etree as etree
import lxml.builder    
import re
from dotify import charToDots
# os.chdir(os.path.abspath('..\\ui'))
import louis
# os.chdir(os.path.abspath('..\\calibre-pef-plugin-master'))

# namespaces
PEFNS = "http://www.daisy.org/ns/2008/pef" 
DCNS = "http://purl.org/dc/elements/1.1/"

from calibre.ebooks.metadata.meta import get_metadata, set_metadata
from calibre.rpdb import set_trace
from calibre.ebooks.txt.newlines import specified_newlines, TxtNewlines
from calibre.customize.conversion import OutputFormatPlugin, \
    OptionRecommendation
from calibre.ptempfile import TemporaryDirectory, TemporaryFile

NEWLINE_TYPES = ['system', 'unix', 'old_mac', 'windows']

class PEFOutput(OutputFormatPlugin):

    name = 'PEF Output'
    author = 'Matt Venn'
    file_type = 'pef'

    options = set([
        OptionRecommendation(name='newline', recommended_value='system',
            level=OptionRecommendation.LOW,
            short_switch='n', choices=NEWLINE_TYPES,
            help=_('Type of newline to use. Options are %s. Default is \'system\'. '
                'Use \'old_mac\' for compatibility with Mac OS 9 and earlier. '
                'For Mac OS X use \'unix\'. \'system\' will default to the newline '
                'type used by this OS.') % sorted(NEWLINE_TYPES)),
        OptionRecommendation(name='txt_output_encoding', recommended_value='utf-8',
            level=OptionRecommendation.LOW,
            help=_('Specify the character encoding of the output document. ' \
            'The default is utf-8.')),
        OptionRecommendation(name='table',
            recommended_value='UEBC-g2.ctb', level=OptionRecommendation.LOW,
            help=_('Specify braille converter table')),
        OptionRecommendation(name='inline_toc',
            recommended_value=False, level=OptionRecommendation.LOW,
            help=_('Add Table of Contents to beginning of the book.')),
        OptionRecommendation(name='num_rows',
            recommended_value=4, level=OptionRecommendation.LOW,
            help=_('The maximum number of rows per page, defaults to 4.')),
        OptionRecommendation(name='max_line_length',
            recommended_value=40, level=OptionRecommendation.LOW,
            help=_('The maximum number of characters per line. This splits on '
            'the first space before the specified value. If no space is found '
            'the line will be broken at the space after and will exceed the '
            'specified value. Also, there is a minimum of 25 characters. '
            'Use 0 to disable line splitting. Default is 40.')),
        OptionRecommendation(name='force_max_line_length',
            recommended_value=True, level=OptionRecommendation.LOW,
            help=_('Force splitting on the max-line-length value when no space '
            'is present. Also allows max-line-length to be below the minimum. '
            'Default true.')),
        OptionRecommendation(name='txt_output_formatting',
             recommended_value='plain',
             choices=['plain', 'markdown', 'textile'],
             help=_('Formatting used within the document.\n'
                    '* plain: Produce plain text.\n'
                    '* markdown: Produce Markdown formatted text.\n'
                    '* textile: Produce Textile formatted text.')),
        OptionRecommendation(name='keep_links',
            recommended_value=False, level=OptionRecommendation.LOW,
            help=_('Do not remove links within the document. This is only ' \
            'useful when paired with a txt-output-formatting option that '
            'is not none because links are always removed with plain text output.')),
        OptionRecommendation(name='keep_image_references',
            recommended_value=False, level=OptionRecommendation.LOW,
            help=_('Do not remove image references within the document. This is only ' \
            'useful when paired with a txt-output-formatting option that '
            'is not none because links are always removed with plain text output.')),
        OptionRecommendation(name='keep_color',
            recommended_value=False, level=OptionRecommendation.LOW,
            help=_('Do not remove font color from output. This is only useful when ' \
                   'txt-output-formatting is set to textile. Textile is the only ' \
                   'formatting that supports setting font color. If this option is ' \
                   'not specified font color will not be set and default to the ' \
                   'color displayed by the reader (generally this is black).')),
     ])

    def convert(self, oeb_book, output_path, input_plugin, opts, log):
        from calibre.ebooks.txt.txtml import TXTMLizer
        from calibre.utils.cleantext import clean_ascii_chars
        
        self.log = log

        if opts.txt_output_formatting.lower() == 'markdown':
            from calibre.ebooks.txt.markdownml import MarkdownMLizer
            self.writer = MarkdownMLizer(log)
        elif opts.txt_output_formatting.lower() == 'textile':
            from calibre.ebooks.txt.textileml import TextileMLizer
            self.writer = TextileMLizer(log)
        else:
            self.writer = TXTMLizer(log)

        txt = self.writer.extract_content(oeb_book, opts)

        txt = clean_ascii_chars(txt)

        log.debug('\tReplacing newlines with selected type...')
        txt = specified_newlines(TxtNewlines(opts.newline).newline, txt)
        txt = txt.encode(opts.txt_output_encoding, 'replace')
        # print 'BEFORE CONVERTING ...\n', txt, '\n..........'
        # if opts.table:
        # import louis
        newline_char = TxtNewlines(opts.newline).newline
        grade2 = ""
        # print txt
        # print 12, newline_char, len(txt.split(newline_char))
        # for line in txt.split(newline_char): #editted
        for line in txt.splitlines():

            trans = louis.translateString([opts.table], line)
            l = re.split(r"(\\[xX][0-9a-fA-F]+)", trans)
            l1 = []
            l2 = []
            for i in range(len(l)):
                if i%2 == 1:
                    # l1.append(unichr(l[i][3:-1]))
                    s = unichr(int(l[i][2:], 16))
                    line = line.replace(s, '*')
                    if(s in line):
                        print s, ' cannot be converted to braille, replaced by "*" without quotes'

                # else:
                #     l2.append(l[i])



            # grade2 += 
            # print '$$$$$$$$$$$$$$$' ,[opts.table]
            grade2 += louis.translateString([opts.table], line)
            grade2 += "\n"
        log.debug(grade2)
        txt = grade2
        # print txt
        # print 'AFTER CONVERTING ...\n', txt, '\n..........'

        log.debug('\tStripping final newline characters')
        txt = re.sub(TxtNewlines(opts.newline).newline + '*$', '', txt)
        
        log.debug('\tGenerating PEF...')
        metadata = oeb_book.metadata
        pef = self.create_pef(txt, opts, metadata)

        if not os.path.exists(os.path.dirname(output_path)) and os.path.dirname(output_path) != '':
            os.makedirs(os.path.dirname(output_path))

        import codecs
        fh = codecs.open(output_path, "w", "utf-8")
        fh.write(pef)


    def create_pef(self, txt, opts, metadata):
        newline_char = TxtNewlines(opts.newline).newline
         
        # setup PEF doc
        # http://files.pef-format.org/specifications/pef-2008-1/pef-specification.html
        pef = etree.Element('pef', nsmap = {None: PEFNS })
        tree = etree.ElementTree(pef)
 
        pef.set("version", "2008-1")
 
        head = etree.SubElement(pef, 'head')
        meta = etree.SubElement(head, 'meta', nsmap = {"dc" : DCNS})
 
        dc_format = etree.SubElement(meta, '{%s}format' % DCNS)
        dc_format.text = "application/x-pef+xml"
 
        dc_ident = etree.SubElement(meta, "{%s}identifier" % DCNS)
        dc_ident.text = "org.pef-format.00002"
 
        if len(metadata.title):
            title = metadata.title[0].value
            dc_title = etree.SubElement(meta, '{%s}title' % DCNS)
            dc_title.text = title
 
        if len(metadata.author):
            author = metadata.author[0].value
            dc_creator = etree.SubElement(meta, '{%s}creator' % DCNS)
            dc_creator.text = author
 
        body = etree.SubElement(pef, 'body')
 
        volume = etree.SubElement(body, 'volume')
        volume.set("cols", str(opts.max_line_length))
        volume.set("rows", str(opts.num_rows))
        volume.set("rowgap", str(0))
        volume.set("duplex", "true")
 
        section = etree.SubElement(volume, 'section')
        
        page_open = False
        rows = 0
        self.bad_chars = {}

        # for line in txt.split(newline_char): #edited
        for line in txt.splitlines():
            self.log.debug('got new line [%s]' % line)
            if rows % opts.num_rows == 0:
                page = etree.SubElement(section, 'page')
            try:
                row = etree.SubElement(page, 'row')
                stripped = line.strip()
                # pef = self.convert_to_pef(stripped)
                # row.text = ''.join(pef)
 
                row.text = charToDots([opts.table], stripped, len(stripped), mode=128)
                rows += 1
            except ValueError as e:
                print e
                print row.text
                self.log.info("can't convert [%s] to braille" % row.text)
                # self.bad_chars[row.text] = True
        # print "create_pef called .................................\n"
        return lxml.etree.tostring(tree, xml_declaration=True, encoding='UTF-8',pretty_print=True)

    # convert a single alpha, digit or some punctuation to 6 pin braille
    # http://en.wikipedia.org/wiki/Braille_ASCII#Braille_ASCII_values
    # def alpha_to_pef(self, alpha):
    #     mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    #     alpha = alpha.upper()
    #     try:
    #         pin_num = mapping.index(alpha)
    #         return unichr(pin_num+10240)
    #     except ValueError as e:
    #         if not self.bad_chars.has_key(alpha):
    #             self.log.info("can't convert [%s] to braille" % alpha)
    #             self.bad_chars[alpha] = True
    #         return unichr(10240)

    # # convert a list of alphas to pef unicode
    # def convert_to_pef(self, alphas):
    #     return map(self.alpha_to_pef, alphas)

