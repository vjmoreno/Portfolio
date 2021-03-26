

This module adds the product's history. To correctly set it up, install the module, and then create a scheduled action with the following fields:

- Model: Invoice (account.invoice)
- Available on website: False
- Scheduler User: Administrator
- Execute every: 1 Month.
- Next execution date: First day of next month.
- Number of calls: 1
- Priority: 5
- Repeat missed: False

Once you create it, run it manually for the first time to update the history.
					
You will find the history in the form view of the product templates, under the sales tab.