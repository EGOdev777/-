import math
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_step1', methods=['POST'])
def calculate_step1():
    data = request.json
    try:
        av = float(data['av'])
        bv = float(data['bv'])
        h = float(data['h'])
        rc = float(data['rc'])
        rk = 500.0

        a_star = (av * math.pi * h) / math.log(rk / rc)
        b_star = (bv * 2.0 * (math.pi ** 2) * (h ** 2)) / ((1.0 / rc) - (1.0 / rk))

        return jsonify({'success': True, 'a_star': a_star, 'b_star': b_star})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/calculate_step2', methods=['POST'])
def calculate_step2():
    data = request.json
    try:
        a_star = float(data['a_star'])
        b_star = float(data['b_star'])
        h = float(data['h'])
        lg = float(data['lg'])
        rc = float(data['rc'])
        rk = float(data['rk'])
        v = float(data['v'])
        ppl = float(data['ppl'])
        dp = float(data['dp'])

        h1 = max(0.01, h / 2.0 - rc)
        vh1 = v * h1

        t1_a = (2.0 / vh1) * (vh1 + rc * math.log(rc / (rc + vh1)))
        t2_a = (rk - vh1) / (rc + vh1)
        Ag = (a_star / (2.0 * lg)) * (t1_a + t2_a)

        t1_b = (2.0 / vh1) * (math.log((rc + vh1) / rc) - (vh1 / (rc + vh1)))
        t2_b = (rk - vh1) / ((rc + vh1) ** 2)
        Bg = (b_star / (8.0 * (lg ** 2))) * (t1_b + t2_b)

        pressure_term = dp * (2.0 * ppl - dp)
        radicand = max(0.0, Ag ** 2 + 4.0 * Bg * pressure_term)
        
        Q = ((-Ag + math.sqrt(radicand)) / (2.0 * Bg)) if Bg > 0 else 0.0
        Q_thousands = Q * 1000.0

        return jsonify({'success': True, 'ag': Ag, 'bg': Bg, 'q': Q_thousands})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)