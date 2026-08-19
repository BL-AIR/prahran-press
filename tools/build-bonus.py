#!/usr/bin/env python3
"""Generate the bonus-material hub pages from books/bonus.json.

    /books/<isbn>/bonus/chapters.html    one permanent hub per title
    /bonus/                              spoken shortcut, resolves to the right hub

The hub URL is permanent. It is what the bookmark QR lands on and what gets said
out loud at events, so it must still make sense in five years. The page therefore
is NOT "a survey" — it is the book's bonus library, with a ballot module on it
while a ballot happens. Change ballot.state in the config to move through:

    open      the ballot is running
    counting  votes are in, result not announced
    closed    result announced; the winner is named and the module steps aside

Several titles may run bonus material at the same time. Set "live": true on each.
"featured": true picks which one /bonus/ jumps straight to; with none or more than
one featured, /bonus/ shows a short index instead.

    python3 tools/build-bonus.py
    git add books bonus && git commit -m "Update bonus hubs" && git push
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "books" / "bonus.json"

# ─────────────────────────────────────────────────────────────── shared chrome

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="robots" content="{robots}">
    <link rel="canonical" href="{canonical}">

    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="Prahran Publishing">
{og_image}
    <link rel="icon" type="image/x-icon" href="/favicon/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png">

    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga4}');
    </script>
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
    new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    }})(window,document,'script','dataLayer','{gtm}');</script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg: #F7F4EF; --bg-card: #FFFFFF; --text: #1C1C1C;
            --text-muted: #6B6255; --accent: #2A4232; --accent-light: #3D5A47;
            --border: #DDD8CE; --cream: #EDE9E1;
        }}

        html {{ font-size: 16px; scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', system-ui, sans-serif;
            background-color: var(--bg); color: var(--text);
            line-height: 1.7; -webkit-font-smoothing: antialiased;
        }}

        header {{
            text-align: center; padding: 4rem 2rem 3.5rem;
            border-bottom: 1px solid var(--border); position: relative;
            background-image: url('/images/BookBanner.png');
            background-size: cover; background-position: center; overflow: hidden;
        }}
        header::before {{
            content: ''; position: absolute; inset: 0;
            background: rgba(15,20,15,0.52); z-index: 0;
        }}
        header > * {{ position: relative; z-index: 1; }}
        header a {{ text-decoration: none; }}

        .press-logo {{
            display: block; margin: 0 auto 1rem;
            width: clamp(80px,14vw,130px); height: auto;
            filter: brightness(1.1) drop-shadow(0 1px 4px rgba(0,0,0,0.5));
        }}
        .press-name {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: clamp(2.5rem,6vw,4.5rem); font-weight: 400;
            letter-spacing: 0.1em; text-transform: uppercase;
            color: #F7F2EA; line-height: 1.1;
            text-shadow: 0 1px 6px rgba(0,0,0,0.45);
        }}
        .press-location {{
            font-family: 'EB Garamond', Georgia, serif; font-size: 1.05rem;
            font-style: italic; color: #C8BFA8; margin-top: 0.75rem;
            letter-spacing: 0.03em;
        }}

        main {{ max-width: 780px; margin: 0 auto; padding: 3rem 2rem 6rem; }}

        .back-link {{
            display: inline-block; font-size: 0.85rem;
            color: var(--accent); text-decoration: none;
            margin-bottom: 2.5rem; letter-spacing: 0.02em;
        }}
        .back-link:hover {{ text-decoration: underline; }}
        .back-link::before {{ content: '\\2190 '; }}

        .eyebrow {{
            font-size: 0.75rem; font-weight: 500;
            letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-muted); margin-bottom: 0.75rem;
        }}

        .page-title {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: clamp(2rem, 4.5vw, 3rem);
            font-weight: 400; line-height: 1.15; margin-bottom: 0.4rem;
        }}
        .page-sub {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.15rem; font-style: italic;
            color: var(--text-muted); margin-bottom: 2.5rem;
        }}

        .intro {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.2rem; line-height: 1.85; max-width: 58ch;
        }}
        .intro p + p {{ margin-top: 1rem; }}

        section {{ margin-top: 3.5rem; }}

        .section-heading {{
            font-size: 0.75rem; font-weight: 500;
            letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            padding-top: 2rem; margin-bottom: 1.5rem;
        }}

        /* ── ballot ─────────────────────────────────────────────── */
        .ballot {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 2rem 2rem 2.25rem;
        }}
        .ballot-title {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.7rem; font-weight: 400; line-height: 1.2;
            margin-bottom: 0.6rem;
        }}
        .ballot-blurb {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.08rem; line-height: 1.75;
            color: var(--text); max-width: 52ch; margin-bottom: 1.75rem;
        }}
        .ballot-closes {{
            display: inline-block; font-size: 0.72rem; font-weight: 500;
            letter-spacing: 0.09em; text-transform: uppercase;
            background: var(--cream); color: var(--text-muted);
            padding: 0.35rem 0.8rem; margin-bottom: 1.5rem;
        }}
        .options {{ list-style: none; display: grid; gap: 1rem; margin-bottom: 1.75rem; }}
        .option {{
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            padding: 1rem 1.25rem; background: var(--bg);
        }}
        .option-title {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.2rem; margin-bottom: 0.2rem;
        }}
        .option-pitch {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1rem; line-height: 1.65; color: var(--text-muted);
        }}
        .option.is-winner {{ border-left-color: #B01C2E; background: var(--bg-card); }}
        .winner-flag {{
            display: inline-block; font-size: 0.66rem; font-weight: 500;
            letter-spacing: 0.09em; text-transform: uppercase;
            background: #B01C2E; color: #fff; padding: 0.25rem 0.6rem;
            margin-bottom: 0.5rem;
        }}

        .embed-slot {{ margin-top: 0.5rem; }}
        .embed-slot iframe {{ width: 100%; border: 0; min-height: 520px; display: block; }}

        .embed-pending {{
            border: 1px dashed var(--border); background: var(--cream);
            padding: 1.5rem; text-align: center;
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1rem; color: var(--text-muted); font-style: italic;
        }}

        .note {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 0.95rem; font-style: italic;
            color: var(--text-muted); margin-top: 1rem;
        }}

        /* ── chapter library ────────────────────────────────────── */
        .chapters {{ list-style: none; display: grid; gap: 1rem; }}
        .chapter {{
            display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem;
            align-items: baseline; justify-content: space-between;
            border: 1px solid var(--border); background: var(--bg-card);
            padding: 1.15rem 1.35rem;
        }}
        .chapter-main {{ flex: 1 1 22rem; min-width: 0; }}
        .chapter-title {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.25rem; margin-bottom: 0.15rem;
        }}
        .chapter-note {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 0.98rem; line-height: 1.6; color: var(--text-muted);
        }}
        .chapter-spoiler {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 0.9rem; font-style: italic; color: #B01C2E;
            margin-top: 0.35rem;
        }}
        .btn {{
            display: inline-block; padding: 0.6rem 1.25rem;
            background: var(--accent); color: #fff;
            font-size: 0.82rem; font-weight: 500;
            letter-spacing: 0.03em; text-decoration: none;
            transition: background 0.2s ease; white-space: nowrap;
        }}
        .btn:hover {{ background: var(--accent-light); }}
        .btn-quiet {{
            background: transparent; color: var(--text-muted);
            border: 1px solid var(--border); cursor: default;
        }}
        .btn-quiet:hover {{ background: transparent; }}

        .empty {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.05rem; font-style: italic; color: var(--text-muted);
        }}

        footer {{
            border-top: 1px solid var(--border);
            padding: 3rem 2rem; text-align: center;
        }}
        .footer-name {{
            font-family: 'EB Garamond', Georgia, serif;
            font-size: 1.1rem; letter-spacing: 0.08em; text-transform: uppercase;
        }}
        .footer-contact {{ margin-top: 0.75rem; font-size: 0.875rem; color: var(--text-muted); }}
        .footer-contact a {{ color: var(--accent); text-decoration: none; }}
        .footer-contact a:hover {{ text-decoration: underline; }}
        .copyright {{ margin-top: 1.5rem; font-size: 0.8rem; color: var(--border); }}

        @media (max-width: 620px) {{
            main {{ padding: 2rem 1.25rem 4rem; }}
            .ballot {{ padding: 1.5rem 1.25rem 1.75rem; }}
        }}
    </style>
</head>
<body>
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<header>
    <a href="/">
        <img class="press-logo" src="/logo.png" alt="Prahran Publishing">
        <div class="press-name">Prahran Publishing</div>
        <div class="press-location">Melbourne, Victoria &mdash; Australia</div>
    </a>
</header>
"""

