from newsfeedner.models import Feed, Article, Entity, FeedEntities
from django.utils import timezone
from django.db.models import Count
import feedparser
import requests
from bs4 import BeautifulSoup

import os
import pytz
from time import mktime, struct_time
import datetime

import random
import pymorphy2
from transliterate import translit

import re
import random

from razdel import sentenize

from wordcloud import WordCloud


def split_to_sentences(whole_text):
    return [text.text for text in sentenize(whole_text)]


class SentimentAnalyzer:
    def __init__(
        self,
        model: str = "social_network",
        lemmatize: bool = False,
        whole_text: bool = True,
        pooling_type: str = "max",
        tokenizer: str = "razdel",
    ):
        assert model in ["social_network", "toxic"]
        assert pooling_type in ["max", "mean"]
        assert tokenizer in ["razdel", "ud_baseline", "baseline"]
        tokenizers = {
            "razdel": RegexTokenizer,
            "ud_baseline": UDBaselineTokenizer,
            "baseline": BaselineTokenizer,
        }
        models = {
            "social_network": FastTextSocialNetworkModel,
            "toxic": FastTextToxicModel,
        }
        self.whole_text = whole_text
        self.lemmatize = lemmatize
        self.model_name = model
        self.tokenizer_name = tokenizer
        self.pooling_type = pooling_type
        self.model = models[model](
            tokenizer=tokenizers[tokenizer](), lemmatize=lemmatize
        )
        self.pooling_func = max if pooling_type == "max" else lambda x: sum(x) / len(x)

    def get_sentiment(self, text, top_k=None):
        if self.whole_text:
            texts = [text]
        else:
            texts = split_to_sentences(text)
        sentiments = self.model.predict(texts)
        sentiment = dict(
            [
                (
                    key,
                    self.pooling_func([sentiment[key] for sentiment in sentiments]),
                )
                for key in sentiments[0].keys()
            ]
        )
        sentiment = dict(
            sorted(
                sentiment.items(),
                key=lambda key_val_pair: key_val_pair[1],
                reverse=True,
            )[:top_k]
        )
        return sentiment


