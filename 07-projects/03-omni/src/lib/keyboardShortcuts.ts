/**
 * Keyboard shortcut definitions — Figma-parity set.
 *
 * `keys` outer array = alternative chords that trigger the same action.
 * `keys` inner array = individual key badges rendered left-to-right in a chord.
 *
 * Mac modifier symbols:
 *   ⌘ Command   ⌥ Option/Alt   ⇧ Shift   ⌃ Control
 *   ↩ Enter   ⎋ Escape   ⌫ Backspace/Delete   ⇥ Tab   ␣ Space
 *
 * `reserved` = shortcut is recognized/blocked but feature not yet built.
 */

export interface Shortcut {
  label: string;
  keys: string[][];   // outer = alternatives, inner = chord badges
  note?: string;      // context e.g. "(while resizing)"
  reserved?: boolean; // feature not yet implemented — shown dimmed
}

export interface ShortcutGroup {
  title: string;
  shortcuts: Shortcut[];
}

export const SHORTCUT_GROUPS: ShortcutGroup[] = [
  // ─── Essential ──────────────────────────────────────────────────────────────
  {
    title: "Essential",
    shortcuts: [
      { label: "Show/Hide UI",        keys: [["⌘", "\\"]] },
      { label: "Keyboard shortcuts",  keys: [["?"]] },
      { label: "Actions",             keys: [["⌘", "K"]], reserved: true },
      { label: "Pick color",          keys: [["⌃", "C"]], reserved: true },
    ],
  },

  // ─── Tools ──────────────────────────────────────────────────────────────────
  {
    title: "Tools",
    shortcuts: [
      { label: "Move / Select",   keys: [["V"]] },
      { label: "Hand",            keys: [["H"]] },
      { label: "Frame",           keys: [["F"]] },
      { label: "Rectangle",       keys: [["R"]] },
      { label: "Text",            keys: [["T"]] },
      { label: "Pen",             keys: [["P"]] },
      { label: "Pencil",          keys: [["⇧", "P"]], reserved: true },
      { label: "Ellipse",         keys: [["O"]], reserved: true },
      { label: "Line",            keys: [["L"]], reserved: true },
      { label: "Arrow",           keys: [["⇧", "L"]], reserved: true },
      { label: "Slice",           keys: [["S"]], reserved: true },
      { label: "Comments",        keys: [["C"]], reserved: true },
      { label: "Annotation",      keys: [["Y"]], reserved: true },
    ],
  },

  // ─── View ───────────────────────────────────────────────────────────────────
  {
    title: "View",
    shortcuts: [
      { label: "Show/Hide UI",          keys: [["⌘", "\\"]] },
      { label: "Open layers panel",     keys: [["⌥", "1"]] },
      { label: "Show assets",           keys: [["⌥", "2"]] },
      { label: "Tokens",                keys: [["⌥", "3"]] },
      { label: "Open design panel",     keys: [["⌥", "8"]], reserved: true },
      { label: "Open prototype panel",  keys: [["⌥", "9"]], reserved: true },
      { label: "Rulers",                keys: [["⇧", "R"]], reserved: true },
      { label: "Show outlines",         keys: [["⇧", "⌘", "O"]], reserved: true },
      { label: "Pixel preview",         keys: [["⇧", "⌘", "P"]], reserved: true },
      { label: "Layout guides",         keys: [["⇧", "G"]], reserved: true },
      { label: "Pixel grid",            keys: [["⇧", "'"]], reserved: true },
      { label: "Multiplayer cursors",   keys: [["⌥", "⌘", "\\"]], reserved: true },
    ],
  },

  // ─── Zoom ───────────────────────────────────────────────────────────────────
  {
    title: "Zoom",
    shortcuts: [
      { label: "Pan",                    keys: [["␣"]], note: "+ drag" },
      { label: "Zoom in",                keys: [["⌘", "+"]] },
      { label: "Zoom out",               keys: [["⌘", "−"]] },
      { label: "Zoom to 100%",           keys: [["⌘", "0"]] },
      { label: "Zoom to fit",            keys: [["⇧", "1"]] },
      { label: "Zoom to selection",      keys: [["⇧", "2"]] },
      { label: "Zoom to next frame",     keys: [["N"]] },
      { label: "Zoom to previous frame", keys: [["⇧", "N"]] },
      { label: "Previous page",          keys: [["Page Up"]], reserved: true },
      { label: "Next page",              keys: [["Page Down"]], reserved: true },
    ],
  },

  // ─── Selection ──────────────────────────────────────────────────────────────
  {
    title: "Selection",
    shortcuts: [
      { label: "Select all",            keys: [["⌘", "A"]] },
      { label: "Select none",           keys: [["⎋"]] },
      { label: "Select inverse",        keys: [["⇧", "⌘", "A"]], reserved: true },
      { label: "Deep select",           keys: [["⌘"]], note: "+ click" },
      { label: "Select children",       keys: [["↩"]] },
      { label: "Select parent",         keys: [["⎋"], ["\\"]],  note: "from child" },
      { label: "Select next sibling",   keys: [["⇥"]] },
      { label: "Select prev sibling",   keys: [["⇧", "⇥"]] },
      { label: "Select matching layers",keys: [["⌥", "⌘", "A"]], reserved: true },
      { label: "Group selection",       keys: [["⌘", "G"]] },
      { label: "Ungroup selection",     keys: [["⇧", "⌘", "G"], ["⌘", "⌫"]] },
      { label: "Frame selection",       keys: [["⌥", "⌘", "G"]] },
      { label: "Show/Hide selection",   keys: [["⇧", "⌘", "H"]] },
      { label: "Lock/Unlock selection", keys: [["⇧", "⌘", "L"]] },
    ],
  },

  // ─── Edit ───────────────────────────────────────────────────────────────────
  {
    title: "Edit",
    shortcuts: [
      { label: "Copy",                 keys: [["⌘", "C"]] },
      { label: "Cut",                  keys: [["⌘", "X"]] },
      { label: "Paste",                keys: [["⌘", "V"]] },
      { label: "Paste over selection", keys: [["⇧", "⌘", "V"]], reserved: true },
      { label: "Paste to replace",     keys: [["⇧", "⌘", "R"]], reserved: true },
      { label: "Duplicate",            keys: [["⌘", "D"]] },
      { label: "Undo",                 keys: [["⌘", "Z"]], reserved: true },
      { label: "Redo",                 keys: [["⇧", "⌘", "Z"]], reserved: true },
      { label: "Rename",               keys: [["⌘", "R"]], reserved: true },
      { label: "Find",                 keys: [["⌘", "F"]], reserved: true },
      { label: "Export",               keys: [["⇧", "⌘", "E"]], reserved: true },
      { label: "Copy as PNG",          keys: [["⇧", "⌘", "C"]], reserved: true },
      { label: "Copy properties",      keys: [["⌥", "⌘", "C"]], reserved: true },
      { label: "Paste properties",     keys: [["⌥", "⌘", "V"]], reserved: true },
    ],
  },

  // ─── Transform ──────────────────────────────────────────────────────────────
  {
    title: "Transform",
    shortcuts: [
      { label: "Flip horizontal",        keys: [["⇧", "H"]] },
      { label: "Flip vertical",          keys: [["⇧", "V"]] },
      { label: "Edit shape or image",    keys: [["↩"]] },
      { label: "Place image/video",      keys: [["⇧", "⌘", "K"]], reserved: true },
      { label: "Use as mask",            keys: [["⌃", "⌘", "M"]], reserved: true },
      { label: "Set opacity to 10–90%",  keys: [["1"]], note: "… 9" },
      { label: "Set opacity to 100%",    keys: [["0"]] },
      { label: "Set opacity to 0%",      keys: [["0", "0"]] },
      { label: "Resize from center",     keys: [["⌥"]], note: "(while resizing)" },
      { label: "Resize proportionally",  keys: [["⇧"]], note: "(while resizing)" },
      { label: "Crop / ignore constraints", keys: [["⌘"]], note: "(while resizing)", reserved: true },
    ],
  },

  // ─── Arrange ────────────────────────────────────────────────────────────────
  {
    title: "Arrange",
    shortcuts: [
      { label: "Bring forward",                  keys: [["⌘", "]"]] },
      { label: "Send backward",                  keys: [["⌘", "["]] },
      { label: "Bring to front",                 keys: [["]"]] },
      { label: "Send to back",                   keys: [["["]] },
      { label: "Align left",                     keys: [["⌥", "A"]] },
      { label: "Align right",                    keys: [["⌥", "D"]] },
      { label: "Align top",                      keys: [["⌥", "W"]] },
      { label: "Align bottom",                   keys: [["⌥", "S"]] },
      { label: "Align horizontal centers",       keys: [["⌥", "H"]] },
      { label: "Align vertical centers",         keys: [["⌥", "V"]] },
      { label: "Distribute horizontal spacing",  keys: [["⌃", "⌥", "H"]] },
      { label: "Distribute vertical spacing",    keys: [["⌃", "⌥", "V"]] },
      { label: "Tidy up",                        keys: [["⌃", "⌥", "T"]], reserved: true },
      { label: "Add auto layout",                keys: [["⇧", "A"]], reserved: true },
      { label: "Remove auto layout",             keys: [["⌥", "⇧", "A"]], reserved: true },
    ],
  },

  // ─── Text ───────────────────────────────────────────────────────────────────
  {
    title: "Text",
    shortcuts: [
      { label: "Bold",                  keys: [["⌘", "B"]], reserved: true },
      { label: "Italic",               keys: [["⌘", "I"]], reserved: true },
      { label: "Underline",            keys: [["⌘", "U"]], reserved: true },
      { label: "Strikethrough",        keys: [["⇧", "⌘", "X"]], reserved: true },
      { label: "Create link",          keys: [["⇧", "⌘", "U"]], reserved: true },
      { label: "Bulleted list",        keys: [["⇧", "⌘", "7"]], reserved: true },
      { label: "Numbered list",        keys: [["⇧", "⌘", "8"]], reserved: true },
      { label: "Align left",           keys: [["⌥", "⌘", "L"]], reserved: true },
      { label: "Align center",         keys: [["⌥", "⌘", "T"]], reserved: true },
      { label: "Align right",          keys: [["⌥", "⌘", "R"]], reserved: true },
      { label: "Justify",              keys: [["⌥", "⌘", "J"]], reserved: true },
      { label: "Increase font size",   keys: [["⇧", "⌘", ">"]], reserved: true },
      { label: "Decrease font size",   keys: [["⇧", "⌘", "<"]], reserved: true },
      { label: "Increase font weight", keys: [["⌥", "⌘", ">"]], reserved: true },
      { label: "Decrease font weight", keys: [["⌥", "⌘", "<"]], reserved: true },
      { label: "Increase letter spacing", keys: [["⌥", ">"]], reserved: true },
      { label: "Decrease letter spacing", keys: [["⌥", "<"]], reserved: true },
      { label: "Increase line height", keys: [["⌥", "⇧", ">"]], reserved: true },
      { label: "Decrease line height", keys: [["⌥", "⇧", "<"]], reserved: true },
    ],
  },

  // ─── Vector editing ─────────────────────────────────────────────────────────
  {
    title: "Vector editing",
    shortcuts: [
      { label: "Pen tool",            keys: [["P"]] },
      { label: "Pencil tool",         keys: [["⇧", "P"]], reserved: true },
      { label: "Paint bucket",        keys: [["⇧", "B"]], reserved: true },
      { label: "Bend tool",           keys: [["⌘"]], note: "(while in pen)", reserved: true },
      { label: "Remove fill",         keys: [["⌥", "/"]] },
      { label: "Remove stroke",       keys: [["⇧", "/"]] },
      { label: "Swap fill and stroke",keys: [["⇧", "X"]] },
      { label: "Outline stroke",      keys: [["⌥", "⌘", "O"]], reserved: true },
      { label: "Flatten",             keys: [["⌥", "⇧", "F"]], reserved: true },
      { label: "Join selection",      keys: [["⌘", "J"]], reserved: true },
      { label: "Smooth join",         keys: [["⇧", "⌘", "J"]], reserved: true },
      { label: "Delete and heal",     keys: [["⇧", "⌫"]], reserved: true },
    ],
  },

  // ─── Components ─────────────────────────────────────────────────────────────
  {
    title: "Components",
    shortcuts: [
      { label: "Create component",    keys: [["⌥", "⌘", "K"]], reserved: true },
      { label: "Detach instance",     keys: [["⌥", "⌘", "B"]], reserved: true },
      { label: "Component search",    keys: [["⇧", "I"]], reserved: true },
      { label: "Swap instance",       keys: [["⌥"]], note: "(while inserting)", reserved: true },
    ],
  },

  // ─── Nudge ──────────────────────────────────────────────────────────────────
  {
    title: "Nudge",
    shortcuts: [
      { label: "Nudge 1px",   keys: [["↑"], ["↓"], ["←"], ["→"]] },
      { label: "Nudge 10px",  keys: [["⇧", "↑"], ["⇧", "↓"], ["⇧", "←"], ["⇧", "→"]] },
    ],
  },
];
