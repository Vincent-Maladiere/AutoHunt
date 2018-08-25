# -*- coding: utf-8 -*-

"""
AutoHunt.config
"""

"""Targeted websites"""
class targets:
    SeLoger = 'SeLoger'
    Century21 = 'Century21'
    PAP = 'PAP'

"""Parameter fields, name of the desired field to set"""
class fields:
    location = 'Localisation'
    room_number = 'Nombre de pieces'
    budget_min = 'Budget min'
    budget_max = 'Budget max'
    surface_min = 'Surface min'
    surface_max = 'Surface max'
    button1 = 'button1'
    button2 = 'button2'
    button3 = 'button3'
    button4 = 'button4'

"""Result fields, name of the desired field to scrape"""
class results:
    title = 'title'
    photo_url = 'photo_url'
    date_creation = 'date_creation'
    date_update = 'date_update'
    surface = 'surface'
    price = 'price'
    price_per_sq = 'price_per_sq'
    description = 'description'
    saler_coord = 'saler_coord'
    the_plus = 'the_plus'
    general_info = 'general_info'
    inside = 'inside'
    link = 'link'
    arrondissement = 'arrondissement'
    agency = 'agency'
    ref = 'ref'
    boosted = 'boosted'

"""Method linked to the field class"""
class methods:
    pclick = 'pclick' # click launching another page, js
    click = 'click' # standart click, js
    value = 'value' # filling text form in js
    sendkeys = 'sendkeys' # html equivalent of value

SEARCH_LINKS = {
    targets.SeLoger: 'https://www.seloger.com/',
    targets.Century21: 'https://www.century21.fr/acheter/',
    targets.PAP: 'https://www.pap.fr/'
}

URL_BLACK_LIST = ['www.demeures-de-charme.com', 'www.immoneuf.com', 'www.pap.fr/vendeur/estimation-gratuite']

"""Element whose existence has to be checked to insure the correct loading of the webpage"""
KEY_FILLER_CHECKER = {
    targets.SeLoger: '#search-content > div.c-quest-field.location-field > div > div > div.selectize-input.items.not-full.has-options.has-items.oneLine > div.item.active',
    targets.Century21: '#moteurAffineeTop > div.zone-field > ul.token-input-list-facebook > li.token-input-token-facebook > p',
    targets.PAP: 'body > section.search-form-homepage > div > div > form > div > div.col-3-4 > div:nth-child(1) > div.col-3-4 > div > ul > li.token-input-token > p'
}

# HTML Path of elements (CSS Selector only)

"""Describe each website landing page to configure according to the search parameters defined in the google spreadsheet"""
SEARCH_FIELDS = {

    targets.SeLoger: {

        fields.location: {'path': '#search-content > div.c-quest-field.location-field > div > div > div.selectize-input.items.not-full.oneLine > div.jsInlineContainer > input[type="text"]', 'method': methods.sendkeys},
        fields.button1: {'path': '#search-content > div.c-quest-links > a', 'method': methods.click},
        fields.room_number: {'path': '#agatha_roomsNombre de pieces', 'method': methods.click, 'offset': -1}, # pass room_number in argument ## -1
        fields.budget_min: {'path': '#agatha_price > div.container_min > input[type=\"text\"]', 'method': methods.value},
        fields.budget_max: {'path': '#agatha_price > div.container_max > input[type=\"text\"]', 'method': methods.value},
        fields.button2: {'path': '#searchBar > div.search_bar_surface.inactive > div', 'method': methods.pclick, 'next': '#searchBar > div.search_bar_surface.inactive > div'},

        # After the parameter page, in case of technical issues

        fields.button3: {'path': '#searchBar > div.search_bar_surface.inactive > div', 'method': methods.click},
        fields.surface_min: {'path': '#agatha_surface > div.container_min > input[type=\"text\"]', 'method': methods.value},
        fields.surface_max: {'path': '#agatha_surface > div.container_max > input[type=\"text\"]', 'method': methods.value},
        fields.button4: {'path': '#searchPanel > div.search_panel_footer > div.search_panel_footer_main > div.containerRight > button', 'method': methods.pclick}

    },

    targets.Century21: {

        #buttonpath': '//*[@id="btn-id_types_biens_1"]', # select appartment
        fields.location: {'path': '#token-input-id_localisation', 'method': methods.sendkeys},
        fields.budget_max: {'path': '#id_budget_max', 'method': methods.value},
        fields.surface_min: {'path': '#id_surface_min', 'method': methods.value},
        fields.room_number: {'path': '#btn-id_nombres_de_pieces_Nombre de pieces', 'method': methods.click, 'offset': -1}, # -1
        fields.button1: {'path': '#btnRECHERCHE', 'method': methods.pclick}

    },

    targets.PAP: {

        fields.location: {'path': '#token-input-geo_objets_ids', 'method': methods.sendkeys},
        fields.budget_max: {'path': '#prix_max', 'method': methods.value},
        fields.surface_min: {'path': '#surface_min', 'method': methods.value},
        fields.button1: {'path': 'body > section.search-form-homepage > div > div > form > div > div.col-3-4 > div:nth-child(2) > div.col-3-5 > div > div:nth-child(3) > div > div > p', 'method': methods.click},
        fields.room_number: {'path': 'body > section.search-form-homepage > div > div > form > div > div.col-3-4 > div:nth-child(2) > div.col-3-5 > div > div:nth-child(3) > div > div > div > ul > li:nth-child(Nombre de pieces)', 'method': methods.click},
        fields.button2: {'path': 'body > section.search-form-homepage > div > div > form > div > div.col-1-4 > div:nth-child(1) > input.btn.btn-full-width.btn-type-1', 'method': methods.click}

    }

}

