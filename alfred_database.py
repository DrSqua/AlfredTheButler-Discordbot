import sqlite3
import pandas as pd
from alfred_repyclass import AlfredReply
from alfred_repyclass import AlfredCC


def create_db(dbname):
    # Maakt Database aan + De Table
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    c = database.cursor()
    with database:
        c.execute("""CREATE TABLE AlfredKeys (
                        KeyIndex INTEGER NOT NULL PRIMARY KEY,
                        KeyValueID INTEGER, 
                        Message VARCHAR(255)
                        )""")
        c.execute("""CREATE TABLE AlfredAnswers (
                        ValueIndex INTEGER NOT NULL PRIMARY KEY,
                        KeyValueID INTEGER, 
                        Message VARCHAR(255),
                        Filepath TEXT,
                        Reply INTEGER,
                        MentionAuthor INTEGER,
                        EndConvo INTEGER,
                        FOREIGN KEY(KeyValueID) REFERENCES AlfredKeys(KeyValueID)
                        )""")
        c.execute("""CREATE TABLE GenericKeys (
                        KeyIndex INTEGER NOT NULL PRIMARY KEY,
                        KeyValueID INTEGER, 
                        Message VARCHAR(255)
                        )""")
        c.execute("""CREATE TABLE GenericAnswers (
                        ValueIndex INTEGER NOT NULL PRIMARY KEY,
                        KeyValueID INTEGER, 
                        Message VARCHAR(255),
                        Filepath TEXT,
                        Reply INTEGER,
                        MentionAuthor INTEGER,
                        FOREIGN KEY(KeyValueID) REFERENCES GenericKeys(KeyValueID)
                        )""")
        c.execute("""CREATE TABLE cc (
                        KeyIndex INTEGER NOT NULL PRIMARY KEY,
                        Message VARCHAR(255),
                        KeyValueID INTEGER, 
                        Function TEXT,
                        FOREIGN KEY(KeyValueID) REFERENCES AlfredAnswers(KeyValueID)
                        )""")


def refill_table(dbname, file):  # Takes database (Db-Input.xlsx)
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    c = database.cursor()
    with database:
        c.execute("""DELETE FROM AlfredKeys""")
        c.execute("""DELETE FROM AlfredAnswers""")
        c.execute("""DELETE FROM GenericKeys""")
        c.execute("""DELETE FROM GenericAnswers""")
        c.execute("""DELETE FROM cc""")
    xlsx_to_db(dbname, file)
    print("Refilled tables")


def insert_single(dbname):  # for testing
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    c = database.cursor()
    with database:
        c.execute("""INSERT INTO AlfredKeys (KeyValueID, Message) VALUES(:KeyValueID, :Message)
        """, {"KeyValueID": 2, "Message": "ty"})
    with database:
        c.execute("""INSERT INTO AlfredAnswers (KeyValueID, Message, Filepath, Reply, Mentionauthor) 
        VALUES(:KeyValueID, :Message, :Filepath, :Reply, :Mentionauthor :EndConvo)
                  """,
                  {"KeyValueID": 2, "Message": "My Pleasure Sir", "Filepath": "Geen", "Reply": 1, "Mentionauthor": 0,
                   "EndConvo": 1})


def xlsx_to_db(dbname, file):
    alfredkey_panda = pd.read_excel(file, "AlfredKey", engine="openpyxl", index_col=1)
    alfredvalue_panda = pd.read_excel(file, "AlfredValue", engine="openpyxl", index_col=1)
    generickey_panda = pd.read_excel(file, "GenericKey", engine="openpyxl", index_col=1)
    genericvalue_panda = pd.read_excel(file, "GenericValue", engine="openpyxl", index_col=1)
    cc_panda = pd.read_excel(file, "cc", engine="openpyxl", index_col=1)

    alfredkey_panda = alfredkey_panda[alfredkey_panda.columns[:2]]
    generickey_panda = generickey_panda[generickey_panda.columns[:2]]
    alfredvalue_panda = alfredvalue_panda[alfredvalue_panda.columns[:6]]
    genericvalue_panda = genericvalue_panda[genericvalue_panda.columns[:5]]
    cc_panda = cc_panda[cc_panda.columns[:3]]

    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    alfredkey_panda.to_sql("AlfredKeys", database, if_exists="append")
    alfredvalue_panda.to_sql("AlfredAnswers", database, if_exists="append")
    generickey_panda.to_sql("GenericKeys", database, if_exists="append")
    genericvalue_panda.to_sql("GenericAnswers", database, if_exists="append")
    cc_panda.to_sql("cc", database, if_exists="append")


