import louis
from ctypes import *
import struct
import atexit
import sys



liblouis = louis.liblouis

liblouis.lou_charToDots.argtypes = (
	c_char_p, c_wchar_p, c_wchar_p, c_int, c_int)

# Some general utility functions
def _createTablesString(tablesList):

	"""Creates a tables string for liblouis calls"""
	return b",".join([x.encode("ASCII") if isinstance(x, str) else bytes(x) for x in tablesList])


def charToDots(tableList, inbuf, length, mode = 0):
	tablesString = _createTablesString(tableList)
	inbuf = louis.createStr(inbuf)
	inlen = c_int(len(inbuf))
	outlen = c_int(inlen.value*louis.outlenMultiplier)
	outbuf = louis.create_unicode_buffer(outlen.value)
	typeformbuf = None

	liblouis.lou_charToDots(tablesString, inbuf, outbuf, length, mode)

	return outbuf.value


if __name__ == "__main__":
	# t =  charToDots([b'UEBC-g2.ctb'], 'Hello World!', 11, 128)
	# s = unichr(0x20AC)
	# s = open('uni_check.txt').read()
	# s = unicode(s)
	# print type(s[0])
	import codecs
	f = codecs.open('test.txt', encoding='utf-8')
	s = f.read()
	f.close()
	t1 = louis.translateString([b'UEBC-g2.ctb'], s, mode=128)
	t = charToDots([b'UEBC-g2.ctb'], t1, len(t1), mode=128)
	f = codecs.open('test_br.txt', 'w', encoding='utf-8')
	f.write(t1)
	f.close()


	# print s