#! /usr/bin/env python
#
# Print all the unique regions of VF influence
# Not useful, just playing with how gvar fits together

from __future__ import print_function, division, absolute_import
import contextlib
from fontTools import ttLib
import sys

def _gvar_regions(font):
  gvar = font['gvar']
  # gvar.variations: map glyph_name: List of TupleVariation
  # ttLib/tables/TupleVariation.py
  regions = set()
  for tuple_variations in gvar.variations.values():
    for tuple_variation in tuple_variations:
      region = ()
      for axis_tag, (min_v, peak_v, max_v) in tuple_variation.axes.items():
        region += ((axis_tag, min_v, peak_v, max_v))
      regions.add(region)
  return regions

for fontfile in sys.argv[1:]:
  with contextlib.closing(ttLib.TTFont(fontfile)) as font:
    print(fontfile)
    if 'gvar' in font:
      for region in _gvar_regions(font):
        print('  {}'.format(str(region)))
    else:
      print('  No regions in {}'.format(fontfile))
