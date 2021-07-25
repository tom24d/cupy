import unittest

import numpy
import pytest  # noqa

import cupy
from cupy.cuda import runtime
from cupy import testing


@testing.parameterize(*testing.product({
    'UPLO': ['U', 'L'],
}))
@testing.gpu
class TestEigenvalue(unittest.TestCase):

    @testing.for_all_dtypes(no_float16=True, no_complex=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_eigh(self, xp, dtype):
        a = xp.array([[1, 0, 3], [0, 5, 0], [7, 0, 9]], dtype)
        w, v = xp.linalg.eigh(a, UPLO=self.UPLO)

        # Order of eigen values is not defined.
        # They must be sorted to compare them.
        inds = xp.argsort(w)
        w = w[inds]
        v = v[inds]
        return w, v

    def test_eigh_float16(self):
        # NumPy's eigh deos not support float16
        a = cupy.array([[1, 0, 3], [0, 5, 0], [7, 0, 9]], 'e')
        w, v = cupy.linalg.eigh(a, UPLO=self.UPLO)

        assert w.dtype == numpy.float16
        assert v.dtype == numpy.float16

        na = numpy.array([[1, 0, 3], [0, 5, 0], [7, 0, 9]], 'f')
        nw, nv = numpy.linalg.eigh(na, UPLO=self.UPLO)

        testing.assert_allclose(w, nw, rtol=1e-3, atol=1e-4)
        testing.assert_allclose(v, nv, rtol=1e-3, atol=1e-4)

    @testing.for_dtypes('FD')
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_eigh_complex(self, xp, dtype):
        if runtime.is_hip:
            # As of ROCm 4.2.0 rocSOLVER seems to require a Hermitian input
            a = xp.array([[1, 2j, 3], [-2j, 5, 6j], [3, -6j, 9]], dtype)
        else:
            a = xp.array([[1, 2j, 3], [4j, 5, 6j], [7, 8j, 9]], dtype)
        w, v = xp.linalg.eigh(a, UPLO=self.UPLO)

        # Order of eigen values is not defined.
        # They must be sorted to compare them.
        inds = xp.argsort(w)
        w = w[inds]
        v = v[inds]

        # rocSOLVER seems to pick a different convention in eigenvectors,
        # so the results are not directly comparible
        if runtime.is_hip:
            testing.assert_allclose(
                a.dot(v), w*v, rtol=1e-5, atol=1e-5)
            return w
        else:
            return w, v
        return w, v

    @testing.for_all_dtypes(no_float16=True, no_complex=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_eigvalsh(self, xp, dtype):
        a = xp.array([[1, 0, 3], [0, 5, 0], [7, 0, 9]], dtype)
        w = xp.linalg.eigvalsh(a, UPLO=self.UPLO)

        # Order of eigen values is not defined.
        # They must be sorted to compare them.
        inds = xp.argsort(w)
        w = w[inds]
        return w
