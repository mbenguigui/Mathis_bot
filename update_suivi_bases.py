import re
import mwparserfromhell
import pywikibot
from can_run import can_run


def update_suivi_bases(site):
    news_page = pywikibot.Page(site, u'Wikipédia:Ateliers Bases/Nouveautés')
    sections = list(map(lambda x: x.get(0), mwparserfromhell.parse(news_page.text).get_sections(levels=[1, 2])))
    res = ""

    for section in sections:
        if section.level == 1:
            res += f"=={section.title}==\n"
        elif section.level == 2:
            m = re.search(r"{{WD P\|(\d+).+,\s(\d{1,2}\s[\wéû]+\s\d{4}).*", str(section.title))
            if m:
                res += f"* {{{{WD P|{m[1]}}}}}, {m[2]}\n"
            else:
                res += f"* {str(section.title).strip()}\n"

    res += u'\nVoir les discussions dans l’[[Wikipédia:Ateliers Bases/Nouveautés|atelier nouveautés]]\n\n' \
           u'<noinclude>[[Catégorie:Projet:Bases|Nouveautes]]</noinclude>'

    suivi_page = pywikibot.Page(site, u'Projet:Bases/Suivi nouvelles demandes')
    suivi_page.text = res
    suivi_page.save(u'Mise à jour depuis [[Wikipédia:Ateliers Bases/Nouveautés]]')


def main():
    site = pywikibot.Site('fr', 'wikipedia')

    if can_run(site):
        update_suivi_bases(site)


if __name__ == '__main__':
    main()
