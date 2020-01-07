import cutter
import yara

from PySide2.QtCore import QObject, SIGNAL
from PySide2.QtWidgets import QAction, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView

class YaraDockWidget(cutter.CutterDockWidget):
    rule_filename = ''
    rule_basedir = 'rules'
    rules_changed = False
    def __init__(self, parent, action):
        """Initializes the widget gui."""
        super(YaraDockWidget, self).__init__(parent, action)
        self.setObjectName('Yara')
        self.setWindowTitle('Yara')

        self.table = QTableWidget(self)
        self.table.setShowGrid(False)
        self.table.verticalHeader().hide()


        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(['File Offset', 'String Content', 'Rule', 'Filename'])
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.setWidget(self.table)

        cutter.core().seekChanged.connect(self.update_contents)
        self.update_contents()


    def update_contents(self):
        """Scans the file with YARA rules from ./rules directory."""
        if not(self.rules_changed):
            self.table.setRowCount(0)
            filename = self.get_filename()
            try:
                import glob, os
                rules = [f for f in glob.glob('%s\\%s\\*.yar' % (os.path.dirname(os.path.abspath(__file__)), self.rule_basedir))]
                for rule in rules:
                    rules = yara.compile(rule)
                    self.rule_filename = rule.rsplit('\\', 1)[1]
                    rules.match(filename, callback=self.mycallback)
                self.rules_changed = True
            except Exception as e:
                pass

    def get_filename(self):
        """Returns working project from Cutter pipe."""
        binary_information = cutter.cmdj('ij')
        filename = binary_information['core']['file']
        return filename

    def mycallback(self, data):
        """Populates the table with matching YARA rules."""
        if(data['matches']):
            for string in data['strings']:

                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                self.table.setItem(row_position, 0, QTableWidgetItem(str(string[0])))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(string[2])))
                self.table.setItem(row_position, 2, QTableWidgetItem(data['rule']))
                self.table.setItem(row_position, 3, QTableWidgetItem(self.rule_filename))

        yara.CALLBACK_CONTINUE


class MyCutterPlugin(cutter.CutterPlugin):
    name = 'Yara'
    description = 'Scan your Cutter project with Yara rules'
    version = '1.0'
    author = 'Jannis Kirschner'

    def setupPlugin(self):
        pass

    def setupInterface(self, main):
        action = QAction('Yara', main)
        action.setCheckable(True)
        widget = YaraDockWidget(main, action)
        main.addPluginDockWidget(widget, action)

    def terminate(self):
        pass

def create_cutter_plugin():
    return MyCutterPlugin()
