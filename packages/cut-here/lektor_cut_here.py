from lektor.pluginsystem import Plugin


class CutHerePlugin(Plugin):
    name = 'cut-here'
    description = 'Allow to summarize a blog post.'

    def on_setup_env(self, **extra):
        def cut_here(body):
            """Strip the content of an entry and leave only the "teaser".

            To define where to cut, use a comment ``<!-- CUT-HERE -->``.

            You can define it in reST using a comment::

                ..
                    CUT-HERE
            """
            body = body.html
            pos = body.find("<!-- CUT-HERE -->")
            if pos == -1:
                return body

            return body[:pos]

        self.env.jinja_env.filters["cut_here"] = cut_here
