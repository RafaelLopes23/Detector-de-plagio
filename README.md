# Plagiarism Detector Application

Aplicação educacional de detecção de plágio com foco em demonstração e explicabilidade:
- Backend em Python (Flask) calcula similaridade por TF‑IDF + cosseno e produz justificativas (passagens e n‑grams).
- Frontend em Ruby on Rails oferece uma UI simples para colar/enviar arquivos (TXT/LaTeX/PDF), ajustar parâmetros e visualizar resultados.

Foco: portabilidade e execução em notebooks modestos (sem banco de dados, apenas HTTP + assets).

## Stack e versões usadas

Backend (Python):
- Python >= 3.10 (testado com 3.13)
- Flask >= 3.0
- numpy >= 2.1, scikit-learn >= 1.5, pandas >= 2.2, nltk >= 3.9

Frontend (Rails):
- Ruby 3.4
- Rails 6.1
- Puma 6
- Sprockets (assets CSS)
- Gems auxiliares para Ruby 3.4: `mutex_m`, `bigdecimal`, e extração de PDF com `pdf-reader`

## Estrutura do projeto

```
plagiarism-detector-app
├── README.md
├── backend
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── src
│       ├── plagiarism_detector
│       │   ├── __init__.py
│       │   ├── api.py            # Flask API: POST /api/compare
│       │   ├── cli.py            # CLI para comparar dois arquivos
│       │   ├── compare.py        # Similaridade (TF‑IDF/cosseno), passagens e explicações
│       │   └── data_loader.py    # Leitura de arquivos
│       └── tests
│           └── test_compare.py
├── frontend
│   ├── Gemfile
│   ├── config
│   │   ├── application.rb
│   │   ├── boot.rb
│   │   ├── environment.rb
│   │   ├── environments/
│   │   ├── puma.rb
│   │   └── routes.rb
│   ├── config.ru
│   ├── bin/rails
│   ├── app
│   │   ├── controllers/
│   │   │   ├── application_controller.rb
│   │   │   └── submissions_controller.rb
│   │   ├── helpers/application_helper.rb
│   │   ├── views
│   │   │   ├── layouts/application.html.erb
│   │   │   └── submissions/
│   │   │       ├── new.html.erb
│   │   │       └── result.html.erb
│   │   └── assets
│   │       ├── config/manifest.js
│   │       ├── images/
│   │       └── stylesheets/application.css
├── similar_a.txt / similar_b.txt        # Par semelhante (mesmo tema, paráfrase)
├── dissimilar_a.txt / dissimilar_b.txt  # Par distinto (temas não relacionados)
└── infra/
  └── scripts/setup.sh                 # Setup local opcional
```

## Como funciona (visão geral)

1) Similaridade (TF‑IDF + cosseno)
   - Calcula vetores TF‑IDF para os textos A e B e retorna o cosseno entre eles.
   - Parâmetros ajustáveis na UI: analisador (`word` ou `char`) e faixa de n‑grams (ex.: 1–2 para palavras; 3–5 para caracteres).

2) Passagens semelhantes (por sentenças)
   - Divide os textos em sentenças, filtra conteúdo “tipo sentença” e alinha A×B por TF‑IDF.
   - Favorece paráfrases: ignora pares quase idênticos, combina um modelo principal com um modelo com stemming (NLTK) para capturar variações.

3) Explicações (top n‑grams)
   - Exibe os n‑grams com maior contribuição conjunta nos dois textos, como justificativa do score.

## Contrato do endpoint (API)

- Método: POST
- URL: `http://127.0.0.1:5000/api/compare`
- Body (JSON):
  - `text_a`: string
  - `text_b`: string
  - `analyzer`: opcional, `'word'` ou `'char'` (padrão `'word'`)
  - `ngram_range`: opcional, array `[min, max]` (padrão `[1, 2]`)
- Resposta (JSON):
  - `similarity`: float (0.0–1.0)
  - `is_plagiarism`: boolean (limiar padrão 0,5)
  - `threshold`: float (0.5)
  - `method`: string (`"tfidf"`)
  - `analyzer`: `'word' | 'char'`
  - `ngram_range`: `[min, max]`
  - `passages`: lista de objetos `{ a_sentence, b_sentence, similarity }`
  - `explanations`: lista de `{ feature, weight_a, weight_b, contribution }`
  - `matches` (opcional): trechos semelhantes por substrings/token (uso secundário)

## Como rodar (passo a passo, sem Docker)

### 1) Backend (API Flask)

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
python -m plagiarism_detector.api
```

Servidor sobe em `http://127.0.0.1:5000`.

Testes rápidos (opcional):
```
pytest -q
```

CLI (opcional):
```
python -m plagiarism_detector.cli caminho/para/a.txt caminho/para/b.txt
```

### 2) Frontend (Rails UI)

```
cd frontend
bundle install
bundle exec rails server
```

Acesse `http://127.0.0.1:3000`, cole dois textos e envie. O frontend chama o backend em `http://127.0.0.1:5000/api/compare` por padrão.

Caso o backend esteja em outro host/porta, defina a variável de ambiente antes de iniciar o Rails:
```
export PLAGIARISM_API_URL="http://IP:PORT/api/compare"
bundle exec rails server
```

## Notas de uso

- PDFs: a UI suporta extração de texto via `pdf-reader`; apenas PDFs com texto selecionável (não imagem) funcionam.
- Parâmetros:
  - Palavras (1–2): mais conservador, reduz falsos positivos.
  - Caracteres (3–5): mais sensível a paráfrases e variações, pode elevar similaridade em trechos com boilerplate.
  - O limiar padrão de plágio é 0,5; ajuste sua interpretação conforme o contexto.

## Licença

MIT