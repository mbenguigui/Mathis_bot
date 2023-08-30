import pywikibot
import requests
from pywikibot import textlib
from can_run import can_run
from datetime import datetime, timedelta


def close_dpp(section_content, article, revid, admin, protect):
    protect_type = u'edit'
    if u'create' in protect:
        protect_type = u'create'
    elif u'edit' not in protect:
        protect_type = u'move'

    if protect[protect_type][0] == 'sysop':
        protect_level = u'[[Wikipédia:Protection|protection]]'
    elif protect[protect_type][0] == 'autoconfirmed':
        protect_level = u'[[Wikipédia:Semi-protection|semi-protection]]'
    elif protect[protect_type][0] == 'autopatrolled':
        protect_level = u'[[Wikipédia:Semi-protection|semi-protection étendue]]'
    else:
        protect_level = str()

    if protect[protect_type][1] == 'infinity':
        protect_time = u'indéfiniment'
    else:
        end_date = datetime.strptime(protect[protect_type][1], '%Y-%m-%dT%H:%M:%SZ')
        month = ( u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre',
                  u'octobre', u'novembre', u'décembre' )
        protect_time = u'jusqu\'au {} {} {} à {}:{:0>2} (UTC)'.format(end_date.day, month[end_date.month-1],
                                                                      end_date.year, end_date.hour, end_date.minute)

    message = u'\n:{} Page {} [[Spécial:Diff/{}|mise]] en {} {} par {}. ~~~~\n'.format(u'{{fait}}', article, revid, protect_level, protect_time, admin)

    match = section_content.find(u'<!-- Ne pas modifier la ligne qui suit -->')
    if match == -1:
        return False, section_content
    end_section = section_content[match:]
    section_content = section_content.replace(end_section, message) + end_section

    match = u'{{DPP début|statut=|date=<!--~~~~~-->}}'
    replace = u'{{DPP début|statut=oui|date=~~~~~}}'
    if section_content.find(match) == -1:
        match = u'{{DPP début|statut=attente'
        replace = u'{{DPP début|statut=oui'
        if section_content.find(match) == -1:
            match = u'{{DPP début|statut=autre'
            replace = u'{{DPP début|statut=oui'
            if section_content.find(match) == -1:
                return True, section_content
    section_content = section_content.replace(match, replace, 1)

    return True, section_content


def check_protect(current_time, article, site, section_content):
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
            return close_dpp(section_content, article, log['revid'], log['user'], protect)

    return False, section_content


def list_open_dpp(current_time, site):
    page = pywikibot.Page(site, u'Wikipédia:Demande de protection de page')
    full_text = page.text
    sections = textlib.extract_sections(full_text, site)
    save_page = False
    new_text = u'{{Wikipédia:Demande de protection de page/En-tête}}\n\n'

    for section in sections.sections:
        section_content = section.content

        if section.title.startswith(u'== {{a\'|'):
            title_templates = textlib.extract_templates_and_params(section.title)
            for title_template in title_templates:
                article = title_template[1][u'1']
                section_templates = textlib.extract_templates_and_params(section_content)
                for section_template in section_templates:
                    if section_template[0] == u'DPP début':
                        if not section_template[1][u'statut'] \
                                or section_template[1][u'statut'] == u'attente' \
                                or section_template[1][u'statut'] == u'autre':
                            check, section_content = check_protect(current_time, article, site, section_content)
                            if check:
                                save_page = True

        new_text += section.title + section_content

    if save_page:
        page.text = new_text
        page.save(u'Robot : clôture des demandes traitées')


def main():
    site = pywikibot.Site('fr', 'wikipedia')
    current_time = datetime.utcnow()

    if can_run(site):
        list_open_dpp(current_time, site)


if __name__ == '__main__':
    main()