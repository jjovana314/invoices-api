from config import api, app
from resources.assign import Assign
from resources.cancel_assign import CancelAssign
from resources.cancel import Cancel
from resources.change_amount import ChangeAmount
from resources.invoice_details import InvoiceDetails
from resources.login import Login
from resources.paged_liabilities import PagedLiabilities
from resources.register import Register
from resources.revert_amount import RevertAmount
from resources.validate import Validate


api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/invoice/register")
api.add_resource(Assign, "/api/invoice/assign")
api.add_resource(CancelAssign, "/api/invoice/cancel-assign")
api.add_resource(Cancel, "/api/invoice/cancel")
api.add_resource(InvoiceDetails, "/api/invoice/<string:idf>", endpoint="invoice")
api.add_resource(ChangeAmount, "/api/invoice/change-amount")
api.add_resource(PagedLiabilities, "/api/invoice/paged-liabilities")
api.add_resource(RevertAmount, "/api/invoice/revert-amount")
api.add_resource(Validate, "/api/invoice/validate")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
