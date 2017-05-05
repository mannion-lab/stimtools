from __future__ import absolute_import, print_function, division

import itertools

import numpy as np
import numpy.testing as npt


class Psi(object):

    def __init__(
        self,
        alpha_levels,
        beta_levels,
        stim_levels,
        psych_func
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

        Notes
        -----
        * Based on the Kontsevich & Tyler (1999) description. Written more for
          readability than performance.

        """

        self._alpha_levels = alpha_levels
        self._beta_levels = beta_levels
        self._stim_levels = stim_levels
        self._psych_func = psych_func

        self._n_alpha_levels = len(alpha_levels)
        self._n_beta_levels = len(beta_levels)
        self._n_stim_levels = len(stim_levels)

        # initialise the prior to be uniform
        self._prior = np.ones((self._n_alpha_levels, self._n_beta_levels))
        self._prior /= (self._n_alpha_levels * self._n_beta_levels)

        npt.assert_approx_equal(np.sum(self._prior), 1.0)

        self._p_lut = np.empty(
            (
                2,  # response
                self._n_stim_levels,  # x
                self._n_alpha_levels,  # alpha
                self._n_beta_levels  # beta
            )
        )
        self._p_lut.fill(np.NAN)

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

        assert np.sum(np.isnan(self._p_lut)) == 0

        self._curr_stim_index = None

    def get_curr_stim_level(self):

        return self._stim_levels[self._curr_stim_index]

    def get_estimates(self):

        alpha_hat = np.sum(self._alpha_levels[:, np.newaxis] * self._prior)
        beta_hat = np.sum(self._beta_levels[np.newaxis, :] * self._prior)

        return (alpha_hat, beta_hat)

    def step(self):

        p_r_x = np.empty((2, self._n_stim_levels))
        p_r_x.fill(np.NAN)

        for (i_resp, i_stim) in itertools.product(
            range(2),
            range(self._n_stim_levels)
        ):

            p_r_x[i_resp, i_stim] = np.sum(
                self._p_lut[i_resp, i_stim, ...] * self._prior
            )

        assert np.sum(np.isnan(p_r_x)) == 0

        posterior = np.empty(self._p_lut.shape)
        posterior.fill(np.NAN)

        for (i_resp, i_stim) in itertools.product(
            range(2),
            range(self._n_stim_levels)
        ):

            posterior[i_resp, i_stim, ...] = (
                (
                    self._prior * self._p_lut[i_resp, i_stim, ...]
                ) /
                p_r_x[i_resp, i_stim]
            )

        h = np.empty((2, self._n_stim_levels))
        h.fill(np.NAN)

        for (i_resp, i_stim) in itertools.product(
            range(2),
            range(self._n_stim_levels)
        ):

            h[i_resp, i_stim] = -1 * np.sum(
                posterior[i_resp, i_stim, ...] *
                np.log(posterior[i_resp, i_stim, ...] + 1e-10)
            )

        assert np.sum(np.isnan(h)) == 0

        e_h = np.empty((self._n_stim_levels))
        e_h.fill(np.NAN)

        for i_stim in range(self._n_stim_levels):

            e_h[i_stim] = (
                h[0, i_stim] * p_r_x[0, i_stim] +
                h[1, i_stim] * p_r_x[1, i_stim]
            )

        self._curr_stim_index = np.argmin(e_h)

        self._posterior = posterior

    def update(self, trial_success):

        trial_success = int(trial_success)

        self._prior = self._posterior[
            trial_success,
            self._curr_stim_index,
            ...
        ]


def logistic(x, alpha, beta, guess_rate=0.0, lapse_rate=0.0):
    """Logistic psychometric function.

    Parameters
    ----------
    x: float or vector of floats
        Point to evaluate the function
    alpha: float
        Threshold (point where function output is 0.5)
    beta: float, > 0
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


def psi_demo(n_trials=150, fixed_seed=False):
    "Demo of the operation of the psi function"

    true_alpha = 5.0
    true_beta = 5.0

    n_res = 100

    alpha_levels = np.linspace(0, 10, n_res)
    beta_levels = np.linspace(0, 10, n_res)[1:]
    stim_levels = alpha_levels

    # useful for checking that the output doesn't change with refactoring
    if fixed_seed:
        np.random.seed(28513)

    psych_func = logistic

    psi = Psi(
        alpha_levels=alpha_levels,
        beta_levels=beta_levels,
        stim_levels=stim_levels,
        psych_func=psych_func
    )

    psi.step()

    for i_trial in range(n_trials):

        resp_prob = psych_func(
            stim_levels[psi._curr_stim_index],
            true_alpha,
            true_beta
        )

        resp = np.random.choice(
            [0, 1],
            p=[1 - resp_prob, resp_prob]
        )

        psi.update(resp)

        (est_alpha, est_beta) = psi.get_estimates()

        psi.step()

        print(
            "{t:d}  alpha:{a:.3f}   beta:{b:.3f}".format(
                t=i_trial + 1,
                a=est_alpha,
                b=est_beta
            )
        )

    return psi
