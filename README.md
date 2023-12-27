## TODO List:
- **pyd_pyper.py**
	- FIX PITCH DETECTION
	- Use dictionary of (supported) instrument ranges to set for YIN fmin fmax
	- Add arguments to support more customization
	- Add context-dependence to decrease keymap clutter
- **keymaps.py**
	- Make generic instrument keymaps for basic movement/attack
	- Make the process of setting keybinds more user-friendly
	- Make function to check that keymaps are valid (no duplicates, no accidental exclusions)
	- Give option to output current keymap to file for review with in-game keymap
	- Add more customization options (e.g. different scales, different instruments, different actions to different notes, etc.)
	- Add option to save keymaps to file for later use.  These files should be selectable from the command line
	- Add option to save keymap+instrument settings as a config to load immediately later
	- Add defaults for other instruments
- **Other**:
	- Make parser to read in instrument/keymap config files
	- Add logging for future debugging
	- Add subprogram to collect input data to analyze for best note-key matching

<hr>

## Project Overview:
**Pyd Pyper** (pronounced: Pied Piper) is a realtime pitch detection program that takes pitches input by an analog or digital instrument and converts them into keystrokes for use in manipulating a computer.  This program was built with Python 3.11.  Specifically, it is designed with gaming in mind, with the end goal being a fully implemented controller made from the user's instrument of choice and customized keymaps that dictate which note goes to which key(s).  The project is not quite (not at all) ready for release, but the people that are helping me test the program across OS's will need to be able to quickly pull files from the repo for testing, so this will be where that happens for now.

<hr>

## Using Pyd Pyper:
#### Requirements:
For **Pyd Pyper** to be able to function, there has to be a way for the sounds your instrument makes to get on to your computer.  This can be done with a microphone (for acoustic, or electric with an amp), or a hardware/software interface (only for electric).  There are many options within these two, and at this stage in development it's unclear if there are technical challenges to supporting many interfaces/input sources.

In theory, **Pyd Pyper** is OS agnostic, though this has yet to be completely tested.

#### Running the program:
**Pyd Pyper** is activated and configured primarily through the command line with a variety of flags.  The configs for individual instruments and their respective keymaps can be opened in your OS's default text editor from the command line.  They are also stored as plain text in `.../pyd_pyper/instruments/[instrument]/keymaps`, so the command line is not necessary to update them.  The help flag (`python pyd_pyper.py -h` or `python pyd_pyper.py --help`) will also list these options:

| Flag                | Shorthand | Description                                                                                      | Notes                                                                              |
| ------------------- | --------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| --input [input]     | -i        | Set the desired input device to [input].  If omitted, use the computer's default device as input | Optional                                                                           |
| --list              | -l        | List the available input devices at the time of running this program.                            | Optional. This flag will exit the program after printing the devices               |
| --inst [instrument] | N/A       | Set the desired instrument to read keymaps from                                                  | Can have a user-defined default.  If there is a default set, this flag is optional |
| --keymap [keymap]   | N/A       | Use [keymap] (found in `.../pyd_pyper/instruments/[instrument]/keymaps`)                         | Optional.  Keymaps can also have user-defined defaults pet-instrument              |

There will be many more flags added for further customizability as time goes on.

[INCOMPLETE]

<hr>

