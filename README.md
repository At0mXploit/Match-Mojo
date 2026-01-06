# Match-Mojo
TF-IDF content similarity and TMDB genre-based suggestions using Cosine similarity.

[Frontend](https://match-mojo.streamlit.app/)

<img width="1364" height="605" alt="2026-01-06_20-28_1" src="https://github.com/user-attachments/assets/4895e18a-7b90-48d8-9054-0304429bd562" />

<img width="1365" height="614" alt="2026-01-06_20-28" src="https://github.com/user-attachments/assets/9b73c045-5f47-44c1-8cd9-be70bdc2fed6" />

[Backend](https://match-mojo.onrender.com/docs)

<img width="1365" height="603" alt="2026-01-06_20-25" src="https://github.com/user-attachments/assets/83f5f5ad-c952-4d42-9bb3-685c97c28e4a" />

```bash
MatchMojo/
├── app.py               # Streamlit frontend (UI)
├── main.py              # FastAPI backend (API + recommendations)
├── Model/               # Pre-trained `.pkl` models (required)
│   ├── df.pkl           # Movie dataset (pandas DataFrame with 'title', etc.)
│   ├── indices.pkl      # Maps movie title → row index in df
│   ├── tfidf_matrix.pkl # Sparse TF-IDF vectors for all movies ((memory-efficient, mostly zeros)
│   └── tfidf.pkl        # TF-IDF vectorizer (used to transform text)
├── Dataset/             # Dataset used (Old)
├── movies.ipynb         # Notebook used to train models
├── requirements.txt     
├── .env                 # TMDB API key (create this!)
```

## Local Deployment

1. Create .env in the project root:

```bash
TMDB_API_KEY=your_api_key_here
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

3. Backend (FastAPI)

```bash
uvicorn main:app --reload
```

In another terminal,

4. Frontend (Streamlit)

```bash
streamlit run ./app.py
```

- For learning about [Cosine Similarity](https://medium.com/data-science-collective/cosine-similarity-explained-the-math-behind-llms-b20caac9f93c) and [TF-IDF](https://www.geeksforgeeks.org/machine-learning/understanding-tf-idf-term-frequency-inverse-document-frequency/).
- TMDB API Key (free)
- Remotely deployed using Render and Streamlit.
## Todo:

Add Todo Later...

---

