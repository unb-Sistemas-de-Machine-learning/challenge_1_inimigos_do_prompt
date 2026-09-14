<p align="center">
  <img src="website/src/assets/logo_inimigos.png" alt="Logo Inimigos do Prompt" width="300" style="border-radius: 50%;" />
</p>

# Challenge 1 — Inimigos do Prompt

Projeto da disciplina **Sistemas de Machine Learning (2026/02)**. A proposta é ajudar leitores de newsletters de tecnologia em português a identificarem sinais de sensacionalismo (*hype*) e alegações que merecem leitura crítica.

O repositório contém uma prova de conceito composta por pipeline de dados/ML, API local e extensão Chrome. A documentação publicada está em [unb-Sistemas-de-Machine-learning.github.io/challenge_1_inimigos_do_prompt](https://unb-sistemas-de-machine-learning.github.io/challenge_1_inimigos_do_prompt/).

## Estado atual da PoC

- A extensão Chrome observa Gmail e Outlook Live, extrai o texto visível da mensagem, consulta a API local e destaca termos retornados na própria página.
- A API FastAPI produz score de sensacionalismo de 1 a 5, termos destacados e *claims* suspeitas. Ela carrega os artefatos sklearn versionados em `backend/app/ml/artifacts/`; se eles não estiverem disponíveis no ambiente, usa o fallback heurístico.
- A análise real é armazenada no cache da extensão, exibida no side panel e disponibilizada ao dashboard. O painel também verifica a saúde da API e oferece exemplos de integração que consultam o backend de verdade.
- Os controles de confiança e de falso positivo enviam feedback para a API. O pipeline de dados prepara datasets e avalia baselines TF-IDF com Naive Bayes e Regressão Logística; os datasets e métricas locais continuam fora do versionamento.

O campo `disinformation_risk` continua derivado por heurísticas; não representa uma segunda predição de desinformação. A confiança exibida também não é uma probabilidade calibrada.

## Componentes

| Diretório | Finalidade |
| --- | --- |
| `src/` | Coleta, preparação de dados e treinamento/avaliação do baseline. |
| `backend/` | API FastAPI, artefatos sklearn, explicabilidade por léxico, cache em memória e registro de feedback. |
| `extension/` | Extensão Chrome Manifest V3, side panel e dashboard. |
| `website/` | Documentação em Astro Starlight, publicada pelo GitHub Pages. |

## Execução rápida

Inicie a API em um terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-api.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Em outro terminal, compile a extensão:

```bash
cd extension
npm install
npm run build
```

No Chrome, abra `chrome://extensions`, ative o modo de desenvolvedor e carregue `extension/dist` como extensão sem compactação. A API deve permanecer disponível em `http://localhost:8000`.

Para executar o site de documentação:

```bash
cd website
npm install
npm run dev
```

Consulte o [guia de configuração](https://unb-sistemas-de-machine-learning.github.io/challenge_1_inimigos_do_prompt/setup/) e a [execução integrada da PoC](https://unb-sistemas-de-machine-learning.github.io/challenge_1_inimigos_do_prompt/execucao_poc_api/) para o fluxo completo, incluindo pipeline de dados, Docker e limitações conhecidas.

## Objetivos de avaliação

O baseline prioriza precisão por meio do **F-0.5**, reduzindo falsos positivos ao classificar textos legítimos como sensacionalistas. A evolução planejada é separar formalmente as tarefas de sensacionalismo e desinformação, comparar modelos com dados anotados e medir calibração de probabilidade e utilidade percebida por leitores.

## Telas da aplicação

<p align="center">
  <img src="images/print_extensao_1.png" alt="Painel lateral de análise de hype" width="48%" />
  <img src="images/print_extensao_2.png" alt="Painel lateral com claims e ações" width="48%" />
</p>

<p align="center">
  <img src="images/print_dashboard_1.png" alt="Dashboard da PoC" width="100%" />
</p>
