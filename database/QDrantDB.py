from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from .DBInterface import iDB
class QDrantDB(iDB):
    def __init__(self, host: str):
        self.client = QdrantClient(host=host, prefer_grpc=True, timeout=None)

    def createCollection(self, collectionName: str, size: int):
        self.client.recreate_collection(
            collection_name=collectionName,
            vectors_config={"text embedding" : models.VectorParams(
                size=size,
                distance=models.Distance.COSINE
            )}
        )


    def convertToPoints(self, texts: dict) -> list[PointStruct]:
        return [
            PointStruct(id=idx,
                        vector={"text embedding": embedding},
                        payload={"text": text},
                        )
            for idx, (embedding, text) in enumerate(zip(texts.values(), texts.keys()))
        ]


    def saveToCollection(self, collectionName: str, points: list[PointStruct]):
        self.client.upsert(collectionName, points)

    #Texts is a dict combo of text and embeddings output from an embedding model
    def saveToDB(self, texts: dict, collectionName: str):
        points = self.convertToPoints(texts)
        self.saveToCollection(collectionName, points)

    def getCollectionNames(self) -> list[str]:
        return [collection['name'] for collection in self.client.get_collections().dict()['collections']]

    def queryDB(self, embedding: list[float],
                collectionNames: list[str]=None, maxHits: int=100, minSimilarity: float=0) -> list:
        results = []
        if not collectionNames:
            collectionNames = self.getCollectionNames()

        # TODO: make sure to only search collections of the proper size
        for collection in collectionNames:
            results.append(self.client.search(collection_name=collection,
                                              query_vector=("text embedding", embedding),
                                              limit=maxHits,
                                              score_threshold=minSimilarity
                                              ))

        return results



