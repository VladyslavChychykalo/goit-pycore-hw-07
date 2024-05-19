from collections import UserDict
from datetime import datetime
from errors_decorators import action_error, input_error


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
        return self.data.get(search_name)

    @action_error
    def delete(self, search_name: str) -> None:
        del self.data[search_name]

    def get_upcoming_birthdays(self, days: int):
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None and 0 <= days_to_birthday <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    return "Contact not found."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return f"Phones for {name}: {', '.join(p.value for p in record.phones)}"
    return "Contact not found."


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}"
        return "Birthday not set."
    return "Contact not found."


@input_error
def birthdays(_, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays(7)
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(
        f"Upcoming birthday: {record.name.value} on {
            record.birthday.value.strftime('%d.%m.%Y')}"
        for record in upcoming_birthdays
    )


def parse_input(user_input):
    return user_input.strip().split(" ", 1)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            for _, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
