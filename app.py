import os

from flask import Flask, render_template, request, redirect
from data import Author, Book

app = Flask(__name__)
app.debug = True

# Flask is what serves up pages for us.
# app.route indicates what happens when someone visits individual pages


@app.route('/', methods=['GET', 'POST'])
def index():
    # if someone visits the site, (GET request), show them the list of books
    if request.method == 'GET':
        author = request.args.get("author", None)
        # These render_template calls compile the data with the template at \templates\index.html
        if author:
            return render_template('index.html', author=author, books=Book.objects(read=False).order_by("-year"))
        return render_template('index.html', books=Book.objects(read=False).order_by("-year"))
    # handle an add author request
    elif request.method == 'POST':
        author = request.form['author']
        year = request.form['year']
        # Add the author to the database and reload the page
        Author(name=author, year=year).save()
        return redirect('/')


# handle a mark-book-as-read request
@app.route('/read')
def mark_complete():
    the_id = request.args.get('id')
    # Add the book to the database and reload the page
    Book.objects(id=the_id).update(set__read=True)
    return redirect('/')


# run the app!
def main():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))


if __name__ == "__main__":
    main()
