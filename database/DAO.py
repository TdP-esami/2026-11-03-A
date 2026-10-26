from database.DB_connect import DBConnect


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
