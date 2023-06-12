# Calculate VIX ETF RollDown Value
Calculate futures contango rolldown for popular 30 day avg maturity VIX ETFs such as SVXY and XIV

# To Execute
- run: python Calculate_VIX_RollDown.py

# Results Summary
- The sample output looks like:

| VIX: 17.48| 
|---|
| |
| M1: 17.4 matures 2018-03-21 |
| M2: 17.32 matures 2018-04-18 |
| M3: 17.33 matures 2018-05-16 |
| |
| Forward 28 day rolldown: -1.1% |
| VIX shift to flip rolldown: 17.21 ; +-0.27 ; -1.5% |

- VIX denotes the current level of spot VIX
- Mn denotes the nth monthly futures expiry level and expiration date
- Forward 28 day rolldown denotes the implied rolldown over the next 28 days, based on the futures curve and SVXY/XIV construction mechanisms, and assuming the futures curve does not change w.r.t. time
- VIX shift to flip rolldown denotes the value of spot VIX, change from the current spot VIX, and change on a % basis so that implied 28 day rolldown = 0
