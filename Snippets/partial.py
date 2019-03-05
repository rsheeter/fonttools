#! /usr/bin/env python
#
# Drop unwanted parts of gvar

from __future__ import print_function, division, absolute_import
import contextlib
from fontTools import ttLib
import sys

def _subset_gvar(gvar, axes_to_drop):
  variations = {}
  for glyph_name, tuple_variations in gvar.variations.items():
    new_tuple_variations = [tv for tv in tuple_variations 
                            if not tv.axes.keys() & axes_to_drop]
    if new_tuple_variations:
      variations[glyph_name] = new_tuple_variations
  gvar.variations = variations

axes_to_drop = {a for a in sys.argv[1:] if len(a) == 4}
print('Dropping {}'.format(axes_to_drop))

for arg in sys.argv[1:]:
  if len(arg) == 4:
    continue
  with contextlib.closing(ttLib.TTFont(arg)) as font:
    print(arg)
    if 'gvar' in font:
      _subset_gvar(font['gvar'], axes_to_drop)
      subset_file = arg + '.subset'
      font.save(subset_file)
      print('Wrote {}'.format(subset_file))

