import numpy as np
from flask import Flask, render_template, request
import pickle

popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input').lower()  # Convert user input to lowercase

    # Check for an exact match in lowercase
    exact_match_index = np.where(pt.index.str.lower() == user_input)[0]

    if len(exact_match_index) > 0:
        # If there's an exact match, proceed with the exact match logic
        index = exact_match_index[0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[0:10]
    else:
        # If there's no exact match, find titles containing user input words
        matching_titles = books[books['Book-Title'].str.lower().str.contains(user_input)]

        if not matching_titles.empty:
            data = []
            for title in matching_titles['Book-Title']:
                item = []
                temp_df = books[
                    books['Book-Title'].str.lower() == title.lower()]  # Convert book titles to lowercase for comparison
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data.append(item)
        else:
            # If there are no matches, you can provide a message or handle it as per your requirement
            data = ["No matching books found."]

        return render_template('recommend.html', data=data)

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'].str.lower() == pt.index[
            i[0]].lower()]  # Convert book titles to lowercase for comparison
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
