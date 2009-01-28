import urlparse

"""
This module provides XRI parsing functionality.
"""

XRI_SCHEME = "xri://"
SUBSCHEME_PREFIXES = ["http://xri.net/", "https://xri.net/"]
GCS_SYMBOLS = "@=!$+"



is_ucschar_or_iprivate = lambda c: (
	(c >= 0xA0 and c <= 0xD7FF) or
	(c >= 0xE000 and c <= 0xF8FF) or # iprivate
	(c >= 0xF900 and c <= 0xFDCF) or
	(c >= 0xFDF0 and c <= 0xFFEF) or
	(c >= 0x10000 and c <= 0x1FFFD) or
	(c >= 0x20000 and c <= 0x2FFFD) or
	(c >= 0x30000 and c <= 0x3FFFD) or
	(c >= 0x40000 and c <= 0x4FFFD) or
	(c >= 0x50000 and c <= 0x5FFFD) or
	(c >= 0x60000 and c <= 0x6FFFD) or
	(c >= 0x70000 and c <= 0x7FFFD) or
	(c >= 0x80000 and c <= 0x8FFFD) or
	(c >= 0x90000 and c <= 0x9FFFD) or
	(c >= 0xA0000 and c <= 0xAFFFD) or
	(c >= 0xB0000 and c <= 0xBFFFD) or
	(c >= 0xC0000 and c <= 0xCFFFD) or
	(c >= 0xD0000 and c <= 0xDFFFD) or
	(c >= 0xE0000 and c <= 0xEFFFD) or
	(c >= 0xF0000 and c <= 0xFFFFD) or # iprivate
	(c >= 0x100000 and c <= 0x10FFFD)) # iprivate


def strip_prefix(xri_str, subscheme_prefixes=SUBSCHEME_PREFIXES, xri_scheme=True):
	"""
	Removes the given xri_scheme and/or subscheme_prefixes from the input string.
	The input string is not parsed or validated. The string is returned verbatim
	if no xri_scheme or prefixes is found.
	"""
	xri_str_lower = xri_str.lower()

	if xri_scheme:
		if xri_str_lower[:6] == "xri://":
			return xri_str[6:]

	if subscheme_prefixes:
		for prefix in subscheme_prefixes:
			if xri_str_lower.startswith(prefix):
				return xri_str[len(prefix):]

	return xri_str


def parse_bare_xri_unf(xri_str):
	"""
	Parses the input string assuming that it is a bare XRI in URI normal form.

	Input string must be all ASCII only. If the input is a unicode object,
	it will be encoded using the 'ascii' codec. If the input is a str object,
	it will first be converted to unicode using the default system codec,
	and back to a str using the 'ascii' codec. Therefore, it is better to
	pass in unicode.

	Returns (authority, path, query, fragment)
	"""

	# ensure ASCII only
	xri_str = xri_str.encode('ascii')

	# XXX: this depends on internal behavior of urlparse, which isn't rfc3986 compliant
	# XXX: yes, I know it's a hack.
	
	# It can't tell the difference between a component that is missing vs. empty
	url = "http://%s" % xri_str
	(sc, authority, path, query, frag) = urlparse.urlsplit(url)
	return (authority, path, query, frag)


def parse_bare_xri_inf(iri_str):
	parse_bare_xri_unf(iri_to_uri(iri_str))


def parse_bare_xri_xnf(xri_str):
	parse_bare_xri_inf(xri_to_iri(xri_str))



def parse_xri(xri_str, subscheme_prefixes=SUBSCHEME_PREFIXES, xri_scheme=True):
	return parse_bare_xri_unf(strip_prefix(xri_str, subscheme_prefixes, xri_scheme))



def xri_to_iri(s):
	# percent encode all % as %25
	# percent encode all #?/ in cross reference as %2F
	out = []
	xref_level = 0
	for c in s:
		if c == '%':
			out.append('%25')
		else:
			if xref_level:
				if   c == '/':
					out.append('%2F')
				elif c == '?':
					out.append('%3F')
				elif c == '#':
					out.append('%23')
				else:
					out.append(c)
			else:
				out.append(c)

		if c == '(':
			xref_level = xref_level + 1
		elif c == ')' and xref_level > 0:
			xref_level = xref_level - 1

	return ''.join(out)


def iri_to_uri(s):
	if type(s) != unicode:
		s = s.decode()

	out = []
	for c in s:
		if is_ucschar_or_iprivate(ord(c)):
			utf8 = c.encode('utf-8')
			out = out + ["%%%02X" % ord(u) for u in utf8]
		else:
			out.append(c)

	return ''.join(out)


def uri_to_iri(s):
	# XXX: unimplemented
	return s

def iri_to_xri(s):
	# XXX: unimplemented
	return s

def is_xri(
		s,
		allow_bare=True,
		detect_subscheme=True,
		subscheme_prefixes=SUBSCHEME_PREFIXES,
		allow_xri_scheme=True,
		gcs_symbols=GCS_SYMBOLS):
	"""
	Perform simple tests to guess if the input string is an XRI.
	Input can be unicode or str.
	No validity check is done, except that it can't be an empty string.
	Result is a tuple of type (boolean, string), where the first
	element is True if the input string appears to be an XRI,
	and the second element is the bare XRI stripped of any
	(sub)scheme if allowed by the options.
	If first element is False, the second element is undefined.
	"""
	stripped = strip_prefix(s,
			subscheme_prefixes=subscheme_prefixes if detect_subscheme else [],
			xri_scheme=allow_xri_scheme)

	if not allow_bare and len(stripped) == len(s):
		# at least something should be stripped if allow_bare is not True
		return False, None

	first = stripped[:1]
	if len(first) > 0 and first in gcs_symbols:
		return True, stripped

	# XXX should we test IRI-authority and XRef-authority?
	return False, None

