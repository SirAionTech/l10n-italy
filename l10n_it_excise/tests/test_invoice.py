#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.test_tax import TestTaxCommon


@tagged("post_install", "-at_install")
class TestInvoice(TestTaxCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        company = cls.env.company

        original_excise_oil_carburetion_tax = cls.env.ref(
            "l10n_it_excise.account_tax_excise_oil_carburetion"
        )
        cls.excise_oil_carburetion_tax = (
            original_excise_oil_carburetion_tax.sudo().copy(
                default={
                    "company_id": company.id,
                },
            )
        )

        cls.oil_carburetion_product = cls.env["product.product"].create(
            {
                "name": "Oil for Carburetion",
                "volume": 1,
                "taxes_id": [
                    Command.set(cls.excise_oil_carburetion_tax.ids),
                ],
            }
        )

    def test_tax_excise_oil_carburetion_amount(self):
        """Invoice 2000 liters of oil for carburetion.
        The excise tax is 2000 * 728.4 / 1000 = 1456.8
        """
        # Arrange
        product = self.oil_carburetion_product
        quantity = 2000
        excise_tax = product.taxes_id
        # pre-condition
        self.assertEqual(product.volume, 1)
        self.assertEqual(excise_tax, self.excise_oil_carburetion_tax)

        # Act
        invoice = self.init_invoice(
            "out_invoice",
            products=product,
        )
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == product
        )
        invoice_line.quantity = quantity

        # Assert
        expected_excise_amount = 1456800
        self.assertEqual(invoice.amount_tax, expected_excise_amount)
        tax_line = invoice.line_ids.filtered(
            lambda line: line.tax_line_id == excise_tax
        )
        self.assertEqual(tax_line.amount_currency, -expected_excise_amount)