## Project Ingredients:
There are the third party python libraries that allow this project to happen:
- [Pynput for keyboard manipulation](https://pypi.org/project/pynput/)
- [Librosa for audio processing](https://pypi.org/project/librosa/)
- [PyAudio for inputting realtime audio data](https://pypi.org/project/PyAudio/)

<hr>

## Considerations:
- At least initially, the game to be tested with should have simple controls (I'm thinking Hollow Knight or Hades.  Minecraft may also be viable)
- Eventually, there should be a streamlined method of associating notes with an arbitrary (user-decided) keyboard input
- Should work regardless of timbre/tone.  That is, any instrument should be able to work with this program.
- For presenting the final product, I need to be able to record through my screen and my webcam simultaneously so people can more clearly see how I'm playing the game through the bass.  Recording bass audio alongside game audio is already trivial in OBS

<hr>

## Constraints on the controls:
Because of the nature of playing a string instrument, certain combinations of inputs, if mapped poorly, can mutually exclude each other.  This is because, unlike a controller, where the limit of how many inputs you can enter simultaneously is only limited by how many fingers/hands you have to dedicate to controlling the remote, with a bass if you put your finger down on the string, any note on that string lower than that note would be ignored by the program (since it wouldn't change the pitch being played).  This restriction boils down to a constraint on viable keybinds:

> **Inputs that are frequently made simultaneously cannot be on the same string**

So, whatever mapping ends up being used, two exclusive inputs  (for example, `Forward` + `Attack`) can **not** be on the same string, otherwise you would only be able to do one or the other.  It should be noted though, that the specific limitations imposed by the instrument depends on the kind of instrument you are playing.  Relatively speaking, string instruments have it easy because there is the possibility of simultaneous notes at all (because of having multiple strings).

It would be helpful to have a table of inputs that likely would mutually exclude each other in this way.  This depends on the game being played however, as the game dictates what kind of inputs often happen simultaneously.  Generally, though movement happens simultaneously with other inputs (except menus).  Navigating an inventory as if with a mouse would be tricky.  I think the most realistic option is to just start from the first inventory item and cycle through the list of items.  Maybe shortcuts can be added later (jump to top, jump to bottom, etc.).  Supporting multiple menus would also require keybinds for cycling those menus

<hr>

## Idea: context-dependent inputs
There would not be a need for separate inputs for inventory vs. menu if `pyd_pyper.py` knew if an inventory or a menu were opened.  This would make the eventual keymaps simpler and more intuitive as there would not be separate notes for each context.

Context dependence can be taken even further: each context can be thought of as its own keymap.  This means that menu navigation buttons only need to be playable on a fretboard when the menu is open, making space for more keymappings on the main fretboard.

<hr>

## Table of common actions
These are the typical actions of video games (at least, the ones that I play)

| **Movement**   | **Attack**       | **Inventory/Menu Nav** |
| -------------- | ---------------- | ---------------------- |
| Forward        | Primary attack   | Next in queue          |
| Backward       | Secondary attack | Previous in queue      |
| Left           | Special attack   | Jump to front          |
| Right          | Dash/Roll        | Jump to back           |
| Forward-Right  | X                | Open inventory         |
| Forward-Left   | X                | Open menu              |
| Backward-Right | X                | Use/Interact           |
| Backward-Left  | X                | X                      |

<hr>

## Exclusions
In general, all movement actions exclude all attack actions, and vice versa.  Meaning, movement and attack notes cannot be bound to the same string.  There are no exclusions for inventory/menu because these inputs generally only happen one at a time anyways.  ~~In the cases of games that do not disable movement in a menu, for simplicity we can just override the movement notes when in a  menu.  This has the effect of pausing movement without pausing gameplay, which may be annoying, but I'd rather work with this limitation than needing to bind separate keys.~~ <-- this is not a problem with context-dependence

<hr>

## Current keymaps
#### Keymap config syntax:
Keymaps are simply key:value pairs of a note and a desired actrion (**NOT** a keystroke).  Notes are notated in [Note][Octave] format, with a "#" as a sharp, and a "b" as a flat.  There should be no formatting in a keymap config aside from:

```
...
B3:forward
A#3:use
Cb2:dash
...
```
Eventually, I would like to add the ability to create custom actions for niche game environments, but for now a default set of actions should suffice.

**NOTE:** A keymap can only work as expected if the keybinds set in the game mirror those set in **Pyd Paper**.  This cannot be done in the program, so you will need to make these adjustments yourself.

#### Electric bass (prototype)

| 0              | 1              | 2                | 3              |
| -------------- | -------------- | ---------------- | -------------- |
| Open inventory | Open menu      | Use/Interact     |                |
| Primary Attack | Special Attack | Secondary Attack | Dash/roll      |
| Forward-Left   | Forward-Right  | Backward-Left    | Backward-Right |
| Forward        | Left           | Right            | Backward       |
| X              | X              | X                | X              |

<hr>

## Reference
#### 5-String Bass Fretboard (frets 0-4)
| 0   | 1    | 2    | 3    | 4    |
| --- | ---- | ---- | ---- | ---- |
| G2  | \#/b | A2   | \#/b | B2   |
| D2  | \#/b | E2   | F2   | \#/b |
| A1  | \#/b | B1   | C2   | \#/b |
| E1  | F1   | \#/b | G1   | \#/b |
| B0  | C1   | \#/b | D1   | \#/b |
