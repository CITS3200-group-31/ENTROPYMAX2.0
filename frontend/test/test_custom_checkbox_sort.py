"""
Test script to verify custom checkbox column sorting
"""
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import sys


class CustomSortTreeWidgetItem(QTreeWidgetItem):
    """Custom QTreeWidgetItem with sorting support for checkbox column."""
    
    def __lt__(self, other):
        """Custom comparison for sorting.
        
        Column 0 (checkbox): Checked items appear first
        Other columns: Default string/numeric comparison
        """
        column = self.treeWidget().sortColumn()
        
        if column == 0:  # Checkbox column
            # Get check states
            self_checked = self.checkState(0) == Qt.CheckState.Checked
            other_checked = other.checkState(0) == Qt.CheckState.Checked
            
            # If same state, maintain stable order
            if self_checked == other_checked:
                return False
            
            # Checked items should appear first (be "less than" unchecked)
            return self_checked > other_checked
        
        # For other columns, use default comparison
        return super().__lt__(other)


def main():
    app = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    tree = QTreeWidget()
    tree.setHeaderLabels(['✓', 'Sample', 'Value'])
    tree.setSortingEnabled(True)
    
    # Add some items with different check states
    samples = [
        ("A211", True, 100),
        ("A201", True, 90),
        ("A413", False, 80),
        ("Para", False, 70),
        ("A710", False, 60),
        ("A516", True, 50),
    ]
    
    for name, checked, value in samples:
        item = CustomSortTreeWidgetItem()  # Using custom item
        item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        item.setText(1, name)
        item.setText(2, str(value))
        tree.addTopLevelItem(item)
    
    layout.addWidget(tree)
    
    # Print current order
    print("\n=== Initial Order ===")
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        checked = item.checkState(0) == Qt.CheckState.Checked
        print(f"{i}: {item.text(1)} - Checked: {checked}")
    
    # Sort by checkbox column (ascending - checked first)
    tree.sortItems(0, Qt.SortOrder.AscendingOrder)
    print("\n=== After sorting column 0 ASCENDING (Checked first) ===")
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        checked = item.checkState(0) == Qt.CheckState.Checked
        print(f"{i}: {item.text(1)} - Checked: {checked}")
    
    # Sort by checkbox column (descending - unchecked first)
    tree.sortItems(0, Qt.SortOrder.DescendingOrder)
    print("\n=== After sorting column 0 DESCENDING (Unchecked first) ===")
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        checked = item.checkState(0) == Qt.CheckState.Checked
        print(f"{i}: {item.text(1)} - Checked: {checked}")
    
    # Sort by name
    tree.sortItems(1, Qt.SortOrder.AscendingOrder)
    print("\n=== After sorting by Name (column 1) ===")
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        checked = item.checkState(0) == Qt.CheckState.Checked
        print(f"{i}: {item.text(1)} - Checked: {checked}")
    
    window.resize(400, 300)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
