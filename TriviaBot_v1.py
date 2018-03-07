"""
TRIVIA BOT Version 1 (old)

A personal project made by Sai Sameer Pusapaty
I do not condone cheating. Do not use this to cheat.
"""

import io
import os
import crayons

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from googleapiclient.discovery import build

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '[CREDENTIAL PATH]'

#List of common words to filter out from search results
common = ['the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as']
#list of single letters to filter out
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


#READING TEXT FROM IMAGE
def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    overall = []
    for text in texts:
        overall.append('"{}"'.format(text.description))
    prob = overall[0]
    question = ''
    index = 1
    for c in prob[1:len(prob)-1]:
        if c != '?':
            question += c
        else:
            prob = prob[index+1:len(prob)-1]
            question += '?'
            break
        index += 1
    answers = [s.strip() for s in prob.splitlines()]
    answers = answers[len(answers)-3:]
    question = question.lower()
    return question,answers

#'q' is the question text and 'a' is a list of answer choices
q,a = detect_text('[IMAGE PATH]')

#Finding out if the question is a 'not' question
ifNOT = False

if "not" in q.split():
    ifNOT = True
    q = q.split()
    q.remove("not")
    q = ' '.join(q)

if "never" in q.split():
    ifNOT = True
    q = q.split()
    q.remove("never")
    q = ' '.join(q)

#SEARCHING QUESTION ON GOOGLE SEARCH
my_api_key = "#######################"
my_cse_id = "#######################"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

results = google_search(
    q, my_api_key, my_cse_id, num=10)

ansDict = {}
for ans in a:
    ansDict[ans] = 0

test1 = []

#Finding frequencies of each answer choice in a google search of the question
i = 1
for result in results:
    ansDic = []
    final = result['snippet'] + " " + result['title'] + " "

    for ans in a:
        ansCount = 0
        for e in ans.split():
            if (e.lower() in common) or (e.lower() in letters):
                continue
            ansCount += final.count(e)
        ansCount += final.count(ans)
        ansDict[ans] += ansCount
        ansDic.append((ans,ansDict[ans]/i))

    ansDic.sort(key=lambda x: x[1])
    if i==10:
        test1 = ansDic[::-1]
    i+=1

#Running a second google search on separate queries

final_answers = {}
for answer in a:
    final_answers[answer] = 0

for answer in a:
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']


    results = google_search(
        q+" "+answer, my_api_key, my_cse_id, num=10)

    ansDict = {}
    for ans in a:
        ansDict[ans] = 0
    i = 1
    for result in results:
        ansDic = []
        final = result['snippet'] + " " + result['title'] + " "

        for ans in a:
            ansCount = 0
            for e in ans.split():
                if (e.lower() in common) or (e.lower() in letters):
                    continue
                ansCount += final.count(e)
            ansCount += final.count(ans)
            ansDict[ans] += ansCount
            ansDic.append((ans, ansDict[ans] / i))

        ansDic.sort(key=lambda x: x[1])
        # print(ansDic)
        if i == 10:
            for pair in ansDic[::-1]:
                final_answers[pair[0]] += pair[1]
        i += 1

#Sorting and combining final results

sortedAns = []
for answer in a:
    sortedAns.append((answer,final_answers[answer]))

sortedAns.sort(key=lambda x: x[1])

test2 = sortedAns[::-1]

if ifNOT:
    test1 = test1[::-1]
    test2 = test2[::-1]

sum = 0
for i in range(len(test1)):
    sum += test1[i][1] + test2[i][1]


for i in range(len(test1)):
    print(crayons.green(test1[i][0]), end="")
    print(crayons.green(" -- " + str("%.2f" % ((test1[i][1] + test2[i][1])*100/sum) + "%")))


"""
Problems:
Slow code
Messy code
Not easy to adapt and change (develop)
"""
