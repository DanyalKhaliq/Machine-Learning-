import re

class Helper:

    @staticmethod

    def clean_number(string):
        """String cleaning"""
        pattern = re.compile(r"(\s)|(,)|(\.)|(-)")
        string = re.sub(pattern, "", string)
        return string


    @staticmethod
    def is_int(string):
        """Check if a string is an integer"""
        try:
            int(string)
            return True
        except ValueError:
            return False
            

    @staticmethod
    def is_letters(string):
        """String cleaning"""
        if re.search("[0-9@]+", string) is not None:
            return False
        return True

            

    @staticmethod
    def email_regex(mail):
        """email checking"""
        regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        if re.search(regex, mail):
            return True
        return False

