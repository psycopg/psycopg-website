import re

from docutils import nodes, utils
from docutils.parsers.rst import roles
from lektor.pluginsystem import Plugin
from lektor.context import get_ctx, url_to


def ref_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    # match "model/id" or "label <model/id>"
    m = re.match(
        r"(?i)(?:([a-z0-9_-]+)/([a-z0-9_-]+))"
        r"|(?:([^<]+?)\s*<([a-z0-9_-]+)/([a-z0-9_-]+)>)",
        text,
    )
    if m is None:
        msg = inliner.reporter.error(
            "ref shoud be 'model/id' or 'label <model/id>', got '%s'" % text
        )
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    if m.group(3) is not None:
        _, _, label, model, id = m.groups()
    else:
        model, id, label, _, _ = m.groups()

    ctx = get_ctx()
    assert ctx
    pad = get_ctx().pad
    assert pad

    entry = pad.query(model).get(id)
    if entry is None:
        msg = inliner.reporter.error(
            "object with model=%s id=%s not found" % (model, id)
        )
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    if not label:
        label = entry["title"]

    url = entry.parent.path + "/" + entry["_slug"] + "/"
    roles.set_classes(options)
    node = nodes.reference(rawtext, label, refuri=url, **options)
    return [node], []


roles.register_local_role('ref', ref_role)


class RefRolePlugin(Plugin):
    name = 'ref-role'
    description = "Add a 'ref' role to reST markup."
