from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import pandas as pd

def create_kml(file_name, k_value, group_number, output_file_name):
    '''
    creates kml with data assuming chosen k value
        file_name = input file_name
        k_value = k value to show in kml file
        group_number = group number to show, 0 to show all in k
    '''
    df = pd.read_parquet(file_name, filters=[('K', '=', k_value)])
    # checks if group number needs to be filtered
    if group_number != 0:
        df = df[df['Group'] == group_number]
    # initialise document
    doc = KML.kml(KML.Document())
    # iterate through dataframe, adding each to the document
    for index, row in df.iterrows():
        placemark = KML.Placemark(
            KML.name(row["Sample"]),
            KML.description("group number : %i" %(row["Group"])),
            KML.Point(
                KML.coordinates("%f,%f,0" %(row["longitude"], row["latitude"]))
            )
        )
        doc.Document.append(placemark)

    # converting to string to then write to the file
    kml_string = etree.tostring(doc, pretty_print = True).decode('utf-8')
    with open("%s.kml" %(output_file_name), "w") as file:
        file.write(kml_string)

#create_kml("frontend/utils/sample-output-augmented.parquet", 6, 0, "test")