import dtool
import utool as ut
import numpy as np

register_preproc = dtool.make_depcache_decors('annotation')['preproc']

class FeatConfig(dtool.Config):
    _param_info_list = [
        ut.ParamInfo('affine_invariance', True, alias='AI'),
        ut.ParamInfo('rotation_invariance', False, alias='RI'),
        ut.ParamInfo('rotation_heuristic', False, alias='QRH'),
    ]

@register_preproc(
    tablename='feat', parents=['chip'],
    colnames=['num', 'kpts', 'vecs'],
    coltypes=[int, np.ndarray, np.ndarray],
    configclass=FeatConfig,
)
def compute_feats(depc, chip_id_list, config):
    """
    How SIFT features are computed for a set of chips.

    Example:
        >>> # Get circular keypoints of the first three annotations
        >>> config = dict(AI=False)
        >>> kpts_list = depc.get('feat', [1, 2, 3], 'kpts', config)
    """
    import pyhesaff
    chip_gen = depc.get_native('chip', chip_id_list, 'img')
    for chip in chip_gen:
        kpts, vecs = pyhesaff.detect_feats(chip, **config)
        yield len(kpts), kpts, vecs
