"""
TriviaBot Version 2

Made by Sai Sameer Pusapaty
"""

import io
import os
import crayons
from threading import Thread

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from googleapiclient.discovery import build



os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '[CREDENTIALS PATH]'

common = ['the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as']
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

q,a = detect_text('[IMAGE_PATH]')

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

searches = [q]

for answer in a:
    searches.append(q+" "+answer)


#SEARCHING QUESTION ON GOOGLE SEARCH
my_api_key = "##############################"
my_cse_id = "#########################"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

output = {}

def crawl(q,a,search,output,index):

    results = google_search(
        search, my_api_key, my_cse_id, num=10)

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

        if i == 10:
            test1 = ansDic[::-1]
        i += 1

    output[index] = test1

##################################

threads = []

for ii in range(len(searches)):
    # We start one thread per url present.
    process = Thread(target=crawl, args=[q,a,searches[ii], output, ii])
    process.start()
    threads.append(process)

# We now pause execution on the main thread by 'joining' all of our started threads.
# This ensures that each has finished processing the urls.
for process in threads:
    process.join()

#########################################

sums = {}

for i in range(4):
    for e in output[i]:
        if e[0] not in sums:
            sums[e[0]] = e[1]
        else:
            sums[e[0]] += e[1]

total_sum = 0
for k in sums:
    total_sum += sums[k]

test = []
for k in sums:
    sums[k] = sums[k]*100/total_sum
    test.append((k,sums[k]))

test.sort(key=lambda x: x[1])
test = test[::-1]

if ifNOT:
    test = test[::-1]

for i in range(len(test)):
    print(crayons.green(test[i][0]), end="")
    print(crayons.green(" -- " + str("%.2f" % test[i][1] + "%")))