# dictionary with links to rss feed sources
FEED_URLS = {
    # information agencies
    "ria": "https://ria.ru/services/lenta/more.html?&onedayonly=1&articlemask=lenta_common",
    "tass": "http://tass.ru/rss/v2.xml",
    "interfax": "https://www.interfax.ru/rss.asp",
    "rbc": "http://static.feed.rbc.ru/rbc/logical/footer/news.rss",
    "ura.news": "https://ura.news/rss",
    "regnum": "https://regnum.ru/rss/news",
    "rosbalt": "http://www.rosbalt.ru/feed/",
    # papers
    "izvestia": "https://iz.ru/xml/rss/all.xml",
    "kommersant": "https://www.kommersant.ru/RSS/news.xml",
    "vedomosti": "https://www.vedomosti.ru/rss/news",
    "rg": "https://rg.ru/xml/index.xml",
    "kp": "http://kp.ru/rss/allsections.xml",
    "mk": "https://www.mk.ru/rss/index.xml",
    "novayagazeta": "https://content.novayagazeta.ru/rss/all.xml",
    "nezavisimayagazeta": "https://www.ng.ru/rss/",
    "aif": "http://www.aif.ru/rss/all.php",
    "pg": "https://www.pnp.ru/rss/index.xml",
    "argumenti": "http://argumenti.ru/rss/argumenti_online.xml",
    # tv
    # '1tv': '',  # no feed
    "vesti": "https://www.vesti.ru/vesti.rss",
    "rentv": "http://ren.tv/export/feed.xml",
    # 'ntv': '',  # no feed
    "5kanal": "https://www.5-tv.ru/news/rss/",
    "tvrain": "https://tvrain.ru/export/rss/all.xml",
    "zvezda": "https://tvzvezda.ru/export/rss.xml",
    "tvcentr": "https://www.tvc.ru/RSS/news.ashx",
    # radio
    # 'govoritmoskva': '',  # too many different feeds
    # "echo": "https://echo.msk.ru/news.rss",
    "svoboda": "https://www.svoboda.org/api/z-pqpiev-qpp",
    "bfm": "https://www.bfm.ru/news.rss?type=news",
    # internet (if not mentioned above and has rss feed)
    "rt": "https://russian.rt.com/rss",
    "meduza": "https://meduza.io/rss2/all",
    "lenta": "https://lenta.ru/rss",
    "gazeta.ru": "https://www.gazeta.ru/export/rss/lenta.xml",
    "fontanka": "https://www.fontanka.ru/fontanka.rss",
    "znak.com": "https://www.znak.com/rss",
    "life.ru": "https://life.ru/xml/feed.xml?"
    "hashtag=%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D0%B8",
    "dni.ru": "https://dni.ru/rss.xml",
    "vz.ru": "https://vz.ru/rss.xml",
    "theins.ru": "https://theins.ru/feed",
    "newizv.ru": "https://newizv.ru/rss",
    "zona.media": "https://zona.media/rss",
    "pravda.ru": "https://www.pravda.ru/export.xml",
    "takiedela": "https://takiedela.ru/news/feed/",
    "newtimes.ru": "https://newtimes.ru/rss/",
    "mbk-news": "https://mbk-news.appspot.com/feed/",
    "fedpress.ru": "https://fedpress.ru/feed/rss",
    # СНГ
    "belta": "https://www.belta.by/rss",
    "kazinform": "https://www.inform.kz/rss/rus.xml",
    "kabar": "http://kabar.kg/rss/",
    "uza": "https://uza.uz/ru/rss",
    "day.az": "https://news.day.az/rss/",
    "panarmenian": "https://stickers.panarmenian.net/feeds/rus/news",
    "belapan": "http://belapan.com/rss/ru_fresh_news.xml",
    "belgazeta": "http://www.belgazeta.by/ru/1276/?tpl=61",
    "nuz.uz": "https://nuz.uz/feed",
    "vecherniy.kharkov.ua": "https://vecherniy.kharkov.ua/rss/news.xml",
    "asiaplustj": "https://www.asiaplustj.info/ru/rss",
    "armeniasputnik": "https://ru.armeniasputnik.am/export/rss2/archive/index.xml",
    "az.sputniknews": "https://az.sputniknews.ru/export/rss2/archive/index.xml",
    "sputnik.by": "https://sputnik.by/export/rss2/archive/index.xml",
    "sputnik-georgia": "https://sputnik-georgia.ru/export/rss2/archive/index.xml",
    "sputnik.md": "https://ru.sputnik.md/export/rss2/archive/index.xml",
    "sputnik.kz": "https://ru.sputnik.kz/export/rss2/archive/index.xml",
    "sputnik.kg": "https://ru.sputnik.kg/export/rss2/archive/index.xml",
    "tj.sputniknews": "https://tj.sputniknews.ru/export/rss2/archive/index.xml",
    "uz.sputniknews": "https://uz.sputniknews.ru/export/rss2/archive/index.xml",
    "gazeta.uz": "https://www.gazeta.uz/ru/rss/",
    "glavred.info": "https://glavred.info/rss.xml",
    "donbass.ua": "http://donbass.ua/news.xml",
    "sng.today": "https://sng.today/rss.xml",
}

# list of words, which will not be counted as entities
STOPWORDS = ["СМИ"]

# TODAY - midnight Moscow time
MSK = pytz.timezone("Europe/Moscow")


def get_today_midnight():
    today = timezone.localtime(timezone=MSK).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return today


def generate_wordcloud(filepath):
    """
    Function for creating wordcloud pictures of current day entities.
    """

    today = get_today_midnight()
    query_today = FeedEntities.objects.filter(article__published_parsed__gt=today)
    query_ent = (
        query_today.values("ent", "ent__name", "ent__entity_class")
        .annotate(entities_count=Count("ent"))
        .order_by("-entities_count")
    )

    colormaps = {
        "PER": "summer",
        "ORG": "winter",
        "LOC": "autumn",
    }

    for class_ in ["PER", "LOC", "ORG"]:
        freqs = {
            i["ent__name"]: i["entities_count"]
            for i in query_ent
            if (i["ent__entity_class"] == class_) and (i["ent__name"] not in STOPWORDS)
        }

        wordcloud = WordCloud(
            font_path=os.path.join(filepath, "helveticaneue.otf"),
            width=800,
            height=600,
            margin=1,
            background_color="white",
            min_font_size=6,
            mode="RGB",
            colormap=colormaps[class_],
            max_words=100,
            collocations=False,
            normalize_plurals=False,
        ).generate_from_frequencies(freqs)
        wordcloud.to_file(os.path.join(filepath, f"wc-{class_}.png"))


