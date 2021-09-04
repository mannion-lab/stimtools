import IPython.display


def nb_player(sound, sr, vol_reduce=0.1):

    return IPython.display.Audio(
        data=sound * vol_reduce,
        rate=sr,
        embed=True,
        normalize=False,
    )
