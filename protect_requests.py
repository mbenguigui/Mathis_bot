import pywikibot
import requests
from pywikibot import textlib
from can_run import can_run
from datetime import datetime, timedelta


def check_protect(current_time, article, template, site):
    page = pywikibot.Page(site, article)
    protect = page.protection()
    if protect:
        session = requests.Session()
        api_url = u'https://fr.wikipedia.org/w/api.php'
        api_params = {
            'action': 'query',
            'format': 'json',
            'list': 'logevents',
            'lelimit': '1',
            'letitle': article,
            'letype': 'protect'
        }

        api_response = session.get(url=api_url, params=api_params)
        api_data = api_response.json()
        log = api_data['query']['logevents'][0]
        start_date = datetime.strptime(log['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

        if start_date >= current_time - timedelta(minutes=10):
            template[1][u'statut'] = u'oui'
            return True

    return False


def list_open_dpp(current_time, site):
    page = pywikibot.Page(site, u'Wikipédia:Demande de protection de page')
    full_text = page.text
    sections = textlib.extract_sections(full_text, site)
    save_page = False

    for section in sections.sections:
        if section.title.startswith(u'== {{a\'|'):
            title_templates = textlib.extract_templates_and_params(section.title)
            for title_template in title_templates:
                article = title_template[1][u'1']
                section_content = section.content.strip()
                section_templates = textlib.extract_templates_and_params(section_content)
                for section_template in section_templates:
                    if section_template[0] == u'DPP début':
                        if not section_template[1][u'statut'] \
                                or section_template[1][u'statut'] == u'attente' \
                                or section_template[1][u'statut'] == u'autre':
                            save_page = check_protect(current_time, article, section_template, site)

    if save_page:
        page.save()


def main():
    site = pywikibot.Site('fr', 'wikipedia')
    current_time = datetime.utcnow()

    if can_run(site):
        list_open_dpp(current_time, site)


if __name__ == '__main__':
    main()