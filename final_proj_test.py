import unittest
import sqlite3
import final_proj as proj
DBNAME = 'finalproject.db'

### You must write unit tests to show that the data access, storage, and processing components of your project are working correctly.

### You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’.

### Your tests should show that
# you are able to access data from all of your sources,
# that your database is correctly constructed and
# can satisfy queries that are necessary for your program, and that
# your data processing produces the results and data structures you need for presentation.
# -------


class TestDatabase(unittest.TestCase):
    def test_movies_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT ScriptId FROM Movies'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((1534,), result_list)
        self.assertEqual(len(result_list), 2000)
        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT m.ImdbId, c.ScriptId, m.Title, i.Genre, m.Year, i.ImdbRating, c.ImdbCharacterName, c.Words, c.Gender, c.Age
            FROM MoviesImdb as i
            	JOIN Movies as m
            	ON i.ImdbId = m.ImdbId
            	JOIN Characters as c
            	ON c.ScriptId = m.ScriptId
            WHERE i.Genre =  "Romance"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(1371, result_list[0])
        self.assertIn('Starman', result_list[0])
        self.assertIn('Romance', result_list[0])
        conn.close()


### testing the Movie class
class TestMovie(unittest.TestCase):
    def testConstructor(self):
        m1 = proj.Movie()
        m2 = proj.Movie(title="testing title", genre="testing genre")

        self.assertEqual(m1.title, None)
        self.assertEqual(m1.imdbid, None)
        self.assertEqual(m1.genre, None)

        self.assertEqual(m2.title, "testing title"),
        self.assertEqual(m2.genre, "testing genre")
        self.assertEqual(m2.imdbid, None)

    # def testStr(self):
    #     m1 = proj1.Media()
    #     m2 = proj1.Media("1999", "Prince")
    #     self.assertEqual(str(m1), "No Title by No Author(No Release Year)")
    #     self.assertEqual(str(m2), "1999 by Prince(No Release Year)")
    #
    # def testLen(self):
    #     m1 = proj1.Media()
    #     m2 = proj1.Media("1999", "Prince")
    #     self.assertEqual(len(m1), 0)
    #     self.assertEqual(len(m2), 0)

### testing the Movie class
class TestCharacter(unittest.TestCase):
    def testConstructor(self):
        m1 = proj.Character()
        m2 = proj.Character(charname="testing title", gender="testing gender", age=15)

        self.assertEqual(m1.charname, None)
        self.assertEqual(m1.gender, None)
        self.assertEqual(m1.age, None)

        self.assertEqual(m2.charname, "testing title"),
        self.assertEqual(m2.gender, "testing gender")
        self.assertEqual(m2.age, 15)


unittest.main()
# if __name__ == '__main__':
#     unittest.main()
