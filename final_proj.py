from secret import OMDB_KEY
import requests
import json
import sys
import sqlite3
import csv
import plotly.graph_objects as go

###### ----------section1. creating database ----------######
### Your database must have at least two tables, and there must be at least one relation (primary key - foreign key) between the two tables
### 1. from csv - 2 table
DBNAME = 'finalproject.db'
MOVIECSV = 'meta_data7_updated.csv'
CHARCSV = 'character_list5_updated.csv'

### creating the databased with two tables
def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Movies';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'MoviesImdb';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Characters';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE "Movies" (
        	"Id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        	"ScriptId" INTEGER,
        	"ImdbId" TEXT,
        	"Title"	TEXT,
        	"Year"	INTEGER,
        	"Gross"	INTEGER,
            FOREIGN KEY(ScriptId) REFERENCES Characters(ScriptId)
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE "MoviesImdb" (
        	"Id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        	"ImdbId" TEXT,
        	"Genre"	TEXT,
        	"Country" TEXT,
            "Language" TEXT,
        	"ImdbRating" INTEGER,
            FOREIGN KEY(ImdbId) REFERENCES Movies(ImdbId)
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE "Characters" (
        	"Id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        	"ScriptId"	INTEGER,
        	"ImdbCharacterName"	TEXT,
        	"Words"	INTEGER,
        	"Gender"	TEXT,
        	"Age"	INTEGER,
            FOREIGN KEY(ScriptId) REFERENCES Movies(ScriptId)
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()





### inserting data from MOVIECSV(meta_data7.csv')
def insert_data_to_movies_table():
    ### reading from the CSV
    with open(MOVIECSV, newline='', encoding='utf8') as csvfile:
        # print(csvfile)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        movie_row_lst = []
        print(spamreader)

        for row in spamreader:
            # print(row[3])
            # print(', '.join(row))
            movie_row_lst.append(row)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for inst in movie_row_lst[1:]:
        insertion = (inst[0], inst[1], inst[2], inst[3], inst[4])

        statement = '''INSERT INTO "Movies" (ScriptId, ImdbId, Title, Year, Gross)'''
        statement += '''VALUES (?, ?, ?, ?, ?)'''

        cur.execute(statement, insertion)
    conn.commit()
    conn.close()





### inserting data from CHARCSV（character_list5.csv'）
def insert_data_to_characters_table():
    ### reading from the CSV
    with open(CHARCSV, newline='', encoding='utf8') as csvfile:
        # print(csvfile)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        char_row_lst = []
        # print(spamreader)
        for row in spamreader:
            # if len(row) != 5:
            #     print("this one")
            # print(', '.join(row))
            char_row_lst.append(row)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for inst in char_row_lst[1:]:
        insertion = (inst[0], inst[1], inst[2], inst[3], inst[4])

        statement = '''INSERT INTO "Characters" (ScriptId, ImdbCharacterName, Words, Gender, Age)'''
        statement += '''VALUES (?, ?, ?, ?, ?)'''

        cur.execute(statement, insertion)
    conn.commit()
    conn.close()





### step2. getting genre from IMDB API + cache, and then update the Movies table
CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params, private_keys=["apikey"]):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)

def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params)
        print(resp.url)
        resp_dic = json.loads(resp.text)
        if resp_dic["Response"] != "False":
            CACHE_DICTION[unique_ident] = resp_dic
            dumped_json_cache = json.dumps(CACHE_DICTION)
            fw = open(CACHE_FNAME,"w")
            fw.write(dumped_json_cache)
            fw.close() # Close the open file
            return CACHE_DICTION[unique_ident]

### getting the IMDBid from the Movies tables
def getting_imdbid_db():
    imdbid_lst = []
    with open(MOVIECSV, newline='', encoding='utf8') as csvfile:
        # print(csvfile)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        movie_row_lst = []
        for row in spamreader:
            movie_row_lst.append(row)

    for inst in movie_row_lst[1:]:
        imdbid_lst.append(inst[1])

    return imdbid_lst


