from __future__ import absolute_import, print_function, division

import itertools
import pickle

import numpy as np

import scipy.stats


class Psi(object):

    @staticmethod
    def from_file(filename):
        with open(filename, "rb") as file_handle:
            psi = pickle.load(file=file_handle)

        return psi

    def __init__(
        self,
        alpha_levels,
        beta_levels,
        stim_levels,
        psych_func,
        focus="both"
    ):
        """Psi adaptive estimation method.

        Parameters
        ----------
        alpha_levels: vector of floats
            a
        beta_levels: vector of floats
            b
        stim_levels: vector of floats
            c
        psych_func: python method
            Psychometric function. This should accept (at least) three named
            parameters; x, alpha, and beta. To allow other to be specified
            (lapse rate, etc.) use `functools.partial`.
        focus: string, optional, {"alpha", "beta", "both"}
            Whether to focus on estimation of the alpha or beta parameter, or
            both. This is the 'psi-marginal' method.

        Notes
        -----
        * Based on the Kontsevich & Tyler (1999) description. Written more for
          readability than performance.

        """

        self._alpha_levels = alpha_levels
        self._beta_levels = beta_levels
        self._stim_levels = stim_levels
        self._psych_func = psych_func
        self._focus = focus

        self._n_alpha_levels = len(alpha_levels)
        self._n_beta_levels = len(beta_levels)
        self._n_stim_levels = len(stim_levels)

        # initialise the prior to be uniform
        self._prior = np.ones((self._n_alpha_levels, self._n_beta_levels))
        self._prior /= (self._n_alpha_levels * self._n_beta_levels)

        self._p_lut = np.full(
            (
                2,  # response
                self._n_stim_levels,  # x
                self._n_alpha_levels,  # alpha
                self._n_beta_levels  # beta
            ),
            np.nan
        )

        # populate using the supplied psychometric function
        for ((i_alpha, alpha), (i_beta, beta)) in itertools.product(
            enumerate(self._alpha_levels),
            enumerate(self._beta_levels)
        ):

            est = self._psych_func(
                alpha=alpha,
                beta=beta,
                x=self._stim_levels
            )

            # failure
            self._p_lut[0, :, i_alpha, i_beta] = 1.0 - est
            # success
            self._p_lut[1, :, i_alpha, i_beta] = est

        self.curr_stim_index = None

    def __repr__(self):

        (alpha_hat, beta_hat) = self.get_estimates()

        return "Alpha: {alpha:.05f}, Beta: {beta:.05f}".format(
            alpha=alpha_hat,
            beta=beta_hat
        )

    def get_curr_stim_level(self):

        return self._stim_levels[self.curr_stim_index]

    def get_estimates(self):

        alpha_hat = np.sum(self._alpha_levels[:, np.newaxis] * self._prior)
        beta_hat = np.sum(self._beta_levels[np.newaxis, :] * self._prior)

        return (alpha_hat, beta_hat)

    def override_level(self, new_level=None):

        if new_level is None:
            new_level = np.random.choice(self._n_stim_levels)

        self.curr_stim_index = new_level

    def step(self):

        p_r_x = np.sum(
            self._prior[np.newaxis, np.newaxis, ...] * self._p_lut,
            axis=(2, 3)
        )

        posterior = (
            (self._prior[np.newaxis, np.newaxis, ...] * self._p_lut) /
            p_r_x[..., np.newaxis, np.newaxis]
        )

        if self._focus == "both":
            marginal = posterior
            h_sum_ax = (2, 3)
        elif self._focus == "alpha":
            # sum over beta
            marginal = np.sum(posterior, axis=-1)
            h_sum_ax = -1
        elif self._focus == "beta":
            # sum over alpha
            marginal = np.sum(posterior, axis=-2)
            h_sum_ax = -1

        h = -1 * np.sum(
            marginal * np.log(marginal + 1e-10),
            axis=h_sum_ax
        )

        e_h = np.sum(h * p_r_x, axis=0)

        self._prx = p_r_x
        self._pp = posterior
        self.h = h
        self.e_h = e_h

        self.curr_stim_index = np.argmin(e_h)

        self._posterior = posterior

    def update(self, trial_success):

        trial_success = int(trial_success)

        assert trial_success in [0, 1]

        self._prior = self._posterior[
            trial_success,
            self.curr_stim_index,
            ...
        ]

    def save(self, filename):

        with open(filename, "wb") as file_handle:
            pickle.dump(obj=self, file=file_handle)



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


def psi_demo(n_trials=150, fixed_seed=False, verbose=False):
    "Demo of the operation of the psi function"

    true_alpha = 5.0
    true_beta = 1.0

    n_res = 100

    stim_levels = np.linspace(0, 10, n_res)
    beta_levels = np.linspace(0, 10, n_res)[1:]
    alpha_levels = np.linspace(4, 6, n_res)

    # useful for checking that the output doesn't change with refactoring
    if fixed_seed:
        seed = 28513
    else:
        seed = np.random.randint(low=0, high=2 ** 32 - 1)

    rand = np.random.RandomState(seed=seed)

    psych_func = logistic

    psi = Psi(
        alpha_levels=alpha_levels,
        beta_levels=beta_levels,
        stim_levels=stim_levels,
        psych_func=psych_func,
        focus="both",
    )

    psi.step()

    return psi

    for i_trial in range(n_trials):

        resp_prob = psych_func(
            stim_levels[psi.curr_stim_index],
            true_alpha,
            true_beta
        )

        resp = rand.choice(
            [0, 1],
            p=[1 - resp_prob, resp_prob]
        )

        psi.update(resp)

        (est_alpha, est_beta) = psi.get_estimates()

        psi.step()

        if verbose:
            print(
                "{t:d}  alpha:{a:.3f}   beta:{b:.3f}".format(
                    t=i_trial + 1,
                    a=est_alpha,
                    b=est_beta
                )
            )

    print(psi)

    return psi


if __name__ == "__main__":
    psi_demo(n_trials=60, fixed_seed=True)