ITEM_TO_WAIT_FOR = {
    targets.SeLoger: '#annonce-135162721-624165 > div.c-pa-pic > div > div.c-pa-imgs.u-slick-initialized.c-slick > div > div > div.slideContent.c-slick-slide.slick-current.slick-active > a > img',
    targets.Century21: '#blocANNONCES > ul > li:nth-child(1)',
    targets.PAP: 'body > div.right-sidebar-layout.bg-grey-1 > div > div.main-content.search-results-container > div.search-results-list > div:nth-child(1)'
}

ITEMS_URL_GENERATOR = {
    targets.SeLoger: lambda driver: [elem.split('href="')[1].split('"')[0] for elem in driver.find_element_by_xpath('//*[@id="habillage"]/div[1]/div[6]/div/div[3]/div/div/section').get_attribute('outerHTML').split('<!-- c-pa -->')[1:]],
    targets.Century21: lambda driver: ['https://www.century21.fr' + elem.split('"')[0] for elem in driver.find_element_by_xpath('//*[@id="blocANNONCES"]/ul[1]').get_attribute('outerHTML').split('</ul>')[0].split('href="')[1:]],
    targets.PAP: lambda driver: [elem.find_element_by_css_selector('a').get_attribute('href') for elem in driver.find_elements_by_class_name("search-list-item")]
}

FIELD_TO_WAIT_FOR = {
    targets.SeLoger: '#price',
    targets.Century21: '#page > div > div.content > div > h1',
    targets.PAP: 'body'
}

