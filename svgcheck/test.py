import pycodestyle
import unittest
import os
import shutil
import lxml.etree
import subprocess
import six
import sys
from rfctools_common.parser import XmlRfcParser
from rfctools_common.parser import XmlRfcError
from rfctools_common import log
import difflib
from svgcheck.checksvg import checkTree
import io


class TestParserMethods(unittest.TestCase):

    def test_pycodestyle_conformance(self):
        """Test that we conform to PEP8."""
        pep8style = pycodestyle.StyleGuide(quiet=False, config_file="pycode.cfg")
        result = pep8style.check_files(['run.py', 'checksvg.py', 'word_properties.py',
                                        'test.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_circle(self):
        """ Tests/circle.svg: Test a simple example with a small number of required edits """
        test_svg_file(self, "circle.svg")

    def test_rbg(self):
        """ Tests/rgb.svg: Test a simple example with a small number of required edits """
        test_svg_file(self, "rgb.svg")

    def test_dia_sample(self):
        """ Tests/dia-sample-svg.svg: Generated by some unknown program """
        test_svg_file(self, "dia-sample-svg.svg")

    def test_drawberry_sample(self):
        """ Tests/drawberry-sample-2.svg: Generated by DrawBerry """
        test_svg_file(self, "DrawBerry-sample-2.svg")

    def test_example_dot(self):
        """ Tests/example-dot.svg """
        test_svg_file(self, "example-dot.svg")

    def test_httpbis_proxy(self):
        """ Tests/httpbis-proxy20-fig6.svg """
        test_svg_file(self, "httpbis-proxy20-fig6.svg")

    def test_ietf_test(self):
        """ Tests/IETF-test.svg """
        test_svg_file(self, "IETF-test.svg")

    def test_svg_wordle(self):
        """ Tests/svg-wordle.svg """
        test_svg_file(self, "svg-wordle.svg")

    @unittest.skipIf(os.name != 'nt', "xi:include does not work correctly on Linux")
    def test_rfc(self):
        """ Tests/rfc.xml: Test an XML file w/ two pictures """
        test_rfc_file(self, "rfc.xml")

    def test_simple_sub(self):
        check_process(self, [sys.executable, "run.py", "--out=Temp/rfc.xml",
                             "--repair", "--no-xinclude", "Tests/rfc.xml"],
                      "Results/rfc-01.out", "Results/rfc-01.err",
                      "Results/rfc-01.xml", "Temp/rfc.xml")

    def test_to_stdout(self):
        check_process(self, [sys.executable, "run.py", "--repair", "--no-xinclude",
                             "Tests/rfc.xml"], "Results/rfc-02.out", "Results/rfc-02.err",
                      None, None)

    def test_to_quiet(self):
        check_process(self, [sys.executable, "run.py", "--no-xinclude", "--quiet",
                             "Tests/rfc.xml"], "Results/rfc-03.out",
                      "Results/rfc-03.err", None, None)

    def test_rfc_complete(self):
        check_process(self, [sys.executable, "run.py", "--repair", "Tests/rfc-svg.xml"],
                      "Results/rfc-svg.out", "Results/rfc-svg.err", None, None)

    def test_full_tiny(self):
        check_process(self, [sys.executable, "run.py", "--out=Temp/full-tiny.xml",
                             "--repair", "Tests/full-tiny.xml"],
                      "Results/full-tiny.out", "Results/full-tiny.err",
                      "Results/full-tiny.xml", "Temp/full-tiny.xml")
        print("pass 2")
        check_process(self, [sys.executable, "run.py", "--out=Temp/full-tiny-02.xml",
                             "Temp/full-tiny.xml"],
                      "Results/full-tiny-02.out", "Results/full-tiny-02.err",
                      None, None)


def test_rfc_file(tester, fileName):
    """ Run the basic tests for a single input file """

    basename = os.path.basename(fileName)
    parse = XmlRfcParser("Tests/" + fileName, quiet=True, cache_path=None, no_network=True)
    tree = parse.parse()

    log.write_out = io.StringIO()
    log.write_err = log.write_out
    checkTree(tree.tree)

    returnValue = check_results(log.write_out, "Results/" + basename.replace(".xml", ".out"))
    tester.assertFalse(returnValue, "Output to console is different")

    result = io.StringIO(lxml.etree.tostring(tree.tree,
                                             xml_declaration=True,
                                             encoding='utf-8',
                                             pretty_print=True).decode('utf-8'))
    returnValue = check_results(result, "Results/" + basename)
    tester.assertFalse(returnValue, "Result from editing the tree is different")


def test_svg_file(tester, fileName):
    """ Run the basic tests for a single input file """

    basename = os.path.basename(fileName)
    parse = XmlRfcParser("Tests/" + fileName, quiet=True, cache_path=None, no_network=True)
    tree = parse.parse()

    log.write_out = io.StringIO()
    log.write_err = log.write_out
    checkTree(tree.tree)

    (result, errors) = tree.validate(rng_path=parse.default_rng_path.replace("rfc7991", "svg"))

    returnValue = check_results(log.write_out, "Results/" + basename.replace(".svg", ".out"))
    tester.assertFalse(returnValue, "Output to console is different")

    result = io.StringIO(lxml.etree.tostring(tree.tree,
                                             xml_declaration=True,
                                             encoding='utf-8',
                                             pretty_print=True).decode('utf-8'))
    returnValue = check_results(result, "Results/" + basename)
    tester.assertFalse(returnValue, "Result from editing the tree is different")
    tester.assertTrue(result, "Fails to validate againist the RNG")


def check_results(file1, file2Name):
    """  Compare two files and say what the differences are or even if there are
         any differences
    """

    with open(file2Name, 'r') as f:
        lines2 = f.readlines()

    if os.name == 'nt' and (file2Name.endswith(".out") or file2Name.endswith(".err")):
        lines2 = [line.replace('Tests/', 'Tests\\').replace('Temp/', 'Temp\\') for line in lines2]

    if not file2Name.endswith(".out"):
        cwd = os.getcwd()
        if os.name == 'nt':
            cwd = cwd.replace('\\', '/')
        lines2 = [line.replace('$$CWD$$', cwd) for line in lines2]

    file1.seek(0)
    lines1 = file1.readlines()

    d = difflib.Differ()
    result = list(d.compare(lines1, lines2))

    hasError = False
    for l in result:
        if l[0:2] == '+ ' or l[0:2] == '- ':
            hasError = True
            break

    if hasError:
        print("".join(result))

    return hasError


def check_process(tester, args, stdoutFile, errFile, generatedFile, compareFile):
    """
    Execute a subprocess using args as the command line.
    if stdoutFile is not None, compare it to the stdout of the process
    if generatedFile and compareFile are not None, compare them to each other
    """

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutX, stderr) = p.communicate()
    p.wait()

    returnValue = True
    if stdoutFile is not None:
        with open(stdoutFile, 'r') as f:
            lines2 = f.readlines()

        if six.PY2:
            lines1 = stdoutX.splitlines(True)
        else:
            lines1 = stdoutX.decode('utf-8').splitlines(True)

        if os.name == 'nt':
            lines2 = [line.replace('Tests/', 'Tests\\').replace('Temp/', 'Temp\\')
                      for line in lines2]
            lines1 = [line.replace('\r', '') for line in lines1]

        d = difflib.Differ()
        result = list(d.compare(lines1, lines2))

        hasError = False
        for l in result:
            if l[0:2] == '+ ' or l[0:2] == '- ':
                hasError = True
                break
        if hasError:
            print("stdout:")
            print("".join(result))
            returnValue = False

    if errFile is not None:
        with open(errFile, 'r') as f:
            lines2 = f.readlines()

        if six.PY2:
            lines1 = stderr.splitlines(True)
        else:
            lines1 = stderr.decode('utf-8').splitlines(True)

        if os.name == 'nt':
            lines2 = [line.replace('Tests/', 'Tests\\').replace('Temp/', 'Temp\\')
                      for line in lines2]
            lines1 = [line.replace('\r', '') for line in lines1]

        d = difflib.Differ()
        result = list(d.compare(lines1, lines2))

        hasError = False
        for l in result:
            if l[0:2] == '+ ' or l[0:2] == '- ':
                hasError = True
                break
        if hasError:
            print("stderr")
            print("".join(result))
            returnValue = False

    if generatedFile is not None:
        with open(generatedFile, 'r') as f:
            lines2 = f.readlines()

        with open(compareFile, 'r') as f:
            lines1 = f.readlines()

        d = difflib.Differ()
        result = list(d.compare(lines1, lines2))

        hasError = False
        for l in result:
            if l[0:2] == '+ ' or l[0:2] == '- ':
                hasError = True
                break

        if hasError:
            print(generatedFile)
            print("".join(result))
            returnValue = False

    tester.assertTrue(returnValue, "Comparisons failed")


def clear_cache(parser):
    parser.delete_cache()


if __name__ == '__main__':
    unittest.main(buffer=True)
