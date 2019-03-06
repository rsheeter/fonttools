#! /usr/bin/env python
#
# Drop unwanted parts of gvar

from __future__ import print_function, division, absolute_import
import contextlib
from fontTools import ttLib
from fontTools.varLib import models
import re
import sys
from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_list('axis_limits', [],
                  'csv of axes to limit, tag=min:max')
flags.DEFINE_list('axis_drops', [], 'axis tags to drop')

def _pin_axes(tuple_variations, axes_to_pin):
  for tuple_variation in tuple_variations:
    axis_isct = axes_to_pin.keys() & tuple_variation.axes.keys()
    if not axis_isct:
      continue  # this tuple isn't impacted by pinning

    axes_pinned = {tag: tuple_variation.axes[tag] for tag in axis_isct}
    pin_influence = models.supportScalar(axes_to_pin, axes_pinned)
    print('{} pin {} influence {}'.format(axes_pinned, axes_to_pin, pin_influence))

    for i in range(len(tuple_variation.coordinates)):
      original = tuple_variation.coordinates[i]
      if original is None:
        continue
      exact = tuple(v * pin_influence for v in tuple_variation.coordinates[i])
      coord = tuple(int(v) for v in exact)
      print('  {} * {} = {} int {}'.format(tuple_variation.coordinates[i], pin_influence, exact, coord))
      tuple_variation.coordinates[i] = coord

    # remove newly pined axes
    for tag in axis_isct:
      del tuple_variation.axes[tag]

    if not tuple_variation.axes:
      print('TODO tuple has no axes, modify base glyph')

def _subset_gvar_naive(gvar, axis_limits):
  """Applies axis limits to gvar table in place.

  Args:
    gvar: a gvar table
    axis_limits: map of tag => tuple or none
                 tuple is (min, max) new range of axis, inclusive
                   min == max pins axis
                 none means drop axis entirely
  """
  axes_to_drop = {tag for tag in axis_limits if axis_limits[tag] is None}
  axes_to_pin = {tag: axis_limits[tag][0] for tag in axis_limits 
                 if tag not in axes_to_drop 
                    and axis_limits[tag][0] == axis_limits[tag][1]}
  variations = {}
  for glyph_name, tuple_variations in gvar.variations.items():
    new_tuple_variations = [tv for tv in tuple_variations 
                            if not tv.axes.keys() & axes_to_drop]
    if not new_tuple_variations:
      continue  # dropped completely, don't add to new variations map

    # we're keeping these variations but we might need to pin them
    # TODO: if we're removing *all* the axes we need to reflect change into actual outlines
    if axes_to_pin:
      _pin_axes(new_tuple_variations, axes_to_pin)

    variations[glyph_name] = new_tuple_variations
  gvar.variations = variations


def _axes(fvar):
  return {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in fvar.axes}

def _normalized_axis_limits(axes):
  """
  Args:
    axes: map axis_tag: (min, default, max) for axis
  """
  axis_limits = {tag: None for tag in FLAGS.axis_drops}
  for limit in FLAGS.axis_limits:
    match = re.match(r'^(\w{4})=([^:]+)(?:[:](.+))?$', limit)
    if not match:
      raise ValueError('bad limit: {}'.format(limit))
    tag = match.group(1)
    if not tag in axes:
      raise ValueError('No such axis as {}'.format(tag))
    lbound = models.normalizeValue(float(match.group(2)), axes[tag])
    ubound = lbound
    if match.group(3):
      ubound = models.normalizeValue(float(match.group(3)), axes[tag])
    axis_limits[tag] = (lbound, ubound)
    # TEMPORARY
    if lbound != ubound:
        raise ValueError('limit must (for now) be a point')
  return axis_limits

def main(argv):
  for arg in argv[1:]:
    with contextlib.closing(ttLib.TTFont(arg)) as font:
      print(arg)
      axis_limits = _normalized_axis_limits(_axes(font['fvar']))

      for tag in sorted(axis_limits.keys()):
        axis_range = axis_limits[tag]
        if not axis_range:
          axis_range = 'DROP'
        print('{}: {}'.format(tag, axis_range))
      if 'gvar' in font:
        _subset_gvar_naive(font['gvar'], axis_limits)
        subset_file = arg + '.subset'
        font.save(subset_file)
        print('Wrote {}'.format(subset_file))

if __name__ == '__main__':
  app.run(main)