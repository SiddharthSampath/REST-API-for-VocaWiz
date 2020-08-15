import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import xlrd

from models import setup_db, Word, rollback


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Get the words which the user has not learnt yet. We will select a word
    # from this list for the getWord route
    words = Word.query.filter(Word.completed == "no").all()

    # Reset all words to "not completed" so you can start from the beginning
    @app.route('/dbreset/', methods=['GET'])
    def resetWords():
        try:
            words = Word.query.all()
            for word in words:
                word.completed =  "no"
                word.insert()
            return jsonify({
                "success" : True
            })
        except:
            abort(400) 

    # Initially, we create the db from the excel file
    @app.route('/dbinit/', methods=['GET'])
    def initialiseDB():
        try:
            loc = ("Mywords.xlsx")
            wb = xlrd.open_workbook(loc)
            sheet = wb.sheet_by_index(0)
            meanings = []
            # As we are generating options using meanings of other words, we
            # first get all the meanings and store them
            for i in range(sheet.nrows):
                meanings.append(sheet.cell_value(i, 1))

            # We insert the words one by one into the database
            for i in range(1, sheet.nrows):
                word = sheet.cell_value(i, 0).lower()
                meaning = sheet.cell_value(i, 1).lower()
                hint = sheet.cell_value(i, 2).lower()
                completed = sheet.cell_value(i, 3)
                options = []
                while len(options) <= 3:
                    newChoice = random.choice(meanings)
                    if newChoice not in options:
                        options.append(newChoice)
                newWord = Word(
                    word=word,
                    meaning=meaning,
                    hint=hint,
                    options=options,
                    completed=completed)
                newWord.insert()
            return jsonify({
                "success": True
            })
        except BaseException:
            rollback()
            print("Word formatting error")
            abort(400)

    # Route to get one random word at a time
    @app.route('/getWord/')
    def getWord():
        try:
            # Select a random word from the list of words which the user has
            # not completed yet
            word = random.choice(words)
            # print(word)
            if word is None:
                return jsonify({
                    "word": "You have learnt all the words in our database!"
                })

            gotWord = Word.query.get(word.id) 
            gotWord.completed = "yes"
            gotWord.insert()
            words.remove(word)

            return jsonify({
                "id": word.id,
                "word": word.word,
                "meaning": word.meaning,
                "hint": word.hint,
                "options": word.options
            })
        except BaseException:
            rollback()
            abort(400)

    # Route to validate whether the answer received is correct or not

    @app.route('/validateAnswer/', methods=['POST'])
    def validateWord():
        word_json = request.get_json()
        meaning = word_json["meaning"].lower()
        word = word_json["word"].lower()
        try:
            validateWord = Word.query.filter(Word.word == word).one_or_none()
            if validateWord is None:
                # in theory, word should always be valid and never reach here
                abort(400)
            else:
                correctAnswer = None
                if validateWord.meaning == meaning:
                    correctAnswer = True
                else:
                    correctAnswer = False
            return jsonify({
                "correctAnswer": correctAnswer
            })
        except BaseException:
            abort(400)

    # Error Handlers

    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(400)
    def badRequest(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(500)
    def servererror(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500

    return app


app = create_app()
if __name__ == '__main__':
    # APP.run(host='0.0.0.0', port=8080, debug=True)
    app.run(debug=True)


# curl http://localhost:5000/validateAnswer/ -X POST -H "Content-Type:
# application/json" -d '{ "word": "nadir", "meaning": "lowest point"}'
