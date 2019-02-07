
import pickle

import numpy as np


class Psi():

    def __init__(self, params, stim_levels, pf):

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

        for (i_param, (param_name, param)) in enumerate(
            self._params.items()
        ):

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

        self._prior /= self._prior.sum()

        p_r_x = np.sum(
            self._prior[np.newaxis, np.newaxis, ...] * self._p_lut,
            axis=tuple(range(2, self._p_lut.ndim))
        )

        posterior = (
            (self._prior[np.newaxis, np.newaxis, ...] * self._p_lut) /
            p_r_x[..., np.newaxis, np.newaxis]
        )

        self._pp = posterior
        self._prx = p_r_x

        h = -1 * np.sum(
            posterior * np.log2(posterior + 1e-10),
            axis=tuple(range(2, posterior.ndim))
        )

        e_h = np.sum(h * p_r_x, axis=0)

        self.h = h
        self.e_h = e_h

        self.curr_stim_index = np.argmin(e_h)

        self._posterior = posterior

    def update(self, trial_outcome):

        trial_outcome = int(trial_outcome)

        assert trial_outcome in [0, 1]

        self._prior = self._posterior[trial_outcome, self.curr_stim_index, ...]



def from_file(filename):

    with open(filename, "rb") as file_handle:
        psi = pickle.load(file=file_handle)

    return psi
