from database.DBInterface import iDB
from database.QDrantDB import QDrantDB
from embed.embedInterface import iEmbed
from embed.openAIEmbed import OpenAIEmbed
from model.modelInterface import iModel
from model.GPT import GPT
from scraper.iCrawler import ICrawler
from scraper.crawler import Crawler
import click
import os
import sys

def displayMenu():
    print('''ChatCSEC V2
    Options:
    prompt <prompt>
    crawl <url> <depth>
    quit
    ''')


def pause():
    input("Press Enter to Continue")


def promptModel(command: str, model:iModel, embed: iEmbed, db: iDB):
    if command.strip() == "prompt":
        print("Please enter a prompt after the prompt command.")
        pause()
        return

    prompt = command[5:].strip()

    maxHits = int(input("Enter the amount of semantic search results you would like to return: "))
    minSim = float(input("Enter a float for minSimilarity: "))

    promptEmbedding = list(embed.createEmbedding(prompt,
                                                 maxChunkSize=sys.maxsize,
                                                 chunkOverlap=0,
                                                 delimiter="\n"*50).values())[0]
    hydeResponse = model.hydePrompt(prompt)
    hydeEmbedding = list(embed.createEmbedding(hydeResponse,
                                                 maxChunkSize=sys.maxsize,
                                                 chunkOverlap=0,
                                                 delimiter="\n"*50).values())[0]

    promptResults = db.queryDB(promptEmbedding, collectionNames=["CLITesting"], maxHits=50)
    promptResponse = model.prompt(promptResults, prompt)
    hydeResults = db.queryDB(hydeEmbedding, collectionNames=["CLITesting"], maxHits=50)
    hydeResponse = model.prompt(hydeResults, prompt)

    print(f"Prompt Response:\n{promptResponse}\nHyde Response:\n{hydeResponse}")
    pause()

def crawl(command: str, db:iDB, crawler: ICrawler, embed: iEmbed):
    arguments = command.split(" ")
    if len(arguments) < 3:
        print("Invalid arguments supplied")
        pause()
        return

    depth = int(arguments[2])
    baseDirs = input("Input comma seperated urls for base directories, or enter nothing to match any").split(',')
    urlReg = input("Input urlRegex to match on, or enter nothing to match any")
    contReg = input("Input content regex to match on, or enter nothing ot match any")
    skip = input("Skip data that doesn't match regex? [Y/n]")

    if len(baseDirs) == 1 and baseDirs[0] == '':
        baseDirs = None

    if urlReg == '':
        urlReg = None

    if contReg == '':
        contReg = None

    if skip.lower().startswith('n'):
        skip = False
    else:
        skip = True


    outputDir = "./data/"
    crawler.crawl(arguments[1],
                  depth,
                  cores=4,
                  outputDirectory=outputDir,
                  baseDirectory=baseDirs,
                  urlRegexString=urlReg,
                  contentRegexString=contReg,
                  matchSkip=skip)

    embeddings = dict()

    for root, _, fileNames in os.walk(f"{outputDir}/text/"):
        for fileName in fileNames:
            with open(f'{root}/{fileName}', 'r', encoding="utf8") as file:
                # chunk the contents of the file
                embeddings.update(embed.createEmbedding(file.read()))

            os.remove(f'{root}/{fileName}')

    db.saveToDB(embeddings, "CLITesting")


def runCLI(db: iDB, embed: iEmbed, model: iModel, crawler: ICrawler):
    db.createCollection("CLITesting", 1536)
    while True:
        displayMenu()
        command = input('>')
        if command.lower().startswith("prompt"):
            promptModel(command, model, embed, db)
        elif command.lower().startswith("crawl"):
            crawl(command, db, crawler, embed)
        elif command.lower().startswith("quit"):
            print("Exiting")
            sys.exit(0)
        else:
            print("Invalid command")
            pause()
        os.system("cls")



def runTest(db: iDB, embed: iEmbed, model: iModel, crawler: ICrawler):
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
    runCLI(QDrantDB("129.21.21.11"),
        OpenAIEmbed,
        GPT("You are an advanced subject matter expert on the field of cybersecurity", "gpt-4-turbo-preview"),
        Crawler)