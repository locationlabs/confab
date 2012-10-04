"""
Generate configuration files using Jinja2 templates.

We expect as input a Jinja2 Environment, which must use a Loader
that supports list_templates(). Use of the Environment abstraction
nicely separates the concern of which templates to render from
that of rendering them.
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

def _is_temporary(file_name):
    """
    Determine if a file is a temporary file.
    """
    return file_name.endswith('~')

class TemplateWriter(object):
    """
    Helper class that encapsulates writing out a single template.
    """

    def __init__(self, env, template, data, dest_dir):
        self.env = env
        self.template = template
        self.data = data
        self.mime_type = magic.Magic(mime=True).from_file(self.template.filename)
        self.dest_file_name = _render_string(os.sep.join((dest_dir,self.template.name)),
                                             self.env,
                                             self.data)

    def _write_verbatim(self):
        """
        Write the template file verbatim, without templating.
        """
        shutil.copy2(self.template.filename, self.dest_file_name)

    def _write_template(self):
        """
        Write the template file to the destination, preserving ownerships.
        """
        with open(self.dest_file_name, 'w') as dest_file:
            dest_file.write(self.template.render(**self.data) + '\n')
            shutil.copystat(self.template.filename, self.dest_file_name)

    def _is_template(self):
        """
        Should this template be treated as a template (instead of a verbatim file)?
        """
        return self.mime_type.split('/')[0] == 'text' or self.mime_type == 'application/xml'

    def write(self):
        """
        Write the template file.
        """

        # ensure that destination directory exists
        _ensure_dir(os.path.dirname(self.dest_file_name))

        if self._is_template():
            self._write_template()
        else:
            self._write_verbatim()


def generate(env, data, dest_dir):
    """
    Generate templated outputs by listing all available templates in
    the Jinja2 Environment and writing them out.
    """

    # Ensure that destination is exists and is empty
    _clear_dir(dest_dir)
    _ensure_dir(dest_dir)

    def iter_writers():
        for template_name in env.list_templates():
            if not _is_temporary(template_name):
                yield TemplateWriter(env,
                                     env.get_template(template_name),
                                     data,
                                     dest_dir)

    # Write all templates
    for writer in iter_writers():
        writer.write()



