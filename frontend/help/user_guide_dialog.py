"""



Help - CSV Format Examples


Shows format examples for GPS and Grain Size CSV files.


"""





from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit)


from PyQt6.QtCore import Qt








class UsageGuideDialog(QDialog):


    """Dialog showing user guide and flow examples."""


    


    def __init__(self, parent=None):


        super().__init__(parent)


        self.setWindowTitle("User Guide and Flow")


        self.setModal(True)


        self.setFixedSize(1000, 1000)


        self.setStyleSheet("""


            QDialog {


                background-color: #f8f9fa;


            }


        """)


        self._setup_ui()


        


    def _setup_ui(self):


        """Setup the dialog UI."""


        layout = QVBoxLayout(self)


        layout.setSpacing(15)


        layout.setContentsMargins(20, 20, 20, 20)


        


        # Step 1 Section


        stepone = QLabel("Step 1")


        stepone.setStyleSheet("""


            font-size: 16px;


            font-weight: 600;


            color: #009688;


            margin-top: 5px;


            margin-bottom: 5px;


        """)


        layout.addWidget(stepone)


        


        stepone = QTextEdit()


        stepone.setReadOnly(True)


        stepone.setPlainText(


            """Select Input CSV: Press button and navigate to the appropriate CSV file.


            Select GPS CSV: Press button and navigate to the appropriate CSV file.


            For help on what these should look like, please refer to:


            Help > Format Examples"""


        )


        stepone.setFixedHeight(100)  # Fixed height to show all content


        stepone.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepone.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepone.setStyleSheet("""


            QTextEdit {


                background-color: #ffffff;


                border: 1px solid #e0e0e0;


                border-radius: 6px;


                padding: 12px;


                font-family: 'Courier New', monospace;


                font-size: 13px;


                color: #2c3e50;


                line-height: 1.5;


            }


        """)


        layout.addWidget(stepone)





        # Step 2 Section


        steptwo = QLabel("Step 2")


        steptwo.setStyleSheet("""


            font-size: 16px;


            font-weight: 600;


            color: #009688;


            margin-top: 5px;


            margin-bottom: 5px;


        """)


        layout.addWidget(steptwo)


        


        steptwo = QTextEdit()


        steptwo.setReadOnly(True)


        steptwo.setPlainText(


            """Check boxes on whether you require Permutations and Row Proportions


            Input the minimum and maximum group numberings, 


            if no input: it automatically makes Min = 2; Max = 20;


            """


        )


        steptwo.setFixedHeight(75)  # Fixed height to show all content


        steptwo.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        steptwo.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        steptwo.setStyleSheet("""


            QTextEdit {


                background-color: #ffffff;


                border: 1px solid #e0e0e0;


                border-radius: 6px;


                padding: 12px;


                font-family: 'Courier New', monospace;


                font-size: 13px;


                color: #2c3e50;


                line-height: 1.5;


            }


        """)


        layout.addWidget(steptwo)





        # Step 3 Section


        stepthree = QLabel("Step 3")


        stepthree.setStyleSheet("""


            font-size: 16px;


            font-weight: 600;


            color: #009688;


            margin-top: 5px;


            margin-bottom: 5px;


        """)


        layout.addWidget(stepthree)


        


        stepthree = QTextEdit()


        stepthree.setReadOnly(True)


        stepthree.setPlainText(


            """Simply press:


            Step 3: Run Analysis


            and wait for the loading bar, it will say your optimal


            grouping value in the status bar at the bottom of the window.


            """


        )


        stepthree.setFixedHeight(100)  # Fixed height to show all content


        stepthree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepthree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepthree.setStyleSheet("""


            QTextEdit {


                background-color: #ffffff;


                border: 1px solid #e0e0e0;


                border-radius: 6px;


                padding: 12px;


                font-family: 'Courier New', monospace;


                font-size: 13px;


                color: #2c3e50;


                line-height: 1.5;


            }


        """)


        layout.addWidget(stepthree)


        


        # Step 4 Section


        stepfour = QLabel("Step 4")


        stepfour.setStyleSheet("""


            font-size: 16px;


            font-weight: 600;


            color: #009688;


            margin-top: 5px;


            margin-bottom: 5px;


        """)


        layout.addWidget(stepfour)


        


        stepfour = QTextEdit()


        stepfour.setReadOnly(True)


        stepfour.setPlainText(


            """Simply press:


            Step 4: Show Map View


            You are now able to open the map & sample list window.


            Further, if you open the CH analysis or Rs analysis windows,


            you can click on a different K/Grouping value that will reflect


            in the group numbers shown in the map & sample list.


            """


        )


        stepfour.setFixedHeight(150)  # Fixed height to show all content


        stepfour.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepfour.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepfour.setStyleSheet("""


            QTextEdit {


                background-color: #ffffff;


                border: 1px solid #e0e0e0;


                border-radius: 6px;


                padding: 12px;


                font-family: 'Courier New', monospace;


                font-size: 13px;


                color: #2c3e50;


                line-height: 1.5;


            }


        """)


        layout.addWidget(stepfour)





        # Step 5 Section


        stepfive = QLabel("Step 5")


        stepfive.setStyleSheet("""


            font-size: 16px;


            font-weight: 600;


            color: #009688;


            margin-top: 5px;


            margin-bottom: 5px;


        """)


        layout.addWidget(stepfive)


        


        stepfive = QTextEdit()


        stepfive.setReadOnly(True)


        stepfive.setPlainText(


            """Simply press:


            Step 5: Export Results


            You can now save the data as a .CSV, implementing the old Entropy


            Max program. Note: it can not be saved in the program folder! Further,


            if you would like to save as .KML or a .PNG, please go to map window 


            and click on the buttons at the top of the window.


            """


        )


        stepfive.setFixedHeight(150)  # Fixed height to show all content


        stepfive.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepfive.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        stepfive.setStyleSheet("""


            QTextEdit {


                background-color: #ffffff;


                border: 1px solid #e0e0e0;


                border-radius: 6px;


                padding: 12px;


                font-family: 'Courier New', monospace;


                font-size: 13px;


                color: #2c3e50;


                line-height: 1.5;


            }


        """)


        layout.addWidget(stepfive)


        


        


        # Add stretch to push content to top


        layout.addStretch()