---
applyTo: "src/soulspot/static/**/*.{css,js}"
---

# Static Assets Guidelines

## Structure
- CSS files in `src/soulspot/static/css/`
- JavaScript files in `src/soulspot/static/js/`
- Reference via `/static/` URL prefix in templates.

## TailwindCSS
- TailwindCSS is configured in `tailwind.config.js`.
- Use utility classes instead of custom CSS.
- Build process generates compiled CSS.

## JavaScript
- Use vanilla JS or minimal libraries.
- HTMX handles most interactivity.
- Keep JS files small and focused.
