import unittest
from subprocess import run, PIPE

from pybump.pybump import get_setup_py_version, is_semantic_string, bump_version, is_valid_helm_chart

valid_helm_chart = {'apiVersion': 'v1',
                    'appVersion': '1.0',
                    'description': 'A Helm chart for Kubernetes',
                    'name': 'test',
                    'version': '0.1.0'}
invalid_helm_chart = {'apiVersion': 'v1',
                      'notAppVersionKeyHere': '1.0',
                      'description': 'A Helm chart for Kubernetes',
                      'name': 'test',
                      'version': '0.1.0'}
empty_helm_chart = {}

valid_setup_py = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ArieLevs/PyBump",
        license='Apache License 2.0',
        packages=setuptools.find_packages(),
    )
    """

# This setup.py content is missing 'version' key
invalid_setup_py_1 = """
    setuptools.setup(
        name="pybump",
        invalid_version_string="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
    )
    """
# This setup.py content 'version' key declared 3 times
invalid_setup_py_2 = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        version="0.1.2",
        __version__="12356"
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
    )
    """

valid_version_file_1 = """0.12.4"""
valid_version_file_2 = """1.5.0-alpha+meta"""
invalid_version_file_1 = """
    this is some text in addition to version
    1.5.0
    nothing except semantic version should be in this file
    """
invalid_version_file_2 = """
    version=1.5.0
    """


def simulate_get_version(file, app_version=False):
    """
    execute sub process to simulate real app execution,
    return current version from a file
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param app_version: boolean
    :return: CompletedProcess object
    """
    if app_version:
        return run(["python", "pybump/pybump.py", "get", "--file", file, "--app-version"], stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "pybump/pybump.py", "get", "--file", file], stdout=PIPE, stderr=PIPE)


def simulate_set_version(file, version, app_version=False):
    """
    execute sub process to simulate real app execution,
    set new version to a file
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param version: string
    :param app_version: boolean
    :return:
    """
    if app_version:
        return run(["python", "pybump/pybump.py", "set", "--file", file, "--set-version", version, "--app-version"],
                   stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "pybump/pybump.py", "set", "--file", file, "--set-version", version],
                   stdout=PIPE, stderr=PIPE)


def simulate_bump_version(file, level, app_version=False):
    """
    execute sub process to simulate real app execution,
    bump version in file based on level
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param level: string
    :param app_version: boolean
    :return:
    """
    if app_version:
        return run(["python", "pybump/pybump.py", "bump", "--level", level, "--file", file, "--app-version"],
                   stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "pybump/pybump.py", "bump", "--level", level, "--file", file],
                   stdout=PIPE, stderr=PIPE)


class PyBumpTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_is_semantic_string(self):
        self.assertEqual(is_semantic_string('1.2.3'), {'version': [1, 2, 3], 'release': '', 'metadata': ''})
        self.assertEqual(is_semantic_string('1.2.6-dev'), {'version': [1, 2, 6], 'release': 'dev', 'metadata': ''})
        self.assertEqual(
            is_semantic_string('1.2.6-dev+some.metadata'),
            {'version': [1, 2, 6], 'release': 'dev', 'metadata': 'some.metadata'}
        )
        self.assertEqual(
            is_semantic_string('1.2.3+meta-only'), {'version': [1, 2, 3], 'release': '', 'metadata': 'meta-only'}
        )
        self.assertNotEqual(is_semantic_string('1.2.3'), {'version': [1, 2, 4], 'release': '', 'metadata': ''})
        self.assertNotEqual(
            is_semantic_string('1.2.3-ALPHA'), {'version': [1, 2, 3], 'release': '', 'metadata': 'ALPHA'}
        )
        self.assertNotEqual(
            is_semantic_string('1.2.3+META.ONLY'), {'version': [1, 2, 3], 'release': 'META.ONLY', 'metadata': ''}
        )
        self.assertTrue(is_semantic_string('0.0.0'))
        self.assertTrue(is_semantic_string('13.0.75'))
        self.assertTrue(is_semantic_string('0.5.447'))
        self.assertTrue(is_semantic_string('3.0.1-alpha'))
        self.assertTrue(is_semantic_string('1.1.6-alpha-beta-gama'))
        self.assertTrue(is_semantic_string('0.5.0-alpha+meta-data.is-ok'))
        self.assertFalse(is_semantic_string('1.02.3'))
        self.assertFalse(is_semantic_string('000.000.111'))
        self.assertFalse(is_semantic_string('1.2.c'))
        self.assertFalse(is_semantic_string('1.2.-3'))
        self.assertFalse(is_semantic_string('1.9'))
        self.assertFalse(is_semantic_string('text'))

        self.assertFalse(is_semantic_string(4))
        self.assertFalse(is_semantic_string(True))
        self.assertFalse(is_semantic_string(None))

    def test_is_valid_helm_chart(self):
        self.assertTrue(is_valid_helm_chart(valid_helm_chart))
        self.assertFalse(is_valid_helm_chart(invalid_helm_chart))
        self.assertFalse(is_valid_helm_chart(empty_helm_chart))

    def test_bump_version(self):
        self.assertEqual(bump_version([9, 0, 7], 'major'), [10, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'major'), [2, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'minor'), [1, 3, 0])
        self.assertEqual(bump_version([1, 2, 3], 'patch'), [1, 2, 4])
        self.assertEqual(bump_version([0, 0, 9], 'patch'), [0, 0, 10])

        self.assertRaises(ValueError, bump_version, None, 'patch')
        self.assertRaises(ValueError, bump_version, [1, 2, 3], 'not_patch')

    def test_get_setup_py_version(self):
        self.assertEqual(get_setup_py_version(valid_setup_py), '0.1.3')

        with self.assertRaises(RuntimeError):
            get_setup_py_version(invalid_setup_py_1)

        with self.assertRaises(RuntimeError):
            get_setup_py_version(invalid_setup_py_2)

    def test_is_valid_version_file(self):
        self.assertTrue(is_semantic_string(valid_version_file_1))
        self.assertTrue(is_semantic_string(valid_version_file_2))
        self.assertFalse(is_semantic_string(invalid_version_file_1))
        self.assertFalse(is_semantic_string(invalid_version_file_2))
        self.assertEqual(is_semantic_string(valid_version_file_1),
                         {'version': [0, 12, 4], 'release': '', 'metadata': ''})
        self.assertEqual(is_semantic_string(valid_version_file_2),
                         {'version': [1, 5, 0], 'release': 'alpha', 'metadata': 'meta'})

    @staticmethod
    def test_bump_patch():
        simulate_set_version("pybump/test_valid_chart.yaml", "0.1.0")
        completed_process_object = simulate_bump_version("pybump/test_valid_chart.yaml", "patch")

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = simulate_get_version("pybump/test_valid_chart.yaml")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "0.1.1":
            raise Exception("test_bump_patch failed, return version should be 0.1.1 got " + stdout)

        # Simulate with --app-version flag
        simulate_set_version("pybump/test_valid_chart.yaml", "3.1.5", True)
        completed_process_object = simulate_bump_version("pybump/test_valid_chart.yaml", "patch", True)

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = simulate_get_version("pybump/test_valid_chart.yaml", True)
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "3.1.6":
            raise Exception("test_bump_patch failed, return version should be 3.1.6 got " + stdout)

    @staticmethod
    def test_bump_minor():
        simulate_set_version("pybump/test_valid_setup.py", "2.1.5-alpha+metadata.is.useful")
        completed_process_object = simulate_bump_version("pybump/test_valid_setup.py", "minor")

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = simulate_get_version("pybump/test_valid_setup.py")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "2.2.0-alpha+metadata.is.useful":
            raise Exception("test_bump_minor failed, "
                            "return version should be 2.2.0-alpha+metadata.is.useful got " + stdout)

    @staticmethod
    def test_bump_major():
        simulate_set_version("pybump/test_valid_chart.yaml", "0.5.9")
        completed_process_object = simulate_bump_version("pybump/test_valid_chart.yaml", "major")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = simulate_get_version("pybump/test_valid_chart.yaml")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "1.0.0":
            raise Exception("test_bump_major failed, return version should be 1.0.0 got " + stdout)

        # Simulate with --app-version flag
        simulate_set_version("pybump/test_valid_chart.yaml", "2.2.8", True)
        completed_process_object = simulate_bump_version("pybump/test_valid_chart.yaml", "major", True)

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = simulate_get_version("pybump/test_valid_chart.yaml", True)
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "3.0.0":
            raise Exception("test_bump_patch failed, return version should be 3.0.0 got " + stdout)

    @staticmethod
    def test_invalid_bump_major():
        simulate_set_version("pybump/test_invalid_chart.yaml", "3.5.5")
        completed_process_object = simulate_bump_version("pybump/test_invalid_chart.yaml", "major")

        if completed_process_object.returncode != 0:
            pass
        else:
            raise Exception("test_invalid_bump_major failed, test should of fail, but passed")


if __name__ == '__main__':
    unittest.main()
