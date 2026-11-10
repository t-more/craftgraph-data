# CraftGraph shared prices

Auction house prices that players of World of Warcraft Forever choose to share with each other,
for the [CraftGraph](https://github.com/t-more/craftgraph) addon.

This is **optional**. CraftGraph works entirely from your own scans; this only adds other
players' scans as a second opinion, each with a switch in the addon's Data sources window.

## What is in here

```
contributors.json                     who may write, and their characters
data/<auction house>/<github account>.cg.json   one file per player: their latest prices
```

Each file is plain JSON, the same thing the addon's Export makes:

```json
{ "format": "craftgraph-prices", "version": 1,
  "realm": "<auction house>", "from": "<character>", "github": "<account>", "made": 1794317899,
  "items": { "2840": { "t": 1794317022, "n": 148, "l": [970, 14, 974, 61] } } }
```

`l` is the price ladder: price in copper, units, price, units. A file holds only the latest
prices, not history, and is replaced each time its owner shares again.

## Reading (anyone, no account)

With the addon's optional tool:

    python3 sync/craftgraph_sync.py data-pull

It fetches the files for your auction house. At your next login the game lists each player under
Data sources, by character name, with a switch.

## Sharing your prices

**What becomes public:** your character's name, your GitHub account name, and the prices from
your scans of the last day. Nothing else.

1. Ask the owner to let your GitHub account in (open an issue here with your character's name).
2. On your computer: install the [GitHub CLI](https://cli.github.com/) and run `gh auth login`.
3. `python3 sync/craftgraph_sync.py data-sync` shares yours and fetches the others'.

## For the owner: letting someone in

1. Add them to `contributors.json` with their character names.
2. Give their account write access:
   `gh api -X PUT repos/t-more/craftgraph-data/collaborators/<account> -f permission=push`

Every change is checked by `validate.py` (see the Actions tab): a file must be valid, must sit
under its writer's own account name, and its character must be one listed for that account. A
failed check shows as a red mark on the commit; nothing is undone automatically, so the owner
should look when one appears.

Write access is to the whole repository, so this is meant for people who know each other.
