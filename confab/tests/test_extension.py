from confab.definitions import Settings
from confab.iter import iter_conffiles
from confab.tests.utils import TempDir

from fabric.api import settings
from unittest import TestCase
from mock import Mock, patch
from os import makedirs
from os.path import join, dirname


class TestExtension(TestCase):

    def test_extension_paths(self):
        """
        Test loading of templates and data from extension entry points.
        """
        settings_ = Settings.load_from_dict(dict(environmentdefs={'any': ['host1']},
                                                 roledefs={'role1': ['host1']}))

        # use an empty dir as the user's templates dir to make sure
        # only the test templates and data are loaded
        with TempDir() as tmp_dir:
            makedirs(join(tmp_dir.path, 'templates'))
            makedirs(join(tmp_dir.path, 'data'))

            # mock entry point loading to return one entry point with the test templates
            mock_entry_point = Mock()
            mock_entry_point.load.return_value = lambda: join(dirname(__file__), 'extension')

            with patch('confab.iter.iter_entry_points', Mock(return_value=[mock_entry_point])):
                with settings(environmentdef=settings_.for_env('any')):

                    for conffiles in iter_conffiles(tmp_dir.path):
                        conffiles.generate(tmp_dir.path)

                    self.assertEquals('foo', tmp_dir.read('generated/host1/foo.txt'))
