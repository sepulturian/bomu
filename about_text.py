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
4. Plain, conversational human prose: zero em-dashes, zero menu-copy fluff,
   and varied sentence structures.

Keys are recipe names exactly as they appear in the `recipes` table.
"""

ABOUT = {

# ============================ A ============================================

"Adonis": {
    "about": "An 1884 Broadway musical of the same name ran for more than 500 performances "
             "and gave its name to this low-proof aperitif. Because it uses sherry and sweet "
             "vermouth with no hard liquor at all, it sits around 15% ABV and makes an easy "
             "opener before dinner.",
    "tip": "Use a dry sherry like fino or amontillado. Cream sherry makes the drink heavy "
           "and overly sweet, and there is no spirit here to cut through it.",
},
"Affinity": {
    "about": "Bartenders call a Manhattan split evenly between sweet and dry vermouth a "
             "'Perfect,' and the Affinity applies that exact idea to Scotch. The dry vermouth "
             "keeps the sweet vermouth in check so the whisky stays smoky and dry instead of "
             "tasting candied.",
    "tip": "Using equal parts of both vermouths is the whole point. If you only have sweet "
           "vermouth open, make a Rob Roy instead.",
},
"Airmail": {
    "about": "Esquire printed this sparkling rum, honey, and lime drink in its 1949 Handbook "
             "for Hosts, naming it after the airmail postage stamp. At heart it is a honeyed "
             "Daiquiri lengthened with Champagne.",
    "tip": "Honey straight from the jar stiffens up in a cold shaker. Stir it with a little "
           "warm water first so it mixes into the rum and lime cleanly.",
},
"Algonquin": {
    "about": "New York's Algonquin Hotel hosted the famous Round Table of writers and critics "
             "in the 1920s and lent its name to this unusual three-ingredient cocktail. Rye "
             "whiskey, dry vermouth, and pineapple juice sound strange together on paper, "
             "but in the glass the pineapple drinks dry and slightly tart.",
    "tip": "Canned pineapple juice actually works better than fresh here. Fresh juice can "
           "taste sharp and won't froth up the same way when shaken.",
},
"American Beauty": {
    "about": "This drink takes its name and deep red top from the American Beauty rose. "
             "Underneath the float of port or dry red wine sits a surprisingly smooth mix "
             "of brandy, dry vermouth, orange juice, and grenadine with a hint of mint.",
    "tip": "Pour the red wine slowly over the back of a spoon at the very end so it stays "
           "on top as a separate layer instead of muddying the whole glass.",
},
"Americano": {
    "about": "In 1860s Milan this started out as the Milano-Torino, just Campari and sweet "
             "vermouth, until American tourists began asking for theirs topped up with soda "
             "water. It is bitter, fizzy, low in alcohol, and happens to be the first drink "
             "James Bond ever orders in the novels.",
    "tip": "Replace the soda water with gin and you have a Negroni. Leave the soda out "
           "entirely and you are back to a Milano-Torino.",
},
"Aperol Spritz": {
    "about": "The spritz habit started in the 1800s when Austrian soldiers in northern Italy "
             "watered down strong local wines, and once the Barbieri brothers launched Aperol "
             "in Padua in 1919 the modern recipe fell into place. At roughly 8% ABV, it is "
             "built for late afternoon in the sun.",
    "tip": "Stick to 3 parts prosecco, 2 parts Aperol, and 1 part soda, and pour the "
           "prosecco into the glass first. Pouring wine last onto the Aperol knocks out "
           "too much carbonation.",
},
"Autumn Garibaldi": {
    "about": "A classic Garibaldi pairs northern Italian Campari with southern Italian "
             "orange juice, a nod to Giuseppe Garibaldi uniting the country. This cooler-weather "
             "variation keeps the bitter orange core and adds a warmer, rounder finish.",
    "tip": "A proper Garibaldi depends on frothing the orange juice. Shake or whip the "
           "juice hard before pouring so it lands foamy on top of the Campari.",
},
"Aviation": {
    "about": "Hugo Ensslin published the Aviation in New York in 1916 with a touch of "
             "crème de violette, which gave the drink a pale sky-blue tint. When Harry "
             "Craddock left the violette out of the 1930 Savoy Cocktail Book, most bars "
             "followed suit and poured the three-ingredient gin, lemon, and maraschino "
             "version we have here.",
    "tip": "Maraschino liqueur is nothing like the red syrup in a cherry jar. It is dry, "
           "funky, and distilled from sour cherries and their pits, so measure it carefully.",
},

# ============================ B ============================================

"B-52": {
    "about": "Three liqueurs sit in distinct bands inside a small glass: coffee on the "
             "bottom, Irish cream in the middle, and orange liqueur on top. Most accounts "
             "credit Peter Fich at Alberta's Banff Springs Hotel in the late 1970s, naming "
             "it after either the B-52s band or the bomber.",
    "tip": "Layering only works if you pour from heaviest to lightest (Kahlúa, then Baileys, "
           "then Grand Marnier) slowly over the back of a spoon held against the inside "
           "of the glass.",
},
"Bacardi Cocktail": {
    "about": "A Daiquiri sweetened with real pomegranate grenadine instead of plain sugar "
             "became so famous before Prohibition that it ended up in court. In 1936, a "
             "New York Supreme Court judge ruled that a bar serving a 'Bacardi Cocktail' "
             "legally had to make it with Bacardi rum.",
    "tip": "Use real pomegranate-based grenadine if you can. With only three ingredients "
           "in the shaker, artificial red corn-syrup mixers take over the whole drink.",
},
"Bamboo": {
    "about": "Louis Eppinger came up with the Bamboo in the 1890s while running the bar at "
             "the Grand Hotel in Yokohama, Japan. By combining dry sherry, dry vermouth, "
             "and two kinds of bitters with no base spirit, he made a dry, low-proof "
             "alternative to a Martini.",
    "tip": "Sherry and vermouth are both wines that spoil once opened. Keep both bottles "
           "in the fridge, because a warm, months-old bottle will make this taste flat.",
},
"Batanga": {
    "about": "Don Javier Delgado Corona created the Batanga in 1961 at La Capilla in "
             "Tequila, Mexico, stirring every glass with the same long knife he used to "
             "chop limes and avocados. It is just blanco tequila, fresh lime juice, and "
             "Mexican Coke in a salted glass, and that salt rim makes the whole thing work.",
    "tip": "Do not skip the coarse salt on the rim. The salt cuts the sweetness of the "
           "cola and brings out the peppery note in the tequila.",
},
"Bay Breeze": {
    "about": "Like its late-1970s and 1980s siblings the Sea Breeze and Cape Codder, the "
             "Bay Breeze comes from the era when vodka and fruit-juice highballs ruled "
             "American neighbourhood bars. Pineapple juice softens the tart cranberry and "
             "makes this the easiest-drinking of the three.",
},
"Bee's Kiss": {
    "about": "White rum, honey, and cream shake up into a short, sweet after-dinner drink "
             "from the early twentieth century. Nobody knows for sure who first printed "
             "it, though it showed up regularly in European and Cuban bar books by the 1930s.",
    "tip": "Thin the honey with a splash of warm water before putting it in the shaker. "
           "Cold cream and cold ice will turn raw honey into a stiff lump at the bottom.",
},
"Bee's Knees": {
    "about": "During Prohibition, honey and lemon juice did a lot of work covering up the "
             "rough edges of home-made bathtub gin. Both Frank Meier at the Paris Ritz and "
             "unsinkable Titanic survivor Margaret Brown are often linked to it, and the "
             "name was 1920s slang for something first-rate.",
    "tip": "Mix two parts honey with one part warm water before shaking. Raw honey refuses "
           "to dissolve once it hits cold lemon juice and ice.",
},
"Bellini": {
    "about": "Giuseppe Cipriani started pouring white peach puree and sparkling prosecco "
             "at Harry's Bar in Venice in the 1940s. He named it after the fifteenth-century "
             "Venetian painter Giovanni Bellini because the pale pink colour reminded him "
             "of a saint's toga in one of Bellini's paintings.",
    "tip": "White peach puree is the traditional base. Yellow peaches are sweeter and "
           "lack the floral tartness that balances the prosecco.",
},
"Between the Sheets": {
    "about": "Harry MacElhone is usually credited with pouring this at Harry's New York "
             "Bar in Paris in the 1920s. It takes the cognac, triple sec, and lemon of a "
             "Sidecar and splits the base with white rum, making a strong, dry, tart drink.",
},
"Bicicletta": {
    "about": "In northern Italian cafés, this easy mix of Campari, dry white wine, and "
             "soda was supposedly named for the wobbly bicycle ride home after a few rounds "
             "at aperitivo hour. It is drier and less sweet than an Aperol Spritz.",
    "tip": "Use a dry, unoaked white wine like pinot grigio or sauvignon blanc. Buttery, "
           "oaky chardonnay clashes badly with Campari.",
},
"Black Manhattan": {
    "about": "Bartender Todd Smith came up with this at San Francisco's Bourbon & Branch "
             "in 2005 through the simplest possible swap: trading sweet vermouth for "
             "Italian amaro. It keeps the weight of a Manhattan while adding bitter herbs, "
             "cola, and dark spice.",
    "tip": "Averna is the standard amaro for this recipe. If you substitute a drier or "
           "more bitter bottle like Cynar or Ramazzotti, add an extra splash of whiskey.",
},
"Black Russian": {
    "about": "Gustave Tops mixed the first Black Russian in 1949 at the Hotel Metropole in "
             "Brussels for Perle Mesta, then the U.S. ambassador to Luxembourg. It is just "
             "vodka and coffee liqueur over ice, and adding cream turns it into a White Russian.",
},
"Blood and Sand": {
    "about": "When Rudolph Valentino's bullfighting movie Blood and Sand came out in 1922, "
             "this four-equal-parts Scotch drink followed close behind and landed in the "
             "1930 Savoy Cocktail Book. Scotch, sweet vermouth, cherry liqueur, and orange "
             "juice sound like a disaster on paper, yet somehow taste great together.",
    "tip": "If the equal-parts build tastes a little sweet to you, bump the Scotch up to "
           "a full ounce while keeping the other three at three-quarters of an ounce.",
},
"Bloody Maria": {
    "about": "Swapping the vodka in a Bloody Mary for blanco tequila changes the whole "
             "drink. Where vodka disappears behind the tomato juice, horseradish, and hot "
             "sauce, tequila adds an earthy, peppery taste that stands right up to the spice.",
},
"Bloody Mary": {
    "about": "Fernand Petiot helped shape the modern spiced tomato-and-vodka recipe in "
             "1920s Paris before bringing it to the King Cole Bar at New York's St. Regis "
             "Hotel in 1934. Hotel management thought 'Bloody Mary' sounded too vulgar "
             "for their guests and tried renaming it the Red Snapper.",
    "tip": "Roll the drink gently back and forth between two tins or stir it with ice "
           "instead of shaking hard. Vigorous shaking makes tomato juice foamy and thin.",
},
"Blue Hurricane": {
    "about": "A tropical vacation riff on the classic New Orleans Hurricane that swaps in "
             "blue curaçao for an electric-turquoise look. Rum, pineapple, citrus, and "
             "sweet orange liqueur make it a big, fruity summer pour.",
},
"Bobby Burns Cocktail": {
    "about": "Scotland's national poet Robert Burns gets his own Scotch Manhattan variation "
             "in the 1930 Savoy Cocktail Book. A small measure of Bénédictine brings honey "
             "and herbs to the Scotch and sweet vermouth, making it richer than a standard "
             "Rob Roy.",
},
"Boulevardier": {
    "about": "Erskine Gwynne, an American writer who ran a Paris literary magazine called "
             "The Boulevardier in the 1920s, ordered this regularly at Harry's New York Bar. "
             "It is a Negroni made with bourbon instead of gin, which trades the sharp "
             "botanical snap for oak and vanilla.",
    "tip": "Many bartenders prefer 1 1/2 oz of bourbon to 1 oz each of Campari and sweet "
           "vermouth so the whiskey doesn't get buried under the other two bottles.",
},
"Bourbon Renewal": {
    "about": "Portland bartender Jeffrey Morgenthaler created the Bourbon Renewal in the "
             "early 2000s while looking for a whiskey drink that worked year-round. Splitting "
             "the sweetener in a Whiskey Sour with blackcurrant crème de cassis gives it "
             "a tart dark-berry finish.",
},
"Bramble": {
    "about": "Dick Bradsell created the Bramble at Fred's Club in Soho, London in 1984, "
             "inspired by picking wild blackberries as a kid on the Isle of Wight. You "
             "build a short gin sour over crushed ice and pour blackberry liqueur over the "
             "top so it bleeds down through the glass.",
    "tip": "Pour the blackberry liqueur over the crushed ice at the very end and leave "
           "the spoon alone. The dark purple streaks through the ice are half the point.",
},
"Brandy Alexander": {
    "about": "The earlier Alexander cocktail was actually made with gin, cream, and crème "
             "de cacao, before brandy took over in the 1920s and became the version everyone "
             "remembers. With brandy, chocolate liqueur, cream, and nutmeg on top, it is "
             "essentially liquid dessert.",
    "tip": "Grate a whole nutmeg directly over the drink if you have one. Pre-ground "
           "nutmeg loses most of its smell once it sits in a spice jar.",
},
"Brandy Cobbler": {
    "about": "In mid-1800s America, the Cobbler was a massive hit that helped popularise "
             "both ice-making and drinking straws. Jerry Thomas included it in his 1862 "
             "bar guide: brandy, sugar, and fresh fruit packed in a tall glass of crushed "
             "ice for hot weather.",
    "tip": "Use crushed or cracked ice rather than large cubes. The drink is meant to "
           "chill quickly and frost the outside of the glass as you sip through a straw.",
},
"Brandy Daisy": {
    "about": "Daisies were a nineteenth-century family of sours sweetened with cordial or "
             "grenadine and lengthened with a splash of soda. If the pattern looks familiar, "
             "that is because the Margarita evolved out of the tequila version ('margarita' "
             "is Spanish for daisy).",
},
"Brandy Sour": {
    "about": "Putting brandy into the classic sour ratio of spirit, lemon, and sugar gives "
             "you a softer, fruitier drink than a Whiskey Sour. A couple of dashes of "
             "bitters and optional egg white round off the sharp lemon edge.",
    "tip": "If you use egg white, shake the ingredients without ice first for ten seconds, "
           "then add ice and shake hard again to build a stable foam.",
},
"Brooklyn": {
    "about": "Of the five cocktail recipes named after New York boroughs, the Brooklyn was "
             "the first to follow the Manhattan into print, showing up in Jacques Straub's "
             "1914 book Drinks. It switches to dry vermouth and adds maraschino liqueur and "
             "bitter French Amer Picon.",
    "tip": "Original Amer Picon is hard to find outside Europe. Amaro CioCiaro or "
           "Ramazzotti makes a solid stand-in for that bitter orange-and-herb note.",
},
"Brown Derby": {
    "about": "In 1930s Hollywood, the Vendome Club poured this three-ingredient mix of "
             "bourbon, grapefruit juice, and honey syrup and named it after the famous "
             "hat-shaped Brown Derby restaurant down the street. In Britain, the exact "
             "same drink appeared independently as the De Rigueur.",
    "tip": "Stir your honey with warm water (about three parts honey to one part water) "
           "before shaking so it doesn't stick to the inside of the tin.",
},

# ============================ C ============================================

"Caesar": {
    "about": "Walter Chell invented the Caesar in 1969 to celebrate the opening of an "
             "Italian restaurant at the Calgary Inn, taking inspiration from spaghetti "
             "alle vongole (clams and tomato sauce). Today Canadians drink millions of "
             "them every year while the rest of the world mostly sticks to Bloody Marys.",
    "tip": "Wet the rim with lime and dip it in celery salt rather than plain table salt. "
           "Table salt makes the Clamato taste flat and overly briny.",
},
"Caipirinha": {
    "about": "Brazil's national drink showcases cachaça, which is distilled from fresh "
             "sugarcane juice rather than molasses. One popular story traces it to 1918 "
             "São Paulo as a folk remedy made with lime, garlic, and honey, before someone "
             "wisely dropped the garlic and honey in favour of sugar and ice.",
    "tip": "Muddle the cut lime wedges directly in the sugar before adding the cachaça. "
           "The gritty sugar scrapes the oil out of the lime skin, which gives the drink "
           "most of its flavour.",
},
"Cameron's Kick": {
    "about": "Harry MacElhone included this in his 1922 book ABC of Mixing Cocktails. It "
             "splits the base evenly between blended Scotch and Irish whiskey, then shakes "
             "them with lemon juice and almond orgeat syrup, a combination that works far "
             "better than you might expect.",
    "tip": "Make sure you use proper almond orgeat syrup rather than almond baking extract. "
           "Orgeat adds the body and sweetness that tie the two whiskies together.",
},
"Canchanchara": {
    "about": "During Cuba's nineteenth-century wars of independence against Spain, fighters "
             "in the eastern hills around Trinidad drank warm sugarcane spirit mixed with "
             "local honey and lime out of small gourds. Served cold over ice today, it is "
             "the oldest known ancestor of the Daiquiri.",
    "tip": "Loosen the honey with a little warm water and rum in the bottom of the glass "
           "before adding ice, or the honey will sit untouched at the bottom.",
},
"Cantarito": {
    "about": "Along the roadside stands of Jalisco, Mexico, bartenders build the Cantarito "
             "inside a small unglazed clay cup (a jarrito) with tequila, fresh orange, "
             "grapefruit, and lime juices, a pinch of salt, and grapefruit soda. Even in a "
             "regular highball glass at home, all that fresh citrus makes it a great warm-weather "
             "tequila drink.",
},
"Cape Codder": {
    "about": "In 1945 the Ocean Spray cranberry cooperative started promoting vodka and "
             "cranberry juice as the 'Red Devil,' before renaming it after Massachusetts's "
             "cranberry-growing Cape Cod peninsula in the 1960s. With a squeeze of fresh "
             "lime, it became one of the default bar calls of the twentieth century.",
    "tip": "Check the label on your cranberry bottle. Standard 'cranberry juice cocktail' "
           "is already sweetened, while 100% pure cranberry juice is lip-puckeringly tart "
           "and needs a splash of simple syrup.",
},
"Cardinale": {
    "about": "Rome's Hotel Excelsior came up with the Cardinale in the 1950s for a German "
             "cardinal who liked dry French wines. Replacing the sweet vermouth in a Negroni "
             "with dry vermouth takes away the heavy caramel sweetness and leaves a leaner, "
             "sharper aperitif.",
},
"Champagne Cocktail": {
    "about": "Jerry Thomas wrote down this recipe in 1862, and it hasn't needed any updates "
             "since. You soak a sugar cube in Angostura bitters at the bottom of a flute "
             "and pour cold Champagne over it, creating a steady stream of bubbles from "
             "the sugar crystals.",
    "tip": "Do not stir the sugar cube in. Let it dissolve on its own at the bottom of "
           "the glass so the last few sips taste slightly richer than the first.",
},
"Chatham Artillery Punch": {
    "about": "Savannah's Chatham Artillery militia first mixed this legendary punch in "
             "horse buckets in the late 1700s and early 1800s, famously leaving visiting "
             "officials and rival regiments worse for wear. Blending rum, cognac, and "
             "bourbon with lemon, sugar, and Champagne hides a lot of alcohol behind a "
             "pleasant fizzy punch.",
    "tip": "Our recipe is scaled down to a single glass. If you batch it in a bowl for "
           "company, use one large block of ice rather than small cubes so it doesn't "
           "water down.",
},
"Chet Baker": {
    "about": "Sam Ross created this stirred rum drink at New York's Milk & Honey and "
             "named it after the jazz trumpeter and singer. Aged rum gets stirred with "
             "sweet vermouth, honey syrup, and Angostura bitters, making it drink much "
             "more like a Manhattan than a beach cocktail.",
    "tip": "Thin your honey into a syrup with warm water first, and give the glass a "
           "full 30-second stir over ice so the honey and vermouth open up.",
},
"Chi-Chi": {
    "about": "Take a Piña Colada and swap the rum for vodka and you have a Chi-Chi, a "
             "staple of mid-century tiki lounges and hotel pool bars. Because the vodka "
             "adds almost no flavour of its own, you taste purely pineapple and sweet "
             "coconut.",
    "tip": "If you don't want to drag out the blender, shake everything hard with ice "
           "and strain it over fresh crushed ice.",
},
"Clover Club": {
    "about": "Before Prohibition, a group of Philadelphia journalists, lawyers, and bankers "
             "called the Clover Club met regularly at the Bellevue-Stratford Hotel and "
             "drank this frothy pink mix of gin, lemon, raspberry syrup, and egg white. "
             "Despite the pink colour, it drinks tart and dry.",
    "tip": "Shake all the ingredients without ice first, then add ice and shake again. "
           "Doing the dry shake first builds a thick, stable head of foam.",
},
"Corpse Reviver #2": {
    "about": "Harry Craddock included this in his 1930 Savoy Cocktail Book as a late-morning "
             "pick-me-up, adding a famous footnote: 'Four of these taken in swift succession "
             "will unrevive the corpse again.' Equal parts gin, Cointreau, Lillet Blanc, "
             "and lemon juice over an absinthe rinse makes one of the best gin sours ever written.",
    "tip": "Keep the four main ingredients strictly equal, and only coat the inside of "
           "the glass with absinthe before dumping the excess. Too much absinthe covers "
           "up everything else.",
},
"Corpse Reviver No. 1": {
    "about": "Even though the citrusy No. 2 gets almost all the orders today, the No. 1 "
             "came right before it in the 1930 Savoy Cocktail Book. Made with cognac, "
             "apple brandy (or Calvados), and sweet vermouth, it is a rich, stirred "
             "brandy drink with no citrus at all.",
},
"Cosmopolitan": {
    "about": "Bartenders in Provincetown, Miami, and San Francisco were pouring cousins of "
             "this drink by the mid-1980s before Toby Cecchini nailed down the modern "
             "Cointreau, fresh lime, and cranberry spec at Manhattan's Odeon in 1988. A "
             "decade later, Sex and the City put one in every bar in the world.",
    "tip": "Go easy on the cranberry juice. It is there to turn the drink pale pink and "
           "add a dry tartness, not to drown out the lime and orange liqueur.",
},
"Cuba Libre": {
    "about": "Shortly after the Spanish-American War ended around 1900, Coca-Cola began "
             "exporting to Cuba, where off-duty U.S. Signal Corps soldiers mixed it with "
             "local rum and lime and toasted 'Por Cuba libre!' ('To a free Cuba!'). The "
             "fresh lime is what separates it from a plain rum and Coke.",
    "tip": "Squeeze half a lime into the glass and drop the juiced shell in with the ice "
           "so you get the bitter oil from the skin as well as the juice.",
},

# ============================ D ============================================

"Daiquiri": {
    "about": "In 1898, an American mining engineer named Jennings Cox was working near "
             "the iron mines of Daiquirí on Cuba's southeastern coast and mixed local rum, "
             "limes, sugar, and ice for his guests. Bartenders still treat a simple shaken "
             "Daiquiri as one of the clearest tests of someone's technique.",
    "tip": "Squeeze real limes right before you make it. With only three ingredients in "
           "the glass, bottled lime juice will ruin a Daiquiri immediately.",
},
"Dark and Stormy": {
    "about": "After World War I, sailors in Bermuda started combining ginger beer from a "
             "Royal Navy factory with local Gosling's Black Seal dark rum. Gosling's later "
             "trademarked the name in the United States, making it one of the only classic "
             "cocktails legally tied to a specific brand of spirit.",
    "tip": "Pour the ginger beer over the ice first and float the dark rum on top at the "
           "end. That dark rum layer drifting down through the ginger beer is where the "
           "name comes from.",
},
"Death in the Afternoon": {
    "about": "Ernest Hemingway contributed this recipe to a 1935 celebrity cocktail book "
             "called So Red the Nose, naming it after his 1932 book on Spanish bullfighting. "
             "His original instructions read: pour one jigger of absinthe into a Champagne "
             "glass, add iced Champagne until it turns milky, and drink three to five of "
             "them slowly.",
    "tip": "Pour the chilled Champagne slowly onto the absinthe so it doesn't foam over "
           "the top of the flute as the absinthe clouds up.",
},
"Dirty Martini": {
    "about": "New York bartender John O'Connor was pouring olive brine into Martinis at "
             "the Waldorf Astoria as early as 1901, originally mashing an olive in the "
             "glass before straining. That splash of salty brine cuts the alcohol bite "
             "and makes a dry Martini savoury.",
    "tip": "Taste your olive jar's brine before pouring a full measure. Some brands are "
           "twice as salty as others and can overpower the gin at half an ounce.",
},
"Dry Rob Roy": {
    "about": "A standard Rob Roy is a Manhattan made with Scotch and sweet vermouth; the "
             "Dry Rob Roy swaps in dry French vermouth instead. Without the dark sugar of "
             "sweet vermouth, the malt and smoke of the Scotch sit right up front.",
},

# ============================ E - F ========================================

"El Diablo": {
    "about": "Trader Vic included the El Diablo in his 1946 Book of Food and Drink under "
             "his Mexican recipes. Combining blanco tequila with blackcurrant crème de "
             "cassis, fresh lime, and spicy ginger beer sounds unusual, but blackcurrant "
             "and ginger pair naturally with tequila.",
},
"El Presidente": {
    "about": "During the 1910s and 1920s, when Havana was the cocktail capital for "
             "Americans dodging Prohibition, bartenders like Eddie Woelke and Constantino "
             "Ribalaigua poured the El Presidente for Cuba's upper crust. Stirred cold "
             "with rum, dry or blanc vermouth, orange curaçao, and a barspoon of grenadine, "
             "it drinks like a rum Manhattan.",
    "tip": "Use only a small splash of grenadine. It is meant to give the drink a pale "
           "salmon tint and a hint of pomegranate, not make it syrupy.",
},
"Espresso Martini": {
    "about": "Dick Bradsell mixed the first one at the Soho Brasserie in London in the "
             "late 1980s (originally calling it the Vodka Espresso) after a model walked "
             "up to the bar and asked for something that would 'wake me up, and then "
             "fuck me up.' Thirty years later, it is still one of the most ordered drinks "
             "on earth.",
    "tip": "To get the thick tan foam on top, brew a fresh shot of espresso and shake it "
           "hard with plenty of ice while it still has its crema.",
},
"Fish House Punch": {
    "about": "Philadelphia's Schuylkill Fishing Company (founded in 1732 and still around "
             "today) has been serving this punch for centuries. Lemon juice, sugar, and "
             "water hide a heavy combination of rum, cognac, and peach brandy that sneaks "
             "up on anyone treating it like lemonade.",
    "tip": "If you batch this in a punch bowl for a crowd, rest it over one big block of "
           "ice for half an hour before serving so the spirits and lemon settle down.",
},
"Fog Cutter": {
    "about": "Trader Vic created the Fog Cutter in the 1940s and wrote in his bar guide: "
             "'Fog Cutter, hell. After two of these you won't even see the stuff.' Combining "
             "rum, brandy, and gin with lemon, orange juice, almond orgeat, and a sherry "
             "float makes it both strong and surprisingly tart.",
    "tip": "Measure the three spirits carefully and float the sherry over the crushed "
           "ice at the very end so you taste the dry, nutty wine on your first sip.",
},
"French 75": {
    "about": "During World War I, Paris bartenders named this combination of gin, lemon, "
             "sugar, and Champagne after the French 75-millimetre field gun, famous for "
             "its speed and kick. Harry MacElhone and Harry Craddock both helped cement "
             "the recipe in the 1920s.",
    "tip": "Shake only the gin, lemon juice, and syrup with ice, strain into your glass, "
           "and top with Champagne afterwards. Never put sparkling wine in a closed shaker.",
},
"French Connection": {
    "about": "This 1970s lounge drink took its name from the 1971 Gene Hackman crime movie "
             "and couldn't be simpler: equal parts French cognac and Italian amaretto "
             "poured over ice. It takes thirty seconds to build and works well after dinner.",
},

# ============================ G - H ========================================

"Gibson": {
    "about": "A Gibson is a dry Gin Martini garnished with a pickled cocktail onion instead "
             "of an olive or a lemon twist. Illustrator Charles Dana Gibson and San Francisco "
             "businessman Walter D. K. Gibson both get credited in old bar stories, and "
             "the onion adds a subtle savoury note without making the drink briny.",
    "tip": "Do not pour the pickling liquid from the onion jar into the drink. Unlike a "
           "Dirty Martini, a Gibson stays clean and dry, with just the onion on a pick.",
},
"Gimlet": {
    "about": "For most of the twentieth century, a Gimlet meant gin stirred or shaken with "
             "Rose's sweetened lime cordial rather than fresh lime juice. People often "
             "link it to nineteenth-century Royal Navy Surgeon-General Sir Thomas Gimlette "
             "giving sailors lime juice to prevent scurvy.",
    "tip": "Fresh lime juice and simple syrup makes a sharp modern gin sour, while Rose's "
           "lime cordial gives you the softer, old-school pub version. Both are good.",
},
"Gin And Tonic": {
    "about": "In nineteenth-century colonial India, British officials took daily doses of "
             "bitter quinine powder to ward off malaria and began mixing it with soda "
             "water, sugar, lime, and gin to make the medicine go down. Modern tonic water "
             "has much less quinine, but the pairing with London Dry gin never went away.",
    "tip": "Fill the glass all the way to the top with ice cubes before pouring. More ice "
           "keeps the drink colder, melts slower, and holds onto the carbonation longer.",
},
"Godfather": {
    "about": "Appearing in the 1970s right around the release of Francis Ford Coppola's "
             "film, the Godfather pairs Scotch whisky with sweet almond amaretto over ice. "
             "The amaretto rounds off the sharper, smokier notes of the Scotch without "
             "hiding them.",
},
"Gold Rush": {
    "about": "T.J. Siegal came up with the Gold Rush around 2000 at Sasha Petraske's New "
             "York bar Milk & Honey. It is simply a bourbon Whiskey Sour made with honey "
             "syrup instead of sugar syrup and served over a big cube of ice.",
    "tip": "Stir three parts honey with one part warm water before you start. Straight "
           "honey turns stiff as soon as it touches cold lemon juice and ice.",
},
"Grasshopper": {
    "about": "Philibert Guichet invented the Grasshopper at Tujague's in New Orleans's "
             "French Quarter around 1918 and won second prize with it at a New York "
             "cocktail competition. Equal parts green crème de menthe, white crème de "
             "cacao, and cream taste exactly like liquid mint-chocolate-chip ice cream.",
},
"Greenpoint": {
    "about": "Michael McIlroy created the Greenpoint around 2006 at Milk & Honey in New "
             "York, continuing the bar's habit of naming Manhattan variations after "
             "Brooklyn neighbourhoods. Yellow Chartreuse steps in alongside rye whiskey, "
             "sweet vermouth, and two bitters for an herbal, honeyed twist.",
},
"Greyhound": {
    "about": "The Greyhound first showed up in Harry Craddock's 1930 Savoy Cocktail Book "
             "as gin, grapefruit juice, and ice, before Greyhound bus terminals began "
             "serving a vodka version in their station restaurants after World War II. "
             "Put salt on the rim and the exact same drink is called a Salty Dog.",
},
"Hanky Panky": {
    "about": "Ada 'Coley' Coleman, the famous head bartender at London's Savoy Hotel in "
             "the early 1900s, mixed this for comic actor Sir Charles Hawtrey when he "
             "asked for something with a bit of punch. When he tasted the mix of gin, "
             "sweet vermouth, and two dashes of bitter Fernet-Branca, he shouted, 'By "
             "Jove! That is the real hanky-panky!'",
    "tip": "Measure the Fernet-Branca carefully. Just two dashes add a cool menthol-and-herb "
           "finish to a Sweet Martini, while a heavy pour takes over the whole glass.",
},
"Harvard": {
    "about": "George Kappeler included the Harvard in his 1895 book Modern American Drinks "
             "during a late-nineteenth-century craze for naming cocktails after Ivy League "
             "colleges. It is simply a Manhattan made with cognac instead of rye whiskey, "
             "which makes it rounder and slightly fruitier.",
},
"Hemingway Daiquiri": {
    "about": "When Ernest Hemingway walked into El Floridita in Havana in the 1930s, he "
             "tasted their frozen Daiquiri and asked head bartender Constantino Ribalaigua "
             "for one with no sugar and double the rum. Later on, Ribalaigua added grapefruit "
             "juice and maraschino liqueur to soften the sharp lime.",
    "tip": "Without simple syrup, this is a very tart, bone-dry drink. If it hits a little "
           "too sharp for your taste, add a quarter ounce of simple syrup.",
},
"Horse's Neck": {
    "about": "In the 1890s, a Horse's Neck was actually a non-alcoholic drink of ginger "
             "ale, ice, and a long spiral of lemon peel draped over the edge of the glass. "
             "Within a decade or two, bartenders started adding a stiff measure of brandy "
             "or American whiskey and a dash of bitters, which is how it stayed.",
    "tip": "Cut a single long ribbon of peel around a whole lemon and drape it inside "
           "the glass before you add the ice, otherwise it won't stay put.",
},
"Hot Toddy": {
    "about": "People have been mixing whiskey, hot water, sweetener, and lemon against winter "
             "colds since at least the 1700s, with the name likely borrowed from either "
             "India's fermented palm sap ('tari') or Edinburgh's Tod's Well water supply. "
             "It is still the best thing to hold when you come in out of the cold.",
    "tip": "Fill your mug with hot tap water for a minute and dump it out before building "
           "the drink. A cold ceramic mug pulls the heat right out of a Hot Toddy.",
},
"Hugo Spritz": {
    "about": "Bartender Roland Gruber came up with the Hugo in 2005 in the Alpine region "
             "of South Tyrol, northern Italy, as a gentler alternative to the Aperol "
             "Spritz. Elderflower cordial, prosecco, soda water, and fresh mint leaves "
             "make it floral, light, and not bitter at all.",
},
"Hurricane": {
    "about": "During World War II, whiskey was scarce in the United States, so liquor "
             "distributors forced bar owners to buy cases of Caribbean rum if they wanted "
             "an allocation of Scotch or bourbon. Pat O'Brien's in New Orleans unloaded "
             "all that rum by mixing it with passion fruit and lemon in a tall glass "
             "shaped like a hurricane lamp.",
    "tip": "Using half white rum and half dark rum gives you a fuller flavour than using "
           "one bottle alone.",
},

# ============================ I - L ========================================

"Irish Coffee": {
    "about": "In the winter of 1943, a bad storm forced a transatlantic flying boat back "
             "to Foynes airbase in County Limerick, Ireland, and chef Joe Sheridan added "
             "Irish whiskey to the passengers' coffee. When an American passenger asked "
             "if it was Brazilian coffee, Sheridan told him it was Irish coffee.",
    "tip": "Lightly whip or shake cold heavy cream just until it thickens slightly, then "
           "pour it over the back of a spoon so it floats on top. Drink the hot coffee "
           "straight through the cool cream without stirring.",
},
"Jamaican Mule": {
    "about": "Replacing the vodka in a Moscow Mule with pot-still Jamaican rum gives the "
             "drink a lot more personality. The ripe banana, molasses, and spice notes "
             "in Jamaican rum hold their own right alongside hot ginger beer and fresh lime.",
    "tip": "Use real ginger beer rather than ginger ale. Ginger ale is much sweeter and "
           "lacks the peppery ginger bite that makes a Mule work.",
},
"Japanese Cocktail": {
    "about": "Jerry Thomas published this recipe in his 1862 Bartender's Guide, almost "
             "certainly naming it in honour of the first Japanese diplomatic embassy's "
             "celebrated 1860 visit to New York. There is nothing Japanese in the glass: "
             "just cognac stirred with almond orgeat syrup and bitters.",
    "tip": "Because there is no citrus juice in the recipe, make sure you squeeze a strip "
           "of lemon peel over the top at the end to keep the sweet almond from feeling heavy.",
},
"John Collins": {
    "about": "An 1860s London rhyme credited a head waiter named John Collins at Limmer's "
             "Hotel around Conduit Street with pouring gin, lemon, sugar, and soda over "
             "ice. Once bartenders began making the gin version with Old Tom gin and calling "
             "it a Tom Collins, the name John Collins shifted over to the bourbon or "
             "whiskey version.",
},
"Juan Collins": {
    "about": "A Juan Collins simply takes the tall lemon-and-soda Collins build and swaps "
             "the base spirit for blanco or reposado tequila. If you want a long, fizzy "
             "tequila drink with lemon instead of lime or grapefruit, this is it.",
},
"Jungle Bird": {
    "about": "Jeffrey Ong created the Jungle Bird in 1978 for the Aviary Bar at the Kuala "
             "Lumpur Hilton, where it was originally served in a ceramic bird vessel. "
             "Putting bitter Italian Campari into a tropical mix of dark rum, pineapple "
             "juice, lime, and sugar makes it one of the most distinct tiki drinks ever made.",
    "tip": "Do not cut back on the Campari. The whole point of a Jungle Bird is how "
           "pineapple juice and dark rum tame that bitter red liqueur.",
},
"Kalimotxo": {
    "about": "Half red wine and half cola over ice sounds like a dare until you try one "
             "on a warm day. Popularised in Spain's Basque Country in the early 1970s "
             "(reportedly after festival organisers in Getxo needed to salvage 2,000 litres "
             "of rough red wine), it drinks a lot like an easy two-ingredient sangria.",
    "tip": "Save your good wine for dinner. An inexpensive young red with a bit of tannin "
           "actually works best against the sweet cola.",
},
"Kamikaze": {
    "about": "Equal parts vodka, triple sec, and lime juice surfaced in American bars in "
             "the 1970s, served both as a chilled shooter and a proper up cocktail. It is "
             "essentially a Margarita with vodka in place of the tequila.",
},
"Kentucky Mule": {
    "about": "Using bourbon instead of vodka in a Moscow Mule adds vanilla, caramel, and "
             "oak to the ginger beer and lime. Bourbon and ginger are already an easy match, "
             "and the fresh lime keeps the finish clean.",
},
"Kir Royale": {
    "about": "Canon Félix Kir, a French priest, Resistance fighter, and longtime postwar "
             "mayor of Dijon, served white Burgundy with local blackcurrant crème de cassis "
             "at official city receptions so often that the drink was named after him. "
             "The Kir Royale simply replaces the still white wine with Champagne.",
    "tip": "Put the crème de cassis in the bottom of the flute first, then pour the "
           "Champagne in slowly. The bubbles mix the two on their own without needing a spoon.",
},
"Lemon Drop": {
    "about": "Norman Jay Hobday invented the Lemon Drop in the 1970s at Henry Africa's, "
             "his neighbourhood saloon in San Francisco's Russian Hill. Named after the "
             "hard lemon candies, it shakes vodka, triple sec, and fresh lemon juice into "
             "a sugar-rimmed glass for a sweet-tart finish.",
},
"Long Island Iced Tea": {
    "about": "Robert 'Rosebud' Butt claims he invented this drink in 1972 for a contest "
             "at the Oak Beach Inn on Long Island, New York, using vodka, gin, white rum, "
             "tequila, and triple sec with sour mix and a splash of cola. Somehow those "
             "five clear liquors and lemon end up tasting remarkably like sweet iced tea.",
    "tip": "Measure the five spirits with a jigger rather than free-pouring. Even at "
           "half an ounce each, you are already looking at two and a half ounces of liquor.",
},

# ============================ M ============================================

"Mai Tai": {
    "about": "Victor Bergeron (Trader Vic) mixed the first Mai Tai at his Oakland restaurant "
             "in 1944 for two friends visiting from Tahiti, one of whom took a sip and "
             "said, 'Mai tai, roa ae!' ('Out of this world, the best!'). Despite what hotel "
             "pool bars poured in the 1970s and 1980s, the real recipe has no pineapple "
             "juice, no orange juice, and no grenadine.",
    "tip": "Almond orgeat syrup is essential here. Without orgeat and orange curaçao, you "
           "are just making a rum sour.",
},
"Mamie Taylor": {
    "about": "In the summer of 1899, Broadway musical star Mamie Taylor took a boat trip "
             "in Rochester, New York and asked a bartender for a light ginger drink. His "
             "mix of Scotch whisky, lime juice, and spicy ginger beer became a massive "
             "turn-of-the-century fad forty years before the Moscow Mule was invented.",
    "tip": "A blended Scotch with a bit of peat smoke works really well against the "
           "spicy ginger beer and fresh lime.",
},
"Manhattan": {
    "about": "The Manhattan came out of New York's Manhattan Club in the 1870s or 1880s "
             "as one of the earliest cocktails to pair American whiskey with Italian vermouth. "
             "A famous old story claimed Winston Churchill's mother invented it for an "
             "1874 election banquet, though historians later pointed out she was in England "
             "giving birth to Winston at the time.",
    "tip": "Always stir a Manhattan over ice rather than shaking it. Shaking makes an "
           "all-spirit drink cloudy and thin.",
},
"Margarita": {
    "about": "Half a dozen bartenders in Tijuana, Ensenada, Ciudad Juárez, and Acapulco "
             "claimed to have invented the Margarita between the 1930s and late 1940s, "
             "often for a glamorous actress or socialite. More likely, it grew directly "
             "out of the nineteenth-century Brandy Daisy: when Americans crossed into "
             "Mexico during Prohibition and asked for a Daisy with tequila, 'margarita' "
             "was simply the Spanish word for daisy.",
    "tip": "Salt only half the rim of the glass so you can take a salted sip or an "
           "unsalted sip whenever you like.",
},
"Martinez": {
    "about": "The Martinez showed up in cocktail books of the 1880s, traced either to the "
             "California town of Martinez or San Francisco's Occidental Hotel, as the "
             "direct bridge between the Manhattan and the Martini. Using gin, sweet "
             "vermouth, maraschino liqueur, and bitters makes it darker and sweeter than "
             "any modern Martini.",
    "tip": "If you use a dry London Dry gin instead of a slightly sweeter Old Tom gin, "
           "use a touch less sweet vermouth so the drink doesn't lean cloying.",
},
"Mary Pickford": {
    "about": "When silent-film stars Mary Pickford, Douglas Fairbanks, and Charlie Chaplin "
             "travelled to Havana in the 1920s, bartender Fred Kaufman at the Hotel Nacional "
             "(or Eddie Woelke at the Sevilla-Biltmore) named this pale pink rum drink "
             "for her. Pineapple juice and white rum get a dry, nutty edge from maraschino "
             "liqueur and a blush of grenadine.",
    "tip": "Go easy on the maraschino liqueur. You just want a subtle cherry-pit aroma "
           "behind the pineapple and rum.",
},
"Matador": {
    "about": "Whereas the Margarita pairs tequila with orange liqueur and lime, the Matador "
             "drops the triple sec and shakes blanco tequila with pineapple juice and "
             "fresh lime instead. It first popped up in print in the 1930s and grew popular "
             "across the mid-century tiki years.",
},
"Mexican Mule": {
    "about": "Swapping the vodka in a Moscow Mule for tequila turns a mild ginger highball "
             "into something much livelier. Earthy agave, fresh lime juice, and peppery "
             "ginger beer fit together naturally.",
},
"Mezcal Negroni": {
    "about": "Replacing the gin in a Negroni with mezcal is one of the best modern cocktail "
             "swaps you can make at home. Mezcal's woodsmoke and roasted agave stand right "
             "up to the bitterness of Campari and the richness of sweet vermouth.",
    "tip": "If your mezcal is heavily smoky, try dropping it to 3/4 oz while keeping the "
           "Campari and sweet vermouth at 1 oz each.",
},
"Milano-Torino": {
    "about": "Before the Americano or the Negroni existed, Italian cafés in the 1860s "
             "served this simple half-and-half pour named after its two hometowns: Campari "
             "from Milan and sweet vermouth (originally Punt e Mes) from Turin. Served over "
             "ice with an orange peel, it is rich, bittersweet, and low in proof.",
    "tip": "Top this with soda water and you have an Americano. Add an equal measure of "
           "gin instead and you have a Negroni.",
},
"Mimosa": {
    "about": "Frank Meier is usually credited with pouring equal parts orange juice and "
             "Champagne at the Ritz Hotel in Paris around 1925, naming it after the yellow "
             "flowers of the mimosa tree that blooms across southern France. Three years "
             "earlier in London, Buck's Club was already pouring nearly the same drink as "
             "a Buck's Fizz.",
    "tip": "Have both the orange juice and the Champagne thoroughly chilled before you "
           "open them, since there is no ice in the flute.",
},
"Mint Julep": {
    "about": "Southerners were drinking Juleps made with brandy or whiskey as early as "
             "the late 1700s, long before Churchill Downs made the bourbon version the "
             "official drink of the Kentucky Derby in 1938. Packing the cup with finely "
             "crushed ice is what makes the outside of the cup frost over.",
    "tip": "Press the mint leaves gently into the sugar and water at the bottom of the "
           "cup. Grinding or tearing the leaves releases bitter green sap from the stems.",
},
"Mojito": {
    "about": "Havana's signature highball combines white rum, lime, sugar, mint, and soda "
             "water, and exploded in popularity at La Bodeguita del Medio in the 1930s and "
             "1940s. Cuban lore traces its roots all the way back to a sixteenth-century "
             "rum-and-mint remedy called El Draque after English privateer Francis Drake.",
    "tip": "Press the mint leaves gently two or three times to release the oil from the "
           "leaves. If you shred the mint to bits, it makes the drink bitter and gets "
           "stuck in your teeth.",
},
"Morning Glory Fizz": {
    "about": "Late-nineteenth-century American bar guides had a whole category of morning "
             "fizzes designed to put late-night revellers back on their feet. Combining "
             "Scotch whisky, lemon, lime, egg white, soda, and a few dashes of absinthe "
             "sounds wild on paper, but the citrus and foam tame the Scotch and anise.",
    "tip": "Shake the ingredients without ice first to whip the egg white, then shake "
           "with ice, strain, and add the soda water directly to the glass at the end.",
},
"Moscow Mule": {
    "about": "In 1941, Americans barely drank vodka at all. Then John Martin (who had just "
             "bought the rights to Smirnoff) sat down in Los Angeles with Jack Morgan of "
             "the Cock 'n' Bull pub, who had a basement full of house-made ginger beer, "
             "and an acquaintance who happened to have a load of copper mugs to sell.",
    "tip": "If you don't have a copper mug, a chilled highball glass works just fine. "
           "What matters is using real, spicy ginger beer instead of sweet ginger ale.",
},

# ============================ N - O ========================================

"Negroni": {
    "about": "In 1919 Florence, Count Camillo Negroni asked his bartender Fosco Scarselli "
             "at Caffè Casoni to strengthen his usual Americano by replacing the soda "
             "water with gin. Other customers started asking for 'one of Count Negroni's "
             "drinks,' and that equal-parts mix of gin, Campari, and sweet vermouth has "
             "stayed on bar menus ever since.",
    "tip": "Build and stir it over one large ice cube if you have one. Small cubes melt "
           "fast, and a Negroni tastes best as it opens up slowly.",
},
"Negroni Sbagliato": {
    "about": "In Italian, 'sbagliato' means 'mistaken' or 'botched.' Back in the late 1960s "
             "or early 1970s at Bar Basso in Milan, bartender Mirko Stocchetto reached for "
             "the gin bottle while making a Negroni, grabbed a bottle of sparkling spumante "
             "by mistake, and discovered a lighter, fizzy classic.",
},
"New York Sour": {
    "about": "Bartenders in Chicago and New York were floating a spoonful of dry red wine "
             "on top of a Whiskey Sour by the 1880s, originally calling it a Continental "
             "Sour or Southern Whiskey Sour. Beyond the two-tone look in the glass, the "
             "dry red wine adds a nice tannic bite to the first few sips of bourbon and lemon.",
    "tip": "Hold the back of a spoon just above the surface of the drink and pour the "
           "red wine slowly over it so the wine stays in a distinct band on top.",
},
"Nikolaschka": {
    "about": "This German after-dinner ritual started in Hamburg and was supposedly named "
             "after Tsar Nicholas II. You balance a thin peeled lemon slice on the rim "
             "of a small brandy glass, pile sugar and finely ground coffee on the lemon, "
             "and mix the drink in your own mouth.",
    "tip": "Fold the coffee-and-sugar-topped lemon slice in half, chew and swallow it "
           "first, then immediately drink the cognac right behind it.",
},
"Oaxaca Old Fashioned": {
    "about": "Phil Ward created the Oaxaca Old Fashioned in 2007 while working at Death & "
             "Co in New York's East Village, and it quickly became the drink that introduced "
             "thousands of bar-goers to mezcal. Splitting the base between reposado tequila "
             "and smoky mezcal with agave nectar and mole bitters gives you smoke, oak, "
             "and dark cocoa in one glass.",
    "tip": "If you have matches handy, flame the orange peel over the glass before dropping "
           "it in. The lightly scorched orange oil works really well with the mezcal.",
},
"Old Fashioned": {
    "about": "In 1806, an upstate New York newspaper defined the brand-new word 'cocktail' "
             "as any spirit mixed with sugar, water, and bitters. By the 1870s and 1880s, "
             "bartenders were adding absinthe, curaçao, and vermouth to everything, so "
             "traditionalists began asking for a whiskey cocktail made 'the old-fashioned "
             "way.'",
    "tip": "Skip muddling whole orange slices and neon cherries in the bottom of the glass. "
           "Just stir whiskey, sugar, and bitters with ice and squeeze an orange peel over "
           "the top.",
},
"Old Pal": {
    "about": "Harry MacElhone printed the Old Pal in his 1927 Paris guide Barflies and "
             "Cocktails, dedicating it to his friend William 'Sparrow' Robertson, a colourful "
             "American sports editor at the Paris branch of the New York Herald. Where a "
             "Boulevardier uses bourbon and sweet vermouth, the Old Pal switches to spicy "
             "rye and dry vermouth for a much drier drink.",
    "tip": "Equal parts is the original 1920s spec. If you find the Campari a bit strong "
           "against dry vermouth, bump the rye up to 1 1/2 oz.",
},
"Oreo Mudslide": {
    "about": "The regular Mudslide (vodka, coffee liqueur, and Irish cream) took off at "
             "the Wreck Bar on Grand Cayman in the 1970s, and American chain restaurants "
             "soon started blending it with vanilla ice cream and Oreo cookies. It is "
             "straight-up dessert in a glass: a boozy cookies-and-cream milkshake.",
    "tip": "Blend the ice cream and liquors until smooth before adding the cookies, then "
           "pulse briefly so you still get small bits of cookie rather than grey slush.",
},

# ============================ P ============================================

"Painkiller": {
    "about": "Daphne Henderson started pouring the Painkiller in the 1970s at the six-stool "
             "Soggy Dollar Bar on White Bay in the British Virgin Islands, a beach with no "
             "dock where boaters had to swim to shore with wet money in their pockets. "
             "Dark rum, pineapple, orange juice, and cream of coconut topped with fresh "
             "nutmeg later had its name trademarked by Pusser's Rum.",
    "tip": "Do not skip the freshly grated nutmeg on top. The smell of dry nutmeg over "
           "the coconut and pineapple is what separates a Painkiller from a standard "
           "beach punch.",
},
"Paloma": {
    "about": "While the Margarita is the most famous tequila cocktail abroad, the Paloma "
             "('the Dove') is what people actually drink all day across Mexico. Nobody is "
             "completely sure who poured the first one, though it is often linked to Don "
             "Javier Delgado Corona in Tequila, Jalisco, and it takes less than a minute "
             "to build in the glass.",
    "tip": "Make sure you grab Mexican grapefruit soda (like Squirt or Jarritos Toronja), "
           "not purple grape soda. Add a pinch of salt and fresh lime juice to wake up "
           "the bottled soda.",
},
"Paper Plane": {
    "about": "Sam Ross created the Paper Plane in 2007 for the opening menu of Chicago's "
             "Violet Hour, naming it after the M.I.A. song he couldn't stop listening to "
             "that summer. Following the equal-parts pattern of the Last Word, it shakes "
             "bourbon, Aperol, Amaro Nonino, and fresh lemon juice into an easy bittersweet "
             "sour.",
    "tip": "Amaro Nonino is lighter and more citrusy than most dark Italian amaros. Using "
           "a heavier bottle like Averna changes the drink completely.",
},
"Pegu Club": {
    "about": "In colonial Burma during the 1920s, the Pegu Club outside Rangoon served "
             "this dry gin, orange curaçao, and lime cocktail as its house signature. Two "
             "dashes of bitters take the edge off the orange liqueur and make it much "
             "drier than a standard citrus sour.",
},
"Penicillin": {
    "about": "Sam Ross invented the Penicillin in 2005 while working at Milk & Honey in "
             "New York, combining a Gold Rush (whiskey, lemon, and honey) with fresh "
             "ginger and Scotch. Floating a spoonful of smoky Islay single malt over the "
             "top turned it into one of the defining cocktails of the 2000s.",
    "tip": "Pour the smoky Islay Scotch gently over the top of the ice at the very end "
           "instead of shaking it in. You want that campfire smoke to hit your nose first.",
},
"Pimm's Cup": {
    "about": "James Pimm, a farmer's son from Kent, opened an oyster bar in the City of "
             "London in the 1820s and began serving his house gin-and-herb tonic in a small "
             "tankard known as the 'No. 1 Cup.' Today it is synonymous with British summer "
             "and the Wimbledon tennis championships, where fans drink hundreds of thousands "
             "of cups every June and July.",
    "tip": "When British recipes call for 'lemonade' in a Pimm's Cup, they mean clear "
           "fizzy lemon-lime soda like 7UP or Sprite, not cloudy American lemonade. "
           "Ginger ale works great too.",
},
"Pina Colada": {
    "about": "At least three bartenders in 1950s and 1960s San Juan claimed to have "
             "invented the Piña Colada, with the Caribe Hilton's Ramón 'Monchito' Marrero "
             "getting the best-known nod for his 1954 recipe made with newly invented "
             "Coco López cream of coconut. Puerto Rico officially declared it the island's "
             "national drink in 1978.",
    "tip": "You need sweetened cream of coconut (like Coco López), not unsweetened canned "
           "coconut milk or coconut water. Coconut milk is too thin and has none of the "
           "sugar the recipe relies on.",
},
"Pink Lady": {
    "about": "Ivan Caryll's hit 1911 Broadway musical comedy The Pink Lady lent its name "
             "to this pre-Prohibition mix of gin, lemon, cream, egg white, and a splash "
             "of grenadine for colour. For decades it got written off as an overly sweet "
             "ladies'-lunch drink, even though a properly made one is actually a balanced, "
             "dry gin sour.",
    "tip": "Shake all the liquid ingredients without ice first to whip the egg white and "
           "cream together, then add ice and shake hard to chill it.",
},
"Pisco Punch": {
    "about": "During the late 1800s in San Francisco, Scottish bartender Duncan Nicol "
             "served the famous Pisco Punch at the Bank Exchange saloon, where writers "
             "like Mark Twain and Rudyard Kipling marvelled at how easily it went down. "
             "Nicol guarded his pineapple-infused recipe so closely that he died in 1926 "
             "without ever giving it away.",
},
"Pisco Sour": {
    "about": "An American expat named Victor Vaughen Morris opened Morris' Bar in Lima, "
             "Peru in 1916 and began serving a pisco version of the Whiskey Sour, before "
             "his bartender Mario Bruiget added egg white and Angostura bitters in the "
             "1920s. Both Peru and Chile treat pisco as a matter of national pride and "
             "celebrate their own annual Pisco Sour holidays.",
    "tip": "Drop the Angostura bitters onto the white foam head after straining rather "
           "than shaking them in. They cut the raw egg smell on the nose.",
},
"Planter's Punch": {
    "about": "A Jamaican rum punch old enough that an 1878 London magazine printed its "
             "recipe in verse, and a 1908 New York Times piece boiled the island formula "
             "down to 'one of sour, two of sweet, three of strong, and four of weak.' "
             "Every Caribbean hotel had its own house mix of dark rum, lime, sugar, juice, "
             "and bitters.",
},
"Pornstar Martini": {
    "about": "Douglas Ankrah created this in 2002 at the Townhouse bar in Knightsbridge, "
             "London (originally calling it the Maverick Martini), combining vanilla vodka, "
             "passion-fruit liqueur, passion-fruit puree, and lime with a separate shot "
             "glass of prosecco on the side. Over the past twenty years it has become the "
             "single best-selling cocktail across U.K. bars.",
    "tip": "Serve the prosecco in a small glass on the side rather than pouring it straight "
           "into the coupe, so you can alternate sips between the tart passion fruit and "
           "the dry bubbles.",
},

# ============================ Q - R ========================================

"Queen's Park Swizzle": {
    "about": "Trinidad's grand Queen's Park Hotel opened in Port of Spain in 1895 and made "
             "this tall crushed-ice rum drink famous across the Caribbean. Trader Vic "
             "once called it 'the most delightful form of anesthesia given out today,' "
             "thanks to dark rum, mint, lime, sugar, and a heavy float of Angostura bitters "
             "made right down the road in Trinidad.",
    "tip": "Dash the Angostura bitters generously over the top of the crushed ice at the "
           "end so they sit in a dark red layer above the green mint.",
},
"Ramos Gin Fizz": {
    "about": "Henry C. Ramos opened the Imperial Cabinet Saloon in New Orleans in 1888 and "
             "served a gin fizz enriched with cream, egg white, lemon, lime, and orange "
             "flower water. During Mardi Gras in 1915, his bar employed thirty-five 'shaker "
             "boys' who stood behind the counter passing shakers from one pair of tired "
             "arms to the next.",
    "tip": "Shake the ingredients without ice for a good thirty seconds first, then shake "
           "hard with ice until the tin frosts over. Let it sit for a minute in the glass "
           "before adding soda so the foam rises cleanly above the rim.",
},
"Ranch Water": {
    "about": "Long before anyone sold it in cans, ranchers and oil hands out in West Texas "
             "made Ranch Water by taking a big swig off a cold glass bottle of Topo Chico "
             "mineral water and refilling the neck with blanco tequila and lime juice. "
             "Poured over ice in a glass, it is the cleanest, driest tequila highball you "
             "can make.",
    "tip": "Heavily carbonated mineral water like Topo Chico makes a real difference here "
           "compared to softer club soda.",
},
"Remember the Maine": {
    "about": "Travel and food writer Charles H. Baker Jr. published this in his 1939 book "
             "The Gentleman's Companion, recalling drinking it in Havana during the 1933 "
             "revolution while gunfire echoed down the street. Named after the battleship "
             "USS Maine that sank in Havana Harbor in 1898, it adds cherry liqueur and a "
             "touch of absinthe to a rye Manhattan.",
    "tip": "Either swirl the absinthe around the chilled glass and dump the excess, or "
           "stir in just a few drops. You want a faint anise background, not a mouthful "
           "of licorice.",
},
"Revolver": {
    "about": "Bartender Jon Santer created the Revolver in 2004 while working at Bruno's "
             "in San Francisco's Mission District. By replacing the sweet vermouth in a "
             "Manhattan with coffee liqueur and finishing with orange bitters and a flamed "
             "orange peel, he turned bourbon and coffee into a proper stirred cocktail.",
    "tip": "If you have wooden matches, flame an orange peel over the surface of the "
           "glass before serving. Toasted orange oil and coffee liqueur smell fantastic "
           "together.",
},
"Rob Roy": {
    "about": "A bartender at New York's Waldorf Astoria created the Rob Roy in 1894 to "
             "mark the premiere of an operetta about eighteenth-century Scottish outlaw "
             "Rob Roy MacGregor. It is simply a Manhattan made with Scotch whisky instead "
             "of rye, which trades the peppery grain bite for malty warmth and light smoke.",
},
"Rosita": {
    "about": "Gary Regan spotted an obscure recipe called the Rosita in a 1974 edition of "
             "the Mr. Boston bartender's guide, tweaked the proportions, and put it back "
             "on modern bar menus. Splitting the vermouth in a tequila Negroni between "
             "sweet and dry keeps the drink leaner and lets the agave come through.",
},
"Rum Old Fashioned": {
    "about": "Any well-aged dark spirit works in the classic Old Fashioned mix of spirit, "
             "sugar, water, and bitters, and an aged Caribbean rum fits right in. Because "
             "barrel-aged rum already tastes of molasses, vanilla, and oak, it needs very "
             "little sweetener to come together.",
    "tip": "Go slightly lighter on the syrup than you would with bourbon or rye, since "
           "aged rum starts out rounder on the palate.",
},
"Rusty Nail": {
    "about": "Two Scottish bottles, blended Scotch and heather-honey Drambuie liqueur, "
             "settled into their famous name at New York's 21 Club in the early 1960s "
             "(reportedly after earlier runs under names like the B.I.F. and the Mig-21). "
             "Waiters poured oceans of them through the Rat Pack years.",
    "tip": "Three parts Scotch to one part Drambuie is a much better balance for most "
           "drinkers than the old mid-century 1:1 pours, which can get pretty syrupy.",
},

# ============================ S ============================================

"Salty Dog": {
    "about": "A Salty Dog is simply a Greyhound (gin or vodka with grapefruit juice) "
             "served in a salt-rimmed glass, popularised across American bars in the 1950s. "
             "Salt blocks the tongue's perception of bitterness, which makes tart grapefruit "
             "juice taste noticeably sweeter and fuller without adding sugar.",
    "tip": "Put salt on only half the rim so you aren't locked into a mouthful of salt "
           "on every single sip.",
},
"Saratoga": {
    "about": "Jerry Thomas included the Saratoga Cocktail in the 1887 edition of his "
             "Bartender's Guide, naming it after the upstate New York spa resort and "
             "horse-racing town of Saratoga Springs. Splitting the base of a Manhattan "
             "evenly between rye whiskey and cognac gives you both the spice of rye and "
             "the fruit of brandy.",
},
"Sazerac": {
    "about": "New Orleans's official cocktail traces back to the 1850s at the Sazerac "
             "Coffee House on Royal Street, which originally made it with imported French "
             "Sazerac-de-Forge et Fils cognac and local apothecary Antoine Peychaud's "
             "bitters. After the 1870s phylloxera plague wiped out French vineyards, "
             "New Orleans bartenders switched the base to spicy American rye whiskey.",
    "tip": "Rinse the chilled glass with absinthe, dump the excess, and pour the stirred "
           "drink in without ice. Squeeze the lemon peel over the top and discard it or "
           "perch it on the rim rather than dropping it into the liquid.",
},
"Scofflaw": {
    "about": "In January 1924, a Massachusetts prohibitionist held a nationwide contest "
             "to invent a shaming word for people who illegally drank alcohol, and the "
             "winning entry was 'scofflaw.' Within weeks, Harry's New York Bar in Paris "
             "cheekily answered back with the Scofflaw cocktail: rye whiskey, dry vermouth, "
             "lemon juice, and grenadine.",
},
"Scotch Highball": {
    "about": "Scotch and cold soda over plenty of ice is how a lot of the whisky-drinking "
             "world actually drinks Scotch with dinner, especially in Japan, where "
             "highball bars treat a simple two-ingredient pour with real care.",
    "tip": "Chill the glass first and pack it with ice. Give the Scotch a quick stir "
           "before you pour the cold soda, then lift the ice once with your spoon so "
           "you don't knock the fizz out.",
},
"Screwdriver": {
    "about": "Vodka and orange juice first showed up in print in the late 1940s, backed "
             "by a famous bar yarn that American oil engineers working in the Persian "
             "Gulf secretly spiked their cans of orange juice with vodka and stirred them "
             "with their screwdrivers.",
},
"Sea breeze": {
    "about": "Whereas an early 1930 Savoy recipe used gin and grenadine under the same "
             "name, the modern Sea Breeze took shape in California in the 1970s once Ocean "
             "Spray started pushing cranberry juice mixers. Pairing cranberry with tart "
             "grapefruit juice over vodka keeps it much drier than a pineapple Bay Breeze.",
},
"Seelbach": {
    "about": "In 1995, Louisville's historic Seelbach Hotel introduced this drink with a "
             "great story about rediscovering a lost 1917 pre-Prohibition recipe in the "
             "hotel vaults. Twenty-one years later, former bar manager Adam Seger admitted "
             "to the New York Times that he had made the whole story up in 1995, though "
             "bourbon, Cointreau, Champagne, and fourteen dashes of bitters tastes good "
             "enough that nobody minded.",
    "tip": "Do not shy away from the seven dashes each of Angostura and Peychaud's bitters. "
           "That heavy spice dose is what gives the Champagne its amber colour and dry bite.",
},
"Sex on the Beach": {
    "about": "In 1987, a peach schnapps distributor in Fort Lauderdale, Florida offered a "
             "cash bonus to whichever local bartender sold the most bottles during Spring "
             "Break. Young bartender Ted Pizio mixed peach schnapps with vodka, orange "
             "juice, and cranberry, named it after the two reasons students told him they "
             "came to Florida, and sold legions of them.",
},
"Sherry Cobbler": {
    "about": "By the 1840s, the Sherry Cobbler was the single most popular mixed drink in "
             "the United States, made possible by the new New England ice trade and paper "
             "or rye-grass straws. When Charles Dickens toured America, he praised it in "
             "his novel Martin Chuzzlewit as a 'wonderful invention.'",
    "tip": "Muddle a couple of orange slices gently with the syrup before filling the "
           "glass with crushed ice. The orange oil wakes up the nutty sherry.",
},
"Sidecar": {
    "about": "Both the Ritz Hotel in Paris and Buck's Club in London claim to have mixed "
             "the first Sidecar around the end of World War I, naming it after the "
             "motorcycle sidecar an American army captain rode to the bar in. Whatever "
             "the exact bar, cognac, Cointreau, and lemon juice set the standard for "
             "almost every citrus sour that came after.",
    "tip": "If you put a sugar rim on the glass, coat only half the rim. That way you "
           "can take a sweeter sip or a tarter sip depending on how dry your cognac and "
           "triple sec taste.",
},
"Siesta": {
    "about": "New York bartender Katie Stipe created the Siesta at Flatiron Lounge in 2006 "
             "by taking the grapefruit-and-lime structure of a Hemingway Daiquiri and "
             "moving it over to blanco tequila. Instead of maraschino liqueur, a small "
             "measure of Campari adds a dry, bitter pink finish.",
},
"Singapore Sling": {
    "about": "Ngiam Tong Boon created the Singapore Sling around 1915 at the Long Bar of "
             "Singapore's Raffles Hotel, designing a rosy-pink gin punch that looked "
             "respectable for ladies to drink in public on the verandah. Because the "
             "original recipe book was lost, bars have argued for a century over the "
             "exact proportions of gin, cherry liqueur, Bénédictine, and fruit juice.",
},
"Southside": {
    "about": "Shake gin with fresh lime juice, simple syrup, and a handful of mint leaves "
             "and you get a Southside, which tastes a lot like a Mojito made with gin "
             "and no soda water. Both the Southside Sportsmen's Club on Long Island and "
             "Al Capone's South Side gangs in Prohibition Chicago claim the name.",
},
"Suffering Bastard": {
    "about": "In 1942, as Rommel's tanks advanced toward Egypt, bartender Joe Scialom at "
             "Cairo's Shepheard's Hotel mixed a tall hangover cure of gin, brandy, lime "
             "juice, bitters, and ginger beer for Allied soldiers and correspondents. "
             "Reportedly, the Eighth Army wired ahead from the desert for gallons of it.",
    "tip": "Give the gin, brandy, lime, and bitters a quick shake with ice, then strain "
           "over fresh ice and top with cold ginger beer in the glass.",
},

# ============================ T ============================================

"Tequila Old Fashioned": {
    "about": "Once barrel-aged reposado and añejo tequilas started landing on cocktail "
             "bars outside Mexico in the early 2000s, bartenders noticed how well they "
             "worked in a stirred Old Fashioned. Using agave syrup instead of white sugar "
             "plays straight into the roasted agave and oak.",
    "tip": "An aged reposado or añejo tequila works best here, since barrel time adds "
           "the vanilla and spice you usually get from whiskey.",
},
"Tequila Sour": {
    "about": "Before the Margarita took over American bar menus in the 1950s and 1960s, "
             "the standard way to order tequila in a cocktail was a Tequila Sour: tequila, "
             "lemon juice, sugar, and optional egg white. Skipping the orange liqueur "
             "lets you taste the agave much more directly.",
    "tip": "If you include the egg white, shake everything without ice first for ten "
           "seconds, then add ice and shake hard.",
},
"Tequila Sunrise": {
    "about": "Bobby Lozoff and Billy Rice were pouring the modern orange-juice-and-grenadine "
             "Tequila Sunrise at the Trident in Sausalito, California in 1972 when Mick "
             "Jagger tried one at a private party kicking off the Rolling Stones' American "
             "tour. The band ordered them in every city across the country and turned it "
             "into the defining drink of the 1970s.",
    "tip": "Pour the grenadine down the inside wall of the glass at the very end and do "
           "not stir it. Because grenadine is heavier than orange juice, it sinks to the "
           "bottom and rises in a natural gradient.",
},
"The Last Word": {
    "about": "The Detroit Athletic Club started serving this equal-parts mix of gin, green "
             "Chartreuse, maraschino liqueur, and lime juice around 1916 (reportedly "
             "introduced by vaudeville monologist Frank Fogarty), before it spent seventy "
             "years forgotten in Ted Saucier's 1951 book Bottoms Up. In 2004, Seattle "
             "bartender Murray Stenson put it on the menu at the Zig Zag Café and sparked "
             "a worldwide revival.",
    "tip": "Measure all four ingredients in exact equal quarters. Green Chartreuse and "
           "maraschino are both loud bottles, and the lime juice is what holds them "
           "in check.",
},
"Ti' Punch": {
    "about": "In Martinique and Guadeloupe, 'Ti' Punch' is short for 'petit punch' and "
             "serves as the islands' everyday social ritual. Traditionally, the host sets "
             "out a bottle of grassy rhum agricole, cane syrup, and a plate of limes so "
             "everyone at the table can mix their own glass ('chacun prépare sa propre mort').",
    "tip": "Rhum agricole (distilled from fresh sugarcane juice) gives this drink its "
           "earthy, grassy flavor, though a good dry white rum still makes a clean glass.",
},
"Toasted Almond": {
    "about": "During the 1970s and 1980s lounge era, bartenders paired two workhorse "
             "after-dinner bottles, amaretto and coffee liqueur, with cold cream over "
             "ice. It has no base spirit like vodka or whiskey, so it drinks around half "
             "the strength of a standard cocktail and tastes like roasted nuts and iced "
             "coffee.",
},
"Tom Collins": {
    "about": "During the Great Tom Collins Hoax of 1874, pranksters across New York and "
             "Philadelphia told friends that a stranger named Tom Collins was sitting in "
             "the tavern around the corner talking trash about them. When the angry victim "
             "stormed into the bar demanding 'Tom Collins,' the bartender handed them "
             "this tall gin, lemon, sugar, and soda highball.",
    "tip": "Shake or stir the gin, lemon juice, and syrup with ice first, then top with "
           "cold club soda in the glass.",
},
"Tommy's Margarita": {
    "about": "In 1990 at Tommy's Mexican Restaurant in San Francisco's Richmond District, "
             "Julio Bermejo replaced the triple sec in his house Margarita with agave "
             "nectar so guests could taste the 100%-agave tequila clearly. That three-part "
             "recipe of tequila, fresh lime, and agave syrup now sits on bar menus all "
             "over the world.",
    "tip": "Agave nectar is sweeter and thicker than 1:1 simple syrup, so measure it "
           "carefully and shake hard so it dissolves completely in the cold lime juice.",
},

# ============================ V - Z ========================================

"Vampiro": {
    "about": "Roadside stands in San Luis Soyatlán, Jalisco started pouring the deep "
             "blood-red Vampiro when fruit-stand vendor Oscar Hernández combined blanco "
             "tequila with citrus, grapefruit soda, and sangrita (the spicy tomato, orange, "
             "and chili chaser usually sipped beside neat tequila).",
},
"Vermouth Cocktail": {
    "about": "Before Dry Martinis pushed vermouth into the background, late-nineteenth-century "
             "American cocktail books routinely treated sweet or dry vermouth as the main "
             "pour in the glass, stirred cold with a couple of dashes of bitters and "
             "finished with a lemon peel. It is a great half-strength drink when you have "
             "a good bottle of vermouth open.",
    "tip": "Only make this with a fresh bottle of vermouth that has been kept in the "
           "refrigerator. With no gin or whiskey in the glass, stale vermouth has nowhere "
           "to hide.",
},
"Vesper": {
    "about": "In the opening chapters of Ian Fleming's 1953 novel Casino Royale, James "
             "Bond invents a strong Martini of three measures of Gordon's gin, one of "
             "vodka, and half a measure of Kina Lillet, then names it after double agent "
             "Vesper Lynd. Because the original quinine-bitter Kina Lillet was reformulated "
             "in 1986, Lillet Blanc or Cocchi Americano stands in today.",
    "tip": "Bond insists on shaking his until it is ice-cold, which clouds the drink and "
           "leaves tiny ice shards on top. Stirring it gives you a clearer, smoother glass.",
},
"Vieux Carré": {
    "about": "Head bartender Walter Bergeron created the Vieux Carré in 1938 at the "
             "Carousel Bar in New Orleans's Hotel Monteleone, naming it after the French "
             "term for the French Quarter ('Old Square'). Rye whiskey, cognac, sweet "
             "vermouth, Bénédictine, and two bitters mirror the different cultures that "
             "shaped the neighbourhood.",
    "tip": "Even though Bénédictine is only a small measure, do not leave it out. That "
           "little spoonful of honeyed herbs is what separates a Vieux Carré from a "
           "split-base Manhattan.",
},
"Vodka Gimlet": {
    "about": "By the 1960s and 1970s, as American drinkers drifted away from juniper-heavy "
             "gin toward vodka, the Vodka Gimlet overtook the original gin recipe in many "
             "restaurants and lounges. Without gin's botanicals, it is a pure, cold lime "
             "sour.",
    "tip": "Fresh lime juice and simple syrup work much better with vodka than bottled "
           "lime cordial, which can taste overly syrupy without gin to cut it.",
},
"Vodka Martini": {
    "about": "Early 1930s and 1940s bar guides called this a Kangaroo Cocktail, before the "
             "Vodka Martini took over American steakhouses in the second half of the "
             "twentieth century (helped along by 007 on the big screen). Because vodka "
             "brings chill and weight without botanical spice, you taste the dry vermouth "
             "and lemon twist or olive right up front.",
    "tip": "Use a fresh, refrigerated bottle of dry vermouth. When you pair it with "
           "neutral vodka, an old oxidized bottle of vermouth stands out immediately.",
},
"Vodka Sour": {
    "about": "Shaking neutral vodka in the classic sour ratio of spirit, fresh lemon juice, "
             "simple syrup, and optional egg white strips the sour down to pure texture "
             "and lemon tartness. It goes down easily and shows just how well the basic "
             "sour proportion works.",
    "tip": "If you use egg white, shake the ingredients without ice first for ten seconds, "
           "then add ice and shake hard again to get a thick foam top.",
},
"Ward Eight": {
    "about": "In 1898, Massachusetts politician Martin Lomasney ran for the state legislature "
             "backed by Boston's powerful Ward 8 Democratic machine, and bartenders at "
             "Locke-Ober Café mixed this drink in his honour the night before the polls "
             "even opened. It is a rye Whiskey Sour with small splashes of orange juice "
             "and pomegranate grenadine.",
},
"Whiskey Smash": {
    "about": "Jerry Thomas included the Whiskey Smash in his 1887 Bartender's Guide as "
             "'simply a Julep on a small plan,' before New York bartender Dale DeGroff "
             "modernised it at the Rainbow Room in the 1990s by muddling whole lemon "
             "wedges with the mint and sugar. It drinks halfway between a Mint Julep and "
             "a Whiskey Sour.",
    "tip": "Muddle cut lemon wedges skin-and-all in the bottom of the shaker rather than "
           "using pre-squeezed lemon juice. Pressing the rind adds lemon oil that makes "
           "the drink.",
},
"Whiskey Sour": {
    "about": "The first printed Whiskey Sour recipe appeared in Jerry Thomas's 1862 "
             "Bartender's Guide, though sailors had been mixing spirits, citrus, and "
             "sugar for decades before that. Once you know this three-part balance of "
             "whiskey, fresh lemon juice, and sweetener, half of all cocktail recipes "
             "make instant sense.",
    "tip": "Make sure your sugar or simple syrup dissolves completely in the lemon juice. "
           "If you add optional egg white, shake without ice first before shaking with ice.",
},
"White Lady": {
    "about": "Harry MacElhone's first 1919 London version of the White Lady was a bizarre "
             "mix of crème de menthe, Cointreau, and lemon juice. Once he took over Harry's "
             "New York Bar in Paris in 1929, he wisely swapped the mint liqueur for dry "
             "gin, creating what is essentially a Gin Sidecar.",
},
"White Russian": {
    "about": "Adding a float of cream or milk to a Black Russian first appeared in print "
             "in a 1965 Oakland Tribune newspaper ad for Kahlúa. It remained a quiet "
             "retro nightcap until Jeff Bridges drank nine of them as 'The Dude' in the "
             "1998 cult comedy The Big Lebowski.",
    "tip": "Pour the heavy cream slowly over the back of a spoon onto the top of the "
           "drink and let it marble down through the ice on its own.",
},
"Woo Woo": {
    "about": "Emerging from late-1980s American college bars and nightclubs alongside "
             "Sex on the Beach, the Woo Woo drops the orange juice and shakes vodka, "
             "peach schnapps, and cranberry juice over ice. It is fruity, tart, and easy "
             "to mix for a crowd.",
},
"Zombie": {
    "about": "Ernest Gantt (Don the Beachcomber) invented the Zombie in late-1934 Hollywood, "
             "reportedly to help a hungover regular get through a business flight, who "
             "came back days later and said he had felt like the living dead the whole "
             "trip. For years, Don's menu famously limited every customer to two Zombies "
             "apiece.",
    "tip": "Take that two-drink limit seriously. Between the white rum, gold rum, dark "
           "rum, and overproof 151 float, one glass holds nearly four standard drinks.",
},

}
