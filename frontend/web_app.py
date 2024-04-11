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
        #putting new changes here
        prompt = request.form['user_input']

        promptEmbedding = list(embed.createEmbedding(prompt,
                                                 maxChunkSize=sys.maxsize,
                                                 chunkOverlap=0,
                                                 delimiter="\n"*50).values())[0]

        promptResults = db.queryDB(promptEmbedding, collectionNames=["CLITesting"], maxHits=50)
        promptResponse = model.prompt(promptResults, prompt)

        # response = "This is where the AI response would go for: " + prompt
        return jsonify({'response': promptResponse})
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


def run():
    app.run(debug=True)


if __name__ == '__main__':
    run()