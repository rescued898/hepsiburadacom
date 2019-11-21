import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection


class ListingsService:
    def __init__(self):
        self.hepsiburadaconnection = HepsiburadaConnection()
        self.servicepath = "/listings"
        self.integration = "listing"

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.

    def get_list_of_listings(self, offset, limit):
        company = frappe.defaults.get_user_default("Company")
        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Settings",
                                                            company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        if offset is None or limit is None:
            params = None
        else:
            params = {
                'offset': offset,
                'limit': limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)


@frappe.whitelist()
def initiate_hepsiburada_listings():
    ls = ListingsService()
    listings = ls.get_list_of_listings(None, None)
    meta = frappe.get_meta("hepsiburada Listings")
    for l in listings["listings"]:
        # check if record exists by filters
        if frappe.db.exists({
            'doctype': 'hepsiburada Listings',
            'hepsiburadasku': str(l["hepsiburadaSku"])
        }):
            pass
        else:
            newdoc = frappe.new_doc("hepsiburada Listings")
            newdoc.hepsiburadasku = str(l["hepsiburadaSku"])
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Listings', str(l["hepsiburadaSku"]))
        for p in l.keys():
            if meta.has_field(str(p).lower()):
                frdoc.db_set(str(p).lower(), l[p])

        frdoc.save()

    return "success"