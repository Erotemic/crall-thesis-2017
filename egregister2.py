import dtool
import utool as ut
import numpy as np

register_preproc = dtool.make_depcache_decors('annotation')['preproc']

class FeatConfig(dtool.Config):
    _param_info_list = [
        ut.ParamInfo('affine_invariance', True),
        ut.ParamInfo('rotation_invariance', False),
        ut.ParamInfo('augment_orientation', False),
        ut.ParamInfo('dense', False),
        ut.ParamInfo('dense_stride', False, hideif=lambda cfg: not cfg['dense']),
    ]

@register_preproc(
    tablename='feat', parents=['chip'],
    colnames=['num', 'kpts', 'vecs'],
    coltypes=[int, np.ndarray, np.ndarray],
    configclass=FeatConfig,
)
def compute_feats(depc, chip_id_list, config):
    """
    Compute SIFT features for every input chip.

    Args:
        depc (dtool.DependencyCache): dependency cache object
        cid_list (list): parent chip rowids
        config (dict): configuration options

    Yields:
        tuple: number of features, affine keypoints, SIFT descriptors

    Example:
        >>> import ibeis
        >>> depc = ibeis.opendb('testdb1').depc_annot
        >>> # Get circular keypoints of the first three annotations
        >>> config = dict(affine_invariance=False)
        >>> kpts_list = depc.get('feat', [1, 2, 3], 'kpts', config=config)
    """
    import pyhesaff
    chip_gen = depc.get_native('chip', chip_id_list, 'img')
    for chip in chip_gen:
        kpts, vecs = pyhesaff.detect(chip, **config)
        yield len(kpts), kpts, vecs
