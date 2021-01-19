Sitemap
=================================================

This package creates a sitemap for a given link.

-------------------------------------------------
Installation
-------------------------------------------------

Go to the module folder in the terminal and run

```
python3 setup.py install --user
```

-------------------------------------------------
Example of usage:
-------------------------------------------------

```
import sitemap

if __name__ == '__main__':
    url = 'https://vk.com'
    rec_depth = 1
    site = sitemap.SiteMap(url)
    site.recursion(rec_depth)
```
