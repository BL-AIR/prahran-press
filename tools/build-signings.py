#!/usr/bin/env python3
"""Generate /authors/<slug>/signings/index.html from authors/signings.json.

Each author with a Square Advanced-widget id gets an embedded booking form
that shows only their own 'Author Signing' service, so the author is chosen
by the page itself. Authors without one get a 'not open yet' page instead
of a 404, so a printed URL is never dead.

    python3 tools/build-signings.py
    git add authors tools && git commit -m "Update signing pages" && git push
"""
import json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "authors" / "signings.json").read_text())
LOC = CFG["square_location"]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book {name} for a signing — Prahran Publishing</title>
<meta name="description" content="Bookshops: book {name} for an in-store signing. Metropolitan Melbourne, and further afield when travelling.">
<link rel="canonical" href="https://prahran.press/authors/{slug}/signings/">
<link rel="icon" type="image/x-icon" href="../../../favicon/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="../../../favicon/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="../../../favicon/apple-touch-icon.png">
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-M64RTG88Y3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-M64RTG88Y3');
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-T4FVHTD');</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{ --bg:#F7F4EF; --text:#1C1C1C; --text-muted:#6B6255; --accent:#2A4232; --accent-light:#3D5A47; --border:#DDD8CE; --cream:#EDE9E1; }}
body {{ font-family:'Inter',system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.7; -webkit-font-smoothing:antialiased; }}
header {{ text-align:center; padding:3rem 1.5rem 2.75rem; border-bottom:1px solid var(--border); position:relative; background-image:url('../../../images/BookBanner.png'); background-size:cover; background-position:center; overflow:hidden; }}
header::before {{ content:''; position:absolute; inset:0; background:rgba(15,20,15,0.52); z-index:0; }}
header > * {{ position:relative; z-index:1; }}
header a {{ text-decoration:none; }}
.press-logo {{ display:block; margin:0 auto 0.75rem; width:clamp(70px,12vw,110px); height:auto; filter:brightness(1.1) drop-shadow(0 1px 4px rgba(0,0,0,0.5)); }}
.press-name {{ font-family:'EB Garamond',Georgia,serif; font-size:clamp(2rem,5vw,3.5rem); letter-spacing:0.1em; text-transform:uppercase; color:#F7F2EA; line-height:1.1; text-shadow:0 1px 6px rgba(0,0,0,0.45); }}
main {{ max-width:860px; margin:0 auto; padding:2.5rem 1rem 5rem; }}
.back-link {{ display:inline-block; font-size:0.85rem; color:var(--accent); text-decoration:none; margin-bottom:2rem; }}
.back-link:hover {{ text-decoration:underline; }}
.back-link::before {{ content:'← '; }}
h1 {{ font-family:'EB Garamond',Georgia,serif; font-weight:400; font-size:clamp(2rem,5vw,2.75rem); line-height:1.15; margin-bottom:0.75rem; text-wrap:balance; }}
.lede {{ font-family:'EB Garamond',Georgia,serif; font-size:1.2rem; color:var(--text-muted); margin-bottom:2rem; max-width:62ch; }}
.intro {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:2rem; margin-bottom:2.5rem; padding-bottom:2.5rem; border-bottom:1px solid var(--border); }}
h2 {{ font-size:0.75rem; font-weight:500; letter-spacing:0.14em; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.6rem; }}
.intro ul {{ list-style:none; }}
.intro li {{ padding:0.3rem 0; border-bottom:1px solid var(--border); font-size:0.95rem; }}
.intro li:last-child {{ border-bottom:0; }}
.intro p {{ font-size:0.95rem; margin-bottom:0.6rem; }}
.note {{ background:var(--cream); padding:0.9rem 1.1rem; font-size:0.9rem; margin-bottom:1.5rem; }}
.booking {{ background:#fff; border:1px solid var(--border); padding:1rem; min-height:520px; }}
.fallback {{ margin-top:1rem; font-size:0.85rem; color:var(--text-muted); }}
.fallback a, .intro a {{ color:var(--accent); }}
.buy-btn {{ display:inline-block; padding:0.6rem 1.25rem; background:var(--accent); color:#fff; font-size:0.85rem; font-weight:500; letter-spacing:0.03em; text-decoration:none; }}
.buy-btn:hover {{ background:var(--accent-light); }}
footer {{ border-top:1px solid var(--border); padding:2.5rem 1.5rem; text-align:center; font-size:0.875rem; color:var(--text-muted); }}
footer a {{ color:var(--accent); text-decoration:none; }}
.footer-name {{ font-family:'EB Garamond',Georgia,serif; font-size:1.1rem; letter-spacing:0.08em; text-transform:uppercase; color:var(--text); margin-bottom:0.4rem; }}
@media (max-width:720px) {{ .intro {{ grid-template-columns:1fr; gap:1.5rem; }} }}
</style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-T4FVHTD" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<header>
<a href="/">
<img class="press-logo" src="../../../logo.png" alt="Prahran Publishing">
<div class="press-name">Prahran Publishing</div>
</a>
</header>
<main>
<a class="back-link" href="/authors/{slug}/">{name}</a>
"""

OPEN = """<h1>Book {name} for an in-store signing</h1>
<p class="lede">For bookshops in metropolitan Melbourne, and further afield when {first} is travelling.{book_line}</p>

<section class="intro">
<div>
<h2>What we’ll ask you for</h2>
<ul>
<li><b>Shop name</b> — please put it in the booking note</li>
<li><b>Shop address</b> — where the signing will be held</li>
<li><b>Contact person</b> — name, phone number and email</li>
</ul>
</div>
<div>
<h2>What happens next</h2>
<p>Each request comes to Prahran Publishing for approval. Once the date is confirmed, we’ll email you about consignment stock for the signing and your shop’s percentage of sales.</p>
<p>Questions? <a href="mailto:sales@prahran.press">sales@prahran.press</a> · +61 419 899 233</p>
</div>
</section>

<p class="note">Signings run for two hours. Choose a start time that suits your shop.</p>

<div class="booking" id="booking">
<!-- Start Square Appointments Embed Code --><script src="https://app.squareup.com/appointments/buyer/widget/{widget}/{loc}.js"></script><!-- End Square Appointments Embed Code -->
</div>
<p class="fallback">Booking form not showing? <a href="https://app.squareup.com/appointments/buyer/widget/{widget}/{loc}" target="_blank" rel="noopener">Open it in a new tab</a>.</p>
"""

CLOSED = """<h1>Signings with {name}</h1>
<p class="lede">Signings with {name} aren’t open for online booking yet.</p>
<p class="note">Bookshops interested in hosting a signing can contact <a href="mailto:sales@prahran.press">sales@prahran.press</a> or call +61 419 899 233.</p>
"""

FOOT = """</main>
<footer>
<div class="footer-name">Prahran Publishing</div>
<div>Sales Enquiries: <a href="mailto:sales@prahran.press">sales@prahran.press</a></div>
<div style="margin-top:0.25rem;">ABN: 19 018 340 643 · <a href="/privacy.html">Privacy Policy</a></div>
</footer>
<!-- generated by tools/build-signings.py -->
</body>
</html>
"""

for slug, a in CFG["authors"].items():
    name = html.escape(a["name"])
    first = name.split()[0]
    book_line = f" Author of <i>{a['book']}</i>." if a.get("book") else ""
    body = (OPEN if a.get("square_widget") else CLOSED).format(
        name=name, first=first, book_line=book_line,
        widget=a.get("square_widget") or "", loc=LOC)
    out = ROOT / "authors" / slug / "signings" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HEAD.format(name=name, slug=slug) + body + FOOT, encoding="utf-8")
    print(("OPEN   " if a.get("square_widget") else "closed ") + f"/authors/{slug}/signings/")
