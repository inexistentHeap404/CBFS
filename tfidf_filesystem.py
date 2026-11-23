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
