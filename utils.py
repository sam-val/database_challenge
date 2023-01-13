class Security:
    _node_keywords_map = {
        "encrypt": [
            [
                "fullname",
                "full_name",
                "surname",
                "email",
                "location",
                "home_address",
                "house_address",
                "address",
                "ip_address",
                "username",
                "user_name",
            ],
            [
                "name",
                "contact",
                "date",
                "code",
                "address",
                "house",
                "ip",
                "street",
            ],
        ],
        "hash": [
            ["password", "login_password", "reset_code"],
            ["pass", "security", "login", "code"],
        ],
        "mask": [
            ["credit_card", "credit_card_number", "payment_details"],
            ["payment", "number", "code", "bill"],
        ],
    }

    def __init__(self, column_name, table_name):
        self.column_name = column_name
        self.table_name = table_name

    def predict_node(self):
        for node, keywords in self._node_keywords_map.items():
            # absolute clear keywords:
            if self.column_name.lower() in keywords[0]:
                return node

            is_passed = {
                self.column_name: False,
                self.table_name: False,
            }
            for small_keyword in keywords[1]:
                if small_keyword in self.column_name:
                    is_passed[self.column_name] = True
                if small_keyword in self.table_name:
                    is_passed[self.table_name] = True

            if all(is_passed.values()):
                return node

        return None
