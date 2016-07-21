import codecs
import untangle
import requests
import argparse
from datetime import date
import os


def save_file(url, out_path):
    r = requests.get(url)
    with open(out_path, 'wb') as f:
        f.write(r.content)


def get_command_line_parser():
    today = date.today().strftime('%m-%d-%Y')
    parser = argparse.ArgumentParser(description='Get the word of the day from transparent.com and format into a tab-separated value file ready to import into Anki.')
    parser.add_argument('-d', '--date', nargs='?', help='date in the format MM-DD-YYYY', default=today)
    parser.add_argument('language', choices=['esperanto', 'french', 'german', 'spanish'])
    return parser


def get_url(lang, date):
    if lang == 'esperanto':
        lang_code = 'esp'
    elif lang == 'french':
        lang_code = 'fr'
    elif lang == 'spanish':
        lang_code = 'es'
    elif lang == 'german':
        lang_code = 'de'
    return 'http://wotd.transparent.com/rss/{0}-{1}-widget.xml'.format(date, lang_code)


if __name__ == "__main__":
    parser = get_command_line_parser()
    args = vars(parser.parse_args())

    lang = args['language']
    date = args['date']

    os.makedirs(lang, exist_ok=True)

    url = get_url(lang, date)
    wotd = untangle.parse(url)

    word_audio_file = '{1}-{0}-word.mp3'.format(lang, date)
    save_file(wotd.xml.words.wordsound.cdata, '{0}/{1}'.format(lang, word_audio_file))

    phrase_audio_file = '{1}-{0}-phrase.mp3'.format(lang, date)
    save_file(wotd.xml.words.phrasesound.cdata, '{0}/{1}'.format(lang, phrase_audio_file))


    result = [
        wotd.xml.words.date.cdata,
        wotd.xml.words.word.cdata,
        '[sound:{0}]'.format(word_audio_file),
        wotd.xml.words.translation.cdata,
        wotd.xml.words.fnphrase.cdata,
        '[sound:{0}]'.format(phrase_audio_file),
        wotd.xml.words.enphrase.cdata,
        ]

    tsv_path = '%s/%s-wotd.tsv' % (lang, lang)
    with codecs.open(tsv_path, 'a', 'utf-8-sig') as f:
        f.write('\t'.join(result))
        f.write('\n')
