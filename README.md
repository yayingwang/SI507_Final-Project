# SI507_Final-Project

● Data sources used, including instructions for a user to access the data sources.
Data sources used:
The two csv files used are download from https://github.com/matthewfdaniels/scripts/blob/graphs/meta_data7.csv.
meta_data7.csv contains ImdbId, Title, Year, Gross for 200 movies.
character_list5.csv contains CharacterName, Wordcounts, Gender and Age for 23048 characters.

In addition to the two csv files, I used the ImdbIds to request the following data from OMDB API.
Movie genre
Country (only select the first one)
Language (only select the first one)
IMDB Ratings

● Any other information needed to run the program (e.g., pointer to getting started info for
plotly)
The data presentation are as followed:
1. A "Results List.txt" file listing all the movies and characters from the chosen genre.
2. GRAPH 1. Male vs Female: Characters Age - Wordcounts.
3. GRAPH 2. Male vs Female: wordcounts percentage movies distribution.
4. GRAPH 3. Male vs Female: wordcounts percentage per movie.
The graphs are all created using plotly. (https://plot.ly/python/)


● Brief description of how your code is structured, including the names of significant data
processing functions (just the 2-3 most important functions--not a complete list) and class definitions. If there are large data structures (e.g., lists, dictionaries) that you create to organize your data for presentation, briefly describe them.

There are two classes to store the related data.
1. Class "Movie" is used to store a movie object with imdbid, scriptid, title, year, gross, genre, country, language and IMDB rating.
2. Class "Character" is used to store a character object with charname, scriptid, imdbid, word, gender, age.

Functions:
1. init_movie_classes() and init_char_classes() take a SQL result to create corresponding class instances.

2. cal_gender_wordcounts() takes a character_inst_lst, which is a list of Character instances, and calculates the accumulative word counts within different age range for male and female characters.
The output is gender_wordcounts_dic. Below is one example.
{'m': {'20-': 0, '20+': 0, '30+': 3989, '40+': 9931, '50+': 548, '60+': 1050}, 'f': {'20-': 0, '20+': 1988, '30+': 2421, '40+': 0, '50+': 0, '60+': 0}}

 3. cal_genderpercent_permovie() takes two inputs, a_movie_inst and character_inst_lst, to calculate the percentage of wordcount for all the female characters and male characters in a movie.
 The output is genderpercent_permovie_dic. Below is one example.
{'title': 'The Adjustment Bureau', 'imdbid': 'tt1385826', 'scriptid': 1556, 'gender_percentage': 0.8453366688982066, 'gender_wordcounts': {'m': 95966, 'f': 17558}}


● Brief user guide, including how to run the program and how to choose presentation options.
Please enter "genre " followed by a number below to search interested genre:
		Options:
			1. Action
			2. Comedy
			3. Drama
			4. Crime
			5. Biography
			6. Horror
			7. Adventure
			8. Animation
			9. Mystery
			10. Fantasy
			11. Sci-Fi
			12. Romance
			13. Short
			14. Thriller
			15. Western
			16. Film-Noir
