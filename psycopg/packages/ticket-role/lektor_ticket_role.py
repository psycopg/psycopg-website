from docutils import nodes, utils
from docutils.parsers.rst import roles
from lektor.pluginsystem import Plugin


def ticket_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    try:
        num = int(text.replace('#', ''))
    except ValueError:
        msg = inliner.reporter.error(
            "ticket number must be... a number, got '%s'" % text)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    url_pattern = 'https://github.com/psycopg/psycopg2/issues/%s'
    url = url_pattern % num
    roles.set_classes(options)
    node = nodes.reference(rawtext, 'ticket ' + utils.unescape(text),
            refuri=url, **options)
    return [node], []


roles.register_local_role('ticket', ticket_role)


class TicketRolePlugin(Plugin):
    name = 'ticket-role'
    description = "Add a 'ticket' role to reST markup."
