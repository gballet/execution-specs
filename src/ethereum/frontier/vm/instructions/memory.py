"""
Ethereum Virtual Machine (EVM) Memory Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Implementations of the EVM Memory instructions.
"""
from ethereum.base_types import U8_MAX_VALUE, U256, Uint

from .. import Evm
from ..gas import GAS_BASE, GAS_VERY_LOW, subtract_gas
from ..memory import (
    extend_memory_and_subtract_gas,
    memory_read_bytes,
    memory_write,
)
from ..stack import pop, push


def mstore(evm: Evm) -> None:
    """
    Stores a word to memory.
    This also expands the memory, if the memory is
    insufficient to store the word.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    StackUnderflowError
        If `len(stack)` is less than `2`.
    OutOfGasError
        If `evm.gas_left` is less than
        `3` + gas needed to extend memeory.
    """
    # convert to Uint as start_position + size_to_extend can overflow.
    start_position = Uint(pop(evm.stack))
    value = pop(evm.stack).to_be_bytes32()
    extend_memory_and_subtract_gas(evm, start_position, U256(32))
    evm.gas_left = subtract_gas(evm.gas_left, GAS_VERY_LOW)
    memory_write(evm.memory, start_position, value)


def mstore8(evm: Evm) -> None:
    """
    Stores a byte to memory.
    This also expands the memory, if the memory is
    insufficient to store the word.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    StackUnderflowError
        If `len(stack)` is less than `2`.
    OutOfGasError
        If `evm.gas_left` is less than
        `3` + gas needed to extend memory.
    """
    # convert to Uint as start_position + size_to_extend can overflow.
    start_position = Uint(pop(evm.stack))
    value = pop(evm.stack)
    # make sure that value doesn't exceed 1 byte
    normalized_bytes_value = (value & U8_MAX_VALUE).to_be_bytes()
    extend_memory_and_subtract_gas(evm, start_position, U256(1))
    evm.gas_left = subtract_gas(evm.gas_left, GAS_VERY_LOW)
    memory_write(evm.memory, start_position, normalized_bytes_value)


def mload(evm: Evm) -> None:
    """
    Load word from memory.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    StackUnderflowError
        If `len(stack)` is less than `1`.
    OutOfGasError
        If `evm.gas_left` is less than
        `3` + gas needed to extend memory.
    """
    # convert to Uint as start_position + size_to_extend can overflow.
    start_position = Uint(pop(evm.stack))
    # extend memory and subtract gas for allocating 32 bytes of memory
    extend_memory_and_subtract_gas(evm, start_position, U256(32))
    value = U256.from_be_bytes(
        memory_read_bytes(evm.memory, start_position, U256(32))
    )
    evm.gas_left = subtract_gas(evm.gas_left, GAS_VERY_LOW)
    push(evm.stack, value)


def msize(evm: Evm) -> None:
    """
    Push the size of active memory in bytes onto the stack.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    OutOfGasError
        If `evm.gas_left` is less than `2`
    """
    evm.gas_left = subtract_gas(evm.gas_left, GAS_BASE)
    memory_size = U256(len(evm.memory))
    push(evm.stack, memory_size)
