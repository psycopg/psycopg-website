You can work with objects from a console by creating a pad. Here it's called
site for consistency with what you find in the templates:

.. code:: python

    from lektor.project import Project
    project = Project.discover()
    env = project.make_env()
    site = env.new_pad()

You can get blog posts by:

.. code:: pycon

    >>> list(site.get('/articles').children.limit(3))                                                         
    [<Page model='blog-post' path='/articles/psycopg-284-released'>,
     <Page model='blog-post' path='/articles/psycopg-283-released'>,
     <Page model='blog-post' path='/articles/psycopg-281-282-released'>]