### getting data from OMDB API using the IMDBid list from getting_imdbid_db
def getting_data_omdbapi():
    movieid_lst = getting_imdbid_db()
    print("212")
    print(type(movieid_lst), len(movieid_lst))
    # print(movieid_lst)

    response_dic_lst = []
    baseurl = "http://www.omdbapi.com/?"
    params = {"apikey": OMDB_KEY}

    for a_movieid in movieid_lst:
        # print(a_movieid)
        params["i"] = a_movieid
        # print(params)
        response_dic = make_request_using_cache(baseurl, params)
        response_dic_lst.append(response_dic)
    return response_dic_lst

def update_movies_with_omdbdata():
    imdb_moviedic_lst = getting_data_omdbapi()

    movies_fordb_lst = []
    for a_moviedic in imdb_moviedic_lst:
        movies_fordb_dic = {}
        # print(type(a_moviedic))
        # print(a_moviedic)
        movies_fordb_dic["ImdbId"] = a_moviedic["imdbID"]
        movies_fordb_dic["Genre"] = a_moviedic["Genre"].split(', ')[0]
        movies_fordb_dic["Country"] = a_moviedic["Country"].split(', ')[0]
        movies_fordb_dic["Language"] = a_moviedic["Language"].split(', ')[0]
        movies_fordb_dic["ImdbRating"] = a_moviedic["imdbRating"]
        movies_fordb_lst.append(movies_fordb_dic)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for a_moviedic_fordb in movies_fordb_lst:
        # print("238")
        # print(a_moviedic_fordb)
        inst = list(a_moviedic_fordb.values())
        # print(inst)
        # print(type(inst))

        insertion = (inst[0], inst[1], inst[2], inst[3], inst[4])

        statement = '''INSERT INTO "MoviesImdb" (ImdbId, Genre, Country, Language, ImdbRating)'''
        statement += '''VALUES (?, ?, ?, ?, ?)'''

        cur.execute(statement, insertion)
    conn.commit()
    conn.close()
    print("Done!")




###### ----------section2. data Processing ----------######
### Program creates data structures and data processing results needed for presentation.
### At least one class is defined.
class Movie(object):
    def __init__(self, imdbid=None, scriptid=None, title=None, year=None, gross=None, genre=None, country=None, language=None, imdbrating=None):
        self.imdbid = imdbid
        self.scriptid = scriptid
        self.title = title
        self.year = year
        self.gross = gross
        self.genre = genre
        self.country = country
        self.language = language
        self.imdbrating = imdbrating

    def __str__(self):
        # return "{} {} is a {} movie from {}".format(self.imdbid, self.title, self.genre, self.year)
        return "{: <12} {: <30} {: <20} {: <20} {: <20}".format(self.imdbid, self.title, self.year, self.genre, self.imdbrating)


class Character(object):
    def __init__(self, charname=None, scriptid=None, imdbid=None, word=None, gender=None, age=None):
        self.charname = charname
        self.scriptid = scriptid
        self.imdbid = imdbid
        self.word = word
        self.gender = gender
        self.age = age

    def __str__(self):
        # return "{} is a {} years-old {} character from movie {} {}".format(self.charname, self.age, self.gender, self.imdbid, self.scriptid)
        return "{: <20} {: <20} {: <20} {: <20}".format(self.charname, self.age, self.gender, self.word)

def init_movie_classes(sql_result_lst):
    movie_inst_lst = []
    movie_id_record = []

    for a_char_sqltuple in sql_result_lst:
        # print(a_char_sqltuple)
        ### movie class first
        if a_char_sqltuple[0] not in movie_id_record:
            # print("320 creating movie classes")
            a_movie_inst = Movie(title=a_char_sqltuple[2], imdbid=a_char_sqltuple[0], scriptid=a_char_sqltuple[1], year=a_char_sqltuple[4], genre=a_char_sqltuple[3], imdbrating=a_char_sqltuple[5])
            movie_inst_lst.append(a_movie_inst)
            movie_id_record.append(a_char_sqltuple[0])   ### record the movie created
            # print("326")
            # print(a_movie_inst)
        # print(len(movie_inst_lst))
        # print(len(movie_id_record))
    return movie_inst_lst

