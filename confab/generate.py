"""
Generate configuration files using Jinja2 templates.

We expect as input a Jinja2 Environment, which must use a Loader
that supports list_templates(). Use of the Environment abstraction
nicely separates the concern of which templates to render from
that of rendering them.

Users can provide two further customizations:
 - a filter_func that limits which templates are returned by list_templates()
 - a mime_type_func that limits which templates are treated as templates
"""

import os
import shutil
import magic

def _clear_dir(dir_name):
    """
    Remove an entire directory tree.
    """
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)

def _ensure_dir(dir_name):
    """
    Ensure that a directory exists.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def _render_string(source, env, data):
    """
    Render a string as a template.
    """
    return env.from_string(source).render(**data)

def _is_template(mime_type):
    """
    Should a template of this mime type be treated as a template (instead of a verbatim file)?
    """
    return mime_type.split('/')[0] == 'text' or mime_type == 'application/xml'


class TemplateWriter(object):
    """
    Helper class that encapsulates writing out a single template.
    """

    def __init__(self, env, template, data, dest_dir, mime_type_func):
        self.env = env
        self.template = template
        self.data = data
        self.mime_type = magic.Magic(mime=True).from_file(self.template.filename)
        self.dest_file_name = _render_string(os.sep.join((dest_dir,self.template.name)),
                                             self.env,
                                             self.data)
        self.mime_type_func = mime_type_func if mime_type_func else _is_template

    def _write_verbatim(self):
        """
        Write the template file verbatim, without templating.
        """
        shutil.copy2(self.template.filename, self.dest_file_name)

    def _write_template(self):
        """
        Write the template file to the destination, preserving ownership.
        """
        with open(self.dest_file_name, 'w') as dest_file:
            dest_file.write(self.template.render(**self.data) + '\n')
            shutil.copystat(self.template.filename, self.dest_file_name)

    def write(self):
        """
        Write the template file.
        """

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(self.dest_file_name))

        if self.mime_type_func(self.mime_type):
            self._write_template()
        else:
            self._write_verbatim()


def generate(env, data, dest_dir, filter_func=None, mime_type_func=None):
    """
    Generate templated outputs by listing all available templates in
    the Jinja2 Environment and writing them out.

    Callers may optionally provide a filter_func, e.g. to omit temporary
    files or files that match an unexpected pattern.
    """

    # Ensure that destination exists and is empty
    _clear_dir(dest_dir)
    _ensure_dir(dest_dir)

    def iter_writers():
        for template_name in env.list_templates(filter_func=filter_func):
            yield TemplateWriter(env,
                                 env.get_template(template_name),
                                 data,
                                 dest_dir,
                                 mime_type_func)

    # Write all templates
    for writer in iter_writers():
        writer.write()
