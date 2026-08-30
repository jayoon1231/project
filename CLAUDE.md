# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static HTML portfolio/self-introduction page for 김재윤 (Jason). The project consists of a single `index.html` file with embedded CSS — no build tooling, dependencies, package manager, or test suite.

## Preview & Development

There is no build or compilation step. To view the page:

- **Direct browser**: Open `index.html` directly in your browser
- **Local server**: From the project root, run:
  ```bash
  python -m http.server 8000
  ```
  Then navigate to `http://localhost:8000`

## File Structure

**`index.html`** — the only source file

- **Inline CSS** in `<style>` block: includes layout (CSS Grid, Flexbox), responsive design (breakpoint at `768px` for mobile), and component styling (nav, hero section, cards, footer)
- **Content sections** in `<body>`:
  - `#about` — self-introduction with personal info
  - `#skills` — skill cards (Frontend, Backend, Database, Tools)
  - `#projects` — project cards (currently placeholders)
  - `#contact` — contact links (email, GitHub, LinkedIn, Twitter)
- **Navigation**: sticky header with in-page anchor links

## Language & Content Notes

- All text content is in Korean
- Contact email: jayoonwas@gmail.com
- Project cards and social media links contain placeholder URLs and descriptions — these would need to be updated with real content and links if extended
- The page is fully responsive and styled for light mode (no dark mode stylesheet)

## Common Changes

- **Update personal info**: Edit the About section text or the info box values
- **Add/modify projects**: Add new `.project-card` divs in the projects section with matching structure
- **Update social links**: Edit `href` attributes in the contact links (e.g., replace `https://github.com` with actual GitHub profile URL)
- **Adjust colors**: Primary gradient color is `#667eea` to `#764ba2`; find-and-replace to update theme-wide
