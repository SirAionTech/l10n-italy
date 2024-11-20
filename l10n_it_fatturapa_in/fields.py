#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Float

orig_convert_to_cache = Float.convert_to_cache
orig_get_digits = Float.get_digits


def get_digits(self, env):
    digits = orig_get_digits(self, env)
    if l10n_it_fatturapa_in_precision := env.context.get(
        "l10n_it_fatturapa_in_precision"
    ):
        digits = digits[0], l10n_it_fatturapa_in_precision
    return digits


def convert_to_cache(self, value, record, validate=True):
    if record._name in ("account.move", "account.move.line"):
        if record.fatturapa_attachment_in_id:
            # The invoice [line] has been created by importing an e-invoice.
            # If a different precision has been used,
            # keep using that precision to read values that have it.
            field_precision = self._digits
            if isinstance(field_precision, str):
                l10n_it_fatturapa_in_precision = None
                if field_precision == "Product Price":
                    l10n_it_fatturapa_in_precision = (
                        record.fatturapa_attachment_in_id.price_decimal_digits
                    )
                elif field_precision == "Product Unit of Measure":
                    l10n_it_fatturapa_in_precision = (
                        record.fatturapa_attachment_in_id.quantity_decimal_digits
                    )
                elif field_precision == "Discount":
                    l10n_it_fatturapa_in_precision = (
                        record.fatturapa_attachment_in_id.discount_decimal_digits
                    )

                if l10n_it_fatturapa_in_precision:
                    record = record.with_context(
                        l10n_it_fatturapa_in_precision=l10n_it_fatturapa_in_precision
                    )

    return orig_convert_to_cache(self, value, record, validate=validate)


Float.convert_to_cache = convert_to_cache
Float.get_digits = get_digits
