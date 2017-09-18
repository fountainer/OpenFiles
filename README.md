### Usage

- Press `ctrl+shift+o` to display the files and folders in current 
folder on the quick panel. 
- Press `ctrl+shift+alt+o` to display all the files (including igored files)
and folders.
- Press `ctrl+alt+b` to display the bookmarks which can be set in the settings.
- Press `right` key on the quick panel to choose action. Current 
actions include "Open in Explorer", "Copy Path to Clipboard", "Copy Name
to Clipboard" and "Open in Application". Open pdf files and Excel files.
- Press `left` key on the quick panel to navigate back to file list when
in menu list, back to parent directory when in file list.
- Press `ctrl+alt+b` to show bookmarked folders in quick panel. Support 
`left` and `right` key.
- Press `tab` key on the quick panel to show hidden files.
- Press `ctrl+alt+h` to show recent files
- Press `ctrl+shift+alt+h` to show recent folders.


### ToDO

- Create new file/folder in right key actions.
- Use [send2trash](https://github.com/hsoft/send2trash/blob/master/send2trash/plat_win.py)
- Make it work for linux.
- More `right` key actions.
- The file and folder history is not good enough. Save recent files/folders list.
- [Sublime Files](https://packagecontrol.io/packages/Sublime%20Files)
- [File navigator](https://packagecontrol.io/packages/File%20Navigator)

### Bugs

When console panel / find panel / input panel is open, open quick panel and 
then cancel it, move cursor to the console panel, press right key and show the
right key actions. Try to fix it but not injuring other functionalities.