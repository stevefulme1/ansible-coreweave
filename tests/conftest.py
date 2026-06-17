"""Root conftest — set up ansible_collections namespace path for imports."""

import os
import sys

# When running pytest from the collection root, the ansible_collections namespace
# must resolve: ansible_collections/stevefulme1/coreweave → this repo.
# CI checkouts handle this via the checkout path; local dev needs a symlink.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_parent = os.path.dirname(_repo_root)
_ns_dir = os.path.join(_parent, "ansible_collections", "stevefulme1")
_link = os.path.join(_ns_dir, "coreweave")

if not os.path.exists(_link):
    os.makedirs(_ns_dir, exist_ok=True)
    os.symlink(_repo_root, _link)

if _parent not in sys.path:
    sys.path.insert(0, _parent)
