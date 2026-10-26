import copy

import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.Graph()
        self._albums = []
        self._idMap = {}

        self._bestPath = []
        self._bestAffinity = 0
        self._bestDuration = 0

    def getAllGenres(self):
        return DAO.getAllGenres()

    def buildGraph(self, genre):
        self._graph.clear()
        self._albums = DAO.getAlbumsByGenre(genre)
        self._idMap = {a.AlbumId: a for a in self._albums}

        self._graph.add_nodes_from(self._albums)

        for a1, a2, peso in DAO.getEdges(genre, self._idMap):
            self._graph.add_edge(a1, a2, weight=peso)

    def getNumNodes(self):
        return len(self._graph.nodes)

    def getNumEdges(self):
        return len(self._graph.edges)

    def getAllAlbums(self):
        return sorted(self._graph.nodes, key=lambda a: a.Title)

    # ------------------------------------------------------------------
    # PUNTO 1 - Stampa Info
    # ------------------------------------------------------------------
    def getComponentsInfo(self):
        """Restituisce il numero di componenti connesse e la dimensione della piu' grande."""
        components = list(nx.connected_components(self._graph))
        if not components:
            return 0, 0
        return len(components), max(len(c) for c in components)

    def getMaxDegreeAlbum(self):
        """Album di grado massimo e lista dei suoi vicini, ordinati per peso decrescente
        (a parita' di peso, in ordine alfabetico di titolo)."""
        if len(self._graph.nodes) == 0:
            return None, 0, []
        best = max(self._graph.nodes, key=lambda a: self._graph.degree(a))
        neighbors = [(n, self._graph[best][n]['weight']) for n in self._graph.neighbors(best)]
        neighbors.sort(key=lambda x: (-x[1], x[0].Title))
        return best, self._graph.degree(best), neighbors

    def getNumSameArtistEdges(self):
        return sum(1 for u, v in self._graph.edges if u.ArtistId == v.ArtistId)

    # ------------------------------------------------------------------
    # PUNTO 2 - Percorso d'ascolto
    # ------------------------------------------------------------------
    def getBestPath(self, start, maxDuration):
        self._bestPath = []
        self._bestAffinity = 0
        self._bestDuration = 0

        if start.Duration > maxDuration:
            return [], 0, 0

        self._ricorsione([start], start.Duration, 0, maxDuration)
        return self._bestPath, self._bestAffinity, self._bestDuration

    def _ricorsione(self, parziale, durata, affinita, maxDuration):
        # Non c'e' una lunghezza fissata: ogni cammino ammissibile e' una possibile soluzione,
        # quindi il confronto con la migliore va fatto ad ogni livello, non solo "in fondo".
        if (len(self._bestPath) == 0 or affinita > self._bestAffinity
                or (affinita == self._bestAffinity and durata < self._bestDuration)):
            self._bestPath = copy.deepcopy(parziale)
            self._bestAffinity = affinita
            self._bestDuration = durata

        ultimo = parziale[-1]
        for vicino in self._graph.neighbors(ultimo):
            if vicino in parziale:
                continue
            # due album consecutivi non possono essere dello stesso artista
            if vicino.ArtistId == ultimo.ArtistId:
                continue
            # vincolo di "budget": la durata totale non puo' superare quella massima
            if durata + vicino.Duration > maxDuration:
                continue

            parziale.append(vicino)
            self._ricorsione(parziale, durata + vicino.Duration,
                             affinita + self._graph[ultimo][vicino]['weight'], maxDuration)
            parziale.pop()

    def getWeight(self, a1, a2):
        return self._graph[a1][a2]['weight']
