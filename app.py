from database.DBInterface import iDB
from database.QDrantDB import QDrantDB
from embed.embedInterface import iEmbed
from embed.openAIEmbed import OpenAIEmbed
from model.modelInterface import iModel
from model.GPT import GPT
from scraper.iCrawler import ICrawler
from scraper.crawler import Crawler
from frontend import web_app

import os
import sys

def run(db: iDB, embed: iEmbed, model: iModel, crawler: ICrawler):
    prompt = "What is CVE-2024-29943?"

    '''
    db.createCollection("InitialTesting", 1536)

    outputDir = "./data/"
    crawler.crawl("https://www.mozilla.org/en-US/security/advisories/mfsa2024-15/",
                  1,
                  cores=4,
                  outputDirectory=outputDir)

    embeddings = dict()

    for root, _, fileNames in os.walk(f"{outputDir}/text/"):
        for fileName in fileNames:
            with open(f'{root}/{fileName}', 'r', encoding="utf8") as file:
                # chunk the contents of the file
                embeddings.update(embed.createEmbedding(file.read()))

            os.remove(f'{root}/{fileName}')

    db.saveToDB(embeddings, "InitialTesting")
'''
    promptEmbedding = list(embed.createEmbedding(prompt,
                                                 maxChunkSize=sys.maxsize,
                                                 chunkOverlap=0,
                                                 delimiter="\n"*50).values())[0]
    hydeResponse = model.hydePrompt(prompt)
    hydeEmbedding = list(embed.createEmbedding(hydeResponse,
                                                 maxChunkSize=sys.maxsize,
                                                 chunkOverlap=0,
                                                 delimiter="\n"*50).values())[0]

    promptResults = db.queryDB(promptEmbedding, collectionNames=["InitialTesting"], maxHits=50)
    promptResponse = model.prompt(promptResults, prompt)
    hydeResults = db.queryDB(hydeEmbedding, collectionNames=["InitialTesting"], maxHits=50)
    hydeResponse = model.prompt(hydeResults, prompt)

    print(f"Prompt Response:\n{promptResponse}\nHyde Response:\n{hydeResponse}")

if __name__ == "__main__":
    #run(QDrantDB("129.21.21.11"),
    #    OpenAIEmbed,
    #    GPT("You are an advanced subject matter expert on the field of cybersecurity", "gpt-4-turbo-preview"),
    #    Crawler)
    web_app.run()