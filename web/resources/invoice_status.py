import enum


class InvoiceStatus(enum.Enum):
    """ Invoice status enum. """
    Active = (1, "Active registrated invoice")
    Invalid = (2, "The invoice was rejected by debtor")
    Canceled = (3, "The invoice was canceled by creditor")
    PartiallySettled = (4, "The invoice was partially settled in partial amount")
    Settled = (5, "The invoice has been settled")
    Assigned = (6, "The debtor assigned the invoice to another debtor")
    ProformaInvoice = (7, "Proforma invoice")

    def __new__(cls, member_value, member_message):
        member = object.__new__(cls)  # create new member object (InvoiceStatus member)
        member._value = member_value  # member value is code that we want to send
        member._message = member_message  # member message is message of InvoiceStatus ("Proforma invoice")
        return member

    @property
    def code(self):
        return self._value

    @property
    def message(self):
        return self._message
