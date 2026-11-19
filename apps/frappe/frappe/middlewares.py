# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from pathlib import Path
import werkzeug.utils
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware

import frappe
from frappe.utils import cstr, get_site_name
from frappe.utils.response import FORCE_DOWNLOAD_EXTENSIONS


class StaticDataMiddleware(SharedDataMiddleware):
	def __init__(self, app, exports, **kwargs):
		super().__init__(app, exports, **kwargs)
		self.sites_dir = None
		if isinstance(exports, dict) and "/files" in exports:
			self.sites_dir = Path(exports["/files"])
		elif isinstance(exports, (list, tuple)):
			for k, v in exports:
				if k == "/files" and isinstance(v, str):
					self.sites_dir = Path(v)

	def __call__(self, environ, start_response):
		self.environ = environ
		path = environ.get("PATH_INFO", "")

		# Direct streaming with full HTTP Range request support for videos and media files
		if path.startswith("/files/") and self.sites_dir:
			try:
				site = get_site_name(getattr(getattr(frappe, "app", None), "_site", None) or environ.get("HTTP_HOST", ""))
				files_path = self.sites_dir / site / "public" / "files"
				if not files_path.is_dir() and (self.sites_dir / "public" / "files").is_dir():
					files_path = self.sites_dir / "public" / "files"
				rel_path = path[len("/files/"):].lstrip("/")
				file_path = (files_path / rel_path).resolve()
				if file_path.is_relative_to(files_path) and file_path.is_file():
					as_attachment = file_path.name.lower().endswith(FORCE_DOWNLOAD_EXTENSIONS)
					download_name = file_path.name if as_attachment else None
					response = werkzeug.utils.send_file(
						file_path,
						environ=environ,
						conditional=True,
						as_attachment=as_attachment,
						download_name=download_name,
					)
					response.headers["Accept-Ranges"] = "bytes"
					return response(environ, start_response)
			except Exception:
				pass

		def patch_start_response(status, headers, exc_info=None):
			if (
				(p := environ.get("PATH_INFO", ""))
				and p.startswith("/files/")
				and p.lower().endswith(FORCE_DOWNLOAD_EXTENSIONS)
			):
				from urllib.parse import quote

				filename = Path(p).name
				headers.append(("Content-Disposition", f"attachment; filename*=UTF-8''{quote(filename)}"))

			return start_response(status, headers, exc_info)

		return super().__call__(environ, patch_start_response)

	def get_directory_loader(self, directory):
		def loader(path):
			site = get_site_name(getattr(getattr(frappe, "app", None), "_site", None) or self.environ.get("HTTP_HOST", ""))
			files_path = Path(directory) / site / "public" / "files"
			requested_path = Path(cstr(path))
			path = (files_path / requested_path).resolve()
			if not path.is_relative_to(files_path) or not path.is_file():
				raise NotFound

			return path.name, self._opener(path)

		return loader