def select_by_keyvalueid(dbname, table, keyvalueid):
    """set{key1, key2}:set{value1, value2}"""
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'

    key_panda = pd.read_sql_query("""SELECT * From """ + table + """Keys WHERE KeyValueID =:KeyValueID""", database,
                                  None,
                                  params={"KeyValueID": keyvalueid})
    keys = key_panda["Message"].values
    value_panda = pd.read_sql_query("""SELECT * From """ + table + """Answers WHERE KeyValueID =:KeyValueID""",
                                    database, None,
                                    params={"KeyValueID": keyvalueid})
    values = []
    if table == "Generic":
        for index, row in value_panda.iterrows():
            values.append(AlfredReply(message=row["Message"], file=row["Filepath"], reply=row["Reply"],
                                      mentionauthor=row["MentionAuthor"], endconvo=False))
    elif table == "Alfred":
        for index, row in value_panda.iterrows():
            values.append(AlfredReply(message=row["Message"], file=row["Filepath"], reply=row["Reply"],
                                      mentionauthor=row["MentionAuthor"], endconvo=row["EndConvo"]))
    return tuple(keys), tuple(values)


def select_by_index(dbname, index):
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    key_panda = pd.read_sql_query("""SELECT Message, Function FROM cc WHERE KeyIndex =:Index""",
                                  database, None,
                                  params={"Index": index})
    value_panda = pd.read_sql_query("""SELECT cc.Function, aa.Message, aa.Filepath, aa.Reply, aa.MentionAuthor,
                                                aa.EndConvo 
                                FROM cc LEFT JOIN AlfredAnswers aa ON cc.KeyValueID = aa.KeyValueID 
                                WHERE cc.KeyIndex =:Index""",
                                    database, None,
                                    params={"Index": index})
    keys = key_panda["Message"][0], key_panda["Function"][0]
    values = []
    for index, row in value_panda.iterrows():
        values.append(AlfredReply(message=row["Message"], file=row["Filepath"], reply=row["Reply"],
                                  mentionauthor=row["MentionAuthor"], endconvo=row["EndConvo"]))
    cc = (AlfredCC(function=keys[1], messages=values),)
    return (keys[0],), cc


def load_dictionary(dbname, table):  # Table = "Generic", "Alfred", "cc"
    database = sqlite3.connect(dbname)  # ':memory:' als test # Anders 'database.db'
    c = database.cursor()
    autorespond_dict = {}
    if table == "cc":
        with database:
            c.execute("""SELECT MAX(KeyIndex) FROM """ + table)
            max_index = c.fetchall()[0][0]
        for index in range(1, max_index + 1):
            key, value = select_by_index(dbname, index)
            autorespond_dict[key] = value
    else:
        with database:
            c.execute("""SELECT MAX(KeyValueID) FROM """ + table + """Keys""")
            max_keyvalueid = c.fetchall()[0][0]
        for keyvalueid in range(1, max_keyvalueid + 1):
            key, value = select_by_keyvalueid(dbname, table, keyvalueid)
            autorespond_dict[key] = value
    return autorespond_dict


def main():
    dbname = "alfred_response-database.db"
    xlsx = "Db-Input.xlsx"
    # create_db(dbname)

    # insert_single(dbname)

    refill_table(dbname, xlsx)
    cc = load_dictionary(dbname, "Alfred")
    #print(cc)
    item = list(cc.values())[2]
    #print(item.check_reply()[0])


if __name__ == '__main__':
    main()