def init_char_classes(sql_result_lst):
    character_inst_lst = []
    for a_char_sqltuple in sql_result_lst:
        ### character class
        # print("329 creating character classes")
        a_character_inst = Character(charname=a_char_sqltuple[6], scriptid=a_char_sqltuple[1], imdbid=a_char_sqltuple[0], word=a_char_sqltuple[7], gender=a_char_sqltuple[8], age=a_char_sqltuple[9])
        character_inst_lst.append(a_character_inst)
        # print(a_character_inst)
    return character_inst_lst

### counting words for a char list, devided into make and female
def cal_gender_wordcounts(character_inst_lst):
    m_word_dic = {'20-':0, '20+':0, '30+':0, '40+':0, '50+':0, '60+':0}
    f_word_dic = {'20-':0, '20+':0, '30+':0, '40+':0, '50+':0, '60+':0}
    for a_char_inst in character_inst_lst:
        if a_char_inst.age != "NULL":
            if a_char_inst.gender == "m":
                # print("346")
                # print(a_char_inst.age)
                # print(type(a_char_inst.age))
                if a_char_inst.age <= 20:
                    m_word_dic["20-"] += a_char_inst.word
                elif a_char_inst.age <= 30:
                    m_word_dic["20+"] += a_char_inst.word
                elif a_char_inst.age <= 40:
                    m_word_dic["30+"] += a_char_inst.word
                elif a_char_inst.age <= 50:
                    m_word_dic["40+"] += a_char_inst.word
                elif a_char_inst.age <= 60:
                    m_word_dic["50+"] += a_char_inst.word
                else:
                    m_word_dic["60+"] += a_char_inst.word
            else:
                if a_char_inst.age <=20:
                    f_word_dic["20-"] += a_char_inst.word
                elif a_char_inst.age <=30:
                    f_word_dic["20+"] += a_char_inst.word
                elif a_char_inst.age <=40:
                    f_word_dic["30+"] += a_char_inst.word
                elif a_char_inst.age <=50:
                    f_word_dic["40+"] += a_char_inst.word
                elif a_char_inst.age <=60:
                    f_word_dic["50+"] += a_char_inst.word
                else:
                    f_word_dic["60+"] += a_char_inst.word
    gender_wordcounts_dic = {}
    gender_wordcounts_dic["m"] = m_word_dic
    gender_wordcounts_dic["f"] = f_word_dic
    return gender_wordcounts_dic

### counting f/m percentage per movie for a movie instances list
def cal_genderpercent_permovie(a_movie_inst, character_inst_lst):
    id = a_movie_inst.scriptid
    char_lst_permovie = []
    n_m = 0
    n_f = 0
    gender_words_permovie = {"m":n_m, "f":n_f}  ## dic with f/m as keys
    genderpercent_permovie_dic = {}             ## large dictionary per movie

    for a_char_inst in character_inst_lst:
        if a_char_inst.scriptid == id:
            char_lst_permovie.append(a_char_inst)

        if len(char_lst_permovie) != 0:
            for a_char in char_lst_permovie:
                if a_char.gender == "m":
                    n_m = n_m + a_char.word
                else:
                    n_f = n_f + a_char.word
        gender_words_permovie["m"] = n_m
        gender_words_permovie["f"] = n_f
    # print("404")
    # print(gender_words_permovie)
    ### cal the percentage
    gender_percentage_permovie = n_m/(n_m + n_f)
    # print("408")
    # print(gender_percentage_permovie)

    ### write into the large dict
    genderpercent_permovie_dic["title"] = a_movie_inst.title
    genderpercent_permovie_dic["imdbid"] = a_movie_inst.imdbid
    genderpercent_permovie_dic["scriptid"] = id
    genderpercent_permovie_dic["gender_percentage"] = gender_percentage_permovie   ### a percentage number
    genderpercent_permovie_dic["gender_wordcounts"] = gender_words_permovie   ### {'m': 100, "f":1000}
    return genderpercent_permovie_dic



