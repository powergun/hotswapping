
import hotswapping

import unittest
import time

import packageFoo


class MockModuleDescriptor(object):

    def __init__(self, fs_path):
        self.fs_path = fs_path


class TestNewerSemanticVersion(unittest.TestCase):

    def setUp(self):
        self.rule = hotswapping.NewerSemanticVersion()

    def test_noPhysicalFsPath_expectNothingFound(self):
        m = MockModuleDescriptor('')
        self.assertFalse(self.rule.search(m))

    def test_fsPathHasNoVersion_expectNothingFound(self):
        m = MockModuleDescriptor('/dir/mo')
        self.assertFalse(self.rule.search(m))

    def test_compareVersions(self):
        self.assertEqual(0, self.rule.compare_versions('', ''))
        self.assertEqual(0, self.rule.compare_versions('bb', 'aa'))
        self.assertEqual(0, self.rule.compare_versions('1.1.3v', '1.2.3.3'))
        self.assertEqual(1, self.rule.compare_versions('0.0.1', ''))
        self.assertEqual(1, self.rule.compare_versions('1.0.0', '0.9.9'))
        self.assertEqual(-1, self.rule.compare_versions('0.0.1', '0.0.11'))
        self.assertEqual(0, self.rule.compare_versions('1.000.0', '01.0.0'))

    def test_noNewVersion_expectNotFound(self):
        m = MockModuleDescriptor('/dir/mo/1.0.0/f.py')

        def _(d):
            return iter([('1.0.0', '/dir/mo/1.0.0'),
                         ('.git', '/dir/mo/.git')])

        self.rule.iter_dir = _
        self.assertFalse(self.rule.search(m))

    def test_hasNewerVersion_expectFound(self):
        m = MockModuleDescriptor('/dir/mo/1.0.0/f.py')

        def _(d):
            return iter([('1.2.0', '/dir/mo/1.2.0'),
                         ('1.0.9', '/dir/mo/1.0.9')])

        self.rule.iter_dir = _
        self.assertEqual('/dir/mo/1.2.0/f.py', self.rule.search(m))

    def test_newVersionFileDoesNotExist_expectNotFound(self):
        self.rule.check_existence = True
        m = MockModuleDescriptor('/dir/mo/1.0.0/f.py')

        def _(d):
            return iter([('1.2.0', '/dir/mo/1.2.0'),
                         ('1.0.9', '/dir/mo/1.0.9')])

        self.rule.iter_dir = _
        self.assertFalse(self.rule.search(m))


class TestNewPackageVersion(unittest.TestCase):

    def setUp(self):
        self.dao = packageFoo.PackageFoo()
        self.sut = hotswapping.NewerPackageVersion(self.dao)

    @staticmethod
    def _create_fake_m(path):
        m = hotswapping.ModuleDescriptor()
        m.birth_time = time.time()
        m.fs_mtime = 123
        m.fs_path = path
        m.deprecated = False
        return m

    def test_expectNewPackage(self):
        m = hotswapping.create_descriptor_from_package_dao('doom-1.1', self.dao, fs_creator=self._create_fake_m)
        new_package = self.sut.search(m)
        self.assertEqual('doom-1.2', new_package)

    def test_expectNoNewPackage(self):
        m = hotswapping.create_descriptor_from_package_dao('doom-1.2', self.dao, fs_creator=self._create_fake_m)
        new_package = self.sut.search(m)
        self.assertFalse(new_package)


if __name__ == '__main__':
    unittest.main()
