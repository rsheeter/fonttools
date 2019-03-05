#! /usr/bin/env python
#
# Drop unwanted parts of gvar

from __future__ import print_function, division, absolute_import
import contextlib
from fontTools import ttLib
import sys

def _subset_gvar(gvar, axes_to_drop):
  for glyph_name, tuple_variations in gvar.variations.items():
    for tuple_variation in tuple_variations:
      drop = bool(tuple_variation.axes.keys() & axes_to_drop)
      action = 'DROP'
      if not drop:
        action = 'KEEP'
      print('{} {} for {}'.format(
            glyph_name, action, sorted(tuple_variation.axes.keys())))

axes_to_drop = {a for a in sys.argv[1:] if len(a) == 4}
print('Dropping %s'.format(axes_to_drop))

for arg in sys.argv[1:]:
  if len(arg) == 4:
    continue
  with contextlib.closing(ttLib.TTFont(arg)) as font:
    print(arg)
    if 'gvar' in font:
      font['gvar'] = _subset_gvar(font['gvar'], axes_to_drop)