###### ----------section4. data presentation ----------######
def plot_age_distribution(character_inst_lst):
    print("...Creating GRAPH 1...")
    gender_wordcounts_dic = cal_gender_wordcounts(character_inst_lst)
    ages = ['20-', '20+', '30+', '40+', '50+', '60+']
    # print("409")
    # print(ages)
    m_wordcounts = list(gender_wordcounts_dic["m"].values())
    f_wordcounts = list(gender_wordcounts_dic["f"].values())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = ages,
        y = m_wordcounts,
        name='Male characters',
        marker_color="rgb(28, 119, 195)"
    ))
    fig.add_trace(go.Bar(
        x=ages,
        y = f_wordcounts,
        name='Female characters',
        marker_color='rgb(205, 92, 92)'
    ))


    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_layout(title_text='GRAPH 1. Male vs Female: Characters Age - Wordcounts')
    fig.show()
    print("OUTPUT GRAPH 1 is created!")
    pass


def plot_genderpercent_histogram(movie_inst_lst, character_inst_lst):
    print("...Creating GRAPH 2...")
    genderpercent_lst = []
    movie_title_lst = []

    for a_movie_inst in movie_inst_lst:
        # print("608")
        # print(a_movie_inst)
        # print(character_inst_lst)
        genderpercent_permovie_dic = cal_genderpercent_permovie(a_movie_inst, character_inst_lst)  ## return a genderpercent_permovie_dic for a movie
        genderpercent_lst.append(genderpercent_permovie_dic["gender_percentage"])
        movie_title_lst.append(genderpercent_permovie_dic["title"])
    # print("435")
    # print(genderpercent_lst)

    fig = go.Figure(
        data=[go.Histogram(
            x = genderpercent_lst,
            xbins = {"size": 0.05},
            marker_color="rgb(20, 142, 121)"
            # color= genderpercent_lst,
            # color_continuous_scale='Magma'
            )])
    fig.update_layout(barmode="overlay",bargap=0.1)
    fig.update_layout(title_text='GRAPH 2. Male vs Female: wordcounts percentage movies distribution.', xaxis={"title": "Male characters' wordcounts percentage"}, yaxis={"title": "Number of movies"})
    fig.show()
    print("OUTPUT GRAPH 2 is created!")

    print("...Creating GRAPH 3...")
    re_genderpercent_lst = []
    for a_perecent in genderpercent_lst:
        re_perecent = 1 - a_perecent
        re_genderpercent_lst.append(re_perecent)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=movie_title_lst,
        x=genderpercent_lst,
        name='Male characters',
        orientation='h',
        marker=dict(
            color='rgb(28, 119, 195)',  ### male color
            )
        )
    )
    fig.add_trace(go.Bar(
        y=movie_title_lst,
        x=re_genderpercent_lst,
        name='Female characters',
        orientation='h',
        marker=dict(
            color='rgb(205, 92, 92)',  ### female color
            )
        )
    )
    # fig.update_traces(marker_width=10)
    fig.update_layout(barmode='stack', title_text='GRAPH 3. Male vs Female: wordcounts percentage per movie.')
    fig.show()
    print("OUTPUT GRAPH 3 is created!")
    pass


def write_txt(movie_inst_lst, character_inst_lst):
    genre = movie_inst_lst[0].genre

    outputfile_txt = ""
    outputfile_txt += "--------------------There are {} number of movies from genre: {}.--------------------".format(len(movie_inst_lst), genre)
    outputfile_txt += "\n{: <5} {: <10} {: <30} {: <20} {: <20} {: <20}".format(" ", "IMDB ID", "Movie Title", "Year", "Genre", "IMDB Rating")
    n = 1
    for a_movie_inst in movie_inst_lst:
        outputfile_txt += "\n"
        outputfile_txt += str(n) + ". "
        outputfile_txt += str(a_movie_inst)
        n += 1

    outputfile_txt += "\n\n\n\n"
    outputfile_txt += "--------------------There are {} number of characters from genre: {}.--------------------".format(len(character_inst_lst), genre)
    outputfile_txt += "\n{: <5} {: <18} {: <20} {: <20} {: <20}".format(" ", "Character Name", "Actor/Actress age", "Actor/Actress gender", "Character word counts")
    m = 1
    for a_char_inst in character_inst_lst:
        outputfile_txt += "\n"
        outputfile_txt += str(m) + ". "
        outputfile_txt += str(a_char_inst)
        # outputfile_txt += "\n"
        m += 1

    # print(outputfile_txt)

    outfile = open("Results List.txt","w")
    for a_line in outputfile_txt:
        outfile.write(a_line)
    outfile.close()
    print("OUTPUT 1. Results List.txt is created!")
    return None



