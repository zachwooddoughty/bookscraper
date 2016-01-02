import os

from flask import Flask, render_template, request, redirect
from data import Author, Book

app = Flask(__name__)
app.debug = True


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', books=Book.objects(read=False).order_by("-year"))
    elif request.method == 'POST':
        author = request.form['author']
        year = request.form['year']
        Author(name=author, year=year).save()
        return redirect('/')


@app.route('/read')
def mark_complete():
    the_id = request.args.get('id')
    Book.objects(id=the_id).update(set__read=True)
    return redirect('/')


def main():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))


if __name__ == "__main__":
    main()
