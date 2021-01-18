import sitemap
import json

if __name__ == '__main__':
    url = 'https://yandex.ru'
    site = sitemap.SiteMap(url)
    site.recursion(0)
    with open('yandex.json', 'w', encoding='utf-8') as f:
        json.dump(site.sitemap, f, ensure_ascii=False)
    g = sitemap.Graph(site.sitemap, site._name)
    g()
