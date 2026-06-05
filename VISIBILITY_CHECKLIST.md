# OASIS Free Visibility Checklist

Production site:

```txt
https://tiny-joy-oasis.vercel.app
```

Use clean share URLs:

```txt
https://tiny-joy-oasis.vercel.app/oasis/zh/today
https://tiny-joy-oasis.vercel.app/oasis/en/today
https://tiny-joy-oasis.vercel.app/oasis/tc/today
```

Avoid sharing URLs with `?page=1`.

## Search Engine Setup

### Google Search Console

1. Open `https://search.google.com/search-console`.
2. Add URL-prefix property:

```txt
https://tiny-joy-oasis.vercel.app
```

3. Choose HTML meta tag verification.
4. Add Google's verification meta tag to `oasis/index.html` or send it to Codex to add.
5. Redeploy on Vercel.
6. Click Verify in Google Search Console.
7. Submit sitemap:

```txt
https://tiny-joy-oasis.vercel.app/oasis/sitemap.xml
```

8. Use URL Inspection and request indexing for:

```txt
https://tiny-joy-oasis.vercel.app/oasis/zh/today
https://tiny-joy-oasis.vercel.app/oasis/en/today
https://tiny-joy-oasis.vercel.app/oasis/tc/today
https://tiny-joy-oasis.vercel.app/oasis/zh/guide/digital-hug
https://tiny-joy-oasis.vercel.app/oasis/en/guide/digital-hug
```

### Bing Webmaster Tools

1. Open `https://www.bing.com/webmasters`.
2. Import from Google Search Console, or add the site manually.
3. Submit the same sitemap:

```txt
https://tiny-joy-oasis.vercel.app/oasis/sitemap.xml
```

## Free Distribution

English:

- Product Hunt
- Hacker News `Show HN`
- Reddit: `r/InternetIsBeautiful`, `r/SideProject`, `r/webdev`
- Indie Hackers
- Dev.to or Medium

Chinese:

- V2EX `分享创造`
- 即刻
- 小红书
- 知乎想法/文章
- 豆瓣相关小组

## Copy Templates

### Chinese

```txt
我做了一个免费的数字避难所 OASIS。

它很小：一句温柔话、一层白噪音、一个匿名释放烦恼的气泡，还有一个可以和陌生人交换小开心的角落。

不是治疗，也不说教，只是给某个很累的瞬间留一点柔软。

https://tiny-joy-oasis.vercel.app/oasis/zh/today
```

### English

```txt
I built OASIS, a tiny free digital sanctuary.

It has digital hugs, soft ambient sounds, a private worry-release bubble, and an anonymous joy swapper.

Not therapy, not productivity, just a small calming web corner for heavy moments.

https://tiny-joy-oasis.vercel.app/oasis/en/today
```

## Weekly Review

Check once a week:

- Google Search Console impressions
- Search queries that triggered OASIS
- Pages indexed
- Top referrers in OASIS analytics
- Most visited language
- Whether people use Today, Sound, Vent, or Joy most
