import unittest

import rope.base.history
from rope.base import exceptions
from rope.base.change import *
from ropetest import testutils


class HistoryTest(unittest.TestCase):

    def setUp(self):
        super(HistoryTest, self).setUp()
        self.project = testutils.sample_project()
        self.history = self.project.history

    def tearDown(self):
        testutils.remove_project(self.project)
        super(HistoryTest, self).tearDown()

    def test_undoing_writes(self):
        my_file = self.project.root.create_file('my_file.txt')
        my_file.write('text1')
        self.history.undo()
        self.assertEquals('', my_file.read())

    def test_moving_files(self):
        my_file = self.project.root.create_file('my_file.txt')
        my_file.move('new_file.txt')
        self.history.undo()
        self.assertEquals('', my_file.read())

    def test_moving_files_to_folders(self):
        my_file = self.project.root.create_file('my_file.txt')
        my_folder = self.project.root.create_folder('my_folder')
        my_file.move(my_folder.path)
        self.history.undo()
        self.assertEquals('', my_file.read())

    def test_writing_files_that_does_not_change_contents(self):
        my_file = self.project.root.create_file('my_file.txt')
        my_file.write('')
        self.project.history.undo()
        self.assertFalse(my_file.exists())


class IsolatedHistoryTest(unittest.TestCase):

    def setUp(self):
        super(IsolatedHistoryTest, self).setUp()
        self.project = testutils.sample_project()
        self.history = rope.base.history.History(self.project)
        self.file1 = self.project.root.create_file('file1.txt')
        self.file2 = self.project.root.create_file('file2.txt')

    def tearDown(self):
        testutils.remove_project(self.project)
        super(IsolatedHistoryTest, self).tearDown()

    def test_simple_undo(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.assertEquals('1', self.file1.read())
        self.history.undo()
        self.assertEquals('', self.file1.read())

    def test_tobe_undone(self):
        change1 = ChangeContents(self.file1, '1')
        self.assertEquals(None, self.history.tobe_undone)
        self.history.do(change1)
        self.assertEquals(change1, self.history.tobe_undone)
        change2 = ChangeContents(self.file1, '2')
        self.history.do(change2)
        self.assertEquals(change2, self.history.tobe_undone)
        self.history.undo()
        self.assertEquals(change1, self.history.tobe_undone)

    def test_tobe_redone(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.assertEquals(None, self.history.tobe_redone)
        self.history.undo()
        self.assertEquals(change, self.history.tobe_redone)

    @testutils.assert_raises(exceptions.HistoryError)
    def test_undo_limit(self):
        history = rope.base.history.History(self.project, maxundos=1)
        history.do(ChangeContents(self.file1, '1'))
        history.do(ChangeContents(self.file1, '2'))
        try:
            history.undo()
            history.undo()
        finally:
            self.assertEquals('1', self.file1.read())

    def test_simple_redo(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.history.undo()
        self.history.redo()
        self.assertEquals('1', self.file1.read())

    def test_simple_re_undo(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.history.undo()
        self.history.redo()
        self.history.undo()
        self.assertEquals('', self.file1.read())

    def test_multiple_undos(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        change = ChangeContents(self.file1, '2')
        self.history.do(change)
        self.history.undo()
        self.assertEquals('1', self.file1.read())
        change = ChangeContents(self.file1, '3')
        self.history.do(change)
        self.history.undo()
        self.assertEquals('1', self.file1.read())
        self.history.redo()
        self.assertEquals('3', self.file1.read())

    @testutils.assert_raises(exceptions.HistoryError)
    def test_undo_list_underflow(self):
        self.history.undo()

    @testutils.assert_raises(exceptions.HistoryError)
    def test_redo_list_underflow(self):
        self.history.redo()

    def test_undoing_choosen_changes(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.history.undo(change)
        self.assertEquals('', self.file1.read())
        self.assertFalse(self.history.undo_list)

    def test_undoing_choosen_changes2(self):
        change1 = ChangeContents(self.file1, '1')
        self.history.do(change1)
        self.history.do(ChangeContents(self.file1, '2'))
        self.history.undo(change1)
        self.assertEquals('', self.file1.read())
        self.assertFalse(self.history.undo_list)

    def test_undoing_choosen_changes_not_undoing_others(self):
        change1 = ChangeContents(self.file1, '1')
        self.history.do(change1)
        self.history.do(ChangeContents(self.file2, '2'))
        self.history.undo(change1)
        self.assertEquals('', self.file1.read())
        self.assertEquals('2', self.file2.read())

    def test_undoing_writing_after_moving(self):
        change1 = ChangeContents(self.file1, '1')
        self.history.do(change1)
        self.history.do(MoveResource(self.file1, 'file3.txt'))
        file3 = self.project.get_resource('file3.txt')
        self.history.undo(change1)
        self.assertEquals('', self.file1.read())
        self.assertFalse(file3.exists())

    def test_undoing_folder_movements_for_undoing_writes_inside_it(self):
        folder = self.project.root.create_folder('folder')
        file3 = folder.create_file('file3.txt')
        change1 = ChangeContents(file3, '1')
        self.history.do(change1)
        self.history.do(MoveResource(folder, 'new_folder'))
        new_folder = self.project.get_resource('new_folder')
        self.history.undo(change1)
        self.assertEquals('', file3.read())
        self.assertFalse(new_folder.exists())

    def test_undoing_changes_that_depend_on_a_dependant_change(self):
        change1 = ChangeContents(self.file1, '1')
        self.history.do(change1)
        changes = ChangeSet('2nd change')
        changes.add_change(ChangeContents(self.file1, '2'))
        changes.add_change(ChangeContents(self.file2, '2'))
        self.history.do(changes)
        self.history.do(MoveResource(self.file2, 'file3.txt'))
        file3 = self.project.get_resource('file3.txt')

        self.history.undo(change1)
        self.assertEquals('', self.file1.read())
        self.assertEquals('', self.file2.read())
        self.assertFalse(file3.exists())

    def test_undoing_writes_for_undoing_folder_movements_containing_it(self):
        folder = self.project.root.create_folder('folder')
        old_file = folder.create_file('file3.txt')
        change1 = MoveResource(folder, 'new_folder')
        self.history.do(change1)
        new_file = self.project.get_resource('new_folder/file3.txt')
        self.history.do(ChangeContents(new_file, '1'))
        self.history.undo(change1)
        self.assertEquals('', old_file.read())
        self.assertFalse(new_file.exists())

    @testutils.assert_raises(exceptions.HistoryError)
    def test_undoing_not_available_change(self):
        change = ChangeContents(self.file1, '1')
        self.history.undo(change)

    def test_ignoring_ignored_resources(self):
        self.project.set('ignored_resources', ['ignored*'])
        ignored = self.project.get_file('ignored.txt')
        change = CreateResource(ignored)
        self.history.do(change)
        self.assertTrue(ignored.exists())
        self.assertEquals(0, len(self.history.undo_list))

    def test_get_file_undo_list_simple(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.assertEquals(set([change]),
                          set(self.history.get_file_undo_list(self.file1)))

    def test_get_file_undo_list_for_moves(self):
        change = MoveResource(self.file1, 'file2.txt')
        self.history.do(change)
        self.assertEquals(set([change]),
                          set(self.history.get_file_undo_list(self.file1)))

    # XXX: What happens for moves before the file is created?
    def xxx_test_get_file_undo_list_and_moving_its_contining_folder(self):
        folder = self.project.root.create_folder('folder')
        old_file = folder.create_file('file3.txt')
        change1 = MoveResource(folder, 'new_folder')
        self.history.do(change1)
        self.assertEquals(set([change1]),
                          set(self.history.get_file_undo_list(old_file)))

    def test_clearing_redo_list_after_do(self):
        change = ChangeContents(self.file1, '1')
        self.history.do(change)
        self.history.undo()
        self.history.do(change)
        self.assertEquals(0, len(self.history.redo_list))

    @testutils.assert_raises(exceptions.HistoryError)
    def test_undoing_a_not_yet_performed_change(self):
        change = ChangeContents(self.file1, '1')
        str(change)
        change.undo()

    def test_clearing_up_the_history(self):
        change1 = ChangeContents(self.file1, '1')
        change2 = ChangeContents(self.file1, '2')
        self.history.do(change1)
        self.history.do(change2)
        self.history.undo()
        self.history.clear()
        self.assertEquals(0, len(self.history.undo_list))
        self.assertEquals(0, len(self.history.redo_list))

    def test_redoing_choosen_changes_not_undoing_others(self):
        change1 = ChangeContents(self.file1, '1')
        change2 = ChangeContents(self.file2, '2')
        self.history.do(change1)
        self.history.do(change2)
        self.history.undo()
        self.history.undo()
        redone = self.history.redo(change2)
        self.assertEquals([change2], redone)
        self.assertEquals('', self.file1.read())
        self.assertEquals('2', self.file2.read())


class SavingHistoryTest(unittest.TestCase):

    def setUp(self):
        super(SavingHistoryTest, self).setUp()
        self.project = testutils.sample_project()
        self.history = rope.base.history.History(self.project)
        self.to_data = ChangeToData()
        self.to_change = DataToChange(self.project)

    def tearDown(self):
        testutils.remove_project(self.project)
        super(SavingHistoryTest, self).tearDown()

    def test_simple_set_saving(self):
        data = self.to_data(ChangeSet('testing'))
        change = self.to_change(data)
        self.assertEquals('testing', str(change))

    def test_simple_change_content_saving(self):
        myfile = self.project.get_file('myfile.txt')
        myfile.create()
        myfile.write('1')
        data = self.to_data(ChangeContents(myfile, '2'))
        change = self.to_change(data)
        self.history.do(change)
        self.assertEquals('2', myfile.read())
        self.history.undo()
        self.assertEquals('1', change.old_contents)

    def test_move_resource_saving(self):
        myfile = self.project.root.create_file('myfile.txt')
        myfolder = self.project.root.create_folder('myfolder')
        data = self.to_data(MoveResource(myfile, 'myfolder'))
        change = self.to_change(data)
        self.history.do(change)
        self.assertFalse(myfile.exists())
        self.assertTrue(myfolder.has_child('myfile.txt'))
        self.history.undo()
        self.assertTrue(myfile.exists())
        self.assertFalse(myfolder.has_child('myfile.txt'))

    def test_move_resource_saving_for_folders(self):
        myfolder = self.project.root.create_folder('myfolder')
        newfolder = self.project.get_folder('newfolder')
        change = MoveResource(myfolder, 'newfolder')
        self.history.do(change)

        data = self.to_data(change)
        change = self.to_change(data)
        change.undo()
        self.assertTrue(myfolder.exists())
        self.assertFalse(newfolder.exists())

    def test_create_file_saving(self):
        myfile = self.project.get_file('myfile.txt')
        data = self.to_data(CreateFile(self.project.root, 'myfile.txt'))
        change = self.to_change(data)
        self.history.do(change)
        self.assertTrue(myfile.exists())
        self.history.undo()
        self.assertFalse(myfile.exists())

    def test_create_folder_saving(self):
        myfolder = self.project.get_folder('myfolder')
        data = self.to_data(CreateFolder(self.project.root, 'myfolder'))
        change = self.to_change(data)
        self.history.do(change)
        self.assertTrue(myfolder.exists())
        self.history.undo()
        self.assertFalse(myfolder.exists())

    def test_create_resource_saving(self):
        myfile = self.project.get_file('myfile.txt')
        data = self.to_data(CreateResource(myfile))
        change = self.to_change(data)
        self.history.do(change)
        self.assertTrue(myfile.exists())
        self.history.undo()
        self.assertFalse(myfile.exists())

    def test_remove_resource_saving(self):
        myfile = self.project.root.create_file('myfile.txt')
        data = self.to_data(RemoveResource(myfile))
        change = self.to_change(data)
        self.history.do(change)
        self.assertFalse(myfile.exists())

    def test_change_set_saving(self):
        change = ChangeSet('testing')
        myfile = self.project.get_file('myfile.txt')
        change.add_change(CreateResource(myfile))
        change.add_change(ChangeContents(myfile, '1'))

        data = self.to_data(change)
        change = self.to_change(data)
        self.history.do(change)
        self.assertEquals('1', myfile.read())
        self.history.undo()
        self.assertFalse(myfile.exists())

    def test_writing_and_reading_history(self):
        history_file = self.project.get_file('history.pickle')
        self.project.set('save_history', True)
        history = rope.base.history.History(self.project)
        myfile = self.project.get_file('myfile.txt')
        history.do(CreateResource(myfile))
        history.write()

        history = rope.base.history.History(self.project)
        history.undo()
        self.assertFalse(myfile.exists())

    def test_writing_and_reading_history2(self):
        history_file = self.project.get_file('history.pickle')
        self.project.set('save_history', True)
        history = rope.base.history.History(self.project)
        myfile = self.project.get_file('myfile.txt')
        history.do(CreateResource(myfile))
        history.undo()
        history.write()

        history = rope.base.history.History(self.project)
        history.redo()
        self.assertTrue(myfile.exists())


def suite():
    result = unittest.TestSuite()
    result.addTests(unittest.makeSuite(HistoryTest))
    result.addTests(unittest.makeSuite(IsolatedHistoryTest))
    result.addTests(unittest.makeSuite(SavingHistoryTest))
    return result

if __name__ == '__main__':
    unittest.main()
