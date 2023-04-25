import pywikibot

def can_run(site):
	page = pywikibot.Page(site, u'Discussion utilisateur:Mathis bot')
	return not page.text