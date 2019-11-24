import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection


class ListingsService:
    def __init__(self):
        self.hepsiburadaconnection = HepsiburadaConnection()
        self.servicepath = "/listings"
        self.integration = "listing"
        self.company = frappe.defaults.get_user_default("Company")

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.

    def get_list_of_listings(self, offset, limit):

        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Setting",
                                                            self.company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        if offset is None or limit is None:
            params = None
        else:
            params = {
                "offset": offset,
                "limit": limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)


@frappe.whitelist()
def initiate_hepsiburada_listings():
    ls = ListingsService()
    listings = ls.get_list_of_listings(None, None)
    totalcount = listings["totalCount"]
    meta = frappe.get_meta("hepsiburada Listing")
    for l in listings["listings"]:
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": 'hepsiburada Listing',
            "hepsiburadasku": l["hepsiburadaSku"],
            "company": ls.company
        }):
            newdoc = frappe.new_doc("hepsiburada Listing")
            newdoc.hepsiburadasku = l["hepsiburadaSku"]
            newdoc.company = ls.company
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Listing', l["hepsiburadaSku"])
        # "deactivationReasons": [
        #     "PriceIsLessThanOrEqualToZero",
        #     "StockIsLessThanOrEqualToZero",
        #     "PriceIsLessThanThreshold"
        # ],
        # "lockReasons": [],
        for p in l.keys():
            if meta.has_field(p.lower()):
                frdoc.db_set(p.lower(), l[p])

        frdoc.save()

        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": 'Item',
            "item_code": l["merchantSku"]
        }):
            newdoc = frappe.new_doc("Item")
            # required
            newdoc.item_code = l["merchantSku"]
            newdoc.item_group = frappe.db.get_value("hepsiburadacom Integration Company Setting", ls.company,
                                                    "item_group")
            newdoc.stock_uom = frappe.db.get_value("hepsiburadacom Integration Company Setting", ls.company,
                                                   "stock_uom")
            # optional
            newdoc.is_sales_item = 1
            newdoc.include_item_in_manufacturing = 0
            newdoc.is_stock_item = 1

            newdoc.insert()

    return frappe.db.count("hepsiburada Listing", filters={"company": ls.company}) == totalcount
