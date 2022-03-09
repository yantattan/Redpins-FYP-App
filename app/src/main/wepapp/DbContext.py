import mysql.connector as m


class MySql:
    msg = ""

    try:
        @staticmethod
        def Connect():
            con = m.connect(
                host="localhost",
                user="root",
                password="P@ssw0rd",
                database="RedpinsDB"
            )

            if con.is_connected():
                msg = "DB Connected"
                return con

    except Exception as e:
        MySql.msg = e

    @staticmethod
    def Close(self, con):
        con.Close()


MySql.Connect()
print(MySql.msg)
