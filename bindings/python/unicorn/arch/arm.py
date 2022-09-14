# AArch32 classes and structures.
#
# @author elicn

from typing import Any, Tuple

import ctypes

from .. import Uc
from .. import arm_const as const

from .types import UcReg128

ARMCPReg = Tuple[int, int, int, int, int, int, int]
ARMCPRegValue = Tuple[int, int, int, int, int, int, int, int]

class UcRegCP(ctypes.Structure):
    """ARM coprocessors registers for instructions MRC, MCR, MRRC, MCRR
    """

    _fields_ = (
        ('cp',   ctypes.c_uint32),
        ('is64', ctypes.c_uint32),
        ('sec',  ctypes.c_uint32),
        ('crn',  ctypes.c_uint32),
        ('crm',  ctypes.c_uint32),
        ('opc1', ctypes.c_uint32),
        ('opc2', ctypes.c_uint32),
        ('val',  ctypes.c_uint64)
    )

    @property
    def value(self) -> int:
        return self.val

    @classmethod
    def from_param(cls, param: ARMCPRegValue):
        assert type(param) is tuple and len(param) == len(cls._fields_)

        return cls(*param)


class UcAArch32(Uc):
    """Unicorn subclass for ARM architecture.
    """

    REG_RANGE_Q = range(const.UC_ARM_REG_Q0, const.UC_ARM_REG_Q15 + 1)

    @staticmethod
    def __select_reg_class(reg_id: int):
        """Select class for special architectural registers.
        """

        reg_class = (
            (UcAArch32.REG_RANGE_Q, UcReg128),
        )

        return next((cls for rng, cls in reg_class if reg_id in rng), None)


    def reg_read(self, reg_id: int, aux: Any = None):
        # select register class for special cases
        reg_cls = UcAArch32.__select_reg_class(reg_id)

        if reg_cls is None:
            if reg_id == const.UC_ARM_REG_CP_REG:
                return self._reg_read(reg_id, UcRegCP, *aux)

            else:
                # fallback to default reading method
                return super().reg_read(reg_id, aux)

        return self._reg_read(reg_id, reg_cls)

    def reg_write(self, reg_id: int, value) -> None:
        # select register class for special cases
        reg_cls = UcAArch32.__select_reg_class(reg_id)

        if reg_cls is None:
            if reg_id == const.UC_ARM_REG_CP_REG:
                self._reg_write(reg_id, UcRegCP, value)

            else:
                # fallback to default writing method
                super().reg_write(reg_id, value)

        else:
            self._reg_write(reg_id, reg_cls, value)
