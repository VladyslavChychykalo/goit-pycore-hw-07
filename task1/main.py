from collections import UserDict
from datetime import datetime


def action_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Record with name '{args[1]}' not found")
            raise e
        except ValueError as e:
            raise e

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def validate_phone(self):
        if not self.value.isdigit() or len(str(self.value)) != 10:
            raise ValueError("Phone number should contain 10 digits")


class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y"))
        except ValueError as exc:
            raise ValueError('Invalid date format. Use DD.MM.YYYY') from exc


class Record:
    def __init__(self, record_name: str):
        self.name = Name(record_name)
        self.phones = []
        self.birthday = None

    def __str__(self) -> str:
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime(
            '%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

    def add_phone(self, phone: str) -> None:
        phone_obj = Phone(phone)
        phone_obj.validate_phone()
        self.phones.append(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                phone.validate_phone()
                return
        raise ValueError(f"Phone number '{old_phone}' not found")

    def find_phone(self, phone: str) -> str:
        for p in self.phones:
            if p.value == phone:
                return p.value
        raise ValueError(f"Phone number '{phone}' not found")

    def remove_phone(self, phone: str) -> None:
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError(f"Phone number '{phone}' not found")

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days


class AddressBook(UserDict):
    def add_record(self, new_record: Record) -> None:
        self.data[new_record.name.value] = new_record

    @action_error
    def find(self, search_name: str) -> Record:
        return self.data[search_name]

    @action_error
    def delete(self, search_name: str) -> None:
        del self.data[search_name]

    def get_upcoming_birthdays(self, days: int):
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                print(f"{record.name.value} has {
                      days_to_birthday} days to birthday")
                if days_to_birthday is not None and 0 <= days_to_birthday <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
john_record.add_birthday("25.12.1990")
book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
jane_record.add_birthday("30.05.1985")
book.add_record(jane_record)

for name, record in book.data.items():
    print(record)

john = book.find("John")
print(john)
john.edit_phone("1234567890", "1112223333")

try:
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")
except ValueError as e:
    print(e)

book.delete("Jane")

upcoming_birthdays = book.get_upcoming_birthdays(7)
print("Upcoming birthdays in the next 7 days:")

for record in upcoming_birthdays:
    print(f"Upcoming birthday: {record.name.value} on {
          record.birthday.value.strftime('%d.%m.%Y')}")
