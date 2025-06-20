import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, render_template_string
from app.calculatrice import addition, soustraction, multiplication, division, puissance

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <title>Calculatrice Web</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f0f4f8;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .container {
      background: white;
      padding: 30px 40px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      width: 350px;
      text-align: center;
    }
    h1 {
      margin-bottom: 25px;
      color: #333;
    }
    input, select {
      width: 100px;
      padding: 8px 10px;
      margin: 0 5px 15px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 4px;
      text-align: center;
    }
    button {
      background: #007bff;
      border: none;
      color: white;
      padding: 10px 20px;
      font-size: 16px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.3s ease;
    }
    button:hover {
      background: #0056b3;
    }
    .result {
      margin-top: 20px;
      font-size: 20px;
      color: #28a745;
      font-weight: bold;
    }
    .error {
      margin-top: 20px;
      font-size: 18px;
      color: #dc3545;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Calculatrice Web</h1>
    <form method="post">
      <input name="a" type="number" step="any" required placeholder="Nombre 1" />
      <select name="operation" required>
        <option value="addition">+</option>
        <option value="soustraction">-</option>
        <option value="multiplication">*</option>
        <option value="division">/</option>
        <option value="puissance">^</option>
      </select>
      <input name="b" type="number" step="any" required placeholder="Nombre 2" />
      <br />
      <button type="submit">Calculer</button>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% elif result is not none %}
      <div class="result">Résultat : {{ result }}</div>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculatrice():
    result = None
    error = None
    if request.method == "POST":
        try:
            a = float(request.form["a"])
            b = float(request.form["b"])
        except ValueError:
            error = "Erreur : Veuillez entrer des nombres valides."
            return render_template_string(HTML, result=result, error=error)

        operation = request.form["operation"]
        
        try:
            match operation:
                case "addition":
                    result = addition(a, b)
                case "soustraction":
                    result = soustraction(a, b)
                case "multiplication":
                    result = multiplication(a, b)
                case "division":
                    result = division(a, b)
                case "puissance":
                    result = puissance(a, b)
        except ValueError as e:
            error = f"Erreur : {e}"
            return render_template_string(HTML, result=result, error=error)
        except Exception as e:
            error = f"Erreur : {e}"
            return render_template_string(HTML, result=result, error=error)
            
    return render_template_string(HTML, result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