class Morpher:
    """
    Class for converting words to normal form.
    """

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def normalize(self, word):
        if word.isupper():
            return word

        p = self.morph.parse(word)[0]
        word_nominative = p.inflect({"nomn"})

        if word_nominative:
            word_norm = word_nominative.word
        else:
            word_norm = p.normal_form

        # convert to initial letter case
        if word.islower():
            result = word_norm
        elif word.isupper():
            result = word_norm.upper()
        else:
            result = word_norm.capitalize()
        return result


class NerModel:
    """
    Named Entity Recognition model class.
    """

    def __init__(self):
        self.model = build_model(configs.ner.ner_rus, download=False)

    def run(self, sentence):
        if isinstance(sentence, str):
            sentence = [sentence]
        return self.model(sentence)


class RIAparser:
    """
    Class to parse https://ria.ru/ news - no access to rss feed.
    Returns result with same fields which will be used later as feedparser result.
    """

    def get(self, url):
        """
        TODO: add retry when status_code != 200
        """
        r = requests.get(url)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, features="html.parser")
        return soup

    def parse(self, feed_url):
        result = {
            "feed": {
                "title": "РИА Новости",
            },
            "href": feed_url,
            "entries": [],
        }

        soup = self.get(feed_url)
        if not soup:
            return result

        d_now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))

        for item in soup.find_all("div", {"class": "list-item"}):
            feed_item = {
                "title": None,
                "published_parsed": None,
                "link": None,
                "id": None,
            }
            id_data = item.find("a", {"class": "list-item__title"})
            id_ = id_data.get("href").split(".")[0].replace("/", "")
            feed_item["id"] = id_

            data = item.find("span", {"class": "share"})
            feed_item["title"] = data.get("data-title")
            feed_item["link"] = data.get("data-url")

            time_data = item.find("div", {"class": "list-item__date"}).text
            if "," in time_data:
                time_data = time_data.split(",")[1]
            h, m = [int(i) for i in time_data.split(":")]
            d_item = d_now
            if (0 <= d_now.hour < 3) and (20 < h <= 23):
                # d_item = d_item.replace(day=d_item.day - 1)
                d_item = d_item - datetime.timedelta(days=1)
            d_item = (
                d_item.replace(hour=h)
                .replace(minute=m)
                .astimezone(pytz.timezone("UTC"))
            )
            feed_item["published_parsed"] = struct_time(d_item.timetuple())

            result["entries"].append(feed_item)
        return result