FOOT = """
<footer>
    <div class="footer-name">Prahran Publishing</div>
    <div class="footer-contact" style="margin-top:0.4rem;">
        General Enquiries: <a href="mailto:info@prahran.press">info@prahran.press</a>
    </div>
    <div class="copyright">&copy; Prahran Publishing</div>
</footer>

<script>
/* Attribute the visit to the bookmark that produced it. The /b/ redirect appends
   ref and loc query params; carry those into GA4 as a bonus_page_view event so
   scans can be read per printed design, not just as one undifferentiated blob. */
(function () {
    var q = new URLSearchParams(location.search);
    var ref = q.get('ref'), loc = q.get('loc');
    if (typeof gtag === 'function') {
        gtag('event', 'bonus_page_view', {
            book: '__ISBN__',
            bookmark_design: ref || '(none)',
            bookmark_location: loc || '(none)',
            ballot_state: '__BALLOT_STATE__'
        });
    }
    /* The ballot itself lives in a third-party iframe, so its submit event is not
       visible to us. Engagement with the module is, which is the next best thing. */
    var slot = document.getElementById('ballot-embed');
    if (slot && typeof gtag === 'function') {
        var fired = false;
        var mark = function () {
            if (fired) return;
            fired = true;
            gtag('event', 'bonus_ballot_engaged', { book: '__ISBN__' });
        };
        slot.addEventListener('mouseenter', mark, { once: true });
        window.addEventListener('blur', function () {
            if (document.activeElement && document.activeElement.tagName === 'IFRAME') mark();
        });
    }
})();
</script>

</body>
</html>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def embed_or_pending(embed, pending_text):
    """Render a third-party embed if the config carries one, otherwise a visible
    holding card. Never fail silently — an empty ballot must look deliberate."""
    if embed:
        return f'        <div class="embed-slot">{embed}</div>\n'
    return (
        '        <div class="embed-slot">\n'
        f'            <div class="embed-pending">{esc(pending_text)}</div>\n'
        '        </div>\n'
    )


def render_ballot(b):
    if not b:
        return ""
    state = b.get("state", "open")
    opts = b.get("options", [])
    winner = (b.get("result") or {}).get("winner_id")

    out = ['<section id="ballot">', '    <div class="ballot">']
    out.append(f'        <h2 class="ballot-title">{esc(b.get("heading",""))}</h2>')

    if state == "open":
        out.append(f'        <p class="ballot-blurb">{esc(b.get("blurb",""))}</p>')
        if b.get("closes_label"):
            out.append(f'        <div class="ballot-closes">{esc(b["closes_label"])}</div>')
    elif state == "counting":
        out.append('        <p class="ballot-blurb">Voting has closed. The votes are being counted '
                   'and the result goes up here — this page, no email required.</p>')
    else:  # closed
        note = (b.get("result") or {}).get("note", "")
        out.append('        <p class="ballot-blurb">You voted. This is what won.'
                   + (" " + esc(note) if note else "") + '</p>')

    if opts:
        out.append('        <ul class="options">')
        for o in opts:
            is_win = state == "closed" and winner and o.get("id") == winner
            cls = "option is-winner" if is_win else "option"
            out.append(f'            <li class="{cls}">')
            if is_win:
                out.append('                <div class="winner-flag">You chose this</div>')
            out.append(f'                <div class="option-title">{esc(o.get("title",""))}</div>')
            out.append(f'                <div class="option-pitch">{esc(o.get("pitch",""))}</div>')
            out.append('            </li>')
        out.append('        </ul>')

    if state == "open":
        out.append('        <div id="ballot-embed">')
        out.append(embed_or_pending(
            b.get("zoho_embed"),
            "The ballot opens shortly. Paste the Zoho Forms embed into "
            "ballot.zoho_embed in books/bonus.json and rebuild."))
        out.append('        </div>')

    out.append('    </div>')
    out.append('</section>')
    return "\n".join(out) + "\n"


def render_chapters(chapters):
    out = ['<section id="chapters">',
           '    <h2 class="section-heading">The bonus chapters</h2>']
    if not chapters:
        out.append('    <p class="empty">Nothing here yet. The first one is being voted on above.</p>')
    else:
        out.append('    <ul class="chapters">')
        for c in chapters:
            available = c.get("status") == "available" and c.get("href")
            out.append('        <li class="chapter">')
            out.append('            <div class="chapter-main">')
            out.append(f'                <div class="chapter-title">{esc(c.get("title",""))}</div>')
            if c.get("note"):
                out.append(f'                <div class="chapter-note">{esc(c["note"])}</div>')
            if c.get("spoiler"):
                out.append('                <div class="chapter-spoiler">Contains spoilers. '
                           'Best read after the novel.</div>')
            out.append('            </div>')
            if available:
                fmt = esc(c.get("format", "Read"))
                out.append(f'            <a class="btn" href="{esc(c["href"])}">Read &mdash; {fmt}</a>')
            else:
                out.append('            <span class="btn btn-quiet">Not yet written</span>')
            out.append('        </li>')
        out.append('    </ul>')
    out.append('</section>')
    return "\n".join(out) + "\n"


def render_signup(s):
    if not s:
        return ""
    out = ['<section id="signup">',
           '    <h2 class="section-heading">' + esc(s.get("heading", "Stay posted")) + '</h2>']
    if s.get("blurb"):
        out.append(f'    <p class="intro" style="font-size:1.08rem">{esc(s["blurb"])}</p>')
    out.append(embed_or_pending(
        s.get("zoho_embed"),
        "Signup form to come. Paste the Zoho Campaigns embed into "
        "signup.zoho_embed in books/bonus.json and rebuild."))
    out.append('    <p class="note">Double opt-in, as the Spam Act requires. '
               'One click to leave, any time.</p>')
    out.append('</section>')
    return "\n".join(out) + "\n"


def render_hub(isbn, t, cfg):
    site = cfg["site"].rstrip("/")
    canonical = f"{site}/books/{isbn}/bonus/chapters.html"
    title = f"{t['name']} — bonus chapters | Prahran Publishing"
    desc = (f"Bonus chapters and extra material for {t['name']} by {t['author']}. "
            "Vote on what gets written next.")
    og_image = (f'    <meta property="og:image" content="{site}{t["cover"]}">\n'
                if t.get("cover") else "")

    head = HEAD.format(
        title=esc(title), description=esc(desc), robots="index, follow",
        canonical=esc(canonical), og_image=og_image,
        ga4=cfg["ga4"], gtm=cfg["gtm"])

    body = [f'<main>\n    <a class="back-link" href="{esc(t["book_page"])}">'
            f'{esc(t["name"])}</a>\n',
            '    <div class="eyebrow">Bonus chapters</div>',
            f'    <h1 class="page-title">{esc(t["name"])}</h1>',
            f'    <div class="page-sub">by {esc(t["author"])}</div>']

    if t.get("intro"):
        body.append('    <div class="intro">')
        for p in t["intro"]:
            body.append(f'        <p>{esc(p)}</p>')
        body.append('    </div>')

    body.append("")
    body.append(render_ballot(t.get("ballot")))
    body.append(render_chapters(t.get("chapters", [])))
    body.append(render_signup(t.get("signup")))
    body.append('</main>')

    foot = (FOOT.replace("__ISBN__", isbn)
                .replace("__BALLOT_STATE__", (t.get("ballot") or {}).get("state", "none")))
    return head + "\n".join(body) + foot


REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting&hellip;</title>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{dest}">
<meta http-equiv="refresh" content="0; url={dest}">
<script>location.replace("{dest}");</script>
<!-- generated by tools/build-bonus.py -->
</head>
<body style="font-family:Georgia,serif;margin:0;padding:3rem 1.5rem;text-align:center;color:#222">
<p><a href="{dest}">Continue &rarr;</a></p>
</body>
</html>
"""


