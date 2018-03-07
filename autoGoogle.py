import webbrowser
import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '[CREDENTIALS_PATH]'

common = ['the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as']
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
irregular = {'!':'', "@":'at', '#':'number', '$':'dollars', '%':'percent','&':'and'}

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

search_entry = ''
for word in q.split():
    if word in irregular:
        search_entry += irregular[word] + '+'
        continue
    search_entry += word + '+'

for ans in a:
    webbrowser.open('https://www.google.com/search?q='+search_entry+ans)
