import xrilib
import unittest

class TestIsXri(unittest.TestCase):
	bare_cases = (
		# GCS
		("@", (True, "@")),
		("=", (True, "=")),
		("!", (True, "!")),
		("$", (True, "$")),
		("+", (True, "+")),

		# non GCS
		("*", (False, None)),
		("#", (False, None)),

		# simple positive
		("@xrid", (True, "@xrid")),
		("=wil", (True, "=wil")),
		("=wil*foo", (True, "=wil*foo")),
		("$res*auth*($v*2.0)", (True, "$res*auth*($v*2.0)")),
		
		# simple negatives
		("", (False, None)),
		(".", (False, None)),
		("/", (False, None)),
		("//", (False, None)),
		("xri://", (False, None)),
		("foo", (False, None)),
		("*bar", (False, None)),
		(u"baz", (False, None)),

		# phishing
		(u"\uFF20", (False, None)), # fullwidth commercial AT
	)


	def testBareXri(self):
		for input, expected in self.bare_cases:
			result = xrilib.is_xri(input, allow_bare=True, detect_subscheme=False, allow_xri_scheme=False)
			self.assertEqual(result, expected)

	def testSubScheme(self):
		for prefix in xrilib.SUBSCHEME_PREFIXES:
			for input, (ex_r, ex_v) in self.bare_cases:
				#print "Testing %s%s" % (prefix, input)
				input = prefix + input
				r, v = xrilib.is_xri(input, allow_bare=False, detect_subscheme=True, allow_xri_scheme=False)
				self.assertEqual((r, v), (ex_r, ex_v))

	def testXriScheme(self):
		for input, expected in self.bare_cases:
			#print "Testing xri://%s" % (input)
			result = xrilib.is_xri("xri://%s" % input, allow_bare=False, detect_subscheme=False, allow_xri_scheme=True)
			self.assertEqual(result, expected)


class TestConversion(unittest.TestCase):
	def testXRItoIRI(self):
		i = "xri://@example.com/(@example/abc%2Fd/ef)"
		e = "xri://@example.com/(@example%2Fabc%252Fd%2Fef)"
		self.assertEqual(xrilib.xri_to_iri(i), e)

		# han
		i = u"=\u8B19"
		e = i
		self.assertEqual(xrilib.xri_to_iri(i), e)


	def testIRItoURI(self):
		# ascii
		i = "@xri"
		e = "@xri"
		self.assertEqual(xrilib.iri_to_uri(i), e)

		# han
		i = u"=\u8B19"
		e = "=%E8%AC%99"
		self.assertEqual(xrilib.iri_to_uri(i), e)

		# percent encoding (unchanged)
		i = "http://www.example.org/D%FCrst"
		e = i
		self.assertEqual(xrilib.iri_to_uri(i), e)


if __name__ == "__main__":
	unittest.main()
