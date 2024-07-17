import pywikibot
import re
from mathis_bot_tools import can_run
from pywikibot import textlib


def replace_flags(site):
    file = open("liste.txt", "r", encoding='utf-8')

    for page_name in file:
        if not can_run(site):
            break

        page = pywikibot.Page(site, page_name)
        text = page.text

        templates = textlib.extract_templates_and_params(text, strip=True)
        for template in templates:
            if template[0] == u'Infobox Élection' and u'pays' in template[1] and template[1][u'pays'] != u'France':
                text = re.sub(r'(pays\s+=\s+)([A-zÀ-ú-\'-’-\-]+)', r'\1France', text, count=1, flags=re.IGNORECASE)

                edit_summary = u'[[WP:RBOT|Requête bot]] : [[Spécial:Lien permanent/216881998#Drapeau pour les'
                edit_summary += u' élections portée nationale en France|Remplacement de drapeaux pour les élections de'
                edit_summary += u' portée nationale en France]]'

                page.text = text
                page.save(edit_summary)

                break


def main():
    site = pywikibot.Site('fr', 'wikipedia')

    replace_flags(site)


if __name__ == '__main__':
    main()
