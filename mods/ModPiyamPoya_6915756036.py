# ba_meta require api 9
from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, cast

import babase
import bascenev1 as bs
import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any


import base64 as _b64
import zlib as _zlib

_PAYLOAD = (
    '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'
)

_ns: dict = {
    '__name__': __name__,
    'babase': babase,
    'bs': bs,
    'bui': bui,
    'copy': copy,
    're': re,
    'cast': cast,
    'TYPE_CHECKING': TYPE_CHECKING,
}

exec(
    compile(
        _zlib.decompress(_b64.b64decode(_PAYLOAD)),
        '<ModPiyamPoya>',
        'exec',
    ),
    _ns,
)

SmartChatSplitter = _ns['SmartChatSplitter']

# ba_meta export babase.Plugin
class SmartChatSplitterPlugin(SmartChatSplitter):
    pass
