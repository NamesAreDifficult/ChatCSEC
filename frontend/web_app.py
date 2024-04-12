from flask import Flask, render_template, request, jsonify
#from database.DBInterface import iDB
from database.QDrantDB import QDrantDB
#from embed.embedInterface import iEmbed0
from embed.openAIEmbed import OpenAIEmbed
#from model.modelInterface import iModel
from model.GPT import GPT
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    db = QDrantDB("129.21.21.11")
    embed = OpenAIEmbed
    model = GPT("You are an advanced subject matter expert on the field of cybersecurity", "gpt-4-turbo-preview")

    if request.method == 'POST':
        #This is where the data comes in
        data = request.json
        prompt = data['user_input']

        if model_selection == 'HYDE':
            hydeResponse = model.hydePrompt(prompt)
            hydeEmbedding = list(embed.createEmbedding(hydeResponse,
                                                    maxChunkSize=sys.maxsize,
                                                    chunkOverlap=0,
                                                    delimiter="\n"*50).values())[0]

            hydeResults = db.queryDB(hydeEmbedding, collectionNames=[collection_selection], maxHits=50)
            hydeResponse = model.prompt(hydeResults, prompt)
            return jsonify({'response': hydeResponse})
        else:
            promptEmbedding = list(embed.createEmbedding(prompt,
                                                    maxChunkSize=sys.maxsize,
                                                    chunkOverlap=0,
                                                    delimiter="\n"*50).values())[0]

            promptResults = db.queryDB(promptEmbedding, collectionNames=[collection_selection], maxHits=50)
            promptResponse = model.prompt(promptResults, prompt)
            return jsonify({'response': promptResponse})

    return render_template('index.html')

model_selection = 'defualt'

@app.route('/switch_model', methods=['POST'])
def switch_model():
    global model_selection
    data = request.get_json()
    model_selection = data['model']
    print(model_selection)
    return jsonify({'message': 'Model switched to ' + model_selection})

collection_selection = "InitialTesting"

@app.route('/switch_collection', methods=['POST'])
def switch_collection():
    global collection_selection
    data = request.get_json()
    collection_selection = data['collection']
    return jsonify({'message': 'Collection switched to ' + collection_selection})

@app.route('/about')
def about():
    #TODO: Make this page better
    return render_template('about.html')


def run():
    app.run(debug=True)


if __name__ == '__main__':
    run()