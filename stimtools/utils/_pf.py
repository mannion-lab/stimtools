
import numpy as np

import scipy.stats


def logistic(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Logistic psychometric function.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is 0.5)
    betae float, > 0
        Slope of the function
    guess_rate, lapse_rate: float, [0,1]
        How often the subject guesses or lapses.

    """

    y = 1.0 / (1 + np.exp(-beta * (x - alpha)))

    y *= 1 - guess_rate - lapse_rate

    y += guess_rate

    return y


def weibull(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Weibull psychometric function.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is ~0.6321)
    beta: float, > 0
        Slope of the function
    guess_rate, lapse_rate: float, [0, 1]
        How often the subject guesses or lapses

    """

    y = 1 - np.exp(-(x / alpha) ** beta)

    y *= 1 - guess_rate - lapse_rate

    y += guess_rate

    return y


def cnorm(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Cumulative normal psychometric function.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is ~0.5)
    beta: float, > 0
        Slope of the function
    guess_rate, lapse_rate: float, [0, 1]
        How often the subject guesses or lapses
    """

    y = scipy.stats.distributions.norm.cdf(x=x, loc=alpha, scale=beta)

    y *= 1 - guess_rate - lapse_rate

    y += guess_rate

    return y


def cnorm_alt(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Alternative cumulative normal psychometric function. Note that this
    works via the logistic function, so is not actually a cumulative normal.
    However, the slope parameter is transformed such that it is pretty close.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is ~0.5)
    beta: float
        Slope of the function
    guess_rate, lapse_rate: float, [0, 1]
        How often the subject guesses or lapses
    """

    transformed_beta = 1.0 / (beta * (np.sqrt(3.0) / np.pi))

    y = logistic(
        x=x,
        alpha=alpha,
        beta=transformed_beta,
        guess_rate=guess_rate,
        lapse_rate=lapse_rate
    )

    return y


def cnorm_wrap(theta, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """'Wrapped' version of a cumulative Normal.

    From Dakin et al. (2005), Appendix B.

    Parameters
    ----------
    theta: float or vector of floats
        Point to evaluate the function, in radians [-pi, +pi]
    alpha: float
        Threshold (point where function output is ~0.5)
    beta: float
        Slope of the function
    guess_rate, lapse_rate: float, [0, 1]
        How often the subject guesses or lapses

    """

    theta = theta - alpha

    def _low_wrap(beta):

        beta_sq = beta ** 2

        return (
            cnorm(x=theta, alpha=0.0, beta=beta_sq) -
            cnorm(x=theta - np.pi, alpha=0.0, beta=beta_sq) +
            (1.0 - cnorm(x=theta + np.pi, alpha=0, beta=beta_sq))
        )

    def _high_wrap(beta):

        beta = np.polyval(
            p=[-3.546, 39.131, -158.724, 309.646, -292.966, 109.1288],
            x=beta
        )

        return cnorm(x=np.sin(theta), alpha=0.0, beta=beta ** 2)

    p = np.where(beta < 1.4, _low_wrap(beta), _high_wrap(beta))

    p *= 1 - guess_rate - lapse_rate

    p += guess_rate

    return p
