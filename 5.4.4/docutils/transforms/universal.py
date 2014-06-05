# $Id: universal.py 6112 2009-09-03 07:27:59Z milde $
# Authors: David Goodger <goodger@python.org>; Ueli Schlaepfer
# Copyright: This module has been placed in the public domain.

"""
Transforms needed by most or all documents:

- `Decorations`: Generate a document's header & footer.
- `Messages`: Placement of system messages stored in
  `nodes.document.transform_messages`.
- `TestMessages`: Like `Messages`, used on test runs.
- `FinalReferences`: Resolve remaining references.
"""

__docformat__ = 'reStructuredText'

import re
import sys
import time
from docutils import nodes, utils
from docutils.transforms import TransformError, Transform


class Decorations(Transform):

    """
    Populate a document's decoration element (header, footer).
    """

    default_priority = 820

    def apply(self):
        header_nodes = self.generate_header()
        if header_nodes:
            decoration = self.document.get_decoration()
            header = decoration.get_header()
            header.extend(header_nodes)
        footer_nodes = self.generate_footer()
        if footer_nodes:
            decoration = self.document.get_decoration()
            footer = decoration.get_footer()
            footer.extend(footer_nodes)

    def generate_header(self):
        return None

    def generate_footer(self):
        # @@@ Text is hard-coded for now.
        # Should be made dynamic (language-dependent).
        settings = self.document.settings
        if settings.generator or settings.datestamp or settings.source_link \
               or settings.source_url:
            text = []
            if settings.source_link and settings._source \
                   or settings.source_url:
                if settings.source_url:
                    source = settings.source_url
                else:
                    source = utils.relative_path(settings._destination,
                                                 settings._source)
                text.extend([
                    nodes.reference('', 'View document source',
                                    refuri=source),
                    nodes.Text('.\n')])
            if settings.datestamp:
                datestamp = time.strftime(settings.datestamp, time.gmtime())
                text.append(nodes.Text('Generated on: ' + datestamp + '.\n'))
            if settings.generator:
                text.extend([
                    nodes.Text('Generated by '),
                    nodes.reference('', 'Docutils', refuri=
                                    'http://docutils.sourceforge.net/'),
                    nodes.Text(' from '),
                    nodes.reference('', 'reStructuredText', refuri='http://'
                                    'docutils.sourceforge.net/rst.html'),
                    nodes.Text(' source.\n')])
            return [nodes.paragraph('', '', *text)]
        else:
            return None


class ExposeInternals(Transform):

    """
    Expose internal attributes if ``expose_internals`` setting is set.
    """

    default_priority = 840

    def not_Text(self, node):
        return not isinstance(node, nodes.Text)

    def apply(self):
        if self.document.settings.expose_internals:
            for node in self.document.traverse(self.not_Text):
                for att in self.document.settings.expose_internals:
                    value = getattr(node, att, None)
                    if value is not None:
                        node['internal:' + att] = value


class Messages(Transform):

    """
    Place any system messages generated after parsing into a dedicated section
    of the document.
    """

    default_priority = 860

    def apply(self):
        unfiltered = self.document.transform_messages
        threshold = self.document.reporter.report_level
        messages = []
        for msg in unfiltered:
            if msg['level'] >= threshold and not msg.parent:
                messages.append(msg)
        if messages:
            section = nodes.section(classes=['system-messages'])
            # @@@ get this from the language module?
            section += nodes.title('', 'Docutils System Messages')
            section += messages
            self.document.transform_messages[:] = []
            self.document += section


class FilterMessages(Transform):

    """
    Remove system messages below verbosity threshold.
    """

    default_priority = 870

    def apply(self):
        for node in self.document.traverse(nodes.system_message):
            if node['level'] < self.document.reporter.report_level:
                node.parent.remove(node)


class TestMessages(Transform):

    """
    Append all post-parse system messages to the end of the document.

    Used for testing purposes.
    """

    default_priority = 880

    def apply(self):
        for msg in self.document.transform_messages:
            if not msg.parent:
                self.document += msg


class StripComments(Transform):

    """
    Remove comment elements from the document tree (only if the
    ``strip_comments`` setting is enabled).
    """

    default_priority = 740

    def apply(self):
        if self.document.settings.strip_comments:
            for node in self.document.traverse(nodes.comment):
                node.parent.remove(node)


class StripClassesAndElements(Transform):

    """
    Remove from the document tree all elements with classes in
    `self.document.settings.strip_elements_with_classes` and all "classes"
    attribute values in `self.document.settings.strip_classes`.
    """

    default_priority = 420

    def apply(self):
        if not (self.document.settings.strip_elements_with_classes
                or self.document.settings.strip_classes):
            return
        # prepare dicts for lookup (not sets, for Python 2.2 compatibility):
        self.strip_elements = dict(
            [(key, None)
             for key in (self.document.settings.strip_elements_with_classes
                         or [])])
        self.strip_classes = dict(
            [(key, None) for key in (self.document.settings.strip_classes
                                     or [])])
        for node in self.document.traverse(self.check_classes):
            node.parent.remove(node)

    def check_classes(self, node):
        if isinstance(node, nodes.Element):
            for class_value in node['classes'][:]:
                if class_value in self.strip_classes:
                    node['classes'].remove(class_value)
                if class_value in self.strip_elements:
                    return 1
