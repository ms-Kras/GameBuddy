import streamlit as st
import pandas as pd
import os

def main():
    st.title('Game Preferences Survey')
    st.subheader('Пожалуйста, заполните опрос')

    # Опросные вопросы
    genres = st.multiselect('Выберите предпочитаемые жанры:', ['Action', 'Adventure', 'Strategy', 'RPG'])
    pass_genres = st.multiselect('Убрать жанры:', ['Action', 'Adventure', 'Strategy', 'RPG'])
    years = st.multiselect('Выбрать год:', [2023, 2022, 2021])
    rating = st.slider('Рейтинг от', min_value=0, max_value=100)
    pop_tags = st.multiselect('Укажите теги', ['открытый мир', 'похоже на Dark Souls', 'тяжелая', 'кооператив'])
    pass_tags = st.multiselect('Исключите теги', ['открытый мир', 'похоже на Dark Souls', 'тяжелая', 'кооператив'])
    language = st.multiselect('Выберите язык', ['English', 'Russian', 'French'])
    votes = st.slider('Минимум отзывов', min_value=0, max_value=100)
    steam_profile = st.text_input('Введите ссылку на профиль в Steam')
    wishes = st.text_input('Укажите свои пожелания')

    if st.button('Submit'):
        # Создание DataFrame с данными опроса
        data = {
            'Genres': [', '.join(genres)],
            'Pass Genres': [', '.join(pass_genres)],
            'Years': [', '.join(map(str, years))],
            'Rating': [rating],
            'Popular Tags': [', '.join(pop_tags)],
            'Pass Tags': [', '.join(pass_tags)],
            'Language': [', '.join(language)],
            'Votes': [votes],
            'steam_profile': [steam_profile],
            'wishes':[wishes]
        }
        df = pd.DataFrame(data)

        # Запись данных в файл CSV
        df.to_csv('/home/nika/GameBuddy/users_data.csv', mode='a', header=not os.path.exists('/home/nika/GameBuddy/users_data.csv'), index=False)
        st.success('Информация сохранена')

if __name__ == '__main__':
    main()