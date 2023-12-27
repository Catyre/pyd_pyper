#### TODO List:
- **pyd_pyper.py**
	- FIX PITCH DETECTION
	- Use dictionary of (supported) instrument ranges to set for YIN fmin fmax
	- Add arguments to support more customization

- **keybinds.py**
	- Make keybinds for basic movement/attack
	- Make the process of setting keybinds more user-friendly
	- Make function to check that keybinds are valid (no duplicates, no accidental exclusions)
	- Give option to output current keymap to file for review with in-game keymap
	- Add more customization options (e.g. different scales, different instruments, different actions to different buttons, etc.)
	- Add option to save keybinds to file for later use.  These files should be selectable from the command line
	- Add option to save keymap+instrument as a config to load immediately later
	- Add defaults for other instruments
- **Other**:
	- Make parser to read in instrument config files
	- Add logging for future debugging
	- Add subprogram to collect input data to analyze for best note-key matching

#### Project Overview:
`pyd_pyper.py`will run in background while playing games and receive audio data (from my bass via the hardware audio interface) and the received audio (for now, individual notes) will be input by the program.  The pitch detection library will determine what note is being played.  Once determined, it will output a keyboard event according to the note it detects, which the game will use as input for some action within the game.

#### Project Ingredients:
- [Pynput for keyboard manipulation](https://pypi.org/project/pynput/)
- [Librosa for audio processing](https://pypi.org/project/librosa/)
- [PyAudio for inputting realtime audio data](https://pypi.org/project/PyAudio/)

#### Considerations:
- At least initially, the game to be tested with should have simple controls (I'm thinking Hollow Knight or Hades.  Minecraft may also be viable)
- Eventually, there should be a streamlined method of associating notes with an arbitrary (user-decided) keyboard input
- Should work regardless of timbre/tone.  That is, any instrument should be able to work with this program.
- For presenting the final product, I need to be able to record through my screen and my webcam simultaneously so people can more clearly see how I'm playing the game through the bass.  Recording bass audio alongside game audio is already trivial in OBS

#### Constraints on the controls:
Because of the nature of playing a string instrument, certain combinations of inputs, if mapped poorly, can mutually exclude each other.  This is because, unlike a controller, where the limit of how many inputs you can enter simultaneously is only limited by how many fingers/hands you have to dedicate to controlling the remote, with a bass if you put your finger down on the string, any note on that string lower than that note would be ignored by the program (since it wouldn't change the pitch being played).  This restriction boils down to a constraint on viable keybinds:

> **Inputs that are frequently made simultaneously cannot be on the same string**

So, whatever mapping ends up being used, two inputs like, for example, "Move forward + Attack" can **not** be on the same string, otherwise you would only be able to do one or the other.  It should be noted though, that the specific limitations imposed by the instrument depends on the kind of instrument you are playing.  Relatively speaking, string instruments have it easy because there is the possibility of simultaneous notes at all (because of having multiple strings).

It would be helpful to have a table of inputs that likely would mutually exclude each other in this way.  This depends on the game being played however, as the game dictates what kind of inputs often happen simultaneously.  Generally, though movement happens simultaneously with other inputs (except menus).  Navigating an inventory as if with a mouse would be tricky.  I think the most realistic option is to just start from the first inventory item and cycle through the list of items.  Maybe shortcuts can be added later (jump to top, jump to bottom, etc.).  Supporting multiple menus would also require keybinds for cycling those menus

#### Idea: context-dependent inputs
There would not be a need for separate inputs for inventory vs. menu if `pyd_pyper.py` knew if an inventory or a menu were opened.  This would make the eventual keybinds more intuitive as there would not be separate notes for each context.

#### Table of common inputs
These are the typical inputs of video games (at least, the ones that I play)

| **Movement Inputs** | **Attack Inputs** | **Inventory/Menu Nav** |
| ------------------- | ----------------- | ---------------------- |
| Forward             | Primary attack    | Next in queue          |
| Backward            | Secondary attack  | Previous in queue      |
| Left                | Special attack    | Jump to front          |
| Right               | Dash/Roll         | Jump to back           |
| Forward-Right       | X                 | Open inventory         |
| Forward-Left        | X                 | Open menu              |
| Backward-Right      | X                 | Use/Interact           |
| Backward-Left       | X                 | X                      |

#### Exclusions
In general, all movement inputs exclude all attack movements, and vice versa.  Meaning, movement and attack buttons cannot be bound to the same string.  There are no exclusions for inventory/menu because these inputs generally only happen one at a time anyways.  In the cases of games that do not disable movement in a menu, for simplicity we can just override the movement notes when in a  menu.  This has the effect of pausing movement without pausing gameplay, which may be annoying, but I'd rather work with this limitation than needing to bind separate keys.

#### 5-String Bass Fretboard (frets 0-4)
| 0   | 1    | 2    | 3    | 4    |
| --- | ---- | ---- | ---- | ---- |
| G2  | \#/b | A2   | \#/b | B2   |
| D2  | \#/b | E2   | F2   | \#/b |
| A1  | \#/b | B1   | C2   | \#/b |
| E1  | F1   | \#/b | G1   | \#/b |
| B0  | C1   | \#/b | D1   | \#/b |


#### Prototype keymapping (bass only [for now])
| 0              | 1                 | 2                | 3              |
| -------------- | ----------------- | ---------------- | -------------- |
| Open inventory | Open menu         | Use/Interact     |                |
| Jump to back   | Previous in queue | Next in queue    | Jump to front  |
| Primary Attack | Special Attack    | Secondary Attack | Dash/roll      |
| Forward-Left   | Forward-Right     | Backward-Left    | Backward-Right |
| Forward        | Left              | Right            | Backward       |
