# Jewel bank

The jewel bank is OpenMU's: the account stores its jewels by their number, so any amount of
them takes no space in the vault or the inventory, and every character of the account shares
them. The server decides which jewels it accepts and keeps the amounts; the window shows what
the server sends. A server without the jewel bank (another server, or OpenMU with the feature
off) never shows the window or its button.

## Opening it

- The jewel bank button at the end of the inventory's button row (a gem in the Kryon theme). It
  appears once the server answered the jewel bank request the client sends when the character
  enters the world, and hides while a merchant, trade, vault or chaos machine is open, like the
  repair button.
- The server's chat command `/banco`.

The window docks beside the inventory, where the vault goes, and opens the inventory with it.
Opening it closes the NPC windows; closing the inventory, or Escape, closes it.

## Using it

Each jewel the server accepts has a row with its name and stored amount (grey while none is
stored):

- **+** deposits every jewel of that kind in the inventory, the single jewels and their bundles.
- **-** asks for an amount to withdraw (**Max** fills in all that is stored). The server puts it
  into the inventory as bundles of 30, 20 and 10 first, then single jewels, and stops when the
  inventory is full; what doesn't fit stays in the bank.
- **Deposit all** deposits every accepted jewel in the inventory.

The server answers each request with the new amounts and tells the player in a message when
nothing could be deposited, the bank is full or the inventory is.

## Themes

The window is `jewel_bank.rml`, styled by each theme's `jewel_bank.rcss`. Kryon's look is
`tools/kryon_theme/handmade/jewel_bank.rcss`, appended to modern's by `generate_theme.py`.
