# Bhargavi Gudisa — Portfolio

Portfolio site for Bhargavi Gudisa, Software Engineer (Cloud Infrastructure & AI Quality).

## Stack

Single-file static site — `index.html` contains the markup, styles and script. No build
step. Two runtime dependencies, both from CDN:

- **GSAP 3.12.5** + ScrollTrigger — entrance animations, scroll reveals, case-study expansion
- **Lenis 1.x** — momentum scrolling, driven by the GSAP ticker so both share one RAF loop

Fonts are Archivo (display), Space Grotesk (body) and JetBrains Mono (labels and code),
loaded from Google Fonts.

## Sections

Hero → Stats → About → Experience → Skills → Projects → Impact → Education → Contact

Each of the seven projects expands into a case study with Problem / Approach / Outcome.
Two carry inline SVG architecture diagrams; all seven carry a code or terminal artifact
(Terraform, Python, Bash, T-SQL).

Every project card states where its source lives. Work done at an employer or for a
client is marked as not public; `07 Review Sentiment & Competitor Radar` links to its
repository and live Streamlit demo.

Projects 05 and 06 are personal work whose repositories are not published yet. Each card
carries a commented-out `<a class="proj-link">` with the intended URL — publish the repo,
then swap the "being prepared" span for that link.

## Degrading safely

`.reveal` elements start at `opacity:0` so they can be animated in, but the rule is scoped
to `html.js`, a class set by a tiny inline script in `<head>`. The main script then checks
`HAS_GSAP`; if GSAP did not load — a blocked CDN on a corporate network, say — it removes
`js`, forces every `.reveal` visible and writes the counters at their final values. The
script is split into a CORE half (theme, nav, case studies, contact, back-to-top: plain
DOM, no dependencies) and a MOTION half that only runs when GSAP is present, so losing the
CDN costs animation and nothing else.

## Link previews

`og-image.jpg` (1200×630) is the card LinkedIn, Slack and iMessage render. It is generated,
not hand-made — if the name, title or URL on the site changes, regenerate it rather than
editing the JPEG. `favicon-32.png` and `apple-touch-icon.png` are the "BG" monogram.

`index.html` also carries a JSON-LD `Person` block. Keep the job title, employer and
`sameAs` links in it consistent with the visible page.

## Theming

Light-first. Tokens are declared on bare `:root`, redefined under
`@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])`, and
again under `:root[data-theme="dark"]` so the in-page toggle wins in both directions. The
choice persists to `localStorage`.

`prefers-reduced-motion: reduce` disables the entrance animations and Lenis, and makes the
case-study panels snap open rather than animate.

## Images

`profile.jpg` / `profile.webp` are the cropped and compressed hero headshot (4:5, 680×850),
with `profile-sm.webp` (340×425) served to narrow viewports through `srcset`.
`profile-source.png` is the full-resolution original — gitignored, kept locally so the crop
can be redone without re-exporting.

## Résumé

`resume/Bhargavi-Gudisa-Resume.tex` is the source for `Bhargavi-Gudisa-Resume.pdf`.
Compile with pdfLaTeX; the easiest route is to upload the `.tex` to Overleaf, which has
every package it uses. Search the file for `TODO` — those are values only Bhargavi can
supply (city, M.S. start date, Wipro city, credential and DOI links). Recompile and
replace the PDF in the repository root when it changes.

## Deployment

GitHub Pages. Push to the default branch of `BhargaviGudisa/BhargaviGudisa.github.io`, then
Settings → Pages → Branch. Live at https://bhargavigudisa.github.io

`github-profile-README.md` is scratch content for the separate GitHub *profile* repo
(`BhargaviGudisa/BhargaviGudisa`). It is gitignored and not part of this site.
