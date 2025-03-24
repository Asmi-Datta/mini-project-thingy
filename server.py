from flask import Flask, jsonify, render_template, request
from scripts import the_big_dipper
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# curl -X POST http://localhost:8000/llm -F dream="haha yes"
@app.route("/llm", methods=["POST"])
def llm_():
    if request.method == "POST":
        dream_text = request.form["dream"]

    response = jsonify(the_big_dipper.main(dream_text=dream_text))
    
    # time.sleep(2)
    # response = jsonify(
    #     {
    #         "archetype": "lover",
    #         "descriptive_content": {
    #             "archetype": {
    #                 "name": "The Everyman",
    #                 "description": "A symbol of ordinary, everyday life and experiences.",
    #             },
    #             "dream": {"description": "Fell off a bridge"},
    #             "interpretation": {
    #                 "lesson1": {
    #                     "title": "Our Conscious Actions are Motivated by our Unconscious Ones",
    #                     "text": "The dream may be highlighting unconscious motivations or desires that are driving your actions in waking life.",
    #                 },
    #                 "lesson2": {
    #                     "title": "Talk A Lot And You Will Eventually Betray Yourself",
    #                     "text": "The dream could be suggesting that you need to examine your own weaknesses and biases, rather than relying on surface-level knowledge or assumptions.",
    #                 },
    #                 "actionableNotes": [
    #                     {
    #                         "title": "What are you lacking?",
    #                         "text": "Consider what areas of your life may be lacking or compensating for shortcomings. Look beyond the qualities you present to others and examine your real defects.",
    #                     }
    #                 ],
    #             },
    #         },
    #     }
    # )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    # return {"data": 1}


if __name__ == "__main__":
    app.run(port=8000, debug=True)
