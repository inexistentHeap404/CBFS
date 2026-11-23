"""
import math

def tf(documents):
    oneliner = ""
    for key in documents:
        s = documents[key].split(" ")
        for word in s:
            if word not in oneliner:
                oneliner += f" {word}"
    oneliner = oneliner.split(" ")[1:]
    occurences = [[] for i in range(len(oneliner))]
    docnumber = 0
    for i in range(len(oneliner)):
        docnumber = 0
        for key in documents:
            count = documents[key].count(oneliner[i])
            occurences[i].append(count)
            docnumber += 1
    return occurences, oneliner

def tfq(unique_words, query):
    count = []
    for i in range(len(unique_words)):
        count.append(query.count(unique_words[i]))
    return count

def idf(occurences, n_documents):
    idf_arr = []
    for i in range(len(occurences)):
        word_doc_occurence = 0
        for j in range(len(occurences[0]) - 1):
            if occurences[i][j] > 0:
                word_doc_occurence += 1
        idf_arr.append(math.log10(n_documents/word_doc_occurence))
    return idf_arr


def tfidf(occurences, idf_arr):
    tfidf_arr = []
    for i in range(len(occurences)):
        buffer = []
        for j in range(len(occurences[i]) ):
            buffer.append(occurences[i][j] * idf_arr[i])
        tfidf_arr.append(buffer)
    return tfidf_arr


def cosinesim(tfidf_arr, documents):
    n_documents = len(documents)
    sim_arr = []
    q_values = []
    doc_mags = []
    q_mag = 0
    for i in tfidf_arr:
        q_values.append(i[len(i) - 1])
        q_mag += i[len(i) - 1]**2
    q_mag = math.sqrt(q_mag)
    docnumber = 0
    while docnumber < len(documents):
        doc_mag = 0
        for i in range(len(tfidf_arr)):
            doc_mag += tfidf_arr[i][docnumber]**2
        doc_mags.append(math.sqrt(doc_mag))
        docnumber += 1 
    docnumber = 0
    while docnumber < len(documents):
        doc_sim_up = 0
        for i in range(len(tfidf_arr)):
            doc_sim_up += tfidf_arr[i][docnumber] * tfidf_arr[i][len(tfidf_arr[i]) - 1]
        sim_arr.append(doc_sim_up/(q_mag * doc_mags[docnumber]))
        docnumber += 1
    return sim_arr

def findbestmatch(sim_arr):
    return sim_arr.index(max(sim_arr))


print("Enter the number of documents: ")
ndocs = int(input())
documents = {}
for i in range(1, ndocs + 1):
    print(f"Enter content for document {i}")
    content = input()
    documents[f"document{i}"] = content
    print(f"Docuemnt {i} saved successfully")



print("Enter the query to search in the document")
query = input()

occurences, unique_words = tf(documents)

print(unique_words)

q_count = tfq(unique_words, query)


for i in range(len(occurences)):
    occurences[i].append(q_count[i]) ## tf table with D1,...,Dn,Q stored in occurences

print(occurences)

idf_arr = idf(occurences, len(documents)) ## idf

print(idf_arr)

tfidf_arr = tfidf(occurences, idf_arr)

print(tfidf_arr)

sim_arr = cosinesim(tfidf_arr, documents)

print(sim_arr)


print(f"document {findbestmatch(sim_arr) + 1} is the best match")
"""



import math
import re
from pathlib import Path
from html.parser import HTMLParser


# ==========================================
# TEXT EXTRACTION
# ==========================================

class HTMLTextParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.data = []

    def handle_data(self, data):
        self.data.append(data)

    def get_text(self):
        return " ".join(self.data)


def extract_text(path):

    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))

        return " ".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif ext == ".docx":
        from docx import Document

        doc = Document(str(path))

        return " ".join(
            p.text for p in doc.paragraphs
        )

    elif ext in (".html", ".htm"):

        parser = HTMLTextParser()

        parser.feed(
            path.read_text(encoding="utf-8", errors="replace")
        )

        return parser.get_text()

    else:

        return path.read_text(
            encoding="utf-8-sig",
            errors="replace"
        )


# ==========================================
# TOKENIZATION
# ==========================================

def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


# ==========================================
# TF
# ==========================================

def tf(documents):

    unique_words = []

    for content in documents.values():

        for word in tokenize(content):

            if word not in unique_words:
                unique_words.append(word)

    occurrences = [[] for _ in unique_words]

    for i, word in enumerate(unique_words):

        for content in documents.values():

            count = tokenize(content).count(word)

            occurrences[i].append(count)

    return occurrences, unique_words


# ==========================================
# QUERY TF
# ==========================================

def tfq(unique_words, query):

    query_words = tokenize(query)

    return [
        query_words.count(word)
        for word in unique_words
    ]


# ==========================================
# IDF
# ==========================================

def idf(occurrences, n_documents):

    idf_arr = []

    for row in occurrences:

        df = sum(
            1 for count in row
            if count > 0
        )

        idf_arr.append(
            math.log10(n_documents / df)
        )

    return idf_arr


# ==========================================
# TF-IDF
# ==========================================

def tfidf(occurrences, idf_arr):

    tfidf_arr = []

    for i in range(len(occurrences)):

        buffer = []

        for count in occurrences[i]:

            buffer.append(
                count * idf_arr[i]
            )

        tfidf_arr.append(buffer)

    return tfidf_arr


# ==========================================
# COSINE SIMILARITY
# ==========================================

def cosinesim(tfidf_arr, n_documents):

    sim_arr = []

    q_mag = math.sqrt(
        sum(row[-1] ** 2 for row in tfidf_arr)
    )

    for docnumber in range(n_documents):

        doc_mag = math.sqrt(
            sum(
                row[docnumber] ** 2
                for row in tfidf_arr
            )
        )

        dot_product = sum(
            row[docnumber] * row[-1]
            for row in tfidf_arr
        )

        if q_mag == 0 or doc_mag == 0:
            sim_arr.append(0)
            continue

        sim_arr.append(
            dot_product / (q_mag * doc_mag)
        )

    return sim_arr


# ==========================================
# SEARCH
# ==========================================

def search(documents, query):

    if not documents:
        return []

    occurrences, unique_words = tf(documents)

    query_counts = tfq(unique_words, query)

    for i in range(len(occurrences)):
        occurrences[i].append(query_counts[i])

    idf_arr = idf(
        occurrences,
        len(documents)
    )

    tfidf_arr = tfidf(
        occurrences,
        idf_arr
    )

    similarities = cosinesim(
        tfidf_arr,
        len(documents)
    )

    results = []

    for filename, score in zip(
        documents.keys(),
        similarities
    ):

        if score > 0:

            results.append({
                "filename": filename,
                "similarity": score
            })

    return sorted(
        results,
        key=lambda x: x["similarity"],
        reverse=True
    )

