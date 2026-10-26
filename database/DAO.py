from database.DB_connect import DBConnect
from model.album import Album


class DAO():

    @staticmethod
    def getAllGenres():
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                select g.Name
                from genre g
                where g.Name is not null
                order by g.Name
                """

        cursor.execute(query)

        for row in cursor:
            results.append(row["Name"])

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getAlbumsByGenre(genre):
        """Album con almeno un brano del genere selezionato venduto almeno una volta.
        La durata e' quella complessiva dell'album (tutti i brani), in minuti."""
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                select al.AlbumId, al.Title, al.ArtistId, ar.Name as ArtistName,
                       d.TotMs / 60000 as Duration
                from album al, artist ar,
                     (select t.AlbumId, sum(t.Milliseconds) as TotMs
                      from track t
                      group by t.AlbumId) d
                where al.ArtistId = ar.ArtistId
                and d.AlbumId = al.AlbumId
                and al.AlbumId in (select t.AlbumId
                                   from track t, genre g, invoiceline il
                                   where t.GenreId = g.GenreId
                                   and il.TrackId = t.TrackId
                                   and g.Name = %s)
                order by al.Title
                """

        cursor.execute(query, (genre,))

        for row in cursor:
            row["Duration"] = float(row["Duration"])
            results.append(Album(**row))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getEdges(genre, idMap):
        """Coppie di album con brani del genere selezionato presenti nella stessa fattura.
        Il peso e' il numero di fatture distinte in comune."""
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                select t1.AlbumId as a1, t2.AlbumId as a2, count(distinct il1.InvoiceId) as peso
                from invoiceline il1, invoiceline il2, track t1, track t2, genre g
                where il1.InvoiceId = il2.InvoiceId
                and il1.TrackId = t1.TrackId
                and il2.TrackId = t2.TrackId
                and t1.GenreId = g.GenreId
                and t2.GenreId = g.GenreId
                and g.Name = %s
                and t1.AlbumId < t2.AlbumId
                group by t1.AlbumId, t2.AlbumId
                """

        cursor.execute(query, (genre,))

        for row in cursor:
            if row["a1"] in idMap and row["a2"] in idMap:
                results.append((idMap[row["a1"]], idMap[row["a2"]], row["peso"]))

        cursor.close()
        conn.close()
        return results
