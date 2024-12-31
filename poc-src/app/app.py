from flask import Flask, render_template, request  # type: ignore
from local_model import get_llm_response
from embedder import get_embeddings
""""
GESTISCE LA RICEZIONE DELLA DOMANDA, LA FORMULAZIONE DI UNA RISPOSTA E IL RENDERING DELL'HTML
"""
app = Flask(__name__)

conversation_pile = []  # la storia della chat (per contesto e per display)

@app.route("/", methods=["GET", "POST"])
def index():
    global conversation_pile
    if request.method == "POST":
        question = request.form.get("question") # riceve domanda dalla POST
        if question:
            id_to_embed, text_to_embed = get_embeddings(question)    # chiama il modello di embedding sulla domanda e restituisce il documento (il testo in questo caso) piu' simile al prompt (oltre all'id del prodotto)
            
            response = get_llm_response(conversation_pile, question, text_to_embed) # chiede al modello di rispondere alla domanda (con contesto la history della chat ed il testo estratto dal modello di embedding)
            # inserisce la nuova conversazione nella storia della chat #
            conversation_pile.append({"role": "user", "content": question})
            conversation_pile.append({"role": "assistant", "content": response})
            conversation_pile.append({"role": "system", "content": id_to_embed})

    return render_template("index.html", conversation_pile=conversation_pile)   # Flask renderizza .html e .css dentro a ./templates/ e ./static/

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
