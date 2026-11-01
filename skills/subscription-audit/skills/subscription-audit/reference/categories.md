# Categories, read by subscriptions.py

_Edit this file to change how rows are tagged. `scripts/subscriptions.py` reads the six tables below on every run, and nothing else is hard-coded. Patterns are Python regular expressions matched against the upper-cased description. The first match wins, so put specific rows above general ones. Write `\|` for an alternation inside a table cell. A blank flow means "decide by sign": money out is `spend`, money in is `refund` on a card and `income` on a bank account._

_Add your own merchants at the top of Patterns: your utility, your insurer, your school. Keep amounts, account numbers and transaction lines out of this file._

## Patterns

| pattern | category | flow | what it is |
|---|---|---|---|
| ONLINE TRANSFER\|TRANSFER TO (CHECKING\|SAVINGS)\|TRANSFER FROM (CHECKING\|SAVINGS)\|EXT TRNSFR\|INTERNAL TRANSFER\|OVERDRAFT PROTECTION | transfer-own | transfer-own | Money moved between your own accounts |
| AUTOMATIC PAYMENT - THANK\|PAYMENT - THANK YOU\|PAYMENT THANK YOU\|AUTOPAY PYMT\|CRD AUTOPAY\|CREDIT CARD PAYMENT\|E-PAYMENT\|MOBILE PYMT\|CAPITAL ONE AUTOPAY\|CITI AUTOPAY\|DIRECTPAY FULL BALANCE | card-payment | card-payment | A card bill paid, seen from either side |
| PAYROLL\|DIRECT DEP | payroll | income | Salary |
| INTEREST PAID\|INTEREST PAYMENT | interest-earned | income | Savings interest |
| MONTHLY SERVICE FEE\|MAINTENANCE FEE\|ATM FEE\|LATE FEE\|LATE PAYMENT FEE\|ANNUAL FEE\|MEMBERSHIP FEE\|FOREIGN TRANSACTION FEE\|OVERDRAFT FEE\|INSUFFICIENT FUNDS\|NSF FEE\|INTEREST CHARGE\|FINANCE CHARGE\|\bSERVICE FEE\b\|WIRE FEE | fee | fee | Bank or card fee |
| ANTHROPIC\|CLAUDE\.AI\|OPENAI\|CHATGPT\|MIDJOURNEY\|PERPLEXITY\|GEMINI\|ELEVENLABS\|CURSOR\|GITHUB\|COPILOT\|GRAMMARLY\|QUILLBOT\|JASPER\|RUNWAY | ai-software | spend | AI tool subscription |
| GOOGLE \*CLOUD\|GOOGLE CLOUD\|AMAZON WEB SERVICES\|\bAWS\b\|DIGITALOCEAN\|HEROKU\|VERCEL\|NETLIFY | cloud | spend | Cloud computing, billed by product |
| GODADDY\|CLOUDFLARE\|NAMECHEAP\|SQUARESPACE\|\bWIX\b\|BLUEHOST\|HOSTINGER\|WORDPRESS | domains-hosting | spend | Domain or web hosting |
| GOOGLE \*GOOGLE ONE\|GOOGLE ONE\|ICLOUD\|DROPBOX\|BACKBLAZE | storage | spend | Cloud storage plan |
| MICROSOFT\|NOTION\|ADOBE\|INTUIT\|TURBOTAX\|ZOOM\.US\|CANVA\|1PASSWORD\|LASTPASS\|NORDVPN\|EXPRESSVPN\|EVERNOTE\|TODOIST | software | spend | Software or app subscription |
| APPLE\.COM/BILL | apple-services | spend | Apple subscription or app, product unknown from the line |
| GOOGLE \*\|GOOGLE PLAY | google-services | spend | Google purchase or subscription, product unknown from the line |
| SPOTIFY\|PRIME VIDEO\|NETFLIX\|HULU\|DISNEY\|YOUTUBE\|PARAMOUNT\|AMAZON PRIME\|PEACOCK\|MAX\.COM\|HBO\|AUDIBLE\|SIRIUSXM\|PANDORA\|CRUNCHYROLL | streaming | spend | Music, video or audiobook streaming |
| NYTIMES\|WSJ\|WASHPOST\|MEDIUM\|SUBSTACK\|PATREON\|ECONOMIST | news-and-media | spend | News, newsletter or creator subscription |
| PLAYSTATION\|STEAMGAMES\|NINTENDO\|XBOX | games-and-apps | spend | Game or app purchase |
| PLANET FITNESS\|LA FITNESS\|24 HOUR FITNESS\|ANYTIME FITNESS\|PELOTON\|CLASSPASS\|STRAVA\|NOOM | fitness | spend | Gym or fitness subscription |
| COSTCO \*ANNUAL\|ANNUAL RENEWA\|SAMS CLUB MEMBER\|AAA\b | membership | spend | Membership renewal |
| ACORNS\|BETTERMENT\|WEALTHFRONT\|STASH | investing-app | spend | Investing app subscription or deposit |
| ELECTRIC\|ENERGY\|POWER CO\|DUKE ENERGY\|PG&E\|CON ED\|NATIONAL GRID\|WATER\b\|UTILIT\|WASTE MANAGEMENT\|REPUBLIC SERVICES | utilities | spend | Electricity, gas, water or trash |
| T-MOBILE\|VERIZON\|AT&T\|MINT MOBILE\|CRICKET\|VISIBLE\|GOOGLE FI | phone | spend | Phone service |
| COMCAST\|XFINITY\|SPECTRUM\|COX COMM\|FRONTIER\|STARLINK | internet | spend | Home internet or TV |
| ALLSTATE\|PROGRESSIVE\|GEICO\|STATE FARM\|LIBERTY MUTUAL\|FARMERS\|USAA\|LEMONADE\|INSURANCE\|INS PREM | insurance | spend | Insurance premium |
| MORTGAGE\|HOME LOAN\|LOAN SERVIC\|ROCKET MORTGAGE\|MR\. COOPER | mortgage | spend | Mortgage payment |
| \bRENT\b\|APARTMENTS\|PROPERTY MGMT | rent | spend | Rent |
| AUTO LOAN\|AUTO PAY LOAN\|AUTO FINANCE\|TOYOTA FINANCIAL\|HONDA FINANCIAL | auto-loan | spend | Car loan |
| DEPT EDUCATION\|NELNET\|NAVIENT\|MOHELA\|SALLIE MAE | student-loan | spend | Student loan payment |
| \bHOA\b\|HOMEOWNERS ASSOC | hoa | spend | Homeowners association |
| DAYCARE\|CHILD CARE\|PRESCHOOL\|MONTESSORI | childcare-school | spend | Childcare or school |
| PEST CONTROL\|LAWN\|POOL SERVICE\|CLEANING\|SECURITY SYSTEM\|ADT\b\|RING\b\|SIMPLISAFE | home-services | spend | Regular service at the house |
| E-ZPASS\|SUNPASS\|FASTRAK\|TOLL | tolls | spend | Toll road |
| TUITION\|COURSERA\|UDEMY\|DUOLINGO\|MASTERCLASS\|SKILLSHARE | education | spend | Course or learning subscription |
| DONATION\|CHARITY\|GOFUNDME\|RED CROSS | charity | spend | Donation |
| DOCTOR\|DENTAL\|CLINIC\|HOSPITAL\|MEDICAL\|VISION\b\|PEDIAT | medical | | Medical, dental or vision |
| WALGREENS\|CVS\|PHARMACY | pharmacy | spend | Pharmacy |
| SHELL\|CHEVRON\|EXXON\|BP\b\|CIRCLE K\|VALERO\|MOBIL\|7-ELEVEN\|COSTCO GAS | fuel | spend | Fuel |
| UBER\|LYFT\|PARKING | transport | spend | Rides and parking |
| AIRLINES\|HOTEL\|AIRBNB\|EXPEDIA\|BOOKING\.COM | travel | spend | Travel |
| KROGER\|WALMART\|WAL-MART\|COSTCO WHSE\|ALDI\|TRADER JOE\|WHOLE FOODS\|SAFEWAY\|PUBLIX\|INSTACART | groceries | spend | Groceries |
| STARBUCKS\|MCDONALD\|CHICK-FIL-A\|RESTAURANT\|PIZZA\|DOMINO\|DOORDASH\|GRUBHUB\|UBER EATS\|COFFEE\|CAFE\|TST\* | dining | spend | Eating out |
| AMAZON\|AMZN\|TARGET\|BEST BUY\|HOME DEPOT\|LOWE'S\|LOWES\|IKEA\|ETSY\|EBAY\|TEMU | shopping | | Shopping |
| ATM WITHDRAWAL\|^WITHDRAWAL | cash | spend | Cash |
| ^CHECK\b | checks | | Paper check |
| DEPOSIT | deposit | income | Deposit |

