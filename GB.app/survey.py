from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder='/home/nika/GameBuddy/gamebuddy_app/templates/opros')

db_path = '/home/nika/GameBuddy/gamebuddy_app/database.db'

genres = ['Action', 'Adventure', 'Strategy', 'RPG']
tags = ['Tag1', 'Tag2', 'Tag3', 'Tag4']
years = ['2023', '2022', '2021', '2020']
languages = ['English', 'Russian', 'French']

class GameRecommendationApp:
    def __init__(self, recommendations):
        self.recommendations = recommendations
        self.current_index = 0

    def get_next_game(self):
        if self.current_index < len(self.recommendations):
            return self.recommendations[self.current_index]
        else:
            return None

    def rate_game(self, rating):
        game = self.recommendations[self.current_index]

        if rating == 'like':
            self.save_rating(game, 'like')
        elif rating == 'dislike':
            self.save_rating(game, 'dislike')

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

recommendations = ['Игра 11', 'Игра 7', 'Игра 8', 'Игра 9', 'Игра 10']
game_app = GameRecommendationApp(recommendations)

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
        return render_template('index.html', genres=genres, tags=tags, years=years, languages=languages)

@app.route('/recommendations')
def recommendations():
    game = game_app.get_next_game()
    if game:
        return render_template('rate.html', game=game)
    else:
        return render_template('completed.html')

@app.route('/rate', methods=['POST'])
def rate():
    rating = request.form['rating']
    game_app.rate_game(rating)
    return redirect(url_for('recommendations'))

if __name__ == '__main__':
    app.run()