#!/usr/bin/env python3
# Note this is a python3 application, python 2 will barf
import sys
import os
from collections import defaultdict

import tinycss
from tinycss.css21 import RuleSet, TokenList, Declaration


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
        counter = 5
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
                    for decl in rule.declarations:
                        print('{0.name}: {1}{2}'.format(
                            decl,
                            decl.value.as_css(),
                            ' !' + decl.priority if decl.priority else ''))
                        counter -= 1
                        if counter <= 0:
                            break


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
