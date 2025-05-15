import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from mpl_toolkits.mplot3d import Axes3D

class LorenzAttractor:
    def __init__(self, rho=28.0, sigma=10.0, beta=8.0/3.0):
        self.rho = rho
        self.sigma = sigma
        self.beta = beta

    def system_equations(self, state, t):
        x, y, z = state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return dx, dy, dz

    def simulate(self, initial_state, time_points):
        return odeint(self.system_equations, initial_state, time_points)

    def plot_trajectory(self, states, title="Атрактор Лоренца"):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(states[:, 0], states[:, 1], states[:, 2])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title)
        plt.show()

    def demonstrate_sensitivity(self, initial_state, perturbation=0.001, time_points=None):
        if time_points is None:
            time_points = np.arange(0.0, 40.0, 0.01)

        states1 = self.simulate(initial_state, time_points)

        perturbed_state = [x + perturbation for x in initial_state]
        states2 = self.simulate(perturbed_state, time_points)

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(states1[:, 0], states1[:, 1], states1[:, 2], label='Початкова траєкторія')
        ax.plot(states2[:, 0], states2[:, 1], states2[:, 2], label='Збурена траєкторія')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Демонстрація чутливості до початкових умов')
        ax.legend()
        plt.show()

        distance = np.sqrt(np.sum((states1 - states2)**2, axis=1))
        plt.figure(figsize=(10, 6))
        plt.plot(time_points, distance)
        plt.xlabel('Час')
        plt.ylabel('Відстань між траєкторіями')
        plt.title('Експоненціальне розходження траєкторій')
        plt.show()

if __name__ == "__main__":
    lorenz = LorenzAttractor()

    initial_state = [1.0, 1.0, 1.0]
    time_points = np.arange(0.0, 40.0, 0.01)

    lorenz.demonstrate_sensitivity(initial_state, perturbation=0.001, time_points=time_points) 