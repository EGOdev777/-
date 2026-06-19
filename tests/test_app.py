import math
import unittest

from app import app


class Step3ChartTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_rk_dependency_uses_uniform_x_step(self):
        response = self.client.post(
            "/calculate_step3",
            json={
                "a_star": 0.05,
                "b_star": 0.001,
                "h": 10,
                "lg": 600,
                "rc": 0.1,
                "rk": 500,
                "v": 0.3,
                "ppl": 18,
                "dp": 0.1,
                "param": "rk",
            },
        )

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["x"]), 21)

        steps = [
            payload["x"][index + 1] - payload["x"][index]
            for index in range(len(payload["x"]) - 1)
        ]
        self.assertTrue(
            all(math.isclose(step, steps[0], abs_tol=1e-6) for step in steps[1:])
        )


if __name__ == "__main__":
    unittest.main()
