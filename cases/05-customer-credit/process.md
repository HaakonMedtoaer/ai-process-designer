# Case 05: Customer credit approval and collections (order-to-cash)

## Process text (paste this into the tool)

Nordbakk AS sells on invoice to business customers and decides who gets credit.

1. A new business customer fills in a credit application: company details, trade references, latest financial statements and requested limit.
2. Credit staff pull a credit report and check references.
3. Credit staff read the financial statements and the report and assess the customer's ability to pay.
4. A credit limit and payment terms are set. Limits above a set level need the credit manager's sign-off.
5. The customer is told the outcome and the account is set up in the system with its limit.
6. When orders come in, the system compares open receivables plus the new order against the limit and holds orders that exceed it.
7. A held order is released or kept on hold by the credit manager, with the reason logged.
8. When an invoice passes its due date, a written reminder is sent. Further reminders follow on a fixed schedule.
9. For accounts still unpaid after the reminders, the credit department decides whether to call the customer, agree a payment plan, stop credit or send the account to a collection agency.
10. Bad debts are written off by someone with delegated write-off authority.

## Sources (step pattern modelled on)
Mostly templates and company policies, not standards.
- Holcim Australia, national credit policy: https://www.holcim.com.au/sites/australia/files/2022-12/holcim-australia_national-credit-policy.pdf
- Irish Red Cross, credit control policy: https://www.redcross.ie/wp-content/uploads/2015/05/credit-control-policy.pdf (written reminder after terms)
- Florida Atlantic University, billing and collections best practices: https://www.fau.edu/fiscal/best-practices/billing-collections.pdf
- Cleverence, setting customer credit limits in ERP: https://www.cleverence.com/articles/sage-documentation/set-a-customers-credit-limit-4827/ (open AR + pending orders vs limit, override with audit log)
- Business-in-a-Box, credit policy template: https://www.business-in-a-box.com/template/credit-policy-D12633/
