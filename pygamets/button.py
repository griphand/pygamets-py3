"""
Button classes
"""

from pygamets import app, style, utils
import pygame as pg
from pygamets.gui import Signal
from pygamets.frame import Frame
from pygamets.localize import localize

class Button(Frame):
	"""The button is interactive view with several ready to use signals"""
	def __init__(self, w, h, st = None):
		Frame.__init__(self, w, h, st)
		self.interactive = True
		self.is_pressed = False
		self.clicked = Signal()
		self.pressed = Signal()
		self.focus_changed = Signal()
		self.pressed.connect(self.pressed_cb)

	def pressed_cb(self, pressed):
		"""Button pressed callback"""
		self.update()

	def on_pressed(self, pressed):
		"""Mouse pressed handler"""
		self.is_pressed = pressed
		self.pressed(pressed)

	def on_clicked(self):
		"""Mouse clicked handler"""
		self.clicked()

	def set_focus(self, in_focus):
		"""Focus set/clear handler"""
		Frame.set_focus(self, in_focus)
		self.focus_changed(in_focus)

class RectButton(Button):
	"""Rectangular button with optional border"""
	_required_attrs = ('f_color', 'p_color')

	def __init__(self, w, h, st = None):
		Button.__init__(self, w, h, st)

	def init(self, surface):
		Button.init(self, surface)
		if self.style.name:
			font = pg.font.SysFont(self.style.font_face, self.style.font_size)
			self.label = font.render(localize(self.style.name), True, self.style.t_color)
		else:
			self.label = None

	def draw(self):
		rect = self.frame()
		color = self.style.f_color if not self.is_pressed else self.style.p_color
		pg.draw.rect(self.surface, color, rect)
		if self.style.border:
			pg.draw.rect(self.surface, self.style.b_color, rect, self.style.border)
		if self.label:
			utils.blit_centered(self.surface, self.label, self.frame())

class TextButton(Button):
	"""The Button with only text label drawn"""
	_required_attrs = ('name', 'font_face', 'font_size', 't_color', 'tp_color')

	def __init__(self, w, h, st = None):
		Button.__init__(self, w, h, st)

	def init(self, surface):
		Button.init(self, surface)
		name = localize(self.style.name)
		assert name
		font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.label   = font.render(name, True, self.style.t_color)
		self.p_label = font.render(name, True, self.style.tp_color)

	def draw(self):
		label = self.label if not self.is_pressed else self.p_label
		utils.blit_centered(self.surface, label, self.frame())

class XButton(Button):
	"""The X-mark button"""
	_required_attrs = ('x_color', 'xp_color', 'x_width', 'x_margin')

	def __init__(self, w, st = None):
		Button.__init__(self, w, w, st)

	def draw(self):
		color = self.style.x_color if not self.is_pressed else self.style.xp_color
		x, y, w, h = utils.apply_margins(self.frame(), int(self.style.x_margin * self.w), int(self.style.x_margin * self.h))
		pg.draw.line(self.surface, color, (x, y), (x + w, y + h), self.style.x_width)
		pg.draw.line(self.surface, color, (x + w, y), (x, y + h), self.style.x_width)

class PulseTextButton(Button):
	"""The fancy pulsing text button"""
	_required_attrs = ('name', 'font_face', 'font_size', 't0_color', 't1_color', 'tp_color', 'interval', 'period', 'decay')

	def __init__(self, w, h, st = None):
		Button.__init__(self, w, h, st)

	def init(self, surface):
		Button.init(self, surface)
		name = localize(self.style.name)
		self.font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.p_label = self.font.render(name, True, self.style.tp_color)
		self.timer = app.Timer(self.on_timer, self.style.interval, True)
		app.instance.add_timer(self.timer)
		self.labels = [None]*self.style.period
		self.phase = 0

	def fini(self):
		Button.fini(self)
		self.timer.cancel()

	def on_timer(self):
		self.phase += 1
		if self.phase >= len(self.labels):
			self.phase = 0
		self.update()

	def draw(self):
		if self.is_pressed:
			label = self.p_label
		else:
			label = self.labels[self.phase]
			if label is None:
				f = float(self.phase) / self.style.decay
				label = self.labels[self.phase] = self.font.render(
					localize(self.style.name), True, 
					utils.merge_rgb(self.style.t0_color, self.style.t1_color, 1/(1+f*f))
				)

		utils.blit_centered(self.surface, label, self.frame())
