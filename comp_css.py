#!/usr/bin/env python3
# Note this is a python3 application, python 2 will barf
import sys
import os
from collections import defaultdict

import tinycss
from tinycss.css21 import Declaration

# pylint: disable=R0913,R0903
# imho, pylint being rather dumb about those warnings


class FunctionalDeclaration(Declaration):
    """A wrapper for :py:class:`tinycss.css21.Declaration` that redefines equality to functional
    equality (ignoring line and column values).

    .. attribute:: name

        The property name as a normalized (lower-case) string.

    .. attribute:: value

        The property value as a :class:`~.token_data.TokenList`.

        The value is not parsed. UAs using tinycss may only support
        some properties or some values and tinycss does not know which.
        They need to parse values themselves and ignore declarations with
        unknown or unsupported properties or values, and fall back
        on any previous declaration.

        :mod:`tinycss.color3` parses color values, but other values
        will need specific parsing/validation code.

    .. attribute:: priority

        Either the string ``'important'`` or ``None``.

    .. attribute:: line

        The line number in the source file at which the declaration is found.

    .. attribute:: column
        The column in the source file at which the declaration is found (begins).

    """
    def __init__(self, name_or_obj, value=None, priority=None, line=None, column=None):
        """
        :param name_or_obj: Either the declaration's name (a :py:class:`str`), or the
            :py:class:`~tinycss.css21.Declaration` instance to be wrapped.

        :param str value: The declaration's value, ignored if name_or_obj is
            :py:class:`~tinycss.css21.Declaration` instance.

        """
        if isinstance(name_or_obj, Declaration):
            super().__init__(name_or_obj.name, name_or_obj.value, name_or_obj.priority,
                             name_or_obj.line, name_or_obj.column)
        else:
            super().__init__(name_or_obj, value, priority, line, column)

    def __eq__(self, other):
        # pylint: disable=W1504
        # I don't want to use instance() because I don't want child classes (if any) to be ==
        return (type(other) == type(self) and other.name == self.name and
                other.value == self.value and other.priority == self.priority)

    def __str__(self):
        return "{0}: {1}{2}".format(
            self.name, self.value.as_css(), " !" + self.priority if self.priority else '')

    def __hash__(self):
        return hash(str(self))


class Stylesheet(object):
    """Assorted information about a parsed stylesheet."""

    _parser = tinycss.make_parser('page3')

    def __init__(self, filename):
        """Parse stylesheet from file ``filename``."""
        self.filename = filename
        self.parse = self._parser.parse_stylesheet_file(filename)
        self._selectors_dict = None  # lazy-loaded

    @property
    def selector_dict(self):
        """Returns a :py:class:`dict` whose keys are each selector phrase present in the parsed
        stylesheet, and whose values are the associated :py:class:`RuleSets`.

        """
        if self._selectors_dict is None:
            self._selectors_dict = defaultdict(list)
            for rule in self.parse.rules:
                phrases = rule.selector.as_css().split(",")
                for phrase in phrases:
                    self._selectors_dict[phrase].append(rule)
        return self._selectors_dict

    @property
    def selector_keys(self):
        """Returns a :py:class:`set` of the selector phrases parsed from the sytlesheet."""
        return set([key.strip() for key in self.selector_dict])

    def compare_selectors(self, other):
        """Compares the selectors in this sheet to those in `other`, which must be an instance
        of :py:class:`StyleSheet`. Returns a tuple ``(missing, extra)`` where :py:attr:`missing`
        is the set of selectors in this sheet not found in `other`, and :py:attr:`extra` is the
        set of selectors in `other` not present in this sheet.

        """
        return (self.selector_keys - other.selector_keys,
                other.selector_keys - self.selector_keys)

    def check_selectors(self, other):
        """Checks the set of distinct selectors in this sheet against the set in `other`.
        Reports differences found.

        """
        missing, extra = self.compare_selectors(other)

        print("Found {:,} distinct selector phrases in {}.".format(len(self.selector_keys),
                                                                   self.filename))
        print("Found {:,} distinct selector phrases in {}.".format(len(other.selector_keys),
                                                                   other.filename))

        print("There are {:,} phrases from {} missing from {}.".format(len(missing),
                                                                       self.filename,
                                                                       other.filename))

        print("There are {:,} extra phrases found from {}.".format(len(extra),
                                                                   other.filename))

        missing = list(missing)
        missing.sort()

        extra = list(extra)
        extra.sort()

        counter = 5
        print("===== missing (1st 5) =====")
        for selector in missing:
            print("[{}]".format(selector))
            counter -= 1
            if counter <= 0:
                break

        print("=====  extra (1st 5)  =====")
        counter = 5
        for selector in extra:
            print("[{}]".format(selector))
            counter -= 1
            if counter <= 0:
                break

    def check_rules(self, other):
        for selector in self.selector_keys:
            if selector in other.selector_keys:
                # we care whether the set of declarations for the selector is the same
                # we don't care if the organization is the same
                # i.e.
                #     .fred {
                #         width: 100px;
                #     }
                #     .fred {
                #         height: 200px;
                #     }
                # should compare equal to
                #     .fred {
                #         height: 200px;
                #         width: 100px;
                # }
                # so we keep a set of declarations over all the selector's rules
                self_declarations = set()
                other_declarations = set()
                for rule in self.selector_dict[selector]:
                    self_declarations.update([FunctionalDeclaration(decl) for decl
                                              in rule.declarations])
                for rule in other.selector_dict[selector]:
                    other_declarations.update([FunctionalDeclaration(decl) for decl
                                               in rule.declarations])
                missing = self_declarations - other_declarations
                extra = other_declarations - self_declarations
                if missing or extra:
                    print("selector: {}".format(selector))
                if missing:
                    print("    found in {} but not {}:".format(self.filename, other.filename))
                    for decl in missing:
                        print("        {}".format(decl))
                if extra:
                    print("    found in {} but not {}:".format(other.filename, self.filename))
                    for decl in extra:
                        print("        {}".format(decl))


def usage():
    sys.stderr.write("Usage: {} file1 file2\n".format(os.path.basename(sys.argv[0])))
    sys.stderr.write("       Compares file1 and file2 (which should be CSS stylesheets) and\n")
    sys.stderr.write("       reports functional differences between the two.\n")


def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    sheet1 = Stylesheet(sys.argv[1])
    sheet2 = Stylesheet(sys.argv[2])
    sheet1.check_selectors(sheet2)
    sheet1.check_rules(sheet2)


if __name__ == '__main__':
    main()
