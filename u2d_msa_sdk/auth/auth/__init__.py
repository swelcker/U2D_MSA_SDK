from .auth import Auth as Auth
from .auth import AuthBackend as AuthBackend
from .auth import AuthRouter as AuthRouter

from os.path import dirname, basename, isfile, join
import glob

__version__ = "0.1.0"
__url__ = "https://github.com/swelcker/U2D_MSA_SDK"
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]