#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import jinja2
import os
import qrcode
import qrcode.image.svg
import sys
import toml

class Wifi_QRCode:

	def __init__(self, _toml):
		self.read_conf(_toml)
		self._factory = qrcode.image.svg.SvgPathImage

	def read_conf(self, _toml):
		"""Interpret toml that contains Wifi network information"""
		data = toml.loads(_toml)
		self._title = data.get("title", "Title placeholder")
		self._ssid = data.get("ssid", "SSID placeholder")
		self._type = data.get("type", "Wifi type placeholder")
		self._passphrase = data.get("passphrase", "Wifi passphrase")

		# Set the QR Data required for Wifi integration
		# Escape special chars in SSID and passphrase elements
		ssid = self._ssid.replace(":", "\\:").replace(";", "\\;")
		passphrase = self._passphrase.replace(":", "\\:").replace(";", "\\;")
		self._qrdata = f"WIFI:S:{ssid};T:{self._type};P:{passphrase};;"

	def render(self, jinja2_path):
		"""Generate the QRCode and output the rendered HTML"""

		# These are the recommended default for SVG
		# See https://github.com/lincolnloop/python-qrcode
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_M,
			box_size=10,
			border=4
		)
		qr.add_data(self._qrdata)
		qr.make(fit=True)

		img = qr.make_image(image_factory=self._factory)
		# lxml returns bytes for tostring(), decode it to utf-8
		self.svg = img.to_string().decode('utf-8')

		# Jinja2 templates
		path = os.path.split(jinja2_path)
		# Head (dirname)
		template_path = jinja2.FileSystemLoader(path[0])
		env = jinja2.Environment(loader=template_path)
		# Tail (filename)
		j2_template = env.get_template(path[1])
		output = j2_template.render(
			title = self._title,
			ssid  = self._ssid,
			type = self._type,
			passphrase = self._passphrase,
			qrcode = self.svg
		)
		return output

	@property
	def ssid(self):
		return self._ssid

	@property
	def passphrase(self):
		return self._passphrase

	@property
	def title(self):
		return self._title

	@property
	def type(self):
		return self._type


if __name__ == "__main__":
	toml_str = sys.stdin.read()
	wifi_qrcode = Wifi_QRCode(toml_str)
	html_output = wifi_qrcode.render("./template.j2")
	print(html_output)