class FeedDownloader:
    """
    Main class for feed downloads and database updates.
    Used in cron jobs for periodical updates.
    """

    def __init__(self, feed_urls=FEED_URLS):
        self.feed_urls = feed_urls
        self.rss_raw = {}

        # Get new data (if any) from feed sources
        print("Parsing feeds\n")
        for key in self.feed_urls:
            print(key)
            if key == "ria":
                self.rss_raw[key] = RIAparser().parse(self.feed_urls[key])
            else:
                self.rss_raw[key] = feedparser.parse(self.feed_urls[key])

        print("Done parsing feeds\n")
        print("Init NerModel\n")
        self.ner_model = NerModel()
        print("Done Init NerModel\n")
        print("Init Morpher\n")
        self.morpher = Morpher()
        print("Done Init Morpher\n")

    def parse_ner_result(self, result):
        """
        Parse result of ner model.
        Returns parsed sentence as a list of dicts:
            [
                {
                    'ent_class': str ('PER'|'LOC'|'ORG'|'O'),
                    'words': str (entity words together or None for 'O'),
                    'entity': str (entity words together normalized or None for 'O'),
                    'entity_translit': str (transliterated entity or None for 'O'),
                },
                ...
            ]
        """
        current_dict = None
        sentence_parsed = []

        # if result is empty
        if not result[1]:
            result[1].append([])

        for word, (i, tag) in zip(
            result[0][0] + ["<END>"], enumerate(result[1][0] + ["O"])
        ):
            if "-" in tag:
                # if entity - clear from punctuation
                word = word.strip()
                for char in ["«", "»", "`" '"', "'"]:
                    word = word.replace(char, "")

                position, entity_class = tag.split("-")
                if position == "B":
                    if current_dict:
                        sentence_parsed.append(current_dict)
                    word_normalized = self.morpher.normalize(word)
                    current_dict = {
                        "entity_class": entity_class,
                        "entity": word_normalized,
                        "words": word,
                        "entity_translit": (
                            translit(word_normalized, "ru", reversed=True)
                            .replace(" ", "-")
                            .replace("'", "_")
                            .replace("/", "-")
                        ),
                    }
                elif position == "I" and current_dict:
                    word_normalized = self.morpher.normalize(word)
                    current_dict["entity"] += " " + word_normalized
                    current_dict["words"] += " " + word
                    current_dict["entity_translit"] = (
                        translit(current_dict["entity"], "ru", reversed=True)
                        .replace(" ", "-")
                        .replace("'", "_")
                        .replace("/", "-")
                    )
            elif tag == "O":
                if current_dict:
                    sentence_parsed.append(current_dict)
                    current_dict = None
                sentence_parsed.append(
                    {
                        "entity_class": tag,
                        "words": word,
                        "entity": None,
                        "entity_translit": None,
                    }
                )
        return sentence_parsed[:-1]

    def get_feeds(self):
        """
        Create or update feeds data.
        """
        for feed in self.rss_raw:
            try:
                feed_name = self.rss_raw[feed]["feed"]["title"]
                feed_url = self.rss_raw[feed]["href"]
            except KeyError as e:
                print(feed, e)
            time_now = timezone.now()

            new_feed, created = Feed.objects.get_or_create(
                name=feed_name,
                url=feed_url,
                defaults={"last_fetched_at": time_now},
            )

            new_feed.last_fetched_at = time_now
            new_feed.save()

    def get_articles(self):
        """
        Update feeds article data.
        """
        new_articles = []
        for feed in self.rss_raw:
            print(feed)
            for article in self.rss_raw[feed]["entries"]:
                if article:
                    try:
                        feed_name = self.rss_raw[feed]["feed"]["title"]
                        feed_id = Feed.objects.get(name=feed_name)
                        url = article["link"]
                        id_in_feed = article.get("id", url)
                        title = article["title"]
                        title = title.replace('"', "")  # remove " for NER convenience
                        if article.get("published_parsed"):
                            published_parsed = datetime.datetime.fromtimestamp(
                                mktime(article["published_parsed"]),
                                tz=pytz.timezone("UTC"),
                            )
                        else:
                            published_parsed = datetime.datetime.now(
                                tz=pytz.timezone("UTC")
                            )

                        if not Article.objects.filter(
                            feed=feed_id, id_in_feed=id_in_feed
                        ).exists():
                            new_article = Article(
                                feed=feed_id,
                                id_in_feed=id_in_feed,
                                url=url,
                                title=title,
                                title_json=None,
                                published_parsed=published_parsed,
                            )
                            new_articles.append(new_article)
                    except Exception as e:
                        print(feed, e, article)

        Article.objects.bulk_create(new_articles)

    def get_entities(self):
        """
        Recognize unparsed titles' entities, update database.
        """
        articles_to_parse = Article.objects.filter(
            is_entities_parsed=False, is_text_parsed=True
        )

        for article in articles_to_parse:
            print(article.title)
            max_len = 10000
            result = self.ner_model.run(article.title + " " + article.text[:max_len])
            title_parsed = self.parse_ner_result(result)
            article_entities = [i for i in title_parsed if i["entity"]]

            if article_entities:
                for d in article_entities:
                    entity_name = d["entity"]
                    entity_translit = d["entity_translit"]
                    entity_class = d["entity_class"]
                    entity_words = d["words"]

                    # skip too long entities
                    if (
                        len(entity_name) > 100
                        or len(entity_translit) > 100
                        or len(entity_words) > 100
                    ):
                        continue
                    try:
                        new_entity, created = Entity.objects.get_or_create(
                            name=entity_name,
                            name_translit=entity_translit,
                            entity_class=entity_class,
                        )
                    except Exception as e:
                        print(
                            e,
                            entity_name,
                            entity_class,
                            entity_translit,
                            end="\n\n\n\n",
                        )
                        continue

                    (new_feed_entity, created,) = FeedEntities.objects.get_or_create(
                        ent=new_entity,
                        words=entity_words,
                    )
                    article.article_entities.add(new_feed_entity)

            article.title_json = title_parsed
            article.is_entities_parsed = True
            article.save()

    def get_texts(self):
        """
        Scrape and parse news texts
        """
        articles_to_parse = Article.objects.filter(is_text_parsed=False)
        articles_to_parse = list(articles_to_parse)
        random.shuffle(articles_to_parse)

        for article in articles_to_parse:
            print(article.title)
            try:
                article_news = Article_news(article.url, language="ru")
                article_news.download()
                article_news.parse()
                text = re.sub("\n{2,}", " ", article_news.text)
                if text.startswith("Регистрация пройдена успешно!"):
                    print("Will retry next time")
                    continue
            except Exception as e:
                print(e)
                continue

            article.text = text
            article.is_text_parsed = True
            article.save()

    def get_sentiment(self):
        """
        Get sentiments for articles without them
        """
        analyzer = SentimentAnalyzer()
        articles_to_parse = Article.objects.filter(
            sentiment__isnull=True,
            is_text_parsed=True,
        )
        for article in articles_to_parse:
            sentiment = analyzer.get_sentiment(article.text)
            single_score = 0 + sentiment["positive"] - sentiment["negative"]
            article.sentiment = single_score
            article.save()


