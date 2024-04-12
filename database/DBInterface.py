from abc import ABC, abstractmethod

class iDB(ABC):

    @abstractmethod
    def createCollection(self, collectionName: str, size: int):
        pass

    @abstractmethod
    def saveToDB(self, texts: dict, collectionName: str):
        pass

    @abstractmethod
    def queryDB(self, embedding: list[float],
                collectionNames: list[str]=None, maxHits: int=100, minSimilarity: float=0) -> list:
        pass

    @abstractmethod
    def getCollectionNames(self):
        pass