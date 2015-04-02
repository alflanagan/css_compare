import tinycss
from tinycss.css21 import RuleSet, TokenList, Declaration
from collections import defaultdict


def get_all_selectors(css_sheet):
    """Returns a :py:class:`dict` whose keys are each selector phrase present in the parsed
    stylesheet 'css_sheet', and whose values are the associated :py:class:`RuleSets`.

    """
    selectors = defaultdict(list)
    for rule in css_sheet.rules:
        phrases = rule.selector.as_css().split(",")
        for phrase in phrases:
            selectors[phrase].append(rule)
    return selectors


def check_selectors(sheet, newsheet):
    oldselectors = set([key.strip() for key in get_all_selectors(sheet)])
    newselectors = set([key.strip() for key in get_all_selectors(newsheet)])

    print("Found {:,} distinct selector phrases in site.css.".format(len(oldselectors)))
    print("Found {:,} distinct selector phrases in site-new.css.".format(len(newselectors)))

    missing = oldselectors - newselectors
    print("There are {:,} phrases from site.css missing from site-new.css".format(len(missing)))

    extra = newselectors - oldselectors
    print("There are {:,} extra phrases found from site-new.css".format(len(extra)))

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


def check_rules(sheet, newsheet):
    oldselectors = get_all_selectors(sheet)
    newselectors = get_all_selectors(newsheet)
    counter = 5
    for selector in oldselectors:
        if selector in newselectors:
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
            old_declarations = set()
            new_declarations = set()
            for oldrule in oldselectors[selector]:
                for decl in oldrule.declarations:
                    print('{0.name}: {1}{2}'.format(decl, decl.value.as_css(),
                                                     ' !' + decl.priority if decl.priority else ''))
            counter -= 1
            if counter <= 0:
                break

def main():
    parser = tinycss.make_parser('page3')
    sheet = parser.parse_stylesheet_file("site.css")
    newsheet = parser.parse_stylesheet_file("site-new.css")
    check_selectors(sheet, newsheet)
    check_rules(sheet, newsheet)


if __name__ == '__main__':
    main()
