# -*- coding: utf-8 -*-
"""
About + tip copy for every recipe in the catalog.

RULES THIS FILE FOLLOWS
-----------------------
1. Nothing is invented. Where a drink has a documented origin it is stated.
   Where the origin is contested, the text says it is contested rather than
   picking a side and sounding confident. Where there is no real history, the
   text is about flavour and occasion only and makes no historical claim.
2. Every entry has `about`. `tip` is optional and only present where there is
   a genuine technique note worth reading before you start. A tip that says
   nothing is worse than no tip.
3. Tips are written as instructions, not trivia. They earn their place by
   changing what you do.

Keys are recipe names exactly as they appear in the `recipes` table.
"""

ABOUT = {

# ============================ A ============================================

"Adonis": {
    "about": "Named after the 1884 Broadway musical Adonis, which ran for an unheard-of "
             "500-plus performances. Sherry and sweet vermouth, no spirit at all, so it "
             "lands around 15% and is built for drinking before dinner rather than after.",
    "tip": "Use fino or amontillado. Cream sherry turns this cloying and there is no "
           "spirit here to cut through it.",
},
"Affinity": {
    "about": "A Rob Roy that uses both vermouths instead of picking one, which bartenders "
             "call a Perfect. The dry vermouth keeps the sweet one honest, so you get the "
             "Scotch rather than a syrupy version of it.",
    "tip": "Equal parts of both vermouths is the point. If you only own sweet vermouth "
           "you are making a Rob Roy, which is a fine drink but a different one.",
},
"Airmail": {
    "about": "Rum, honey and lime with champagne on top, first printed in Esquire's 1949 "
             "Handbook for Hosts. The name is the airmail postage stamp, which is also "
             "why it is sometimes garnished with one. It drinks like a Daiquiri that got "
             "upgraded at the gate.",
    "tip": "Honey straight from the jar seizes in a cold shaker. Thin it first with an "
           "equal splash of warm water and it will actually mix.",
},
"Algonquin": {
    "about": "Named for the Manhattan hotel that housed the Algonquin Round Table. Rye "
             "and dry vermouth with pineapple juice, which sounds like a mistake and is "
             "not: the pineapple reads as dry and slightly savoury here, not tropical.",
    "tip": "Canned pineapple juice genuinely works better than fresh in this one. Fresh "
           "is too sharp and does not foam the same way.",
},
"American Beauty": {
    "about": "Named after the rose, and built to look like one: brandy, dry vermouth, "
             "orange juice and grenadine under a float of red wine that sits on top like "
             "a stain. Far better than the ingredient list suggests.",
    "tip": "Pour the wine float slowly over the back of a spoon. Rushing it mixes the "
           "wine in and you lose the whole visual point of the drink.",
},
"Americano": {
    "about": "Campari, sweet vermouth and soda. It started life in 1860s Milan as the "
             "Milano-Torino and picked up its current name from the American tourists who "
             "drank it. It is also the first drink James Bond orders in print, in Casino "
             "Royale, long before the Martini business.",
    "tip": "Add gin instead of soda and you have a Negroni. Drop the soda entirely and "
           "you are back to a Milano-Torino. Same two bottles, three drinks.",
},
"Aperol Spritz": {
    "about": "The spritz habit comes from Austrian soldiers in the Veneto in the 1800s "
             "cutting strong local wine with water. Aperol arrived in Padua in 1919 and "
             "the two eventually found each other. Around 8% ABV, faintly bitter, and "
             "correct at 4pm.",
    "tip": "The ratio is 3 prosecco, 2 Aperol, 1 soda. Pour the prosecco first. Adding "
           "it last to a glass of Aperol kills the bubbles on contact.",
},
"Autumn Garibaldi": {
    "about": "The Garibaldi is Campari and orange juice, named for Giuseppe Garibaldi "
             "because it unites the bitter north with Sicilian oranges. This is the "
             "colder-weather version, deeper and less breakfast-adjacent.",
    "tip": "The real Garibaldi trick is fluffy juice: aerate the orange juice hard before "
           "it goes in and the drink gets a foamy body it otherwise lacks.",
},
"Aviation": {
    "about": "Hugo Ensslin published it in 1916 at the Hotel Wallick in New York. The "
             "original had creme de violette, which turned it a pale sky blue and gave the "
             "drink its name. The 1930 Savoy Cocktail Book left the violette out, which is "
             "why most versions since, including this one, are gin, lemon and maraschino.",
    "tip": "Maraschino is not the syrup from a cherry jar. It is a dry, funky cherry-pit "
           "liqueur and half an ounce of it will run the whole drink if you overpour.",
},

# ============================ B ============================================

"B-52": {
    "about": "Three liqueurs layered so they sit in visible bands. Peter Fich at the Banff "
             "Springs Hotel in Alberta is the most commonly cited creator, in the late "
             "1970s, though the story is not settled. Named either for the bomber or the "
             "band, depending on who is telling it.",
    "tip": "Layering works because each liqueur is less dense than the one below. Pour "
           "every layer slowly over the back of a bar spoon touching the glass wall, and "
           "keep the order: Kahlua, then Baileys, then Grand Marnier.",
},
"Bacardi Cocktail": {
    "about": "Rum, lime and grenadine. In 1936 the New York Supreme Court actually ruled "
             "that a drink sold under this name had to be made with Bacardi rum, which is "
             "the only cocktail in this catalog with case law attached.",
    "tip": "Real pomegranate grenadine matters more here than almost anywhere else. With "
           "only three ingredients there is nothing for the neon stuff to hide behind.",
},
"Bamboo": {
    "about": "Created by Louis Eppinger at the Grand Hotel in Yokohama in the 1890s. Dry "
             "sherry and dry vermouth with bitters, so it is essentially a Martini with "
             "the alcohol taken out and the savouriness left in.",
    "tip": "Both bottles here are wine and both go off. If the sherry or vermouth has "
           "been open more than a few weeks at room temperature, this drink will taste "
           "flat and it is not your technique.",
},
"Batanga": {
    "about": "From La Capilla in Tequila, Mexico, where Don Javier Delgado Corona served "
             "it for decades. Tequila, lime and Coke with a salt rim. He stirred every one "
             "with the same knife he used to cut the limes, which is the part everybody "
             "repeats.",
    "tip": "The salt rim is doing real work. It is not garnish here, it is what keeps the "
           "Coke from tasting flabby against the tequila.",
},
"Bay Breeze": {
    "about": "Vodka, cranberry and pineapple. No history worth reporting, it is a 1980s "
             "highball. What it is good at is being easy: sweet, tart, low effort, and "
             "hard to get wrong.",
},
"Bee's Kiss": {
    "about": "Rum, honey and cream. Closer to dessert than to a cocktail, and best treated "
             "that way. It has no documented origin story, just a good name and a short "
             "ingredient list.",
    "tip": "Thin the honey with warm water first. Cold cream plus cold honey means the "
           "honey never dissolves and you get sweet threads in the glass.",
},
"Bee's Knees": {
    "about": "A Prohibition-era drink and one of the best arguments for gin, lemon and "
             "honey being all you need. Attribution is contested between Frank Meier at "
             "the Ritz Paris and the socialite Margaret Brown. The name is 1920s slang: "
             "the bee's knees meant the best, in the same family as the cat's pyjamas.",
    "tip": "Make honey syrup rather than using honey neat. Two parts honey to one part "
           "warm water, stirred until it runs thin. Neat honey clumps the moment it hits "
           "cold citrus and never fully mixes.",
},
"Bellini": {
    "about": "Giuseppe Cipriani invented it at Harry's Bar in Venice sometime between the "
             "1930s and 1940s and named it after the pink he kept seeing in Giovanni "
             "Bellini's paintings. Two ingredients, no shaking, no ice.",
    "tip": "White peach puree, not yellow, and not peach juice. Yellow peaches are too "
           "sweet and the drink loses the faint tartness that makes it work.",
},
"Between the Sheets": {
    "about": "A Sidecar with rum added, from the Prohibition era, usually credited to "
             "Harry MacElhone in Paris though the claim is not firm. Strong, dry and "
             "citrus-forward, with none of the softness the name implies.",
},
"Bicicletta": {
    "about": "Northern Italian, named for the unsteady bicycle ride home. Campari, white "
             "wine and soda comes out around 8%, which makes it one of the few cocktails "
             "you can have two of in the afternoon without writing off the day.",
    "tip": "Any crisp dry white works. Pinot grigio is traditional. Anything oaked or "
           "off-dry fights the Campari instead of carrying it.",
},
"Black Manhattan": {
    "about": "Todd Smith created it at Bourbon & Branch in San Francisco in the mid-2000s. "
             "It swaps the sweet vermouth in a Manhattan for amaro, which keeps the "
             "richness but adds a bitter edge underneath.",
    "tip": "Averna is the standard choice and the sweetest of the common amari. A drier "
           "amaro like Ramazzotti works but you may want a touch more rye to balance it.",
},
"Black Russian": {
    "about": "Made by Gustave Tops at the Hotel Metropole in Brussels in 1949, for the "
             "American ambassador to Luxembourg. Vodka and coffee liqueur, nothing else. "
             "Add cream and it becomes a White Russian.",
},
"Blood and Sand": {
    "about": "Named after the 1922 Rudolph Valentino bullfighting film and printed in the "
             "Savoy Cocktail Book in 1930. Equal parts Scotch, cherry liqueur, sweet "
             "vermouth and orange juice, which reads like a dare and somehow works.",
    "tip": "Equal parts is the published spec but a blended Scotch pushed slightly ahead "
           "of the other three keeps it from tipping into fruit punch.",
},
"Bloody Maria": {
    "about": "A Bloody Mary with tequila instead of vodka. The swap is not cosmetic: "
             "tequila has a vegetal edge that meets the tomato halfway, where vodka just "
             "sits underneath it.",
},
"Bloody Mary": {
    "about": "Fernand Petiot is generally credited, first at Harry's New York Bar in Paris "
             "in the 1920s and later at the St. Regis in New York, where management made "
             "him rename it the Red Snapper because Bloody Mary was considered too coarse.",
    "tip": "Do not shake it hard. Roll it between two tins or stir it. Hard shaking "
           "aerates the tomato juice and turns the texture thin and frothy.",
},
"Blue Hurricane": {
    "about": "A Hurricane rebuilt around blue curacao, so it is bright turquoise and "
             "tastes mostly of passion fruit and orange. Pure spectacle, and it knows it.",
},
"Bobby Burns Cocktail": {
    "about": "Named for Robert Burns, Scotland's national poet, and printed in the Savoy "
             "Cocktail Book. Scotch and sweet vermouth with a measure of Benedictine, "
             "which adds honey and herbs without making it sweet.",
},
"Boulevardier": {
    "about": "Erskine Gwynne, an American writer running a magazine in 1920s Paris, gets "
             "the credit via Harry MacElhone's 1927 book Barflies and Cocktails. It is a "
             "Negroni with bourbon in place of gin, and the whiskey rounds off the Campari "
             "in a way gin never does.",
    "tip": "Push the whiskey to 1 1/2 oz against 1 oz each of Campari and vermouth. Strict "
           "equal parts lets the Campari bully the bourbon.",
},
"Bourbon Renewal": {
    "about": "Jeffrey Morgenthaler's drink, and one of the more widely adopted modern "
             "recipes in this catalog. A bourbon sour with creme de cassis, which adds "
             "dark fruit without adding much sweetness.",
},
"Bramble": {
    "about": "Dick Bradsell created it at Fred's Club in London in the mid-1980s, aiming "
             "for something that tasted British. A gin sour over crushed ice with creme de "
             "mure drizzled through it so the drink bleeds red from the top down.",
    "tip": "Drizzle the blackberry liqueur over the finished drink and do not stir it. "
           "The gradient is the drink. Stirred in, it is just a purple sour.",
},
"Brandy Alexander": {
    "about": "The Alexander began as a gin drink and the brandy version overtook it "
             "completely. Cream, creme de cacao and brandy, served up with nutmeg. It is "
             "dessert and there is no use pretending otherwise.",
    "tip": "Grate the nutmeg fresh over the top. Pre-ground nutmeg tastes of dust and this "
           "drink has nowhere to hide it.",
},
"Brandy Cobbler": {
    "about": "The Cobbler is one of the oldest American drink families, documented by "
             "Jerry Thomas in 1862, and it is what made crushed ice and drinking straws "
             "popular in the first place. Spirit, sugar, fruit, mountain of ice.",
    "tip": "Crushed ice is not optional. The Cobbler dilutes as you drink it, which is the "
           "design. Cubes give you a strong first half and a watery second half.",
},
"Brandy Daisy": {
    "about": "The Daisy is a 19th century family: spirit, citrus, sweetener and a splash "
             "of soda, served over crushed ice. It matters historically because the "
             "Margarita is a Daisy, and margarita is Spanish for daisy.",
},
"Brandy Sour": {
    "about": "The sour template applied to brandy, and a good demonstration of why the "
             "template survived. Spirit, citrus, sugar, in balance, with nothing to hide "
             "behind.",
    "tip": "The egg white is optional but it is what turns this from a decent drink into "
           "one that looks like it came from a bar. Dry shake without ice first, then "
           "shake again with ice.",
},
"Brooklyn": {
    "about": "The least famous of the borough cocktails, printed in Jacques Straub's "
             "Drinks in 1914. Rye and dry vermouth with maraschino and Amer Picon, which "
             "is the reason it stayed obscure.",
    "tip": "Amer Picon is almost impossible to buy outside France. Amaro CioCiaro is the "
           "usual substitute and Ramazzotti will do at a push.",
},
"Brown Derby": {
    "about": "A 1930s Hollywood drink, named for the Brown Derby restaurant though most "
             "accounts say it was actually created at the Vendome Club nearby. Bourbon, "
             "grapefruit and honey, which is a sharper combination than it sounds.",
    "tip": "Honey syrup, not honey. Roughly three parts honey to one part warm water, "
           "stirred until it pours freely.",
},

# ============================ C ============================================

"Caesar": {
    "about": "Invented in Calgary in 1969 by Walter Chell and now drunk something like "
             "400 million times a year, almost entirely in Canada. The difference from a "
             "Bloody Mary is Clamato, tomato juice with clam broth in it, which sounds "
             "wrong and is not.",
    "tip": "Rim the glass with celery salt rather than plain salt, and do it with a lime "
           "wedge so it sticks. Plain salt makes it taste like seasoned soup.",
},
"Caipirinha": {
    "about": "Brazil's national drink and the reason anyone outside Brazil has heard of "
             "cachaca. The common account traces it to a Spanish flu remedy in Sao Paulo "
             "around 1918, which was lime, garlic and honey before the garlic sensibly "
             "left.",
    "tip": "Muddle the lime with the sugar, not with the cachaca. The sugar crystals "
           "abrade the peel and pull the oil out, which is where the flavour actually is.",
},
"Cameron's Kick": {
    "about": "From Harry MacElhone's 1922 ABC of Mixing Cocktails. Scotch and Irish "
             "whiskey together, with lemon and orgeat. Two whiskies in one glass is the "
             "entire point, so one bottle will not do it.",
    "tip": "Orgeat is almond syrup, not almond extract. It is what stops the two whiskies "
           "from simply arguing with each other.",
},
"Canchanchara": {
    "about": "From Trinidad in Cuba, and old enough that it is usually tied to the "
             "independence fighters of the 1800s. Rum, honey and lime, traditionally in a "
             "clay cup. The ancestor of the Daiquiri in everything but name.",
    "tip": "Loosen the honey with a splash of warm water before it goes anywhere near the "
           "lime, or it will sit at the bottom of the cup in a lump.",
},
"Cantarito": {
    "about": "Named for the clay cup it is served in, from Jalisco. Tequila with three "
             "citrus juices and a salt rim, topped with soda. The clay is not decoration: "
             "it keeps the drink cold and adds a faint earthiness.",
},
"Cape Codder": {
    "about": "Vodka and cranberry, which owes its existence to Ocean Spray's marketing "
             "department pushing cranberry juice as a mixer in the mid-1900s. Two "
             "ingredients and a lime.",
    "tip": "Cranberry juice, not cranberry cocktail, if you can find it. Cocktail blends "
           "are mostly apple or grape juice with sugar and the drink turns flat and sweet.",
},
"Cardinale": {
    "about": "A Negroni built with dry vermouth instead of sweet. Same gin, same Campari, "
             "completely different drink: sharper, drier, and noticeably more bitter "
             "without the sweet vermouth padding underneath.",
},
"Champagne Cocktail": {
    "about": "Documented by Jerry Thomas in 1862 and essentially unchanged since. A sugar "
             "cube soaked in bitters at the bottom of a flute, topped with champagne, so "
             "the drink slowly changes as the cube dissolves.",
    "tip": "Do not stir it. The cube is meant to sit there fizzing and sweetening the last "
           "third of the glass. Stirring gives you sweet champagne and nothing to watch.",
},
"Chatham Artillery Punch": {
    "about": "From Savannah, Georgia in the early 1800s, mixed by the local militia in "
             "ice-filled buckets and used, by most accounts deliberately, to flatten "
             "visiting dignitaries. Three base spirits at once, which makes it the rare "
             "drink that justifies owning a full shelf.",
    "tip": "This spec is scaled down to one glass. For a bowl, multiply by your guest "
           "count and build it over one large block of ice rather than cubes, which melt "
           "far too fast.",
},
"Chet Baker": {
    "about": "A modern drink, named for the trumpeter. Aged rum, sweet vermouth, honey and "
             "Angostura, in the Old Fashioned mould rather than the tiki one. Short, "
             "stirred and considerably more serious than most rum drinks.",
    "tip": "Honey syrup rather than neat honey, and stir it long enough. This is a spirit "
           "drink and it needs the dilution that 30 seconds of stirring gives you.",
},
"Chi-Chi": {
    "about": "A Pina Colada made with vodka instead of rum. The vodka does less, which "
             "some people prefer: it lets the coconut and pineapple do all the talking.",
    "tip": "No blender is not a dealbreaker. Shake it very hard over ice and pour it over "
           "fresh crushed ice. It will not be as thick but it will taste right.",
},
"Clover Club": {
    "about": "Named after a gentlemen's club that met at the Bellevue-Stratford Hotel in "
             "Philadelphia before Prohibition. Gin, lemon, raspberry and egg white, and it "
             "spent decades dismissed as frivolous before coming back properly.",
    "tip": "Dry shake without ice first to build the foam, then shake again with ice. Do "
           "it in the other order and the foam never forms.",
},
"Corpse Reviver #2": {
    "about": "From the Savoy Cocktail Book, 1930, in a chapter of drinks meant to be drunk "
             "before 11am. Harry Craddock's own note says four of them taken in swift "
             "succession will unrevive the corpse, which remains good advice.",
    "tip": "Equal parts gin, Cointreau, Lillet and lemon, with only a rinse of absinthe. "
           "Absinthe measured rather than rinsed will take over the entire drink.",
},
"Corpse Reviver No. 1": {
    "about": "The other Corpse Reviver, and much less known than the No. 2. Cognac, apple "
             "brandy and sweet vermouth, all spirit and no citrus, so it is a stirred "
             "drink where its sibling is a shaken one.",
},
"Cosmopolitan": {
    "about": "Attribution is genuinely contested, with claims from Toby Cecchini in New "
             "York in 1988 and from South Florida bartenders earlier in the decade. Sex "
             "and the City made it famous and then made it unfashionable, neither of which "
             "has much to do with whether it is a good drink.",
    "tip": "Cranberry is for colour and a little tartness, not bulk. Too much of it and "
           "you lose the citrus and end up with a pink vodka drink.",
},
"Cuba Libre": {
    "about": "Rum and Coke with a lime and a slogan attached. The name comes from the "
             "Cuban independence movement, and the drink is usually dated to Americans in "
             "Havana around 1900, shortly after Coca-Cola arrived on the island.",
    "tip": "Squeeze the lime in and drop the spent shell in with it. The oil from the peel "
           "is most of what separates this from rum and Coke.",
},

# ============================ D ============================================

"Daiquiri": {
    "about": "Named after a beach and an iron mine near Santiago de Cuba, where the "
             "American engineer Jennings Cox is credited with making it around 1898. Rum, "
             "lime and sugar in balance, and the drink every bartender uses to judge "
             "whether a bar is any good.",
    "tip": "There is nowhere to hide in three ingredients. Bottled lime juice will ruin "
           "it outright, and this is the drink where that is most obvious.",
},
"Dark and Stormy": {
    "about": "Bermuda's drink, and one of the very few cocktails with a trademark on it: "
             "Gosling's holds rights to the name in the US and maintains it has to be "
             "their Black Seal rum. Dark rum poured over ginger beer so it clouds "
             "downward, which is where the name comes from.",
    "tip": "Ginger beer first, rum floated on top. Building it the other way round mixes "
           "the two immediately and you lose the storm cloud.",
},
"Death in the Afternoon": {
    "about": "Hemingway's own recipe, contributed to a 1935 celebrity cocktail book and "
             "named after his book on bullfighting. Absinthe and champagne, nothing else. "
             "His written instruction was to drink three to five of them slowly, which "
             "should be read as a warning.",
    "tip": "Pour the champagne slowly into the absinthe and watch it turn cloudy. That "
           "louching is the anise oils dropping out of solution, and it is the whole "
           "visual point.",
},
"Dirty Martini": {
    "about": "A Martini with olive brine in it. The brine adds salt and body, which "
             "flattens the gin's sharper edges. Purists object, which has never once "
             "slowed the drink down.",
    "tip": "The brine is the liquid straight from the olive jar. Taste it first. Jars vary "
           "enormously in salt and some will wreck the drink at a quarter ounce.",
},
"Dry Rob Roy": {
    "about": "A Rob Roy made with dry vermouth instead of sweet, so the Scotch is far more "
             "exposed. Worth making if you like your Scotch drinks lean, and worth "
             "skipping if you were hoping for a Manhattan.",
},

# ============================ E - F ========================================

"El Diablo": {
    "about": "A Trader Vic drink from the 1940s. Tequila, creme de cassis, lime and ginger "
             "ale, which is a stranger combination than it reads: the blackcurrant and the "
             "ginger meet in the middle and the tequila holds the floor.",
},
"El Presidente": {
    "about": "Havana in the 1920s, named for the Cuban president and drunk heavily by "
             "Americans avoiding Prohibition. Rum, dry vermouth, curacao and a bar spoon "
             "of grenadine, stirred rather than shaken, which makes it a rum Martini more "
             "than a rum punch.",
    "tip": "The grenadine is a colouring agent and a rounding agent, not a sweetener. A "
             "quarter ounce is plenty and more will drag the whole thing sweet.",
},
"Espresso Martini": {
    "about": "Dick Bradsell made it in London in the late 1980s after a customer asked for "
             "something that would wake her up and get her drunk. It contains no vermouth "
             "and is not a Martini in any meaningful sense, but the name stuck.",
    "tip": "The foam only comes from fresh, hot espresso shaken hard against ice. Cold "
           "coffee or cold brew will taste fine and will not foam at all.",
},
"Fish House Punch": {
    "about": "From the State in Schuylkill fishing club near Philadelphia, founded 1732, "
             "which makes this plausibly the oldest American punch still in circulation. "
             "It is dangerously easy to drink, and by all accounts that was the intention.",
    "tip": "Scaled here to a single glass. As a bowl it wants a large ice block and an "
           "hour to sit, which is how punch was always meant to be served.",
},
"Fog Cutter": {
    "about": "Trader Vic's, and one of the heavier things he built: rum, brandy and gin in "
             "one glass with orgeat and citrus, finished with a sherry float. Vic's own "
             "line was that after two of these you would not taste the third.",
    "tip": "Three separate base spirits means this will not show as makeable unless you "
           "own all three. It is worth the shelf space more than most tiki drinks.",
},
"French 75": {
    "about": "Named after the French 75mm field gun of the First World War, on the grounds "
             "that it hits with similar force. Associated with Harry's New York Bar in "
             "Paris and printed in the Savoy Cocktail Book in 1930.",
    "tip": "Gin, lemon and sugar shaken first, then topped with champagne. Shaking the "
           "champagne is a mistake you only make once.",
},
"French Connection": {
    "about": "Cognac and amaretto, equal parts, no ice unless you want it. Named after the "
             "1971 film. Two ingredients and no technique, which makes it a good after "
             "dinner drink when you cannot be bothered.",
},

# ============================ G - H ========================================

"Gibson": {
    "about": "A Martini garnished with a pickled cocktail onion instead of an olive or a "
             "twist. Several origin stories compete and none of them win. The onion is not "
             "a gimmick: it adds a savoury note the olive does not.",
    "tip": "Do not add onion brine. That makes a different drink, and not a better one. "
           "The Gibson is dry and clean, and the onion is a garnish.",
},
"Gimlet": {
    "about": "Gin and lime, historically with Rose's lime cordial rather than fresh juice, "
             "which is why it tastes older than it looks. The Royal Navy scurvy story and "
             "the naval surgeon it is supposedly named after are repeated everywhere and "
             "confirmed nowhere.",
    "tip": "Fresh lime and simple syrup makes a sharper, brighter drink. Cordial makes the "
           "historical one. Both are correct, they are just not the same drink.",
},
"Gin And Tonic": {
    "about": "British officers in India took quinine against malaria, found it unbearable, "
             "and fixed it with gin, sugar and lime. The medicine stopped being necessary "
             "and the drink did not. Still the best argument for owning gin.",
    "tip": "Fill the glass completely with ice. A half-filled glass warms fast and the "
           "melt ruins it. More ice means less dilution, not more.",
},
"Godfather": {
    "about": "Scotch and amaretto, named after the film. Two ingredients, poured over ice, "
             "and the almond takes the edge off the Scotch without hiding it.",
},
"Gold Rush": {
    "about": "Created at Milk & Honey in New York around 2000, generally credited to T.J. "
             "Siegal. A Whiskey Sour with honey syrup instead of sugar, which is a small "
             "change that makes a substantially rounder drink.",
    "tip": "Honey syrup, three parts honey to one part warm water. Neat honey will not "
           "combine with cold lemon juice no matter how hard you shake it.",
},
"Grasshopper": {
    "about": "From Tujague's in New Orleans, usually dated to around 1918. Green creme de "
             "menthe, white creme de cacao and cream, in equal parts. It is mint chocolate "
             "chip ice cream in a glass and makes no apology for it.",
},
"Greenpoint": {
    "about": "Michael McIlroy's drink from Milk & Honey in New York, part of the wave of "
             "borough-named Manhattan variations. Rye with both vermouths and yellow "
             "Chartreuse, which gives it a honeyed, herbal centre.",
},
"Greyhound": {
    "about": "Gin or vodka with grapefruit juice, and that is the entire drink. Salt the "
             "rim and it becomes a Salty Dog, which is a genuinely different experience "
             "for the sake of one ingredient.",
},
"Hanky Panky": {
    "about": "Ada Coleman created it at the American Bar at the Savoy in London, where she "
             "was head bartender in an era when that was close to unheard of. The actor "
             "Charles Hawtrey tried it and said it was the real hanky-panky, and the name "
             "stuck.",
    "tip": "Two dashes of Fernet-Branca, no more. It is the most assertive bottle in most "
           "people's collections and a heavy hand turns this into medicine.",
},
"Harvard": {
    "about": "Brandy, sweet vermouth and bitters, which makes it a Manhattan with cognac "
             "in place of whiskey. Late 1800s, from the era when every drink was named "
             "after a university or a club.",
},
"Hemingway Daiquiri": {
    "about": "Constantino Ribalaigua made it for Hemingway at El Floridita in Havana. "
             "Hemingway asked for no sugar and double rum, which is why the original is "
             "also called the Papa Doble. Grapefruit and maraschino do the work the sugar "
             "would have.",
    "tip": "The historically accurate version has no sugar at all and is bracingly dry. "
           "A quarter ounce of simple syrup makes it drinkable for most people.",
},
"Horse's Neck": {
    "about": "Started in the 1890s as a soft drink: ginger ale, ice, and a long lemon "
             "peel. Someone added the whiskey and the name stayed. The peel is the point, "
             "so cut it properly.",
    "tip": "Peel the lemon in one continuous spiral and hook it over the rim before you "
           "add ice. Trying to thread it in afterwards does not work.",
},
"Hot Toddy": {
    "about": "Spirit, honey, lemon and hot water, and old enough that the etymology is "
             "argued over between Scotland and India. Whether or not it does anything for "
             "a cold, it is the drink people reach for when they have one.",
    "tip": "Warm the mug with hot water first and pour it out. A cold mug drops the "
           "temperature immediately and a lukewarm toddy is a sad object.",
},
"Hugo Spritz": {
    "about": "Roland Gruber created it in South Tyrol in 2005, originally with lemon balm "
             "syrup before elderflower took over. Lighter and more floral than an Aperol "
             "Spritz, and not bitter at all.",
},
"Hurricane": {
    "about": "Pat O'Brien's in New Orleans, 1940s. Whiskey was scarce during the war and "
             "distributors forced bars to take crates of rum to get any, so O'Brien's "
             "invented something to move it. The glass is shaped like a hurricane lamp.",
    "tip": "Splitting the rum between a light and an aged bottle is the upgrade. Published "
           "specs disagree wildly on this drink, so treat any single version as one "
           "opinion.",
},

# ============================ I - L ========================================

"Irish Coffee": {
    "about": "Joe Sheridan made it at Foynes airbase in Ireland in the 1940s for cold, "
             "delayed transatlantic passengers. A travel writer named Stanton Delaplane "
             "took it to the Buena Vista in San Francisco in 1952 and it went from there.",
    "tip": "The cream has to float, which means it must be lightly whipped to a pourable "
           "thickness and poured over the back of a spoon. Then drink through it, not "
           "around it.",
},
"Jamaican Mule": {
    "about": "A Moscow Mule built on Jamaican rum, which has enough funk to stand up to "
             "the ginger rather than disappearing under it. Lime, rum, ginger beer, over "
             "a lot of ice.",
    "tip": "Ginger beer, not ginger ale. Ale is sweet and mild and makes a noticeably "
           "duller drink.",
},
"Japanese Cocktail": {
    "about": "In Jerry Thomas's 1862 Bartender's Guide, and thought to be connected to the "
             "first Japanese diplomatic mission to the United States in 1860. Brandy, "
             "orgeat and bitters, with nothing Japanese in it at all.",
    "tip": "Three ingredients and no citrus in the glass, which is unusual for a drink "
           "this old. The lemon twist is doing the citrus work entirely through oil.",
},
"John Collins": {
    "about": "The Collins family is spirit, lemon, sugar and soda in a tall glass. The "
             "name traces back to a head waiter at Limmer's Hotel in London. Made with Old "
             "Tom gin it is a Tom Collins, and the John is now usually whiskey.",
},
"Juan Collins": {
    "about": "A Collins built with tequila. The template is durable enough that it takes "
             "almost any base spirit, and tequila gives it a vegetal edge that gin does "
             "not.",
},
"Jungle Bird": {
    "about": "Created at the Kuala Lumpur Hilton in 1978 and largely forgotten until tiki "
             "revivalists dug it out. Dark rum and Campari with pineapple, which is the "
             "rare tiki drink built around bitterness rather than sweetness.",
    "tip": "Campari and pineapple is the whole idea. Do not reduce the Campari to make it "
           "friendlier, because friendly is not what this drink is for.",
},
"Kalimotxo": {
    "about": "Red wine and cola, from the Basque Country, generally credited to a festival "
             "in Getxo in the 1970s where the wine on hand was bad enough to need "
             "rescuing. Enormously popular in Spain and treated with suspicion everywhere "
             "else.",
    "tip": "Do not use good wine. The point is that it rescues cheap wine, and decent "
           "wine just tastes ruined.",
},
"Kamikaze": {
    "about": "Vodka, triple sec and lime in equal parts. A Margarita template with vodka, "
             "or a Cosmopolitan without the cranberry, depending which direction you come "
             "at it from.",
},
"Kentucky Mule": {
    "about": "A Moscow Mule with bourbon. Vodka contributes nothing to a Mule by design, "
             "so swapping in something with actual flavour is an obvious improvement.",
},
"Kir Royale": {
    "about": "The Kir is white wine and creme de cassis, named after Felix Kir, a "
             "Resistance figure and long-serving mayor of Dijon who promoted it. The "
             "Royale swaps the white wine for champagne.",
    "tip": "Cassis first, champagne poured slowly over the back of a spoon. Adding cassis "
           "to a full flute makes it fizz over.",
},
"Lemon Drop": {
    "about": "Created by Norman Jay Hobday at Henry Africa's in San Francisco in the "
             "1970s, in what is often called the first fern bar. Vodka, triple sec and "
             "lemon with a sugared rim, and it is essentially a sour in disguise.",
},
"Long Island Iced Tea": {
    "about": "Attribution is contested between Robert Butt at the Oak Beach Inn on Long "
             "Island in 1972 and an earlier Prohibition-era drink from a place called Long "
             "Island in Tennessee. Five spirits and a splash of cola, and it contains no "
             "tea.",
    "tip": "It looks like a joke drink and it is not. Half an ounce of each spirit still "
           "adds up to roughly triple a normal cocktail. Measure it properly.",
},

# ============================ M ============================================

"Mai Tai": {
    "about": "Trader Vic claimed it in Oakland in 1944 and Don the Beachcomber claimed an "
             "earlier one, which is the standard tiki dispute. The name is from the "
             "Tahitian maitai, meaning good, reportedly what the first person to try it "
             "said. The original had no pineapple juice in it at all.",
    "tip": "Orgeat is the ingredient that makes this a Mai Tai rather than a rum sour. If "
           "you skip it you are making something else.",
},
"Mamie Taylor": {
    "about": "Rochester, New York, 1899, named for an opera singer who ordered something "
             "else entirely and got this instead. It predates the Moscow Mule by half a "
             "century and is arguably the better drink.",
    "tip": "A smoky Scotch works surprisingly well here. The ginger is sweet enough to "
           "carry peat that would overwhelm a lighter mixer.",
},
"Manhattan": {
    "about": "New York, 1880s, associated with the Manhattan Club. The popular story that "
             "Winston Churchill's mother invented it at a party is repeated constantly and "
             "is not true: she was in England and pregnant with him at the time.",
    "tip": "Stir, do not shake. Shaking a drink with no citrus in it makes it cloudy and "
           "over-aerated, and you can taste the difference immediately.",
},
"Margarita": {
    "about": "Structurally a Daisy, the 19th century family of spirit, citrus and orange "
             "liqueur, and margarita is Spanish for daisy. Half a dozen people have "
             "claimed to have invented it and none of the claims hold up cleanly.",
    "tip": "Salt half the rim, not all of it. It lets you take a sip either way and most "
           "people discover they prefer one.",
},
"Martinez 2": {
    "about": "Widely treated as the missing link between the Manhattan and the Martini. "
             "Old Tom gin, sweet vermouth, maraschino and orange bitters, which makes it "
             "far sweeter and rounder than a modern Martini.",
    "tip": "Old Tom gin is the historically correct choice and is sweeter than London Dry. "
           "With London Dry, ease off the vermouth slightly or it turns thin.",
},
"Mary Pickford": {
    "about": "Havana in the 1920s, named for the silent film star, from the era when "
             "Hollywood went to Cuba to drink. Rum, pineapple, grenadine and maraschino, "
             "pale pink and considerably drier than it looks.",
    "tip": "Published specs disagree on how much maraschino belongs here, from a bar spoon "
           "to a full quarter ounce. Start low. It is a loud liqueur.",
},
"Matador": {
    "about": "Tequila, pineapple and lime. Simple, tart, and one of the easier ways to "
             "drink tequila long without reaching for grapefruit soda.",
},
"Mexican Mule": {
    "about": "A Mule with tequila. Ginger and agave are a natural pairing, arguably more "
             "so than ginger and vodka, which is the version everyone knows.",
},
"Mezcal Negroni": {
    "about": "A Negroni with mezcal standing in for gin. The smoke and the Campari's "
             "bitterness pull in the same direction, which makes this a heavier, moodier "
             "drink than the original rather than just a smoky version of it.",
    "tip": "Mezcal is more assertive than gin. Pulling it back to three quarters of an "
           "ounce against a full ounce of each of the others keeps it balanced.",
},
"Milano-Torino": {
    "about": "Campari from Milan, sweet vermouth from Turin, equal parts, no soda. This is "
             "the drink the Americano was built from in 1860s Milan, and it is still the "
             "cleanest way to taste what each of those two bottles actually does.",
    "tip": "Add soda and it is an Americano. Add gin and it is a Negroni. Learning this "
           "one first makes the other two make sense.",
},
"Mimosa": {
    "about": "Credited to the Ritz in Paris around 1925 and named after the yellow "
             "flowering shrub. Orange juice and champagne in roughly equal parts, and "
             "there is nothing else to it.",
    "tip": "Chill both properly and pour the champagne down the side of the glass. Warm "
           "juice kills the bubbles faster than anything else you could do to it.",
},
"Mint Julep": {
    "about": "American and considerably older than its Kentucky Derby association, which "
             "only became official in 1938. Bourbon, sugar and mint over a packed cup of "
             "crushed ice, traditionally in metal so it frosts on the outside.",
    "tip": "Do not shred the mint. Press it gently against the sugar to release oil. "
           "Torn mint releases chlorophyll and the drink turns grassy and bitter.",
},
"Mojito": {
    "about": "Cuban, and usually traced to an older drink called El Draque, which links "
             "back to Francis Drake's crew in the 1500s taking aguardiente with lime and "
             "mint. The chain of evidence is thin but the drink is genuinely old.",
    "tip": "Persuade the mint, do not pulverise it. A firm press against the sugar is "
           "enough. Muddling it to a pulp makes the drink taste of lawn.",
},
"Morning Glory Fizz": {
    "about": "A Victorian hangover cure, and it takes that job seriously: Scotch, lemon, "
             "egg white, a dash of absinthe and soda on top. Jerry Thomas's era, when "
             "drinks were prescribed as much as ordered.",
    "tip": "Dry shake without ice first for the foam, then shake with ice, then top with "
           "soda in the glass. Soda in the shaker is how you get a mess.",
},
"Moscow Mule": {
    "about": "Invented in 1941 in Los Angeles by a Smirnoff executive with vodka nobody "
             "wanted and a bar owner with ginger beer nobody wanted. The copper mugs were "
             "a third party's unsold stock. It is essentially a drink built out of "
             "inventory problems, and it worked.",
    "tip": "The copper mug is not just branding. It takes the cold fast and holds it, so "
           "the drink stays colder than it would in glass.",
},

# ============================ N - O ========================================

"Negroni": {
    "about": "Florence, around 1919. Count Camillo Negroni asked for his Americano "
             "strengthened with gin instead of soda, and the bar started making them for "
             "everyone. Equal parts gin, Campari and sweet vermouth, and it has been right "
             "ever since.",
    "tip": "Stir it in the glass over one large cube. Small ice dilutes it fast, and this "
           "is a drink you are meant to sit with.",
},
"Negroni Sbagliato": {
    "about": "Sbagliato means mistaken. Mirko Stocchetto at Bar Basso in Milan reached for "
             "gin, grabbed sparkling wine instead, and served it anyway. Lighter, fizzier "
             "and around half the strength of the original.",
},
"New York Sour": {
    "about": "A Whiskey Sour with a float of red wine sitting on top. Late 1800s, and the "
             "wine is not decoration: it adds tannin and dark fruit that meets the lemon "
             "on the way down.",
    "tip": "Float the wine over the back of a spoon and do not stir. Mixed in, it just "
           "muddies the colour and you lose the layered first sip.",
},
"Nikolaschka": {
    "about": "German, and more of a ritual than a cocktail. A glass of cognac with a lemon "
             "slice laid across the rim, sugar on one half and ground coffee on the other. "
             "You eat the lemon, then drink the cognac.",
    "tip": "Fold the lemon slice in half and put the whole thing in your mouth first, then "
           "the cognac. Doing it in the other order defeats the entire point.",
},
"Oaxaca Old Fashioned": {
    "about": "Phil Ward created it at Death & Co in New York around 2007 and it did more "
             "than almost any other drink to put mezcal behind ordinary bars. Tequila and "
             "mezcal together with agave and mole bitters.",
    "tip": "Flame the orange twist if you can. Holding a lit match under the peel as you "
           "squeeze it caramelises the oil and it meets the smoke properly.",
},
"Old Fashioned": {
    "about": "This is what the word cocktail originally meant: spirit, sugar, water and "
             "bitters, full stop. By the late 1800s bars had started adding things, so "
             "drinkers began asking for it the old fashioned way, and the name is "
             "literally that request.",
    "tip": "No muddled fruit. The orange and cherry salad is a later addition and it "
           "turns a spirit drink into a fruit one. Express a twist over the top instead.",
},
"Old Pal": {
    "about": "From Harry MacElhone's Barflies and Cocktails, 1927, out of the same Paris "
             "scene as the Boulevardier. Rye, dry vermouth and Campari, so it is the lean, "
             "dry, considerably more bitter cousin.",
    "tip": "Equal parts is the historical spec. Pushing the rye to an ounce and a half "
           "makes it friendlier if you find the original too austere.",
},
"Oreo Mudslide": {
    "about": "Vodka, coffee liqueur and Irish cream blended with ice cream. Not a cocktail "
             "in any traditional sense and not trying to be. It is a milkshake that will "
             "get you drunk.",
    "tip": "Blend until completely smooth before you even think about the cookie. Chunks "
           "of unblended ice cream ruin the texture and cannot be fixed afterwards.",
},

# ============================ P ============================================

"Painkiller": {
    "about": "From the Soggy Dollar Bar on Jost Van Dyke in the British Virgin Islands, so "
             "named because the beach has no dock and you swim ashore with wet money. "
             "Pusser's later trademarked the name and defends it aggressively.",
    "tip": "Grate the nutmeg fresh over the top. It is the one ingredient that separates "
           "this from a pina colada with orange juice in it.",
},
"Paloma": {
    "about": "Far and away the most popular tequila drink in Mexico, well ahead of the "
             "Margarita, and almost always made with grapefruit soda straight from the "
             "bottle rather than anything measured.",
    "tip": "Grapefruit soda, not grape soda. Squirt or Jarritos Toronja are the usual "
           "choices. Salt the rim and squeeze in extra lime to cut the sweetness.",
},
"Paper Plane": {
    "about": "Sam Ross created it in 2007 for The Violet Hour in Chicago and named it "
             "after the M.I.A. song. Equal parts bourbon, Aperol, Amaro Nonino and lemon, "
             "and the equal-parts structure is a large part of why it caught on.",
    "tip": "Amaro Nonino is not easily substituted. It is grappa-based and lighter than "
           "most amari, and swapping in Averna or Montenegro makes a noticeably heavier "
           "drink.",
},
"Pegu Club": {
    "about": "Named after the British officers' club in Rangoon and printed in the Savoy "
             "Cocktail Book in 1930. Gin, orange curacao and lime with two kinds of "
             "bitters, and the bitters are what stop it being a gin sour.",
},
"Penicillin": {
    "about": "Sam Ross made it at Milk & Honey in New York around 2005 and it is probably "
             "the most widely copied cocktail of this century. Blended Scotch with honey, "
             "ginger and lemon, finished with a float of Islay Scotch so the smoke arrives "
             "at the nose before the drink does.",
    "tip": "The Islay float is meant to sit on top and not be stirred in. One bottle can "
           "do both jobs, but if you own a peated Scotch this is what it is for.",
},
"Pimm's Cup": {
    "about": "James Pimm sold it at his London oyster bar in the 1840s as a digestive "
             "tonic. It is now permanently attached to Wimbledon, where they get through "
             "something in the order of 300,000 glasses a fortnight.",
    "tip": "Lemonade in the British sense, meaning cloudy sparkling lemonade, not American "
           "still lemonade. Ginger ale is the usual North American substitute.",
},
"Pina Colada": {
    "about": "Puerto Rico's official drink. Ramon Marrero at the Caribe Hilton in 1954 is "
             "the most cited creator, though at least two other bartenders have claimed "
             "it. Rum, coconut and pineapple, blended.",
    "tip": "Coconut cream, not coconut milk and not coconut water. Cream of coconut is "
           "sweetened and thick, and it is what gives the drink its body.",
},
"Pink Lady": {
    "about": "Gin, grenadine, cream and egg white. It spent most of the late 20th century "
             "as a punchline about unserious drinks, which was unfair: it is a "
             "well-constructed gin sour with a soft edge.",
    "tip": "Dry shake without ice first to build the foam, then shake again with ice. The "
           "pale pink crown only forms if you do it in that order.",
},
"Pisco Punch": {
    "about": "Duncan Nicol served it at the Bank Exchange saloon in San Francisco in the "
             "late 1800s and took the recipe to his grave, which is why every version "
             "since is reconstruction. Pisco with pineapple and citrus.",
},
"Pisco Sour": {
    "about": "Victor Vaughen Morris is generally credited, at his bar in Lima in the "
             "1920s. Peru and Chile both claim the drink as national property and the "
             "argument is entirely serious.",
    "tip": "The Angostura goes on top of the foam at the end, not in the shaker. Dashed "
           "over the surface it is aroma; shaken in it just muddies the colour.",
},
"Planter's Punch": {
    "about": "Jamaican, and old enough to come with a rhyme that doubles as the recipe: "
             "one of sour, two of sweet, three of strong, four of weak. That structure "
             "underpins a large share of rum drinks that came later.",
},
"Pornstar Martini": {
    "about": "Douglas Ankrah created it in London around 2002, originally under the name "
             "Maverick Martini. Passion fruit and vanilla vodka, served with a shot of "
             "prosecco alongside rather than in it. Consistently one of the best selling "
             "cocktails in Britain.",
    "tip": "The prosecco goes in a separate shot glass on the side. Alternate sips. "
           "Pouring it in is a different and much less interesting drink.",
},

# ============================ Q - R ========================================

"Queen's Park Swizzle": {
    "about": "From the Queen's Park Hotel in Trinidad, and effectively a Mojito that grew "
             "up. Rum, lime, sugar and mint swizzled over crushed ice, with a heavy dose "
             "of Angostura floated on top.",
    "tip": "Dash the bitters over the finished ice dome and do not stir them in. The first "
           "sip is aromatic and the rest is not, which is the entire design.",
},
"Ramos Gin Fizz": {
    "about": "Henry Ramos, New Orleans, 1888. It became so popular that his bar employed "
             "teams of shaker boys passing the tin down a line, because the drink was "
             "understood to need twelve minutes of shaking. It does not, but it needs more "
             "than you want to give it.",
    "tip": "Dry shake without ice for a full minute, then shake hard with ice, then let it "
           "sit before topping with soda. Rushing any of the three stages collapses the "
           "head.",
},
"Ranch Water": {
    "about": "West Texas, tequila and lime topped with Topo Chico. Barely a cocktail and "
             "not pretending to be one. Three ingredients, no shaker, and it is very hard "
             "to make it badly.",
    "tip": "Highly carbonated mineral water makes a real difference here over ordinary "
           "soda water. There is nothing else in the glass to carry it.",
},
"Remember the Maine": {
    "about": "Recorded by Charles H. Baker, who claimed he drank it in Havana in 1933 "
             "while a revolution was going on outside. Named after the USS Maine, whose "
             "explosion in Havana harbour started the Spanish-American War. Rye, sweet "
             "vermouth, cherry liqueur and absinthe.",
    "tip": "Baker's own instruction was to stir it gently, in a clockwise direction, while "
           "gazing into the distance. The gazing is optional.",
},
"Revolver": {
    "about": "Jon Santer's drink from San Francisco in the 2000s. A Manhattan-shaped "
             "bourbon drink with coffee liqueur in place of vermouth and a flamed orange "
             "peel, which gives it a roasted, slightly burnt-orange top note.",
    "tip": "Flame the orange peel: hold a lit match an inch from the skin and squeeze. The "
           "caramelised oil is most of what makes this drink distinctive.",
},
"Rob Roy": {
    "about": "Created at the Waldorf Astoria in New York in 1894 to mark the opening of an "
             "operetta about the Scottish outlaw Rob Roy MacGregor. It is a Manhattan with "
             "Scotch, and the Scotch changes it more than you would expect.",
},
"Rosita": {
    "about": "A tequila Negroni with both vermouths, printed in the Mr. Boston guide in "
             "the 1970s and pulled back into circulation by Gary Regan decades later. "
             "Bitter, herbal and considerably drier than most tequila drinks.",
},
"Rum Old Fashioned": {
    "about": "The Old Fashioned template is indifferent to which spirit you use, and aged "
             "rum takes to it better than almost anything except bourbon. The rum is "
             "already faintly sweet, so it needs less sugar than the original.",
    "tip": "Go lighter on the syrup than you would with bourbon, and use demerara syrup "
           "instead of simple if you ever make it twice.",
},
"Rusty Nail": {
    "about": "Scotch and Drambuie, which is itself Scotch sweetened with honey and herbs. "
             "It found its audience in the 1960s and has been Rat Pack shorthand ever "
             "since. Two ingredients, one of which is most of the other.",
    "tip": "Start at three parts Scotch to one part Drambuie. Older recipes call for equal "
           "parts and most people now find that far too sweet.",
},

# ============================ S ============================================

"Salty Dog": {
    "about": "A Greyhound with a salted rim, and the salt is not a garnish: it suppresses "
             "bitterness, so the grapefruit reads sweeter and rounder than it does without "
             "it. One of the clearest demonstrations that a rim can change a drink.",
    "tip": "Salt only half the rim. It gives you a direct comparison in the same glass, "
           "and the difference is larger than most people expect.",
},
"Saratoga": {
    "about": "In Jerry Thomas's 1887 edition, from the era when Saratoga Springs was where "
             "New York went in the summer. Brandy and rye together with sweet vermouth, "
             "which is a split base you rarely see now.",
},
"Sazerac": {
    "about": "New Orleans, and named after Sazerac de Forge et Fils, the cognac brand that "
             "was the original base before rye took over. The Peychaud's is not "
             "substitutable: Antoine Peychaud was a local apothecary and his bitters are "
             "what make it taste like this and not like an Old Fashioned.",
    "tip": "The absinthe is a rinse, not an ingredient. Coat the chilled glass, tip out "
           "the excess, and build the drink separately. Measured in, it takes over.",
},
"Scofflaw": {
    "about": "Made at Harry's New York Bar in Paris in 1924, days after a Boston "
             "competition coined the word scofflaw for someone who drank through "
             "Prohibition. Naming a cocktail after it, in Paris, was the joke.",
},
"Scotch Highball": {
    "about": "Scotch and soda over ice. The highball is the format that most of the world "
             "actually drinks whisky in, and Japan in particular has turned it into "
             "something close to a discipline.",
    "tip": "Chill the glass, fill it completely with ice, and stir the Scotch alone for a "
           "moment before adding soda. Then stir once. Every extra stir costs you bubbles.",
},
"Screwdriver": {
    "about": "Vodka and orange juice. The name is usually explained by American oil "
             "workers stirring theirs with whatever tool was in reach, which is a story "
             "with no evidence behind it and enormous staying power.",
},
"Sea breeze": {
    "about": "Vodka, cranberry and grapefruit. Same family as the Cape Codder and the Bay "
             "Breeze, distinguished only by which juices go in. The grapefruit is what "
             "keeps it from being simply sweet.",
},
"Seelbach": {
    "about": "Presented for years as a lost 1917 recipe rediscovered at the Seelbach Hotel "
             "in Louisville. In 2016 the hotel's own former bar manager admitted he made "
             "the whole story up in the 1990s and invented the drink himself. It is "
             "excellent, which is presumably why nobody checked.",
    "tip": "Seven dashes each of Angostura and Peychaud's, which looks like a typo and is "
           "not. The bitters are a primary ingredient here, not a seasoning.",
},
"Sex on the Beach": {
    "about": "A late 1980s Florida drink, generally attributed to spring break promotions "
             "for peach schnapps. Vodka, peach, cranberry and orange. Its reputation is "
             "worse than the drink deserves, but not by an enormous margin.",
},
"Sherry Cobbler": {
    "about": "One of the most popular drinks in 19th century America, and the one that "
             "made drinking straws and crushed ice mainstream. Dickens gave it a scene in "
             "Martin Chuzzlewit where an Englishman tries one and is visibly changed.",
    "tip": "Muddle the orange slices with the syrup before anything else goes in. The "
           "citrus oil from the peel is what lifts the sherry.",
},
"Sidecar": {
    "about": "Contested between the Ritz in Paris and Buck's Club in London, both around "
             "the end of the First World War. The story attached to it, an officer driven "
             "to the bar in a motorcycle sidecar, is repeated everywhere and confirmed "
             "nowhere.",
    "tip": "Sugar the rim only if your Cointreau is on the drier side. Between the sugar "
           "rim and the liqueur it is easy to overshoot.",
},
"Siesta": {
    "about": "Katie Stipe created it in New York in 2006. A Hemingway Daiquiri rebuilt on "
             "tequila, with Campari where the maraschino would be, which gives it a "
             "bitter, grapefruit-forward finish.",
},
"Singapore Sling": {
    "about": "From the Long Bar at Raffles Hotel in Singapore, made by Ngiam Tong Boon "
             "around 1915. The original recipe was lost, so every modern version including "
             "this one is a reconstruction, and they differ substantially from each other.",
},
"Southside": {
    "about": "Gin, lime and mint, essentially a Mojito without the rum or the soda. "
             "Attribution splits between a Long Island sportsmen's club and Chicago's "
             "South Side during Prohibition, where the story is that the local gin was bad "
             "enough to need the mint.",
},
"Suffering Bastard": {
    "about": "Joe Scialom built it at Shepheard's Hotel in Cairo in 1942 as a hangover "
             "cure for British officers in the North African campaign. Gin and cognac in "
             "the same glass is unusual, and it works.",
    "tip": "Shake it only briefly. It gets topped with ginger beer, so over-diluting in "
           "the tin leaves you with a thin drink.",
},

# ============================ T ============================================

"Tequila Old Fashioned": {
    "about": "The Old Fashioned template with tequila and agave syrup in place of bourbon "
             "and sugar. Stirred, spirit-forward and short, which is the opposite of what "
             "most people expect a tequila drink to be.",
    "tip": "Blanco works but reposado is better here. The vanilla and oak from the barrel "
           "are doing the job the bourbon would have done.",
},
"Tequila Sour": {
    "about": "The sour template on tequila. It is less common than the Margarita and "
             "arguably a better showcase, because there is no orange liqueur in the way of "
             "the agave.",
    "tip": "Dry shake first without ice to build the foam, then shake again with ice. "
           "Skipping the dry shake gives you a flat drink with no head.",
},
"Tequila Sunrise": {
    "about": "The modern version is from the Trident in Sausalito in the early 1970s, and "
             "it spread because the Rolling Stones drank their way through them on the "
             "1972 American tour. The gradient comes from grenadine sinking, not from "
             "layering.",
    "tip": "Pour the grenadine last, slowly, down the inside of the glass. It is denser "
           "than the juice and will sink and bloom on its own. Do not stir it.",
},
"The Last Word": {
    "about": "From the Detroit Athletic Club around 1916, then completely forgotten until "
             "Murray Stenson found it in an old book and put it on a Seattle menu in 2004. "
             "Equal parts gin, green Chartreuse, maraschino and lime.",
    "tip": "Green Chartreuse is made by monks to a recipe almost nobody knows, and it is "
           "not substitutable. Equal parts is also not negotiable in this one.",
},
"Ti' Punch": {
    "about": "Martinique's everyday drink. The lime is a coin cut from the side of the "
             "fruit rather than a wedge, so you get oil and a little juice but no pith. "
             "Traditionally served without ice and mixed by the drinker, not the bartender.",
    "tip": "Rhum agricole, made from cane juice rather than molasses, is the real thing "
           "and tastes grassy and sharp. Any decent white rum still makes a good drink.",
},
"Toasted Almond": {
    "about": "Amaretto, coffee liqueur and cream. A dessert drink from the era when those "
             "were a category, and it does exactly what the name promises with no "
             "complications.",
},
"Tom Collins": {
    "about": "Named for Old Tom gin, the sweeter style it was originally built on. It also "
             "shares a name with an 1874 New York prank where people were told a man named "
             "Tom Collins was badmouthing them in a nearby bar, and sent off to find him.",
    "tip": "Build it in the glass over ice and top with soda. Shaking the soda is the one "
           "way to get this wrong.",
},
"Tommy's Margarita": {
    "about": "Julio Bermejo created it at his family's restaurant in San Francisco around "
             "1990 by dropping the orange liqueur and using agave syrup instead. Three "
             "ingredients, and it tastes far more of tequila than the original.",
    "tip": "Agave syrup is sweeter than simple syrup, so use less than you think. Thinning "
           "it with a little water first makes it much easier to mix cold.",
},

# ============================ V - Z ========================================

"Vampiro": {
    "about": "Mexican, tequila with sangrita, which is a tomato, citrus and chilli mixer "
             "traditionally sipped alongside tequila rather than mixed into it. Savoury, "
             "spicy, and a long way from a Margarita.",
},
"Vermouth Cocktail": {
    "about": "Vermouth, bitters, ice, twist. It appears in the earliest cocktail books and "
             "it is the simplest possible demonstration that vermouth is a drink in its "
             "own right rather than a modifier.",
    "tip": "Only worth making with a bottle opened recently and kept in the fridge. "
           "Vermouth is wine and it oxidises. There is nothing else here to hide it.",
},
"Vesper": {
    "about": "Ian Fleming wrote it into Casino Royale in 1953 and named it after Vesper "
             "Lynd. Kina Lillet, the original ingredient, no longer exists in the form he "
             "meant, so nobody alive has had the drink exactly as written.",
    "tip": "Fleming specified shaken, which is why everyone remembers it. Shaking a "
           "citrus-free drink over-dilutes and clouds it, so stir if you care more about "
           "the drink than the reference.",
},
"Vieux Carré": {
    "about": "Walter Bergeron created it at the Hotel Monteleone in New Orleans in 1938 "
             "and named it after the French Quarter. Rye and cognac together with vermouth "
             "and Benedictine, which makes it one of the most layered drinks in the "
             "catalog.",
    "tip": "Two base spirits means two bottles, and half an ounce each is deliberate. This "
             "is a sipping drink and it is stronger than it tastes.",
},
"Vodka Gimlet": {
    "about": "A Gimlet with vodka, which strips out the botanical layer and leaves lime "
             "and cold. Some people want exactly that, and there is no arguing with it.",
    "tip": "Fresh lime, not cordial. Rose's makes a completely different and much sweeter "
           "drink, and with vodka there is nothing else to balance it.",
},
"Vodka Martini": {
    "about": "The Martini with vodka in place of gin, which became the default in the "
             "second half of the twentieth century largely through advertising. Vodka "
             "contributes texture and cold rather than flavour, so the vermouth matters "
             "more here, not less.",
    "tip": "Dry vermouth specifically. Sweet vermouth makes something else entirely, and "
           "the vermouth needs to be fresh because there is no gin to cover for it.",
},
"Vodka Sour": {
    "about": "A sour with vodka in place of whiskey. The template is strong enough to "
             "carry a base spirit that brings nothing of its own, which is a decent "
             "argument for how good the template is.",
    "tip": "Dry shake without ice first for the foam, then shake with ice. The egg white "
           "is doing all the texture work here.",
},
"Ward Eight": {
    "about": "Boston, 1898, traditionally said to have been made at Locke-Ober to "
             "celebrate an election win in the city's eighth ward, on the night before the "
             "votes were counted. A rye sour with grenadine.",
},
"Whiskey Smash": {
    "about": "The Smash is a julep with citrus in it, documented as its own family since "
             "the 1800s. Whiskey, lemon, sugar and mint over crushed ice, and it is what "
             "to make when someone says they do not like whiskey.",
    "tip": "Muddle the lemon wedges themselves, not just the juice. The oil in the peel is "
           "half the drink.",
},
"Whiskey Sour": {
    "about": "Documented by Jerry Thomas in 1862 and the template that most cocktails on "
             "this list are variations of. Spirit, citrus, sugar. Everything else is "
             "detail.",
    "tip": "Dissolve the sugar in the lemon juice before the whiskey and ice go in. "
           "Undissolved sugar sinks and the drink gets sweeter as you go down the glass.",
},
"White Lady": {
    "about": "Harry MacElhone's, though he made two versions: an early one with creme de "
             "menthe that he later disowned, and the gin, Cointreau and lemon version "
             "everyone now means. Essentially a Sidecar built on gin.",
},
"White Russian": {
    "about": "A Black Russian with cream floated on top. It existed quietly for decades "
             "and then The Big Lebowski came out in 1998 and it has never gone away since.",
    "tip": "Float the cream over the back of a spoon rather than stirring it in. It looks "
           "better and the first few sips are noticeably different from the last.",
},
"Woo Woo": {
    "about": "Vodka, peach schnapps and cranberry. A late 1980s drink with no history "
             "worth reporting and no ambitions beyond being pink and easy, which it "
             "achieves completely.",
},
"Zombie": {
    "about": "Don the Beachcomber, Hollywood, mid-1930s, and the drink that effectively "
             "started tiki. He limited customers to two, and kept the recipe secret by "
             "having staff work from coded, pre-mixed bottles so none of them could copy "
             "it.",
    "tip": "The two-drink limit was not showmanship. Three rums plus an overproof float is "
           "close to four standard drinks in one glass.",
},

}
