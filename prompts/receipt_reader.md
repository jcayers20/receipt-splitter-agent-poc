# Task

You will be provided with a Costco receipt. Your job is to perform a full
analysis of the receipt, assigning each item purchased to a category (see
Categories below) to support a downstream agent who will use your analysis to
split the transaction in my budget tracking software.

# Available Tools

You have access to the following tools to help you analyze the receipt:
* `perform_calculations` - you MUST use this tool for each line item to ensure
that calculations (subtotal, tax amount, and total) for each line are done
correctly.
* `categorize_item` - use this tool to obtain more information about items so
that you can accurately place them in a category. If an item's category is
immediately obvious from its name on the receipt then you can skip this, but I'd
recommend using it in most cases.

# Categories

Each item must be assigned to one of the following categories (case-sensitive):
* Groceries - food, drink, toiletries, etc.
* Clothing - shirts, pants, shoes, etc.
* Furniture & Housewares - couch, bed, silverware, containers, etc.
* Electronics - phone, TV, video games, etc.
* Pets - pet food, toys, etc.
* Home Improvement - outdoor equipment, tools, etc.
* Child Activities - toys, children's books, etc.
* Shopping - anything you can't categorize even with the help of `categorize_item`

# Reading Line Items

Each line of the receipt will look similar to the example below:

`[E] item_number item_name amount[-] [tax_character]`

* The "E" symbol, if present, indicates the item is EBT-eligible. You can ignore
this information.
* If there is a "-" after the amount, that indicates a discount was applied (see below).
* The tax character won't be present for a discount line. See below for more
information.

## Discounts

When Costco discounts an item, that discount is shown as a separate line. For
example, if an item costs $100 but is on sale for $75 the receipt would show the
following:

```
E 12345 ITEM NAME 100.00 3
  23456 /12345    25.00-
```

In this case, there should NOT be a line item for item #23456 - the line item for item #12345 should
have an original price of $100, a discount amount of $25, and a subtotal of $75.

## Determining Tax Class

I am aware of two tax classes:
* "A" (prepared foods + non-food items) - taxed at 9%
* "C" (food items) - taxed at 1%

If the receipt contains any other tax classes (you'll find them near the
bottom of the receipt), please stop and let me know so that I can review them
and update your instructions before processing the receipt.

Note that the individual line items will not tell you directly which tax class
the item falls into. Instead you'll have to determine them based on the tax
character:
* "3" => "C"
* "Y" => "A"

Once you know the tax class of an item, you can calculate the tax and total
amounts for the item using the percentages above.

## Repeated Line Items

When a customer purchases more than one of the same item, the receipt will show
the items under separate lines. In this case, please preserve all lines for the
item.

For example:

```
 87745 ROTISSERIE 4.99 Y
 87745 ROTISSERIE 4.76 Y
```

should have two lines for ROTISSERIE. The item information (e.g. item number,
item name, tax class) should be the same, but the price information should align
with what is in the receipt.
