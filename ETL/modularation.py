import json
import pandas as pd
file = json.load(open("./output.json", "r", encoding="utf-8"))

movies = {}
for i in file.keys():
    if file[i]["movie_results"] != []:
        movies[i] = (file[i]["movie_results"][0])

tv = {}
for i in file.keys():
    if file[i]["tv_results"] != []:
        tv[i] = (file[i]["tv_results"][0])

episodes = {}
for i in file.keys():
    if file[i]["tv_episode_results"] != []:
        episodes[i] = (file[i]["tv_episode_results"][0])


json.dump(movies, open("./movies.json", "w", encoding="utf-8"), indent=4)
json.dump(tv, open("./tv.json", "w", encoding="utf-8"), indent=4)
json.dump(episodes, open("./episodes.json", "w", encoding="utf-8"), indent=4)