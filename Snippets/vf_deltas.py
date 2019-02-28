#! /usr/bin/env python
#
# Examine all the point deltas in gvar, output basic stats

from __future__ import print_function, division, absolute_import
import contextlib
from fontTools import ttLib
from fontTools import varLib
import sys
import statistics

def _gvar_deltas(font):
  gvar = font['gvar']
  # gvar.variations: map glyph_name: List of TupleVariation
  # ttLib/tables/TupleVariation.py
  results = list()
  for glyph_name, tuple_variations in gvar.variations.items():
    # based on varLib/mutator.py; at time of writing this looks confusing as #@#$
    coords, control = varLib._GetCoordinates(font, glyph_name)
    end_pts = control[1] if control[0] >= 1 else list(range(len(control[1])))
    
    for tuple_variation in tuple_variations:
      deltas = tuple_variation.coordinates
      if None in deltas:
        deltas = varLib.iup.iup_delta(deltas, coords, end_pts)
      results.extend([xy_tuple for xy_tuple in deltas])
  return results

flat = []
for fontfile in sys.argv[1:]:
  with contextlib.closing(ttLib.TTFont(fontfile)) as font:
    if 'gvar' in font:
      for delta in _gvar_deltas(font):
        flat.extend(delta)
    else:
      print('  No deltas in {}'.format(fontfile))

print('min {} median {} mean {:.1f} stdev {:.1f} max {}'.format(
  min(flat), statistics.median(flat), statistics.mean(flat), statistics.stdev(flat), max(flat)))
