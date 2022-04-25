"""
Touch screen calibration management code
"""

import os, math, imp

config_folder = 'config'
config_file   = 'calibration'

def det3(
	a11, a12, a13,
	a21, a22, a23,
	a31, a32, a33
):
	"""Returns the 3x3 matrix determinant"""
	return (a11) * (a22) * (a33) + (a12) * (a23) * (a31) + (a13) * (a21) * (a32) \
		 - (a12) * (a21) * (a33) - (a11) * (a23) * (a32) - (a13) * (a22) * (a31)

def lsm_solve(F, X, Y):
	"""
	Find and return a, b, c giving lowest mean square error in the equation:
		f = ax + by + c
	The arguments F, X, Y are the lists of f, x, y.
	"""
	n = len(F)
	assert n == len(X) == len(Y)
	sf, sx, sy = sum(F), sum(X), sum(Y)
	sx2, sy2 = sum((x*x for x in X)), sum((y*y for y in Y))
	sxy = sum((x*Y[i] for i, x in enumerate(X)))
	sfx = sum((f*X[i] for i, f in enumerate(F)))
	sfy = sum((f*Y[i] for i, f in enumerate(F)))
	d = det3(
		sx,  sy,  n,
		sx2, sxy, sx,
		sxy, sy2, sy
	)
	da = det3(
		sf,  sy,  n,
		sfx, sxy, sx,
		sfy, sy2, sy
	)
	db = det3(
		sx,  sf,  n,
		sx2, sfx, sx,
		sxy, sfy, sy
	)
	dc = det3(
		sx,  sy,  sf,
		sx2, sxy, sfx,
		sxy, sy2, sfy
	)
	return da/d, db/d, dc/d

def build(screen_pts, touch_pts):
	"""
	Returns the (calibration, maximum deviation) tuple
	given the list of relative screen coordinates (in 0..1 range)
	and the list of the corresponding touch points.
	"""
	screen_x, screen_y = zip(*screen_pts)
	touch_x,  touch_y  = zip(*touch_pts)
	ax, bx, cx = lsm_solve(screen_x, touch_x, touch_y)
	ay, by, cy = lsm_solve(screen_y, touch_x, touch_y)
	dmax = 0
	for i, (tx, ty) in enumerate(touch_pts):
		x, y = screen_pts[i]
		dx, dy = ax*tx + bx*ty + cx - x, ay*tx + by*ty + cy - y
		d = math.sqrt(dx*dx + dy*dy)
		dmax = max(dmax, d)
	return ((ax, bx, cx), (ay, by, cy)), dmax

def config_dir():
	"""Returns the path to config directory with calibration file"""
	return os.path.join(os.path.abspath(os.path.dirname(__file__)), config_folder)

def config_path():
	"""Returns the full path to the calibration file"""
	return os.path.join(config_dir(), config_file + '.py')

def save(calib):
	"""Save calibration coefficients"""
	(ax, bx, cx), (ay, by, cy) = calib
	try:
		# ensure the config directory exists
		os.mkdir(config_dir())
	except:
		pass
	with open(config_path(), 'w') as f:
		f.write('# Autogenerated touch-screen calibration coefficients\n')
		f.write('calib=((%f, %f, %f), (%f, %f, %f))\n' % (ax, bx, cx, ay, by, cy))

def load():
	"""Load calibration coefficients"""
	m = imp.find_module(config_file, [config_dir()])
	module = imp.load_module(config_file, m[0], m[1], m[2])
	return module.calib

def to_screen_rel( x, y, calib ):
	"""Convert touch screen point (x, y) to relative screen coordinate (in 0..1 range)"""
	(ax, bx, cx), (ay, by, cy) = calib
	return max(0., min(1., x*ax + y*bx + cx)), max(0., min(1., x*ay + y*by + cy))

def to_screen(x, y, w, h, calib):
	"""Convert touch screen point (x, y) to screen coordinate given the screen width, height tuple and calibration"""
	rx, ry = to_screen_rel( x, y, calib )
	return min(w, int(w*rx)), min(h, int(h*ry))
