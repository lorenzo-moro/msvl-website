# Lab website — how to use it

The website is this folder. Every page is a `.qmd` text file written in Markdown,
which is like a simpler LaTeX: `## Heading`, `**bold**`, `*italic*`, `- bullet`,
`[link text](https://...)`.

| File | Page |
|---|---|
| `index.qmd` | Home |
| `research.qmd` | Research |
| `people.qmd` | People |
| `publications.qmd` | Publications (built from `Articles.bib`) |
| `facilities.qmd` | Facilities & Tools |
| `join.qmd` | Join Us |
| `_quarto.yml` | Site settings: lab name in the top bar, menu, footer |
| `_variables.yml` | Lab name, your name and email used inside pages |
| `styles.scss` | Colours and fonts |
| `images/` | Photos |

## 1. One-time setup on your Mac (about 15 minutes)

1. Install Quarto: download the macOS installer from <https://quarto.org/docs/get-started/> and run it.
2. In VS Code, install the **Quarto** extension (Extensions panel, search "Quarto").
3. Open this folder in VS Code (File → Open Folder).

## 2. See the site on your computer

In the VS Code terminal (View → Terminal), inside this folder, run:

```
quarto preview
```

Your browser opens the site. Leave it running: every time you save a file, the page refreshes.
Press `Ctrl+C` in the terminal to stop.

## 3. First edits

- Lab name: change `[Lab Name]` in **both** `_quarto.yml` and `_variables.yml`.
- Email: change `your-email@mun.ca` in `_variables.yml`.
- Publications: replace `Articles.bib` with the one from your Overleaf CV project
  (Overleaf → Menu → Download → Source, then copy `Articles.bib` here).
- Photos: put your photos in `images/` **with the same file names** as the placeholders
  (e.g. `ice.jpg`), or change the file name in the page. Landscape about 1200 × 800 px;
  people photos square, about 600 × 600 px.
- Fill the `[...]` placeholders (stipend, project titles, alumni positions).
- Colours: change `$primary` and `$secondary` at the top of `styles.scss`.

## 4. Put it online (GitHub Pages, free)

1. Create a GitHub account at <https://github.com> if you don't have one.
2. Install **GitHub Desktop** (<https://desktop.github.com>) — it avoids typing git commands.
3. In GitHub Desktop: File → Add Local Repository → choose this folder → "create a repository" →
   then **Publish repository** (untick "Keep this code private" so the site can be public).
4. In the VS Code terminal, run once:

   ```
   quarto publish gh-pages
   ```

   Answer "Y". It builds the site and gives you the address,
   e.g. `https://yourname.github.io/lab-website/`.
5. From now on: edit files → in GitHub Desktop write a short note, click **Commit**, then **Push**.
   GitHub rebuilds the site automatically in 2–3 minutes (file `.github/workflows/publish.yml` does this).

Later, if Memorial gives you a mun.ca address, it can be pointed at the same site
(GitHub repository → Settings → Pages → Custom domain).

## Each semester

- Update `people.qmd`
- Swap 1–2 items under "Recent highlights" in `index.qmd`
- Check `join.qmd` is still accurate
- Copy the latest `Articles.bib`