###### ---------- user interaction ----------######
def process_command_insql(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    main_command = command.split()[0]     ### genre
    params_command = command.split()[1:]     ### other detail commands

    ### decide which SQL command to run
    if main_command == 'genre':
        # print("running BARS blocks")
        base_statement = '''
            SELECT m.ImdbId, c.ScriptId, m.Title, i.Genre, m.Year, i.ImdbRating, c.ImdbCharacterName, c.Words, c.Gender, c.Age
            FROM MoviesImdb as i
            	JOIN Movies as m
            	ON i.ImdbId = m.ImdbId
            	JOIN Characters as c
            	ON c.ScriptId = m.ScriptId
        '''

        genre_dic = {
        			"1": "Action", "2": "Comedy", "3": "Drama",
        			"4": "Crime", "5": "Biography", "6": "Horror",
        			"7": "Adventure", "8": "Animation", "9": "Mystery",
        			"10": "Fantasy", "11": "Sci-Fi", "12": "Romance",
        			"13": "Short", "14": "Thriller",  "15": "Western",
        			"16": "Film-Noir"
        }

        genre_query = genre_dic[params_command[0]]
        filter_state = ''' WHERE i.Genre =  "{}"'''.format(genre_query)
        # print(base_statement + filter_state)

    ### executing SQL
    sql_statement_str = base_statement + filter_state

    cur.execute(sql_statement_str)
    sql_result_lst = cur.fetchall()

    conn.commit()
    conn.close()
    return sql_result_lst      ### the query result from sql database


### making sure the command is valid
def command_checker(main_command, params_command):
    check = True
    # print()

    ### judging main_command
    if main_command == 'genre':
        v_params_command = [ "1", "2", "3", "4", "5", "6", "7", "8", "9","10","11","12","13","14","15","16"
        ]
    else:
        check = False

    ### judging params_command
    for param in params_command:
        # if "=" in param:
        #     param = param.split("=")[0]
        if param not in v_params_command:
            # print("587 command_checker incorrect")
            check = False
        else:
            # print("590 command_checker correct")
            pass
    return check

def load_help_text():
    with open('help.txt') as f:
        return f.read()


def interactive_prompt():
    help_text = load_help_text()
    response = ''

    while True:
        response = input('Please enter a command: ')

        if response == 'help':
            print(help_text)

        elif "exit" in response:
            print("Bye!")
            break

        elif response and response.isspace() == False:     ### not space and empty
            main_command = response.split()[0]
            params_command = response.split()[1:]     ### other details commands

            if len(params_command) != 0:
                if command_checker(main_command, params_command) == True:
                    sql_result_lst = process_command_insql(response)
                    movie_inst_lst = init_movie_classes(sql_result_lst)      ### creating movies instances
                    character_inst_lst = init_char_classes(sql_result_lst)   ### creating char instances

                    write_txt(movie_inst_lst, character_inst_lst)

                    ### creating 3 GRAPHs
                    plot_age_distribution(character_inst_lst)
                    plot_genderpercent_histogram(movie_inst_lst, character_inst_lst)
                else:
                    print('Command not recognized: ' + response)
            else:
                print('No number for '+ response)
        else:
            print('Empty command. Please try again.' + response)



### recreating the db or not
if len(sys.argv) > 1 and sys.argv[1] == '--init':
    print('Deleting db and starting over from scratch.')
    init_db()
    insert_data_to_movies_table()
    insert_data_to_characters_table()
    update_movies_with_omdbdata()
else:
    print('Leaving the DB alone.')

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    interactive_prompt()
