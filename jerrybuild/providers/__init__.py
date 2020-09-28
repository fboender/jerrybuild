from . import generic
from . import github
from . import gogs

providers = {
    "generic": generic,
    "github": github,
    "gogs": gogs,
}
