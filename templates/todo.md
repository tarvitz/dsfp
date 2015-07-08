# Todo



## Gestures
What are their values, where are they saved? Where is equipped gestures saved?
What decides if the speech option to learn a gestures is available?


## CharacterParams
Most of these should be testable by either creating a new character and setting all sliders to an extremely low value except one. It is time consuming though.
One could possibly instead edit the save file value and see the result ingame?

## Backpack size
Everything I've seen indicates that 2048 is max size. But theoretically it could be a dynamic sized object, just that it has to have a reason to increase the size. Try adding 2048 different items to the backpack and see what happens?

## Character stats

* What is the UnknownCharStat? Does it ever change?
* Is sin correct? All saves I have lack sin, so I cant verify.

## Pack

Many slots have an index, relating to the index part of the backpack struct. The indexes are variable and unique for each playthrough, so you can't depend on them to stay consistent. Maybe we could build a local array while parsing the rest of the file that maps those indexes to actual item ids, and use a read function to display which item the represent?

The exact relation between item index and gear slot selection needs to be examined and documented. 

## Backpack & bottomless box
The partiallyusedbox struct represent the inventory, the inventory can have gaps, if backpack size is 60 you are not guaranteed that all those 60 items are at the beginning of the array. This could possibly be handled better?

## Attunement
Is attunement slot count inferred from attunement stat or is it a number somewhere? Can you get more attunement slots despite not leveling up by simply writing data to the empty parts in the attunementslots array? Can you write any spell you want into the slots or do you have to own them? Can you increase usecount beyond normal size? What is the field size for these fields?



## Bonfires

What determines if a bonfire is lit? Can you light bonfires by writing to the save file? If each bonfire is toggled by one bit, 32 bits wont fit all bonfires, where are the rest? Are they the special bonfires that are not available until bosses have been defeated etc? Note that the burg bonfire toggle is not found in the marked bitfield.


## Onlinedata
Exactly how are the different parts of these fields mapped?

## Unknown area
Is this actually not just random data?