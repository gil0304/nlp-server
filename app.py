from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy

# SpaCyのモデルをロード
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text")
    
    doc = nlp(text)
    
    results = {
        "subjects": [],
        "verbs": [],
        "objects": []
    }
    
    for token in doc:
        # 主語 (nsubj) の解析
        if token.dep_ == "nsubj" or token.dep_ == "nsubjpass":
            subject_phrase = [child.text for child in token.subtree if not child.is_punct]
            results["subjects"].append(" ".join(subject_phrase))
        
        # 動詞フレーズの解析。助動詞 (aux) を主要動詞に結合する
        if token.pos_ == "VERB":
            verb_phrase = []
            
            # 動詞に関連する助動詞（aux）を前に追加
            for child in token.children:
                if child.dep_ == "aux" or child.dep_ == "auxpass":
                    verb_phrase.insert(0, child.text)
            
            # メインの動詞をフレーズに追加
            verb_phrase.append(token.text)
            
            # 不要な要素を除外（不定詞や修飾語）
            verb_clean = " ".join(verb_phrase)
            
            # 不定詞や冗長な修飾句を含む動詞フレーズは除外する
            if "to " not in verb_clean and "from " not in verb_clean:
                results["verbs"].append(verb_clean)
        
        # 目的語 (dobj, pobj) の解析
        if token.dep_ == "dobj" or token.dep_ == "pobj":
            object_phrase = [child.text for child in token.subtree if not child.is_punct]
            results["objects"].append(" ".join(object_phrase))
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