def render_index(live, cfg):
    """/bonus/ — jumps straight through when exactly one title is featured,
    otherwise lists everything that is live so it never lands on the wrong book."""
    site = cfg["site"].rstrip("/")
    featured = [(i, t) for i, t in live if t.get("featured")]

    if len(featured) == 1:
        isbn = featured[0][0]
        return REDIRECT.format(dest=esc(f"{site}/books/{isbn}/bonus/chapters.html")), "redirect"

    head = HEAD.format(
        title=esc("Bonus chapters | Prahran Publishing"),
        description=esc("Bonus chapters and extra material for Prahran Publishing titles."),
        robots="index, follow",
        canonical=esc(f"{site}/bonus/"), og_image="",
        ga4=cfg["ga4"], gtm=cfg["gtm"])

    body = ['<main>', '    <a class="back-link" href="/">All books</a>',
            '    <div class="eyebrow">Bonus chapters</div>',
            '    <h1 class="page-title">Extra material</h1>',
            '    <div class="page-sub">More of the story than fits between the covers</div>',
            '    <ul class="chapters" style="margin-top:2.5rem">']
    if not live:
        body.append('    </ul>')
        body.append('    <p class="empty">Nothing running just now. Check back.</p>')
    else:
        for isbn, t in live:
            state = (t.get("ballot") or {}).get("state")
            note = {"open": "A ballot is open — vote on what gets written next.",
                    "counting": "Votes are in. Result shortly.",
                    "closed": "The result is up."}.get(state, "")
            body.append('        <li class="chapter">')
            body.append('            <div class="chapter-main">')
            body.append(f'                <div class="chapter-title">{esc(t["name"])}</div>')
            body.append(f'                <div class="chapter-note">by {esc(t["author"])}'
                        + (f' &mdash; {esc(note)}' if note else '') + '</div>')
            body.append('            </div>')
            body.append(f'            <a class="btn" href="/books/{isbn}/bonus/chapters.html">Open</a>')
            body.append('        </li>')
        body.append('    </ul>')
    body.append('</main>')

    foot = FOOT.replace("__ISBN__", "(index)").replace("__BALLOT_STATE__", "(index)")
    return head + "\n".join(body) + foot, "index"


