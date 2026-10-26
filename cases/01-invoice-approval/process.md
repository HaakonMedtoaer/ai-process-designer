# Case 01: Supplier invoice approval (purchase-to-pay)

## Process text (paste this into the tool)

Nordbakk AS receives supplier invoices by email, mostly as PDFs, some scanned.

1. An accounts payable clerk opens the invoice mailbox and saves each invoice to the AP system.
2. The clerk types in supplier name, invoice number, date, amount, VAT and the purchase order number.
3. The system checks whether the invoice number has already been registered for that supplier.
4. The invoice is matched against the purchase order and, for goods, the goods receipt. Quantities and prices must agree within a tolerance.
5. If the match fails, the clerk finds out why: wrong price, partial delivery, missing goods receipt, or wrong PO. This means checking the PO history, asking the person who ordered, and sometimes contacting the supplier.
6. Invoices without a PO are sent to the budget holder, who must confirm the purchase and assign a cost centre.
7. Invoices above the clerk's limit are approved by a manager with the right approval authority.
8. Approved invoices are scheduled into the next payment run.
9. The finance manager reviews and releases the payment run in the bank.

## Sources (step pattern modelled on)
- University of South Carolina, PO processing: https://cupasr.sc.edu/about/offices_and_divisions/controller/documents/po_processing.pdf (voucher entry, 2-/3-way match, requestor notified on mismatch)
- Rockefeller University, two-way and three-way matches: https://www.rockefeller.edu/materials-management/purchasing/two-way-and-three-way-matches/
- Clemson University procurement policy: https://www.clemson.edu/procurement/faculty-staff/policies/procurement/psv75pol.html

Not taken from sources (added for the case): duplicate check (step 3), approval limit (step 7), payment-run release (step 9). These are common controls, but I have no source in hand for them.
