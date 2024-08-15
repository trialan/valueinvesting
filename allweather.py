import numpy as np
from scipy.optimize import minimize

# Numerical values for the standard deviations (risks) of each asset
sigma_eq = 0.153
sigma_com = 0.213
sigma_cc = 0.041
sigma_em = 0.105
sigma_il = 0.073
sigma_nom = 0.08

# Define the risk equations for each quadrant
def risk_diff(weights):
    w_eq, w_com, w_cc, w_em, w_il, w_nom = weights
    # Risk for each quadrant
    R1 = w_eq/2. * sigma_eq + w_com/2. * sigma_com + w_cc * sigma_cc + w_em/2. * sigma_em
    R2 = w_il/2. * sigma_il + w_com/2. * sigma_com + w_em/2. * sigma_em
    R3 = w_nom/2. * sigma_nom + w_il/2. * sigma_il
    R4 = w_eq/2. * sigma_eq + w_nom/2. * sigma_nom
    # Difference between risks (we want to minimize this difference)
    return (R1 - R2)**2 + (R1 - R3)**2 + (R1 - R4)**2

# Initial guess for the weights
initial_guess = np.array([1/6, 1/6, 1/6, 1/6, 1/6, 1/6])

# Constraints: sum of weights = 1
constraints = ({
    'type': 'eq',
    'fun': lambda weights: np.sum(weights) - 1
})

# Bounds: weights should be between 0 and 1 (i.e., non-negative and not exceeding 1)
bounds = [(0, 1) for _ in range(6)]

# Minimize the risk difference with the constraints and bounds
result = minimize(risk_diff, initial_guess, bounds=bounds, constraints=constraints)

# Output the solution
if result.success:
    print("Optimized weights:", result.x)
else:
    print("Optimization failed:", result.message)

"""
Result:
    array([0.11129921, 0.01442717, 0.13121359, 0.12701067, 0.29618735,
       0.31986202])

These are the fractions of our portfolio, so that gives us:
    11.13% in Equities
    1.44% in Commodities
    13.12% in Corporate Credit
    12.70% in EM Credit
    29.62% in IL Bonds
    31.99% in Nominal Bonds

This sums to exactly 100%. For a total risk of 8.6%. See this calculation:

In [7]: (result.x * np.array([sigma_eq, sigma_com, sigma_cc, sigma_em, sigma_il,
   ...:  sigma_nom])).sum()
Out[7]: 0.08602828114133718

And a total expected return of ???
"""