## Person-to-person

A row matching one of these is a payment between people. It is counted and left out, never named or totalled per person.

| pattern |
|---|
| ^ZELLE |
| ^VENMO |
| ^CASH APP |
| PAYPAL INST XFER .*(FROM\|TO) [A-Z]+ [A-Z]+$ |

## Bank categories

Used when no pattern matched: the bank's own label, then ours.

| bank label | category | flow |
|---|---|---|
| Payment | card-payment | card-payment |
| Return | shopping | refund |
| Fee | fee | fee |
| Fees & Adjustments | fee | fee |
| Interest | fee | fee |
| Payment/Credit | card-payment | card-payment |
| Payments and Credits | card-payment | card-payment |
| Groceries | groceries | |
| Supermarkets | groceries | |
| Food & Drink | dining | |
| Restaurants | dining | |
| Gas | fuel | |
| Gasoline | fuel | |
| Automotive | auto | |
| Entertainment | entertainment | |
| Travel | travel | |
| Shopping | shopping | |
| Merchandise | shopping | |
| Home | home-services | |
| Home Improvement | shopping | |
| Bills & Utilities | utilities | |
| Utilities | utilities | |
| Health & Wellness | medical | |
| Medical Services | medical | |
| Education | education | |
| Gifts & Donations | charity | |
| Personal | other | |
| Professional Services | other | |
| Transfer | transfer-own | transfer-own |
| Credit Card Payment | card-payment | card-payment |
| Paycheck | payroll | income |
| ACCT_XFER | transfer-own | transfer-own |
| FEE_TRANSACTION | fee | fee |

