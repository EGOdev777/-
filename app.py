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

        a_star = max(0.0, (av * math.pi * h) / math.log(rk / rc))
        b_star = max(0.0, (bv * 2.0 * (math.pi ** 2) * (h ** 2)) / ((1.0 / rc) - (1.0 / rk)))

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

        dp = min(dp, ppl)

        h1 = max(0.01, h / 2.0 - rc)
        vh1 = v * h1

        t1_a = (2.0 / vh1) * (vh1 + rc * math.log(rc / (rc + vh1)))
        t2_a = (rk - vh1) / (rc + vh1)
        Ag = max(0.0, (a_star / (2.0 * lg)) * (t1_a + t2_a))

        t1_b = (2.0 / vh1) * (math.log((rc + vh1) / rc) - (vh1 / (rc + vh1)))
        t2_b = (rk - vh1) / ((rc + vh1) ** 2)
        Bg = max(0.0, (b_star / (8.0 * (lg ** 2))) * (t1_b + t2_b))

        pressure_term = dp * (2.0 * ppl - dp)
        radicand = max(0.0, Ag ** 2 + 4.0 * Bg * pressure_term)
        
        Q = ((-Ag + math.sqrt(radicand)) / (2.0 * Bg)) if Bg > 0 else 0.0
        Q_thousands = Q * 1000.0

        return jsonify({'success': True, 'ag': Ag, 'bg': Bg, 'q': Q_thousands})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/calculate_step3', methods=['POST'])
def calculate_step3():
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
        param_to_vary = data['param']

        param_limits = {
            'h': (5.0, 2000.0),
            'lg': (100.0, 10000.0),
            'rc': (0.05, 0.3),
            'rk': (3.0, 20000.0),
            'v': (0.1, 1.0),
            'ppl': (0.101, 100.0),
            'dp': (0.01, ppl)
        }

        p_min, p_max = param_limits[param_to_vary]
        x_vals = []
        y_vals = []

        test_values = []
        
        if param_to_vary == 'rk':
            dense_steps = 50
            for i in range(dense_steps):
                test_values.append(3.0 + (500.0 - 3.0) * i / dense_steps)
            
            sparse_steps = 15
            for i in range(sparse_steps + 1):
                test_values.append(500.0 + (20000.0 - 500.0) * i / sparse_steps)
        else:
            steps = 20
            for i in range(steps + 1):
                test_values.append(p_min + (p_max - p_min) * i / steps)

        for val in test_values:
            curr_h = val if param_to_vary == 'h' else h
            curr_lg = val if param_to_vary == 'lg' else lg
            curr_rc = val if param_to_vary == 'rc' else rc
            curr_rk = val if param_to_vary == 'rk' else rk
            curr_v = val if param_to_vary == 'v' else v
            curr_ppl = val if param_to_vary == 'ppl' else ppl
            curr_dp = val if param_to_vary == 'dp' else dp

            if param_to_vary == 'ppl':
                curr_dp = min(dp, curr_ppl)
            elif param_to_vary == 'dp':
                curr_dp = min(val, ppl)
            else:
                curr_dp = min(curr_dp, curr_ppl)

            h1 = max(0.01, curr_h / 2.0 - curr_rc)
            vh1 = curr_v * h1

            if vh1 <= 0 or (curr_rc + vh1) <= 0:
                continue

            try:
                t1_a = (2.0 / vh1) * (vh1 + curr_rc * math.log(curr_rc / (curr_rc + vh1)))
                t2_a = (curr_rk - vh1) / (curr_rc + vh1)
                Ag = max(0.0, (a_star / (2.0 * curr_lg)) * (t1_a + t2_a))

                t1_b = (2.0 / vh1) * (math.log((curr_rc + vh1) / curr_rc) - (vh1 / (curr_rc + vh1)))
                t2_b = (curr_rk - vh1) / ((curr_rc + vh1) ** 2)
                Bg = max(0.0, (b_star / (8.0 * (curr_lg ** 2))) * (t1_b + t2_b))

                pressure_term = curr_dp * (2.0 * curr_ppl - curr_dp)
                radicand = max(0.0, Ag ** 2 + 4.0 * Bg * pressure_term)

                Q = ((-Ag + math.sqrt(radicand)) / (2.0 * Bg)) if Bg > 0 else 0.0
                Q_thousands = Q * 1000.0

                x_vals.append(round(val, 1) if val > 10 else round(val, 2))
                y_vals.append(round(Q_thousands, 2))
            except (ValueError, ZeroDivisionError):
                continue

        return jsonify({'success': True, 'x': x_vals, 'y': y_vals})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)