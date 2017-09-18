import sublime, sublime_plugin
import json
import os
import subprocess

class OpenFilesCommand(sublime_plugin.WindowCommand):
    view_quick_panel = None
    active = False
    active_menu = False
    active_list = False
    view_bookmarks, view_file_history, view_folder_history = None, None, None
    actions_folder = ["Open Folder in Explorer", "Copy Path to Clipboard",
                      "Copy Folder Name to Clipboard", "New File in This Folder"]
    actions_file = ["Copy File Path to Clipboard", "Copy File Name to Clipboard",
                    "Open with Application"]

    @classmethod
    def reset(cls):
        cls.active = False

    def __init__(self, window):
        super(OpenFilesCommand, self).__init__(window)
        # risky? API may not be ready at initial time?
        self.s = sublime.load_settings("OpenFiles.sublime-settings")

    def run(self, path = None, ignore = True, list_type = None, key = None):
        self.set_items(path, ignore, list_type, key)
        # type(self).active = True
        if not key:
            self.open(ignore, list_type)
        elif key == "right":
            self.choose_menu(list_type)
        elif key == "left":
            self.backward(list_type)
        elif key == "tab":
            self.show_hidden_files()
        else:
            pass

    def open(self, ignore = True, list_type = None):
        if not list_type:
            type(self).active = True
        elif list_type in ("bookmarks", "file_history", "folder_history"):
            type(self).active_list = list_type
        else:
            sublime.error_message('Wrong type list: {}'.format(list_type))
        self.window.show_quick_panel(self.names_entries, 
                                     lambda i: self.on_done_open(i, ignore),
                                     sublime.MONOSPACE_FONT, 0, 
                                     self.on_highlighted)

    def choose_menu(self, list_type):
        self.window.run_command("hide_overlay")
        type(self).active_menu = True
        # must after command "hide_overlay"
        if not list_type:
            type(self).active = True
        else:
            type(self).active_list = list_type
        full_path = self.paths_entries[self.index_highlighted]
        if os.path.isfile(full_path):
            actions_list = [
                [action, full_path] for action in type(self).actions_file]
            on_done = self.act_file
        elif os.path.isdir(full_path):
            actions_list = [
                [action, full_path] for action in type(self).actions_folder]
            on_done = self.act_folder
        else:
            sublime.error_message(
                "{} is not a file or folder!".format(full_path))

        self.window.show_quick_panel(actions_list, on_done, 
                                     sublime.MONOSPACE_FONT,
                                     0, None)

    def act_folder(self, index):
        type(self).active_menu = False
        full_path = self.paths_entries[self.index_highlighted]
        if not os.path.isdir(full_path):
            sublime.error_message('"{}" is not a folder!'.format(full_path))
        if index == 0:
            # for windows
            full_path = full_path.replace("/", "\\")
            subprocess.call(["explorer", full_path])
        elif index == 1:
            sublime.set_clipboard(full_path)
        elif index == 2:
            sublime.set_clipboard(os.path.basename(full_path))
        elif index == 3:
            # TODO:
            print("TODO: create file.")
        else:
            type(self).reset()
            # type(self).view_quick_panel = None

    def act_file(self, index):
        type(self).active_menu = False
        full_path = self.paths_entries[self.index_highlighted]
        if not os.path.isfile(full_path):
            sublime.error_message('"{}" is a not a file!'.format(full_path))
        if index == 0:
            sublime.set_clipboard(full_path)
        elif index == 1:
            sublime.set_clipboard(os.path.basename(full_path))
        elif index == 2:
            # TODO
            print("TODO: open it with application.")
        else:
            type(self).reset()
            # type(self).view_quick_panel = None

    def backward(self, list_type = None):
        self.window.run_command("hide_overlay")
        type(self).active = True
        if not list_type:
            if type(self).active_menu:
                self.window.run_command(
                    "open_files", {"path": self.paths_entries[1]})
            else:
                self.window.run_command(
                    "open_files", {"path": self.paths_entries[0]})
        elif list_type in ("bookmarks", "file_history", "folder_history"):
            self.window.run_command("open_files", {"list_type": list_type})
    def show_hidden_files(self):
        self.window.run_command("hide_overlay")
        if not type(self).active_menu:
            self.window.run_command(
                "open_files", 
                {"path": self.paths_entries[1], "ignore": False, })
        pass

    def on_done_open(self, index, ignore = True):
        if index == -1:
            # can not do this, otherwise left/right key does not work.
            # type(self).view_quick_panel = None
            return
        full_path = self.paths_entries[index]
        if os.path.isfile(full_path):
            self.window.open_file(full_path)
        elif os.path.isdir(full_path):
            self.window.run_command(
                "open_files", {"path": full_path, "ignore": ignore})
        else:
            sublime.error_message('{} does not exist!'.format(full_path))

    def on_highlighted(self, index):
        self.index_highlighted = index

    def set_items(self, path = None, ignore = True, list_type = None, key = None):
        # does not set item, 
        # so that backward action can work when pressing left several times
        if key:
            return
        if not list_type:
            self.set_items_current_folder(path, ignore)
        elif list_type == "bookmarks":
            self.set_items_bookmarks()
        elif list_type in ("file_history", "folder_history"):
            self.set_items_history(list_type)
        else:
            sublime.error_message("Wrong list type: {}".format(list_type))

    def set_items_current_folder(self, path, ignore = True):
        if not path:
            view = self.window.active_view()
            file_name = view.file_name()
            if file_name:
                path = os.path.dirname(file_name)
            else:
                sublime.error_message("This file does not exist in disk!")
        path_parent = os.path.dirname(path)
        entries = os.listdir(path)
        paths_entries = [os.path.join(path, entry) for entry in entries]
        paths_files = [path for path in paths_entries if os.path.isfile(path)]
        paths_folders = list(set(paths_entries) - set(paths_files))
        
        if ignore:
            ignored_files_exts = tuple(self.s.get("ignored_files_exts", ()))
            paths_files = [path for path in paths_files 
                           if not path.endswith(ignored_files_exts)]
        self.names_entries = ["..", "."] + \
            [os.path.basename(entry) + "/" for entry in paths_folders] + \
            [os.path.basename(entry) for entry in paths_files]
        self.paths_entries = [path_parent, path] + paths_folders + paths_files

    def set_items_bookmarks(self):
        bookmarks = self.s.get("bookmarks", [])
        if bookmarks:
            pkgs_path = sublime.packages_path()
            bookmarks = [bm if os.path.isabs(bm) else 
                os.path.join(pkgs_path, bm) for bm in bookmarks]
            self.paths_entries = bookmarks
            self.names_entries = [[os.path.basename(bm), os.path.dirname(bm)]
                                  for bm in bookmarks]
        else:
            sublime.error_message("No bookmarks. Please add it")

    def set_items_history(self, list_type):
        # for portable version
        path_data = os.path.dirname(sublime.packages_path())
        path_session = os.path.join(
            path_data, "Local", "Session.sublime_session")
        with open(path_session, encoding = "utf-8") as file:
            session = json.load(file)
        if list_type == "file_history":
            paths_list = session["settings"]["new_window_settings"]["file_history"]
        elif list_type == "folder_history":
            paths_list = session["folder_history"]
        else:
            sublime.error_message("Wrong list type: {}".format(list_type))
        if not paths_list:
            sublime.error_message("Empty file or folder history!")
        paths_list = [path[1] + ":" + path[2:] for path in paths_list]
        paths_list = [path for path in paths_list if os.path.exists(path)]
        max_history = self.s.get("max_history", 15)
        paths_list = paths_list[0: min(len(paths_list), max_history)]
        self.paths_entries = paths_list
        self.names_entries = [[os.path.basename(path), os.path.dirname(path)]
                              for path in paths_list]

class OpenFilesListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        # Is buffer id unique for input panel and find panel?
        # Input panel and find panel also have (-1, -1)
        if (view.window().get_view_index(view) == (-1, -1)
                and OpenFilesCommand.active):
            OpenFilesCommand.view_quick_panel = view
        else:
            OpenFilesCommand.reset()
            OpenFilesCommand.view_quick_panel = None
        # redundant?
        if view.window().get_view_index(view) != (-1, -1):
            OpenFilesCommand.active_list = False
            OpenFilesCommand.view_bookmarks = None
            OpenFilesCommand.view_file_history = None
            OpenFilesCommand.view_folder_history = None
        else:
            if OpenFilesCommand.active_list == "bookmarks":
                OpenFilesCommand.view_bookmarks = view
            else:
                OpenFilesCommand.view_bookmarks = None
            if OpenFilesCommand.active_list == "file_history":
                OpenFilesCommand.view_file_history = view
            else:
                OpenFilesCommand.view_file_history = None
            if OpenFilesCommand.active_list == "folder_history":
                OpenFilesCommand.view_folder_history = view
            else:
                OpenFilesCommand.view_folder_history = None
        

    def on_query_context(self, view, key, operator, operand, match_all):
        if view == OpenFilesCommand.view_quick_panel:
            if (key == "open_files_choose_menu" 
                    and not OpenFilesCommand.active_menu):
                return True
            elif key == "open_files_backward":
                return True
            elif (key == "open_files_show_hidden_files"
                    and not OpenFilesCommand.active_menu):
                return True
        if view == OpenFilesCommand.view_bookmarks:
            if key == "open_bookmarks_backward":
                return True
            if key == "open_bookmarks_choose_menu":
                return True
        if view == OpenFilesCommand.view_file_history:
            if key == "open_file_history_backward":
                return True
            if key == "open_file_history_choose_menu":
                return True
        if view == OpenFilesCommand.view_folder_history:
            if key == "open_folder_history_backward":
                return True
            if key == "open_folder_history_choose_menu":
                return True
        return None