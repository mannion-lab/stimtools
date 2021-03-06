import numpy as np
import scipy.stats

import stimtools.utils
import stimtools.psi


def psi_demo(n_trials=150, fixed_seed=False, verbose=False, ratio=0.0, check_reset=True):
    "Demo of the operation of the psi function"

    true_alpha = 5.0
    true_beta = 1.0

    n_res = 100

    params = {
        "alpha": {
            "levels": np.linspace(2.5, 7.5, n_res),
            "prior": scipy.stats.distributions.uniform.pdf(
                np.linspace(2.5, 7.5, n_res), loc=2.5, scale=5.0
            ),
            "marginalise": False,
        },
        "beta": {
            "levels": np.linspace(0, 10, n_res)[1:],
            "prior": scipy.stats.distributions.uniform.pdf(
                np.linspace(0, 10, n_res)[1:],
                loc=np.linspace(0, 10, n_res)[1],
                scale=(np.linspace(0, 10, n_res)[-1] - np.linspace(0, 10, n_res)[1]),
            ),
            "marginalise": True,
        },
    }

    stim_levels = np.linspace(0, 10, n_res)

    # useful for checking that the output doesn't change with refactoring
    if fixed_seed:
        seed = 28513
    else:
        seed = np.random.randint(low=0, high=2 ** 32 - 1)

    rand = np.random.RandomState(seed=seed)

    psych_func = stimtools.utils.logistic

    psi = stimtools.psi.Psi(
        params=params, stim_levels=stim_levels, pf=psych_func, seed=seed
    )

    if check_reset:
        n_iterations = 2
    else:
        n_iterations = 1

    for i_iteration in range(n_iterations):

        psi.step()

        for i_trial in range(n_trials):

            resp_prob = psych_func(stim_levels[psi.curr_stim_index], true_alpha, true_beta)

            resp = rand.choice([0, 1], p=[1 - resp_prob, resp_prob])

            psi.update(resp)

            estimates = psi.get_estimates()

            psi.step(ratio=ratio)

            if verbose:
                print(
                    "{t:d}  alpha:{a:.3f}   beta:{b:.3f}".format(
                        t=i_trial + 1, a=estimates["alpha"], b=estimates["beta"]
                    )
                )

        print(psi.get_estimates())

        if check_reset:
            psi.reset()
            rand = np.random.RandomState(seed=seed)

    return psi


if __name__ == "__main__":
    # {'alpha': 4.974747474747475, 'beta': 1.3131313131313131}
    psi_demo(fixed_seed=True)
