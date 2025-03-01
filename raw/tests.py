from _prefix import *
from windows_utils import *
from windows_base import *
from task_flows import *
from windows import *


class _TestUtils(TestCase):

    def test_shrink_path(self):
        path = r"C:\Users\Test\AppData\Local\Microsoft\WindowsApps"
        shrinked = shrink_path(path, 20)
        self.assertEqual(shrinked, r"C:\...ft\WindowsApps")

        path = r"/home/test/.config/"
        shrinked = shrink_path(path, 30)
        self.assertEqual(shrinked, path)

        path = r"/home/test/.config/gnome_shell"
        shrinked = shrink_path(path, 10)
        self.assertEqual(shrinked, r"/home/.../gnome_shell")

    def test_is_dark_color(self):
        self.assertTrue(is_dark_color(0, 0, 0))

        self.assertTrue(is_dark_color(0, 0, 255))
        self.assertTrue(is_dark_color(255, 0, 0))
        self.assertTrue(is_dark_color(255, 0, 255))

        self.assertFalse(is_dark_color(0, 255, 0))
        self.assertFalse(is_dark_color(0, 255, 255))
        self.assertFalse(is_dark_color(255, 255, 0))

        self.assertFalse(is_dark_color(255, 255, 255))


class _TestWindowPosition(TestCase):

    def test_coords_calculation(self):
        x, y = WindowMixin._calculate_coords((1005, 495), (550, 450), (250, 150), (2560, 1440))
        self.assertTrue((x, y) == (1155, 645))
        x, y = WindowMixin._calculate_coords((285, 304), (550, 450), (900, 500), (2560, 1440))
        self.assertTrue((x, y) == (110, 279))
        x, y = WindowMixin._calculate_coords((2240, 224), (550, 450), (900, 500), (2560, 1440))
        self.assertTrue((x, y) == (1630, 199))
        x, y = WindowMixin._calculate_coords((912, 1147), (550, 450), (900, 500), (2560, 1440))
        self.assertTrue((x, y) == (737, 850))


class _TestTaskConfig(TestCase):

    def test_task_assembling(self):
        task_config = TaskConfig()
        task_config.set_specs(30, 2)
        task_config.set_filepath("/test.webm")
        task_config.set_dirs(["/pic/test1"])

        self.assertFalse("--live-preview" in task_config.convert_to_command(True))
        self.assertTrue("--live-preview" in task_config.convert_to_command(False))

    def test_user_format_converting(self):
        test_string = '\ttest\ntest\rtest'

        res_win = TaskConfig.to_user_format(test_string, bash=False)
        self.assertTrue(res_win.startswith('"') and res_win.endswith('"'))
        self.assertTrue(r"\ttest\ntest\rtest" in res_win)

        res_bash = TaskConfig.to_user_format(test_string, bash=True)
        self.assertTrue(res_bash.startswith("'") and res_bash.endswith("'"))
        self.assertTrue(r"\ttest\ntest\rtest" in res_bash)


class _TestFieldsValidators(TestCase):

    def test_color_validator(self):
        self.assertTrue(NewTaskWindow.validate_color(""))
        self.assertTrue(NewTaskWindow.validate_color("#00ff00"))
        self.assertTrue(NewTaskWindow.validate_color("#00"))
        self.assertTrue(NewTaskWindow.validate_color("face00"))
        self.assertTrue(NewTaskWindow.validate_color("ffff"))

        self.assertFalse(NewTaskWindow.validate_color("#0000000"))
        self.assertFalse(NewTaskWindow.validate_color("##000000"))
        self.assertFalse(NewTaskWindow.validate_color("#asjmi"))
        self.assertFalse(NewTaskWindow.validate_color("000#"))

    def test_fps_validator(self):
        self.assertTrue(NewTaskWindow.validate_fps(""))
        self.assertTrue(NewTaskWindow.validate_fps("0"))
        self.assertTrue(NewTaskWindow.validate_fps("1"))
        self.assertTrue(NewTaskWindow.validate_fps("60"))

        self.assertFalse(NewTaskWindow.validate_fps(" "))
        self.assertFalse(NewTaskWindow.validate_fps("-1"))
        self.assertFalse(NewTaskWindow.validate_fps("61"))
        self.assertFalse(NewTaskWindow.validate_fps("a"))
        self.assertFalse(NewTaskWindow.validate_fps("$"))
