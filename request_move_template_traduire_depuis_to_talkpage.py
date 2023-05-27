import pywikibot
from can_run import can_run
from pywikibot import textlib

def move_template(site):
    pages = open("list_pages.txt", "r", encoding="utf-8")

    for page in pages:
        article = pywikibot.Page(site, page)
        talkpage = pywikibot.Page(site, 'Discussion:' + page)

        if not can_run(site):
            break

        article_text = article.text
        templates = textlib.extract_templates_and_params(article_text)
        for template in templates:
            if template[0] == 'Traduire depuis':
                add_text = u'{{Traduire depuis'
                for param in template[1]:
                    add_text += u'|%s=%s' % (param, template[1][param])
                add_text += u'}}'

                talkpage_text = talkpage.text
                talkpage_text = add_text + u'\n' + talkpage_text

                talkpage.text = talkpage_text
                talkpage.save(u'[[WP:RBOT|Requête bot]] : [[Spécial:Diff/204659531#Catégorie:Article à améliorer par une traduction|Déplacement du modèle {{Traduire depuis}} en page de discussion]]')


def main():
    site = pywikibot.Site('fr', 'wikipedia')

    move_template(site)


if __name__ == '__main__':
    main()