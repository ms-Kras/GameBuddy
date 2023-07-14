from flask import Flask, render_template, request, redirect, url_for
from Game_recomender import GameRecommender
import sqlite3

# --------------------------------вот этот кусок оптимизировать--------------------------------------------
FILENAME = '/home/nika/GameBuddy/data/games_with_eng_descriptions_clear.csv'               # позже заменить на БД
game_recommender = GameRecommender(FILENAME, ['Name', 'description'], 'Name', 'description') # позже заменить
df = game_recommender.process()                                                            # вообще как-то убрать внутрь файла
norm_corpus = game_recommender.get_normalized_corpus()                                     # вообще как-то убрать внутрь файла
wts_df = game_recommender.get_bert_weights(norm_corpus)                                    # вообще как-то убрать внутрь файла
# --------------------------------вот этот кусок оптимизировать--------------------------------------------

app = Flask(__name__, template_folder='/home/nika/GameBuddy/GB.app/templates/opros')

db_path = '/home/nika/GameBuddy/GB.app/database.db'

genres = ['Action', 'Adventure', 'AnimationModeling', 'AudioProduction', 'Casual', 'DesignIllustration', 'EarlyAccess', 'Education', 
          'FreetoPlay', 'GameDevelopment', 'Indie', 'MassivelyMultiplayer', 'Movie', 'PhotoEditing', 'RPG', 'Racing', 'Simulation', 
          'SoftwareTraining', 'Sports', 'Strategy', 'Utilities', 'VideoProduction', 'WebPublishing']

tags = ['DPlatformer', 'VideoProduction', 'AudioProduction', 'Utilities', 'DFighter', 'Difficult', 'TurnBasedTactics', 'ChoicesMatter', 
        'FemaleProtagonist', 'SoftwareTraining', 'AutomobileSim', 'Sandbox', 'PointClick', 'Medieval', 'Building', 'Cats', 'SocialDeduction', 
        'Puzzle', 'Zombies', 'ThirdPerson', 'Lemmings', 'WorldWarII', 'Comedy', 'RPGMaker', 'Memes', 'Mechs', 'MMORPG', 'MassivelyMultiplayer', 
        'Spectaclefighter', 'Indie', 'StrategyRPG', 'Relaxing', 'Atmospheric', 'Colorful', 'Music', 'MOBA', 'Typing', 'WarhammerK', 'FreetoPlay', 
        'RTS', 'Nudity', 'Retro', 'ArenaShooter', 'ShootEmUp', 'ThirdPersonShooter', 'Roguelite', 'Crime', 'Exploration']

years = ['2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', 
         '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000']

languages = ['English', 'Russian', 'French']

class GameRecommendationApp:
    def __init__(self, recommendations):
        self.recommendations = recommendations
        self.current_index = 0

    def get_next_game(self):
        if self.current_index < len(self.recommendations):
            game = self.recommendations[self.current_index]
            self.current_index = self.current_index + 1
            return game
        else:
            return None
        
    def get_current_game(self):
        if self.current_index > 0:
            return self.recommendations[self.current_index - 1]
        else:
            return None
        
    def get_current_game_description(self):
        if self.current_index > 0:
            return self.recommendations[self.current_index - 1][1]  # Индекс 1 соответствует описанию игры
        else:
            return None
    
    def has_more_games(self):
        return self.current_index < len(self.recommendations)

    def rate_game(self, rating):
        game = self.recommendations[self.current_index]
        self.save_rating(game, rating)
        self.current_index += 1

    def save_rating(self, game, rating):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            game TEXT,
                            rating TEXT
                        )''')

        cursor.execute("INSERT INTO ratings (game, rating) VALUES (?, ?)", (game, rating))

        conn.commit()
        conn.close()



def save_data(genres, disliked_genres, tags, disliked_tags, years, languages, wishes, steams):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        genres TEXT,
                        disliked_genres TEXT,
                        tags TEXT,
                        disliked_tags TEXT,
                        years TEXT,
                        languages TEXT,
                        wishes TEXT,
                        steams TEXT
                    )''')

    cursor.execute("INSERT INTO user_data (genres, disliked_genres, tags, disliked_tags, years, languages, wishes, steams) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (', '.join(genres), ', '.join(disliked_genres), ', '.join(tags), ', '.join(disliked_tags),
                    ', '.join(years), ', '.join(languages), wishes, steams))

    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')
        selected_disliked_genres = request.form.getlist('disliked_genres')
        selected_tags = request.form.getlist('tags')
        selected_disliked_tags = request.form.getlist('disliked_tags')
        selected_years = request.form.getlist('years')
        selected_languages = request.form.getlist('languages')
        wishes = request.form.get('wishes')
        steams = request.form.get('steams')

        save_data(selected_genres, selected_disliked_genres, selected_tags, selected_disliked_tags,
                  selected_years, selected_languages, wishes, steams)

        return redirect(url_for('recommendations'))
    else:
        game = game_app.get_current_game()
        description = game_app.get_current_game_description()
        return render_template('rate.html', game=game, description=description)
    
def get_user_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT genres, tags, wishes FROM user_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row:
        genres, tags, wishes = row
        input_text = f"{genres} {tags} {wishes}"
        return input_text
    else:
        return ""

# recommendations = game_recommender.recommend_games_by_text(get_user_data(), n=5)  # здесь проставить параметры подбора
# recommendations = recommendations.split('\n')
# game_app = GameRecommendationApp(recommendations)
recomdations=

@app.route('/recommendations')
def recommendations():
    print("run recommendations")
    game = game_app.get_next_game()
    if game:
        index = game_app.current_index
        return render_template('rate.html', game=game, index=index)
    else:
        return render_template('completed.html')

def save_rating(game, rating):
    print("run save_rating")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game TEXT,
                        rating INTEGER
                    )''')

    cursor.execute("INSERT INTO ratings (game, rating) VALUES (?, ?)", (game, rating))

    conn.commit()
    conn.close()

@app.route('/rate', methods=['POST'])
def rate():
    print("start rate")
    rating = int(request.form['rating'])
    action = request.form['action']

    if action == 'Next':    
        print("old rating saved")
        save_rating(game_app.get_current_game(), rating)
        if game_app.has_more_games():
            print("New game received")              
            return redirect(url_for('recommendations'))
        else:
            print("No new game")
            return render_template('completed.html')
    elif action == 'Stop':
        return render_template('completed.html')

if __name__ == '__main__':
    app.run()
