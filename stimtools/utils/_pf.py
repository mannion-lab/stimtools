import numpy as np

try:
    import scipy.stats
except ImportError:
    pass


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


def logistic_alt(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Logistic psychometric function, where `beta` approximates sigma in a cumulative
    normal.

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

    y = 1.0 / (1 + np.exp(-(x - alpha) / ((np.sqrt(3) / np.pi) * beta)))

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

    y = 1 - np.exp(-((x / alpha) ** beta))

    y *= 1 - guess_rate - lapse_rate

    y += guess_rate

    return y


def cnorm(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0, allow_negative_slope=False):
    """Cumulative normal psychometric function.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is ~0.5)
    beta: float
        Slope of the function. If `allow_negative_slope` is `False`, must be positive.
    guess_rate, lapse_rate: float, [0, 1]
        How often the subject guesses or lapses
    allow_negative_slope: bool
        If `True`, the PF is computed with the absolute value of `beta` and the return
        value is given by `1 - y`.
    """

    if allow_negative_slope:
        scale = np.abs(beta)
    else:
        scale = beta

    y = scipy.stats.distributions.norm.cdf(x=x, loc=alpha, scale=scale)

    y *= 1 - guess_rate - lapse_rate

    y += guess_rate

    if allow_negative_slope:
        y = np.where(beta < 0, 1 - y, y)

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
        lapse_rate=lapse_rate,
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

        return (
            cnorm(x=theta, alpha=0.0, beta=beta)
            - cnorm(x=theta - np.pi, alpha=0.0, beta=beta)
            + (1.0 - cnorm(x=theta + np.pi, alpha=0, beta=beta))
        )

    def _high_wrap(beta):

        beta = np.polyval(
            p=[-3.546, 39.131, -158.724, 309.646, -292.966, 109.1288], x=beta
        )

        return cnorm(x=np.sin(theta), alpha=0.0, beta=beta)

    p = np.where(beta < 1.4, _low_wrap(beta), _high_wrap(beta))

    p *= 1 - guess_rate - lapse_rate

    p += guess_rate

    return p
