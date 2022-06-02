import pywikibot
from pywikibot import pagegenerators, textlib

def can_run(site):
	page = pywikibot.Page(site, u'Discussion utilisateur:Mathis bot')
	return True if not page.text else False

def get_users(site):
	cat = pywikibot.Category(site, u'Catégorie:Demande de déblocage')
	gen = pagegenerators.CategorizedPageGenerator(cat)
	users = list()

	for user in gen:
		users.append(user.title(with_ns=False))

	return users

def check_open_ra(text, user):
	match = u'== Demande de déblocage de %s ==' % user
	if match in text:
		ra = text[text.index(match):]
		ra = ra[:ra.index(u"{{RA fin}}")]
		templates = textlib.extract_templates_and_params(ra)
		for template in templates:
			if template[0] == u"RA début":
				if template[1][u'traitée'] != u'oui':
					return True
	return False

def make_ra(users, site):
	page = pywikibot.Page(site, u'Wikipédia:Requête aux administrateurs')
	text = page.text
	save_page = False

	for user in users:
		if not check_open_ra(text, user):
			text += u'\n\n{{subst:Utilisateur:Mathis bot/unblock|%s}}' % user
			save_page = True
		else:
			users.remove(user)

	if save_page:
		page.text = text
		page.save(u'/* Demande de déblocage de %s */ nouvelle section' % users[0], botflag=False)

def main():
	site = pywikibot.Site()

	if can_run(site):
		users = get_users(site)
		make_ra(users, site)

if __name__ == '__main__':
	main()