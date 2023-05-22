import pywikibot
import json
from can_run import can_run


def fix_redirects(site):
    jfile = open("redirects.json", "r", encoding='utf-8')
    redirects = json.load(jfile)

    for template in redirects:
        page = pywikibot.Page(site, template)
        text = page.text

        for values in redirects[template]:
            text = text.replace(values["oldtext"], values["newtext"])

        page.text = text
        page.save(u'[[Spécial:Diff/204497617#Correction_de_palettes|Remplacement de redirections sur palettes]]')


def main():
    site = pywikibot.Site('fr', 'wikipedia')

    if can_run(site):
        fix_redirects(site)


if __name__ == '__main__':
    main()
