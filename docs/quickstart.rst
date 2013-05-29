.. _quickstart:

Quickstart
==========

1.  Install confab::

        pip install confab

2.  Create a ``settings.py`` file::

        cat > settings.py << "EOF"
        environmentdefs = {
            'local': ['localhost']
        }

        roledefs = {
            'example': ['localhost']
        }
        EOF

3.  Create a template::

        mkdir -p templates/example/tmp/
        echo '{{ value }}' > templates/example/tmp/hello.txt

4.  Create data to populate the template::

        mkdir -p data
        echo 'value = "world"' > data/default.py

5.  Review the difference between the template value and the value on the
    target host::

        confab diff

6.  Push changes to the target host::

        confab push

7.  Review the change::

        ssh localhost cat /tmp/hello.txt
