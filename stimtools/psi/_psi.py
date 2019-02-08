
import pickle

import numpy as np


class Psi():

    def __init__(self, params, stim_levels, pf):
        """Initialise a Psi adaptive staircase handler.

        Parameters
        ----------
        params: ordered dict
            Each item has a key that corresponds to a named parameter in `pf`,
            and a dict value. That dict has keys `levels` (an array containing
            the parameter levels), `prior` (an array containing the prior
            density for each parameter level), and `marginalise` (a bool
            indicate whether to marginalise over the parameter when updating).
        stim_levels: array of numbers
            The range of potential stimulus levels, passed to `pf` as `x`.
        pf: function
            Psychometric function. Needs to accept at least `x`, and also the
            parameters named in `params`.

        """

        self._params = params
        self._stim_levels = stim_levels
        self._n_stim_levels = len(stim_levels)
        self._pf = pf

        self._param_names = self._params.keys()
        self._n_params = len(self._params)

        self._param_n_levels = [
            len(param["prior"])
            for param in self._params.values()
        ]

        for (i_param, param) in enumerate(self._params.values()):

            if "marginalise" not in param:
                param["marginalise"] = False

            full_prior = np.reshape(
                param["prior"],
                (len(param["prior"]), ) + (1, ) * (self._n_params - 1)
            )

            i_axes = np.roll(range(self._n_params), -i_param)

            full_prior = np.moveaxis(
                full_prior,
                source=range(self._n_params),
                destination=i_axes
            )

            param["full_prior"] = full_prior

            full_levels = np.reshape(
                param["levels"],
                (len(param["levels"]), ) + (1, ) * (self._n_params - 1)
            )

            full_levels = np.moveaxis(
                full_levels,
                source=range(self._n_params),
                destination=i_axes
            )

            param["full_levels"] = full_levels[np.newaxis, ...]

        self._full_stim_levels = np.reshape(
            self._stim_levels,
            (self._n_stim_levels, ) + (1, ) * self._n_params
        )

        self._prior = np.prod(
            [
                param["full_prior"]
                for param in self._params.values()
            ]
        )

        self._marginal_sum_axes = tuple(
            2 + i_axis
            for (i_axis, param) in enumerate(self._params.values())
            if param["marginalise"]
        )

        # init the probablity lut
        self._p_lut = np.full(
            [2, self._n_stim_levels] + self._param_n_levels,
            np.nan
        )

        pf_params = {
            param_name: param["full_levels"]
            for (param_name, param) in self._params.items()
        }

        est = self._pf(
            x=self._full_stim_levels,
            **pf_params
        )

        self._p_lut[0, ...] = 1.0 - est
        self._p_lut[1, ...] = est

        self.curr_stim_index = None

    def step(self):
        """Steps the Psi handler forward. Inspect `curr_stim_index` and
        `curr_stim_level` to get the info on the stimulus for the next trial.
        """

        self._prior /= self._prior.sum()

        p_r_x_full = self._prior[np.newaxis, np.newaxis, ...] * self._p_lut

        p_r_x = np.sum(
            p_r_x_full,
            axis=tuple(range(2, self._p_lut.ndim))
        )

        posterior = p_r_x_full / p_r_x[..., np.newaxis, np.newaxis]

        marginal = np.sum(posterior, axis=self._marginal_sum_axes)

        h = -1 * np.sum(
            marginal * np.log2(marginal + 10e-10),
            axis=tuple(range(2, marginal.ndim))
        )

        e_h = np.sum(h * p_r_x, axis=0)

        self.curr_stim_index = np.argmin(e_h)
        self.curr_stim_level = self._stim_levels[self.curr_stim_index]

        self._posterior = posterior

    def override_stim_index(self, new_index):

        self.curr_stim_index = new_index
        self.curr_stim_level = self._stim_levels[new_index]

    def override_stim_level(self, new_level):

        self.curr_stim_level = new_level
        (self.curr_stim_index, ) = np.nonzero(
            self._stim_levels == new_level
        )

        if not self.curr_stim_index:
            self.curr_stim_index = np.argmin(
                np.abs(self._stim_levels - new_level)
            )

            print(
                "Warning: the precise new level was not found in the " +
                "stimulus array. Using the closest value instead."
            )

    def update(self, trial_outcome):
        """Updates the Psi handler with the outcome of a trial.

        Parameters
        ----------
        trial_outcome: int, {0, 1}
            Outcome of the trial

        """

        trial_outcome = int(trial_outcome)

        assert trial_outcome in [0, 1]

        self._prior = self._posterior[trial_outcome, self.curr_stim_index, ...]

    def get_estimates(self):
        """Returns a dict with the current estimates for each parameter."""

        estimates = {
            param_name: np.sum(param["full_levels"] * self._prior)
            for (param_name, param) in self._params.items()
        }

        return estimates


def from_file(filename):

    with open(filename, "rb") as file_handle:
        psi = pickle.load(file=file_handle)

    return psi
