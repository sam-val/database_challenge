import time
from collections import namedtuple
from xml.dom import minidom

from db import Database
from utils import Security

type_map = {
    "VARCHAR": "string",
    "VARBINARY": "binary",
    "TINYINT": "byte",
    "TIMESTAMP": "timestamp",
    "TIME": "date",
    "SMALLINT": "short",
    "REAL": "double",
    "NUMERIC": "double",
    "LONGVARCHAR": "string",
    "JAVA_OBJECT": "object",
    "INTEGER": "int",
    "FLOAT": "float",
    "DOUBLE": "double",
    "DECIMAL": "big_decimal",
    "DATE": "date",
    "CLOB": "string",
    "CHAR": "string",
    "BOOLEAN": "boolean",
    "BLOB": "binary",
    "BIT": "byte",
    "BINARY": "binary",
    "BIGINT": "big_integer",
}

postgres_type_to_jdbc = {
    "bool": "BIT",
    "bit": "BIT",
    "int8": "BIGINT",
    "serial": "INTEGER",
    "char": "CHAR",
    "bpchar": "CHAR",
    "bigserial": "BIGINT",
    "oid": "BIGINT",
    "bytea": "BINARY",
    "numeric": "NUMERIC",
    "int4": "INTEGER",
    "int2": "SMALLINT",
    "smallserial": "SMALLINT",
    "float4": "REAL",
    "float8": "DOUBLE",
    "money": "DOUBLE",
    "name": "VARCHAR",
    "text": "VARCHAR",
    "varchar": "VARCHAR",
    "date": "DATE",
    "time": "TIME",
    "timetz": "TIME",
    "timestamp": "TIMESTAMP",
    "timestamptz": "TIMESTAMP",
}

if __name__ == "__main__":
    xml_root = minidom.Document()
    printable_xml_nodes = []
    tables_with_references = {}
    tables_with_references_xml = {}
    with Database() as db:
        tables = db.get_tables()
        for table in tables:
            # table node
            table_name = table[2]
            generate_node = xml_root.createElement('generate')
            generate_node.setAttribute("type", table_name)

            primary_key_column_names = [x[3] for x in db.get_primary_keys(table_name)]
            foreign_keys = db.get_foreign_keys(table_name)
            ConstraintsStat = namedtuple("ConstraintsStat", "pktable pkcolumn") 
            constraints_stats = {x[7]:ConstraintsStat(x[2], x[3]) for x in foreign_keys}
            if foreign_keys:
                tables_with_references[table_name] = {x[2] for x in foreign_keys}

            column_data = db.get_column_data(table_name)
            for column in column_data:
                column_name = column[3]
                postgres_type = column[5]
                type_name = type_map[postgres_type_to_jdbc[postgres_type]]
                attributes = {
                    "type": type_name,
                    "name": column_name,
                }
                # node cases for column 
                if column_name in primary_key_column_names:
                    element = "id"
                elif column_name in constraints_stats.keys():
                    element = "reference"
                    fkStats = constraints_stats[column_name]
                    pktable, pkcolumn = fkStats.pktable, fkStats.pkcolumn
                    attributes["selector"] = f"select {pkcolumn} from {pktable}"
                    attributes["distribution"] = "random"
                else:
                    element = "attribute"
                    security = Security(column_name=column_name, table_name=table_name)
                    security_node = security.predict_node()
                    if security_node:
                        element = security_node

                column_node = xml_root.createElement(element)
                for k, v in attributes.items():
                    column_node.setAttribute(k, v)
                generate_node.appendChild(column_node)

            if table_name not in tables_with_references:
                printable_xml_nodes.append(generate_node)
            else:
                tables_with_references_xml[table_name] = generate_node
        
        # remove table from table_with_references in the order of printability:
        while len(tables_with_references) != 0:
            for table, referenced_tables in tables_with_references.items():
                ready_to_print = True
                for ref_table in referenced_tables:
                    if ref_table in tables_with_references.keys():
                        # case table references itself
                        if ref_table != table:
                            ready_to_print = False

                if ready_to_print:
                    tables_with_references.pop(table)
                    printable_xml_nodes.append(tables_with_references_xml[table])
                    break

    # write to file
    file_name = str(int(time.time())) + ".xml"
    with open(file_name, "w") as f:
        for node in printable_xml_nodes:
            f.write(node.toprettyxml(indent='\t'))
