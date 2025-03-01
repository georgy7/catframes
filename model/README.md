# UI "backend"

This is a model in about the same sense as the model in MVC.

This directory is a suitable place for:

- validation of user input
- storing task statuses
- reading and writing configuration (possible)

The following things must **not** be in this place:

- localization files
- layout in any form
- multithreaded code, including inter-thread communication
- spawning of child processes
- using any parts of any UI framework

You should avoid accessing UI from the model, even through abstractions.

The user interface is the main loop.

In other words, UI uses this model, not the other way around.

---

I would also recommend avoiding inheritance, templates, and STL.

It's just not necessary. Everything is too simple here.