def main():
    cfg = json.loads(CONFIG.read_text())
    live = [(i, t) for i, t in cfg["titles"].items() if t.get("live")]
    written = []

    for isbn, t in cfg["titles"].items():
        if not t.get("live"):
            print(f"  skipped {isbn} ({t['name']}) — live: false")
            continue
        out = ROOT / "books" / isbn / "bonus" / "chapters.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_hub(isbn, t, cfg))
        written.append((out, f"{t['name']} — {(t.get('ballot') or {}).get('state','no ballot')}"))

    page, kind = render_index(live, cfg)
    idx = ROOT / "bonus" / "index.html"
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text(page)
    written.append((idx, f"/bonus/ ({kind})"))

    print(f"\nWrote {len(written)} pages\n")
    for path, what in written:
        print(f"  /{path.relative_to(ROOT)}")
        print(f"      {what}\n")

    for isbn, t in live:
        b = t.get("ballot") or {}
        if b.get("state") == "open" and not b.get("zoho_embed"):
            print(f"  ! {t['name']}: ballot is open but no Zoho embed is set — "
                  f"the page shows a holding card.")
        if (t.get("signup") or {}).get("zoho_embed") is None:
            print(f"  ! {t['name']}: no signup embed set — the page shows a holding card.")


if __name__ == "__main__":
    main()
