import unittest
import numpy as np
from lorenz_attractor import LorenzAttractor

class TestLorenzAttractor(unittest.TestCase):
    def setUp(self):
        self.lorenz = LorenzAttractor()
        self.initial_state = [1.0, 1.0, 1.0]
        self.time_points = np.arange(0.0, 10.0, 0.1)

    def test_initialization(self):
        self.assertEqual(self.lorenz.rho, 28.0)
        self.assertEqual(self.lorenz.sigma, 10.0)
        self.assertAlmostEqual(self.lorenz.beta, 8.0/3.0)

    def test_system_equations(self):
        state = [1.0, 1.0, 1.0]
        dx, dy, dz = self.lorenz.system_equations(state, 0)
        
        expected_dx = self.lorenz.sigma * (state[1] - state[0])
        expected_dy = state[0] * (self.lorenz.rho - state[2]) - state[1]
        expected_dz = state[0] * state[1] - self.lorenz.beta * state[2]
        
        self.assertAlmostEqual(dx, expected_dx)
        self.assertAlmostEqual(dy, expected_dy)
        self.assertAlmostEqual(dz, expected_dz)

    def test_simulation_shape(self):
        states = self.lorenz.simulate(self.initial_state, self.time_points)
        self.assertEqual(states.shape, (len(self.time_points), 3))

    def test_sensitivity_to_initial_conditions(self):
        states1 = self.lorenz.simulate(self.initial_state, self.time_points)
        
        perturbation = 0.001
        perturbed_state = [x + perturbation for x in self.initial_state]
        states2 = self.lorenz.simulate(perturbed_state, self.time_points)
        
        initial_distance = np.sqrt(np.sum((states1[0] - states2[0])**2))
        final_distance = np.sqrt(np.sum((states1[-1] - states2[-1])**2))
        
        self.assertGreater(final_distance, initial_distance)

    def test_custom_parameters(self):
        custom_lorenz = LorenzAttractor(rho=20.0, sigma=15.0, beta=2.0)
        self.assertEqual(custom_lorenz.rho, 20.0)
        self.assertEqual(custom_lorenz.sigma, 15.0)
        self.assertEqual(custom_lorenz.beta, 2.0)

if __name__ == '__main__':
    unittest.main() 