# Xpath or CSS Selector
"""Describe each website results page to scrape"""
SCRAPE_FIELDS = {

    targets.SeLoger: {

        # x is the webdriver
        results.title: [lambda driver: driver.find_element_by_xpath('//*[@id="form-unique-abt"]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/p').get_attribute('innerHTML').replace('Paris', '').replace(' ', '').replace('ème', '')],
        results.photo_url: [lambda driver: driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('background-image: url(&quot;')[1].split('&quot;')[0]],
        results.surface: [lambda driver: int(driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('criterion')[1].split('<li>')[3].split('</li>')[0].split('m')[0])],
        results.price: [lambda driver: driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('js-smooth-scroll-link price')[1].split('</a>')[0].split('&nbsp;')],
        results.description: [lambda driver: driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('js-descriptifBien">')[1].split('</p>')[0]],
        results.saler_coord: [lambda driver: driver.execute_script('document.querySelector("#form-unique-abt > div.contact-haut.c-wrap-side > div.agence-telephone > button").getAttribute("data-phone")')],
        results.the_plus: [lambda driver: [elem.split('</div>')[0] for elem in driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('g-row-50-xs')[1].split('u-left">')[1:]]],
        results.general_info: [lambda driver: [elem.split('</div>')[0] for elem in driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('g-row-50-xs')[1].split('u-left">')[1:]]],
        results.ref: [lambda driver: driver.find_element_by_xpath('//*[@id="form-unique-abt"]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/p').get_attribute('innerHTML')],
        results.agency: [lambda driver: driver.find_element_by_xpath('/html/body').get_attribute('outerHTML').split('agence-title">')[1].split('</h3>')[0]],

        'Belle_Demeure': {
            results.title: [lambda driver: driver.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[1]/div[2]/div/h1').get_attribute('outerHTML').split('Paris')[1].split('ème')[0].replace(' ', '')],
            results.photo_url: [lambda driver: driver.find_element_by_xpath('//*[@id="carousel"]/ul/li[1]').get_attribute('outerHTML').split('data-src')[1].split('"')[0]],
            results.surface: [lambda driver: driver.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[1]/div[2]/div/div/ul/li[1]').get_attribute('innerHTML').replace(' ', '')],
            results.price: [lambda driver: driver.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[1]/div[2]/div/h1').get_attribute('outerHTML').split('<br>')[1].split('</h1>')[0].replace(' ', '')],
            results.description: [lambda driver: driver.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[2]/div[2]/p[1]').get_attribute('outerHTML').replace(' ', '')],
            results.saler_coord: '',
            results.the_plus: [lambda driver: '\n'.join([driver.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[2]/div[3]/ul/li[{0}]'.format(i)).get_attribute('innerHTML') for i in range(len(x.find_element_by_xpath('//*[@id="wrapper"]/div/div/div[2]/div[3]/ul').get_attribute('outerHTML').split('</li>')) - 1)])]
        }
    },

    targets.Century21: {

        results.title: [lambda driver: driver.find_element_by_xpath('//*[@id="page"]/div/div[4]/div/h1').get_attribute('innerHTML').split(' - ')[4].replace('0', '').replace('75', '')],
        results.photo_url: [lambda driver: driver.find_element_by_xpath('//*[@id="formatL"]/div[2]/div[1]/div/div[15]/div/a').get_attribute("href")],
        results.surface: [lambda driver: int(driver.find_element_by_xpath('//*[@id="page"]/div/div[4]/div/h1').get_attribute('innerHTML').split('-')[2].replace(' ', '').split('m')[0])],
        results.price: [lambda driver: int(driver.find_element_by_xpath('//*[@id="focusAnnonceV2"]/section[1]/span').get_attribute('outerHTML').split('<b>')[1].split('</b>')[0].replace(' ', '').replace('€', ''))],
        results.description: [lambda driver: driver.find_element_by_xpath('//*[@id="focusAnnonceV2"]/section[2]/div[2]/p').get_attribute('innerHTML')],
        results.saler_coord: [lambda driver: driver.execute_script('document.querySelector("#focusAnnonceV2 > div.zone_option_photo > div > section > div > ul > li:nth-child(1) > a").getAttribute("data-tel")')],
        results.the_plus: [lambda driver: driver.find_element_by_xpath('//*[@id="ficheDetail"]/div/div[1]/div[3]/ul').get_attribute('outerHTML').split('">')],
        results.general_info: [lambda driver: driver.find_element_by_xpath('//*[@id="ficheDetail"]/div/div[1]/div[1]/ul').get_attribute('outerHTML').split('Année construction</span>')[0].split('</li>')[0].replace(' ', '').replace('"', '').replace(':', '')],
        results.ref: [lambda driver: driver.find_element_by_xpath('//*[@id="focusAnnonceV2"]/section[2]/span[2]').get_attribute('innerHTML')],
        results.agency: [lambda driver: driver.find_element_by_xpath('//*[@id="votreAgence"]/div/div[2]/h4/a').get_attribute('innerHTML')]

    },

    targets.PAP: {

        results.title: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/h1/span[1]').get_attribute('innerHTML').split('m²')[1].replace(' ', '').replace('Paris', '').replace('E', '')],
        results.photo_url: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/div[3]').get_attribute('outerHTML').split('img src="')[1].split('"')[0]],
        results.surface: [lambda driver: [elem.split('</strong>')[0] for elem in driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/div[4]/div/ul').get_attribute('outerHTML').split('<strong>')[1:] if '&nbsp;' in elem.split('</strong>')[0]][0].replace('&nbsp;', '')],
        results.price: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/h1/span[2]').get_attribute('innerHTML')],
        results.saler_coord: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div/strong').get_attribute('innerHTML'),
                              lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/div[5]/strong').get_attribute('innerHTML'),
                              lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/h1/span[2]').get_attribute('innerHTML')
                              ], # WARNG
        results.general_info: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/div[5]/div/p[1]').get_attribute('innerHTML')],
        results.ref: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/p').get_attribute('innerHTML').split(' / ')[0]],
        results.agency: 'Non',
        results.date_creation: [lambda driver: driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/p').get_attribute('innerHTML').split(' / ')[1]]
    }

}

"""Button to click on to go to the next result page"""
NEXT_BUTTON_FIELDS = {
    targets.SeLoger: '#habillage > div > div.c-slice > div > div.c-wrap-main > div > div > section > div.bottomAnchorWrapper > div.annonce.annonce__footer > div > div.pagination-bloc1.u-marg-200 > div:nth-child(5) > a',
    targets.Century21: '#blocPAGINATION > div.pagination_seo > div.elementL > div > ul > li.btnSUIV_PREC.suivant > a',
    targets.PAP: 'body > div.right-sidebar-layout.bg-grey-1 > div > div.main-content.search-results-container > div.search-results-list > div.pagination.align-center.margin-top-50.margin-bottom-60 > ul:nth-child({current_page_number+1_max_3}) > li > a'
}
''

BELLE_DEMEURE = {
    'base_url': 'https://www.bellesdemeures.com',
    'field_to_wait_for': '#wrapper > div > div > div.detailWrapInfos > div.detailDesc.wrapMain.js_contact_wrapper > p.detailDescSummary'
}

"""Parameter to fill the Google Spreadsheet results"""
class IMAGE_PARAMS:
    col_start_index = 0
    col_end_index = 1
    col_pixel_size = 600
    row_start_index = 2
    row_end_index = 100
    row_pixel_size = 300

class DESCRIPTION_PARAMS:
    col_start_index = 15
    col_end_index = 16
    col_pixel_size = 600
    row_start_index = 2
    row_end_index = 100
    row_pixel_size = 300

class GENERALINFO_PARAMS:
    col_start_index = 18
    col_end_index = 19
    col_pixel_size = 600
    row_start_index = 2
    row_end_index = 100
    row_pixel_size = 300

class SMALL_PARAMS:
    col_start_index = 1
    col_end_index = 17
    col_pixel_size = 200
    row_start_index = 2
    row_end_index = 100
    row_pixel_size = 300

# Maximum try number of each action
MAX_ATTEMPT = 5
# Maximum results to gather per targets 
MAX_RESULT_PER_TARGET = 3
# Maximum time to wait while a webpage is loading
EC_MAX_TO_WAIT = 10
# Random time range to wait for between each key typing
TYPING_TIME_RANGE = (0, 1)
# Random time range to wait for between each action
ACTION_TIME_RANGE = (0, 2)
# Button field 
FIELD_WHITELIST = [fields.button1, fields.button2, fields.button3, fields.button4]
# Principal Google Spreadsheet where both your input and result are stored 
GOOGLE_SPREADSHEET_NAME = 'YOUR GOOGLE SPREADSHEET'
# Basic return result of an unfound item 
NOT_FOUND_ITEM = ''
NOT_BOOSTED_ITEM = '.'
# Define the position of fields inside the input spreadsheet
KEYWORDS_COL_NUMBERS = 3
X_INDEX_KEYWORD = 4
Y_INDEX_KEYWORD_TOP = 0
Y_INDEX_KEYWORD_BOTTOM = 3

# Name of the Google Script API Credential file
Apps_Script_Credentials = 'YOUR_CREDENTIAL_FILE.json'