class VkDownloader:
    """
    Main class for feed downloads and database updates.
    Used in cron jobs for periodical updates.
    """

    def __init__(self):
        self.service_token = (
            "aaa3d849aaa3d849aaa3d84948aad36844aaaa3aaa3d" "849f427e606f5804671923eb645"
        )
        self.user_projects = [157, 158, 159, 160, 161, 162, 163, 164, 165]

    def create_django_comments(self, comments):
        new_comments = []
        for comment in comments:
            if not VkComment.objects.filter(comment_id=comment["id"]).exists():
                thread = bool(comment.get("thread"))
                if comment["parents_stack"]:
                    parent_id = comment["parents_stack"][-1]
                    try:
                        parent = VkComment.objects.get(comment_id=parent_id)
                    except VkComment.DoesNotExist:
                        parent = None
                else:
                    parent = None
                if "text" not in comment:
                    comment["text"] = ""
                    continue
                coronavirus_related = self.find_coronavirus(comment["text"])
                if "post_id" not in comment:
                    continue
                post = VkPost.objects.get(post_id=comment["post_id"])
                new_comment = VkComment(
                    thread=thread,
                    thread_comments=comment["thread"]["count"] if thread else 0,
                    owner_id=comment["owner_id"],
                    post_id=post,
                    from_id=comment["from_id"],
                    date=comment["date"],
                    coronavirus_related=coronavirus_related,
                    parent_comment=parent,
                    text=comment["text"],
                    comment_id=comment["id"],
                )
                new_comments.append(new_comment)
        VkComment.objects.bulk_create(new_comments)
        return new_comments

    def find_coronavirus(self, text):
        corona_words = set(
            [
                "коронавирус",
                "корона",
                "пандеми",
                "covid",
                "закрыла границу",
                "карантин",
                "закрывает границу",
                "пустые полки",
                "удаленную работу",
                "удаленная работа",
                "туалетная бумага",
                "гречк",
                "с температурой",
                "вирус",
                "самоизол",
                "режим чс",
                "маски",
                "coronavirus",
                "virus",
                "закрывает границы",
                "эпидем",
                "туалетную бумагу",
                "главврач",
                "коммунарк",
                "больниц",
                "изоляц",
                "изолиров",
                "выходную недел",
                "выходная недел",
                "выходной недел",
            ]
        )
        return any(w in text.lower() for w in corona_words)

    def get_vk_comments(self, post_id, group_id, comment_id=None):
        url = (
            "https://api.vk.com/method/wall.getComments?"
            "post_id={}&v=5.92&access_token={}&owner_id={}".format(
                post_id, self.service_token, group_id
            )
        )
        if comment_id:
            url += "&comment_id={}".format(comment_id)
        comments = requests.get(url).json()["response"]["items"]
        return comments

    def create_django_posts(self, posts):
        new_posts = []
        for post in posts:
            try:
                atachment_url = post["attachments"][0]["link"]["url"]
            except:
                atachment_url = ""
            coronavirus_related = self.find_coronavirus(post["text"])
            # mutable
            post["corona"] = coronavirus_related
            if not coronavirus_related:
                print("not corona", post["text"])
                continue
            if not VkPost.objects.filter(post_id=post["id"]).exists():
                new_post = VkPost(
                    post_id=post["id"],
                    likes=post["likes"]["count"],
                    reposts=post["reposts"]["count"],
                    views=post["views"]["count"],
                    comments=post["comments"]["count"],
                    attachment_url=atachment_url,
                    owner_id=post["owner_id"],
                    from_id=post["from_id"],
                    date=post["date"],
                    text=post["text"],
                    coronavirus_related=coronavirus_related,
                )
                new_posts.append(new_post)
        VkPost.objects.bulk_create(new_posts)

    def get_vk(self):
        # using vk library

        session = vk.Session(self.service_token)
        api = vk.API(session, v="5.92")
        communities = {
            "rambler": -97751087,
            "lentach": -29534144,
            "true_lentach": -125004421,
            "mash": -112510789,
            "kpru": -15722194,
            "ria": -15755094,
            "tass": -26284064,
            "kommersant": -23482909,
            "meduza": -76982440,
        }

        for group_name, group_id in communities.items():
            posts = []
            for i in range(2):
                posts += api.wall.get(owner_id=group_id, offset=i * 100, count=100)[
                    "items"
                ]
            # posts containd dicts which are mutable
            # and changed below
            self.create_django_posts(posts)
            posts = [p for p in posts if p["corona"] and p["comments"]["count"] > 0]
            for post in posts:
                self.process_vk_comments(post, group_id)

    def process_vk_comments(self, post, group_id):
        newline = "-" * 20 + "\n"
        vk_comments = self.get_vk_comments(post["id"], group_id)
        for vk_ci, vk_c in enumerate(vk_comments):
            if "text" not in vk_c:
                vk_c["text"] = ""
                if vk_c["thread"]["count"] == 0:
                    vk_comments[vk_ci] = None
                    continue
            if (
                re.match("^\[id\d+\|.*\],$", vk_c["text"])
                and vk_c["thread"]["count"] == 0
            ):
                vk_comments[vk_ci] = None
                continue
            if vk_c.get("attachments"):
                vk_c = self.get_attachment_text(vk_c)
            vk_c["text"] = "{}\n {} post: {}".format(
                vk_c["text"], newline, post["text"]
            )
            print(">>>comment\n", vk_c["text"], "\n\n\n")
        vk_comments = [c for c in vk_comments if c]
        django_comments = self.create_django_comments(vk_comments)
        all_child_comments = []
        vk_comments = [c for c in vk_comments if c["thread"]["count"] > 0]
        for parent_c in vk_comments:
            child_comments = self.get_vk_comments(post["id"], group_id, parent_c["id"])
            all_child_comments += child_comments
            child_comments_dict = {vk_c["id"]: vk_c["text"] for vk_c in child_comments}
            for child_c in child_comments:
                # the nested dicts are mutable;
                # so the are also changed in all_child_comments
                if child_c.get("text") is None:
                    continue
                if not child_c["text"].strip():
                    child_c["text"] = None
                    continue
                if re.match("^\[id\d+\|.*\],$", child_c["text"]):
                    child_c["text"] = None
                    continue
                if "reply_to_comment" in child_c:
                    replied_text = child_comments_dict.get(child_c["reply_to_comment"])
                    child_c["text"] = "{}\n {} replied_to: {}".format(
                        child_c["text"], newline, replied_text
                    )
                child_c["text"] = "{}\n {} parent: {}".format(
                    child_c["text"], newline, parent_c["text"]
                )
                print(">>>child\n", child_c["text"], "\n\n\n")
                print(">>>parent\n", parent_c["text"], "\n\n\n")

        all_child_comments = [c for c in all_child_comments if c.get("text")]
        django_comments += self.create_django_comments(all_child_comments)
        if post["corona"]:
            text_comments = [c.text for c in django_comments if c.text]
            # default project
            sampled_projects = random.sample(self.user_projects, 2)

    def get_attachment_text(self, vk_c):
        attachment = vk_c.get("attachments")[0]
        if attachment:
            video = attachment.get("video")
            photo = attachment.get("photo")
            doc = attachment.get("doc")
            attachment_title = attachment.get("title")
            for doc_name, document in (
                ("video", video),
                ("photo", photo),
                ("doc", doc),
            ):
                if not document:
                    continue
                attachment_title = document.get("title")
                if not attachment_title:
                    attachment_title = document.get("text")
                if not attachment_title:
                    attachment_title = doc_name
            if attachment_title:
                vk_c["text"] = "{}\n attachment_title: {}".format(
                    vk_c["text"], attachment_title
                )
            else:
                print("attachments", vk_c.get("attachments"))
        return vk_c
