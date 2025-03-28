import pywikibot
from pywikibot import pagegenerators, textlib
from mathis_bot_tools import can_run


def get_users(site):
    cat = pywikibot.Category(site, u'Catégorie:Demande de déblocage')
    gen = pagegenerators.CategorizedPageGenerator(cat)
    return [user.title(with_ns=False) for user in gen if user.namespace() == 3]

def check_open_dd(text, user):
    match = u'== Demande de déblocage de %s ==' % user
    if match in text:
        dd = text[text.rindex(match):]
        if u"\n==" in dd:
            dd = dd[:dd.index(u"\n==")]
        templates = textlib.extract_templates_and_params(dd)
        for template in templates:
            if template[0] == u"Dd":
                if template[1][u'statut'] != u'oui':
                    return True
    return False


def check_if_blocked(username, site):
    user = pywikibot.User(site, username)
    return u'oui' if user.is_blocked(username) else u'non'


def make_dd(users, site):
    page = pywikibot.Page(site, u'Wikipédia:Demande de déblocage')
    text = page.text
    save_page = False
    edit_summary_user = ''

    for user in users:
        if not check_open_dd(text, user):
            if not edit_summary_user:
                edit_summary_user = user
            blocked = check_if_blocked(user, site)
            text += u'\n\n{{subst:Utilisateur:Mathis bot/unblock|%s|bloque=%s}}' % (user, blocked)
            save_page = True

    if save_page:
        page.text = text
        page.save(u'/* Demande de déblocage de %s */ nouvelle section' % edit_summary_user, botflag=False)


def main():
    site = pywikibot.Site('fr', 'wikipedia')

    if can_run(site):
        users = get_users(site)
        make_dd(users, site)


if __name__ == '__main__':
    main()
