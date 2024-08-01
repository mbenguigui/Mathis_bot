import pywikibot
import requests
from pytz import utc
from pywikibot import textlib
from mathis_bot_tools import can_run, timestamp_to_date, utc_to_paris
from datetime import datetime, timedelta, timezone


def close_dpp(section_content, article, revid, admin, is_cascade, start_date, protect):
    protect_type = u'edit'
    if u'create' in protect:
        protect_type = u'create'
    elif u'edit' not in protect:
        protect_type = u'move'

    if protect[protect_type][0] == 'sysop':
        protect_level = u'[[Wikipédia:Protection|protection]]'
    elif protect[protect_type][0] == 'autoconfirmed':
        protect_level = u'[[Wikipédia:Semi-protection|semi-protection]]'
    elif protect[protect_type][0] == 'editextendedsemiprotected':
        protect_level = u'[[Wikipédia:Semi-protection|semi-protection étendue]]'
    else:
        protect_level = str()

    protect_start = timestamp_to_date(utc_to_paris(start_date))

    if is_cascade:
        cascade = u' en cascade'
    else:
        cascade = str()

    if protect[protect_type][1] == 'infinity':
        protect_end = u'indéfiniment'
    else:
        protect_end = u'jusqu\'au ' + timestamp_to_date(utc_to_paris(datetime.strptime(protect[protect_type][1],
                                                                                       '%Y-%m-%dT%H:%M:%SZ')))

    message = u'\n:{} Page {} mise en {}{} {} par {} le [[Spécial:Diff/{}|{}]]. ~~~~\n'.format(u'{{fait}}',
                                                                                               article,
                                                                                               protect_level,
                                                                                               cascade,
                                                                                               protect_end,
                                                                                               admin,
                                                                                               revid,
                                                                                               protect_start)

    match = section_content.find(u'<!-- Ne pas modifier la ligne qui suit -->')
    if match == -1:
        return False, section_content
    end_section = section_content[match:]
    section_content = section_content.replace(end_section, message) + end_section

    match = u'{{DPP début|statut=|date=<!--~~~~~-->}}'
    replace = u'{{DPP début|statut=oui|date=~~~~~}}'
    if section_content.find(match) == -1:
        match = u'{{DPP début|statut=attente|date=<!--~~~~~-->}}'
        replace = u'{{DPP début|statut=oui|date=~~~~~}}'
        if section_content.find(match) == -1:
            match = u'{{DPP début|statut=autre|date=<!--~~~~~-->}}'
            replace = u'{{DPP début|statut=oui|date=~~~~~}}'
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
        start_date = utc.localize(datetime.strptime(log['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))

        if start_date >= current_time - timedelta(minutes=10):
            is_cascade = False
            if 'cascade' in log['params']:
                is_cascade = log['params']['cascade']
            return close_dpp(section_content, article, log['revid'], log['user'], is_cascade, start_date, protect)

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
    current_time = datetime.now(timezone.utc)

    if can_run(site):
        list_open_dpp(current_time, site)


if __name__ == '__main__':
    main()