## Common first words

Two merchant names count as one merchant when they share a distinctive first word. A word listed here is never distinctive: a processor, a bank, a place or an ordinary word that begins many unrelated names. Add your own city and county.

| word |
|---|
| PAYPAL |
| ONLINE |
| GOOGLE |
| AMAZON |
| APPLE |
| CHASE |
| ACH |
| THE |
| CITY |
| COUNTY |
| FIRST |
| AMERICAN |
| NATIONAL |
| PAYMENT |
| AUTOMATIC |
| MONTHLY |
| RECURRING |
| SQ |
| NORTH |
| SOUTH |
| EAST |
| WEST |

## Groups

Each category belongs to one group. `everyday` is never listed as recurring, even when you buy groceries every week. `bills-and-loans` is listed even when the amount moves (an electricity bill). `subscriptions` is listed as `possible` after only two charges. A category not in this table is `other`, and is listed when it repeats on a steady cadence at a steady amount.

| category | group |
|---|---|
| ai-software | subscriptions |
| software | subscriptions |
| cloud | subscriptions |
| domains-hosting | subscriptions |
| storage | subscriptions |
| apple-services | subscriptions |
| google-services | subscriptions |
| streaming | subscriptions |
| news-and-media | subscriptions |
| games-and-apps | subscriptions |
| fitness | subscriptions |
| membership | subscriptions |
| investing-app | subscriptions |
| education | subscriptions |
| utilities | bills-and-loans |
| phone | bills-and-loans |
| internet | bills-and-loans |
| insurance | bills-and-loans |
| mortgage | bills-and-loans |
| rent | bills-and-loans |
| auto-loan | bills-and-loans |
| student-loan | bills-and-loans |
| hoa | bills-and-loans |
| childcare-school | bills-and-loans |
| home-services | bills-and-loans |
| tolls | bills-and-loans |
| fee | fees |
| charity | donations |
| medical | everyday |
| pharmacy | everyday |
| fuel | everyday |
| transport | everyday |
| travel | everyday |
| groceries | everyday |
| dining | everyday |
| shopping | everyday |
| entertainment | everyday |
| auto | everyday |
| cash | everyday |
| checks | everyday |

## Trace routes

Where to find the product behind a charge the line does not explain. The script marks `trace_needed` for rows whose line no pattern explains, and for these categories when the amount moves. Name a charge only from the seller's own record, never from when it started.

| category | where to look |
|---|---|
| apple-services | Apple ID, Subscriptions, then Purchase History |
| google-services | Google Play, Payments and subscriptions, on the paying Google account |
| cloud | The cloud console's billing report, grouped by product |
| ai-software | The provider's billing page, by plan and seat |
| other | The statement line on the bank's site, then the merchant's own receipt or account page |
