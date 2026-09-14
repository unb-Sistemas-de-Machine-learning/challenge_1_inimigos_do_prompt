# Documentação — Inimigos do Prompt

Site de documentação do projeto, construído com Astro e Starlight. O deploy no GitHub Pages é feito pelo workflow `.github/workflows/deploy.yml` quando há *push* em `main` ou `feature/extensao-ui-dashboard`.

## Desenvolvimento local

```bash
npm install
npm run dev
```

O Astro informa a URL local no terminal. Para gerar o site estático em `dist/`:

```bash
npm run build
```

As páginas vivem em `src/content/docs/`; a navegação é configurada em `astro.config.mjs`. O projeto usa a base `/challenge_1_inimigos_do_prompt` para compatibilidade com o GitHub Pages.
