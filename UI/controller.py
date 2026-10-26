import flet as ft

MAX_DURATA = 480


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._albumValue = None

    def fillDDGenre(self):
        try:
            genres = self._model.getAllGenres()
        except Exception as ex:
            self._view.create_alert(f"Errore nella lettura dei generi: {ex}")
            return
        self._view._ddGenre.options = [ft.dropdown.Option(g) for g in genres]
        self._view.update_page()

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        genre = self._view._ddGenre.value
        if genre is None:
            self._view.create_alert("Selezionare un genere dal menu a tendina.")
            return

        try:
            self._model.buildGraph(genre)
        except Exception as ex:
            self._view.create_alert(f"Errore nella creazione del grafo: {ex}")
            return

        self._view._txt_result.controls.append(ft.Text(f"Grafo correttamente creato per il genere {genre}."))
        self._view._txt_result.controls.append(ft.Text(f"Numero di vertici: {self._model.getNumNodes()}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumEdges()}"))
        if self._model.getNumNodes() == 0:
            self._view._txt_result.controls.append(
                ft.Text("Attenzione: nessun brano di questo genere e' mai stato venduto."))

        self.fillDDAlbum()
        self._view.update_page()

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodes() == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        numComp, maxSize = self._model.getComponentsInfo()
        self._view._txt_result.controls.append(ft.Text(f"Numero di componenti connesse: {numComp}"))
        self._view._txt_result.controls.append(
            ft.Text(f"Dimensione della componente connessa piu' grande: {maxSize} album"))

        best, degree, neighbors = self._model.getMaxDegreeAlbum()
        self._view._txt_result.controls.append(ft.Text(f"Album di grado massimo: {best} (grado {degree})"))
        for n, peso in neighbors:
            self._view._txt_result.controls.append(ft.Text(f"    {n} - peso {peso}"))

        self._view._txt_result.controls.append(
            ft.Text(f"Numero di archi tra album dello stesso artista: {self._model.getNumSameArtistEdges()}"))
        self._view.update_page()

    def handlePercorso(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodes() == 0:
            self._view.create_alert("Creare prima il grafo.")
            return

        if self._albumValue is None:
            self._view.create_alert("Selezionare un album di partenza dal menu a tendina.")
            return

        try:
            maxDuration = int(self._view._txtDurata.value)
        except (ValueError, TypeError):
            self._view.create_alert("Inserire un valore intero per la durata massima.")
            return

        if maxDuration <= 0 or maxDuration > MAX_DURATA:
            self._view.create_alert(f"La durata massima deve essere un intero compreso tra 1 e {MAX_DURATA}.")
            return

        path, affinity, duration = self._model.getBestPath(self._albumValue, maxDuration)

        if len(path) == 0:
            self._view._txt_result.controls.append(
                ft.Text(f"Nessun percorso possibile: l'album {self._albumValue} dura "
                        f"{self._albumValue.Duration:.1f} minuti, piu' della durata massima."))
            self._view.update_page()
            return

        self._view._txt_result.controls.append(ft.Text("Percorso d'ascolto trovato:"))
        for i, a in enumerate(path):
            self._view._txt_result.controls.append(
                ft.Text(f"{i + 1}. {a.Title} - {a.ArtistName} - {a.Duration:.1f} min"))
            if i < len(path) - 1:
                self._view._txt_result.controls.append(
                    ft.Text(f"        | peso {self._model.getWeight(a, path[i + 1])}"))

        self._view._txt_result.controls.append(ft.Text(f"Numero di album: {len(path)}"))
        self._view._txt_result.controls.append(ft.Text(f"Affinita' complessiva: {affinity}"))
        self._view._txt_result.controls.append(ft.Text(f"Durata complessiva: {duration:.1f} minuti"))
        self._view.update_page()

    def fillDDAlbum(self):
        self._albumValue = None
        self._view._ddAlbum.value = None
        self._view._ddAlbum.options = [
            ft.dropdown.Option(key=str(a.AlbumId), text=str(a), data=a, on_click=self._choiceAlbum)
            for a in self._model.getAllAlbums()]

    def _choiceAlbum(self, e):
        self._albumValue = e.control.data
