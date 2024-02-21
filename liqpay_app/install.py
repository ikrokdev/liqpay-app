import os
import frappe

def before_install():
    payments_app_name = 'payments'
    payments_app_installed = len([app_name for app_name in frappe.get_installed_apps() if payments_app_name == app_name]) > 0
    
    if not payments_app_installed:
        logger = frappe.logger()
        logger.debug(f"{payments_app_name} app not found in installed app list. {payments_app_name} app is required for correct job. Trying to install app.")
        
        get_app_result = os.system(f'bench get-app {payments_app_name} --overwrite')
        
        if get_app_result == 0:
            install_app_result = os.system(f'bench install-app {payments_app_name}')
            if install_app_result == 0:
                logger.debug(f"{payments_app_name} app successfuly installed")
            else:
                logger.error(f"{payments_app_name} app not installed")
        else:
            logger.error(f"An error occured when try to get {payments_app_name} app")
            

def after_install():
    gateway_name = "LiqPay"
    liqpay_payment_gateway_dict = {
        "doctype": "Payment Gateway",
        "gateway": gateway_name,
        "gateway_settings": "LiqPay Settings"
    }
    new_payment_gateway = frappe.get_doc(liqpay_payment_gateway_dict)
    new_payment_gateway.save()
    frappe.db.commit()

    